/**
 * Auth composable — session-token + WebAuthn passkey management.
 *
 * Login flow:
 *  1. Password login → if user has no passkey + browser supports it,
 *     token goes to _pendingToken (awaitingPasskeySetup = true).
 *     The map is NOT shown yet; a setup screen appears instead.
 *  2. User registers passkey (or skips) → confirmLogin() moves
 *     _pendingToken → _token → map appears.
 *  3. Passkey login → sets _token directly, no intermediate screen.
 */

import { ref, computed } from 'vue'

const SESSION_KEY = 'wc_session'

const _token              = ref<string | null>(sessionStorage.getItem(SESSION_KEY))
const _pendingToken       = ref<string | null>(null)   // waiting for passkey setup decision
const _sessionExpired     = ref(false)
const _hasPasskey         = ref(true)
const _currentEmail       = ref<string | null>(null)

// ── Base64url helpers ─────────────────────────────────────────────────────────

function bufToBase64url(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf)
  let str = ''
  for (const b of bytes) str += String.fromCharCode(b)
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

function base64urlToBuf(b64: string): ArrayBuffer {
  const padded = b64 + '==='.slice(0, (4 - b64.length % 4) % 4)
  const b64Std = padded.replace(/-/g, '+').replace(/_/g, '/')
  const binary = atob(b64Std)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  return bytes.buffer
}

// ── Composable ────────────────────────────────────────────────────────────────

