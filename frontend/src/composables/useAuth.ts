/**
 * Auth composable — session-token management.
 *
 * Security model:
 *  - The WiseCity password is NEVER stored in the browser.
 *  - On login the backend validates credentials and returns a random token
 *    (256-bit entropy, cryptographically secure).
 *  - The token is stored in sessionStorage (cleared when the tab closes;
 *    not accessible from other origins).
 *  - All API calls attach the token as `Authorization: Bearer <token>`.
 *  - A 401 response clears the token and triggers the login screen.
 */

import { ref, computed } from 'vue'

const SESSION_KEY = 'wc_session'

// Module-level singletons — shared across all useAuth() calls.
const _token = ref<string | null>(sessionStorage.getItem(SESSION_KEY))
const _sessionExpired = ref(false)

export function useAuth() {
  const isAuthenticated = computed(() => !!_token.value)

  // ── Login ────────────────────────────────────────────────────────────────

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
    const data = await res.json() as { token: string }
    _token.value = data.token
    sessionStorage.setItem(SESSION_KEY, data.token)
    _sessionExpired.value = false
  }

  // ── Logout ───────────────────────────────────────────────────────────────

  async function logout(): Promise<void> {
    if (_token.value) {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${_token.value}` },
      }).catch(() => { /* fire-and-forget */ })
    }
    _token.value = null
    _sessionExpired.value = false
    sessionStorage.removeItem(SESSION_KEY)
  }

  // ── Authenticated fetch ──────────────────────────────────────────────────

  async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const res = await fetch(url, {
      ...options,
      headers: {
        ...(options.headers as Record<string, string> | undefined ?? {}),
        ...(_token.value ? { Authorization: `Bearer ${_token.value}` } : {}),
      },
    })
    if (res.status === 401) {
      _token.value = null
      sessionStorage.removeItem(SESSION_KEY)
      _sessionExpired.value = true
    }
    return res
  }

  return {
    isAuthenticated,
    sessionExpired: _sessionExpired,
    login,
    logout,
    authFetch,
  }
}