export function useAuth() {
  const isAuthenticated    = computed(() => !!_token.value)
  const awaitingPasskeySetup = computed(() => !!_pendingToken.value)
  const hasPasskey         = computed(() => _hasPasskey.value)
  const currentEmail       = computed(() => _currentEmail.value)
  const passkeySupported   = computed(() =>
    typeof window !== 'undefined' && !!window.PublicKeyCredential
  )

  // ── Password login ──────────────────────────────────────────────────────────

  async function login(email: string, password: string): Promise<void> {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error((data as { detail?: string }).detail ?? 'Error de autenticación')
    }
    const data = await res.json() as { token: string; has_passkey: boolean }
    _currentEmail.value = email
    _hasPasskey.value = data.has_passkey

    if (!data.has_passkey && window.PublicKeyCredential) {
      // Show passkey setup screen before revealing the map
      _pendingToken.value = data.token
    } else {
      _token.value = data.token
      sessionStorage.setItem(SESSION_KEY, data.token)
    }
    _sessionExpired.value = false
  }

  /** Called after the user registers or skips passkey setup. Reveals the map. */
  function confirmLogin(): void {
    if (_pendingToken.value) {
      _token.value = _pendingToken.value
      sessionStorage.setItem(SESSION_KEY, _pendingToken.value)
      _pendingToken.value = null
    }
  }

  // ── Passkey login ───────────────────────────────────────────────────────────

  async function loginWithPasskey(): Promise<void> {
    const beginRes = await fetch('/api/auth/passkey/login/begin', { method: 'POST' })
    if (!beginRes.ok) throw new Error('Error iniciando autenticación')
    const { challenge_id, ...options } = await beginRes.json()

    const publicKey: PublicKeyCredentialRequestOptions = {
      ...options,
      challenge: base64urlToBuf(options.challenge),
      allowCredentials: (options.allowCredentials ?? []).map((c: { id: string; type: string }) => ({
        ...c, id: base64urlToBuf(c.id),
      })),
    }

    let credential: PublicKeyCredential
    try {
      credential = await navigator.credentials.get({ publicKey }) as PublicKeyCredential
    } catch {
      throw new Error('Autenticación cancelada')
    }
    if (!credential) throw new Error('No se pudo autenticar')

    const assertion = credential.response as AuthenticatorAssertionResponse

    const completeRes = await fetch('/api/auth/passkey/login/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        challenge_id,
        credential: {
          id: credential.id,
          rawId: bufToBase64url(credential.rawId),
          response: {
            clientDataJSON:    bufToBase64url(assertion.clientDataJSON),
            authenticatorData: bufToBase64url(assertion.authenticatorData),
            signature:         bufToBase64url(assertion.signature),
            userHandle: assertion.userHandle ? bufToBase64url(assertion.userHandle) : null,
          },
          type: credential.type,
        },
      }),
    })
    if (!completeRes.ok) {
      const err = await completeRes.json().catch(() => ({}))
      throw new Error((err as { detail?: string }).detail ?? 'Autenticación fallida')
    }

    const { token } = await completeRes.json() as { token: string }
    _token.value = token
    _hasPasskey.value = true
    _currentEmail.value = null
    sessionStorage.setItem(SESSION_KEY, token)
    _sessionExpired.value = false
  }

  // ── Passkey registration ────────────────────────────────────────────────────

  async function registerPasskey(email: string): Promise<void> {
    const beginRes = await authFetch('/api/auth/passkey/register/begin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
    if (!beginRes.ok) {
      const err = await beginRes.json().catch(() => ({}))
      throw new Error((err as { detail?: string }).detail ?? 'Error iniciando registro')
    }
    const options = await beginRes.json()

    const publicKey: PublicKeyCredentialCreationOptions = {
      ...options,
      challenge: base64urlToBuf(options.challenge),
      user: { ...options.user, id: base64urlToBuf(options.user.id) },
      excludeCredentials: (options.excludeCredentials ?? []).map(
        (c: { id: string; type: string }) => ({ ...c, id: base64urlToBuf(c.id) }),
      ),
    }

    let credential: PublicKeyCredential
    try {
      credential = await navigator.credentials.create({ publicKey }) as PublicKeyCredential
    } catch {
      throw new Error('Registro cancelado')
    }
    if (!credential) throw new Error('No se pudo crear la credencial')

    const attestation = credential.response as AuthenticatorAttestationResponse

    const completeRes = await authFetch('/api/auth/passkey/register/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: credential.id,
        rawId: bufToBase64url(credential.rawId),
        response: {
          clientDataJSON:    bufToBase64url(attestation.clientDataJSON),
          attestationObject: bufToBase64url(attestation.attestationObject),
          transports: (attestation as AuthenticatorAttestationResponse & { getTransports?: () => string[] }).getTransports?.() ?? [],
        },
        type: credential.type,
      }),
    })
    if (!completeRes.ok) {
      const err = await completeRes.json().catch(() => ({}))
      throw new Error((err as { detail?: string }).detail ?? 'Error completando el registro')
    }
    _hasPasskey.value = true
  }

  // ── Change password ──────────────────────────────────────────────────────────

  async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
    const res = await authFetch('/api/auth/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error((data as { detail?: string }).detail ?? 'Error al cambiar contraseña')
    }
  }

  // ── Delete passkey ───────────────────────────────────────────────────────────

  async function deletePasskey(password: string): Promise<void> {
    const res = await authFetch('/api/auth/passkey', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error((err as { detail?: string }).detail ?? 'Error al eliminar passkey')
    }
    _hasPasskey.value = false
  }

  // ── Logout ──────────────────────────────────────────────────────────────────

  async function logout(): Promise<void> {
    if (_token.value) {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${_token.value}` },
      }).catch(() => { /* fire-and-forget */ })
    }
    _token.value = null
    _pendingToken.value = null
    _hasPasskey.value = true
    _currentEmail.value = null
    _sessionExpired.value = false
    sessionStorage.removeItem(SESSION_KEY)
  }

  // ── Authenticated fetch ─────────────────────────────────────────────────────

  async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
    // Use pending token during the passkey setup phase
    const token = _token.value ?? _pendingToken.value
    const res = await fetch(url, {
      ...options,
      headers: {
        ...(options.headers as Record<string, string> | undefined ?? {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })
    if (res.status === 401 && _token.value) {
      _token.value = null
      sessionStorage.removeItem(SESSION_KEY)
      _sessionExpired.value = true
    }
    return res
  }

  return {
    isAuthenticated,
    awaitingPasskeySetup,
    sessionExpired: _sessionExpired,
    hasPasskey,
    currentEmail,
    passkeySupported,
    login,
    confirmLogin,
    loginWithPasskey,
    registerPasskey,
    changePassword,
    deletePasskey,
    logout,
    authFetch,
  }
}
