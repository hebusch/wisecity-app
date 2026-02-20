<template>
  <div class="login-shell">
    <!-- Background grid -->
    <div class="login-bg" aria-hidden="true">
      <div class="bg-grid" />
      <div class="bg-glow" />
    </div>

    <div class="login-card">
      <!-- Logo / brand -->
      <div class="brand">
        <div class="brand__icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
            <path d="M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>
          </svg>
        </div>
        <div>
          <h1 class="brand__name">WiseCity</h1>
          <p class="brand__sub">GPS Tracker</p>
        </div>
      </div>

      <!-- Form -->
      <form class="form" @submit.prevent="handleLogin">
        <div class="form__group">
          <label class="form__label" for="email">Correo electrónico</label>
          <div class="form__input-wrap">
            <svg class="form__icon" width="15" height="15" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            <input
              id="email"
              v-model="email"
              type="email"
              class="form__input"
              placeholder="tu@email.com"
              autocomplete="username"
              required
              :disabled="loading"
            />
          </div>
        </div>

        <div class="form__group">
          <label class="form__label" for="password">Contraseña</label>
          <div class="form__input-wrap">
            <svg class="form__icon" width="15" height="15" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <rect x="3" y="11" width="18" height="11" rx="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form__input"
              placeholder="••••••••"
              autocomplete="current-password"
              required
              :disabled="loading"
            />
            <button
              type="button"
              class="form__eye"
              @click="showPassword = !showPassword"
              :title="showPassword ? 'Ocultar' : 'Mostrar'"
            >
              <svg v-if="!showPassword" width="14" height="14" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>

        <p v-if="errorMsg" class="form__error">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ errorMsg }}
        </p>

        <button type="submit" class="form__submit" :disabled="loading">
          <span v-if="loading" class="submit-spinner">
            <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="M21 12a9 9 0 1 1-6.22-8.56"/>
            </svg>
            Conectando…
          </span>
          <span v-else>
            Iniciar sesión
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </span>
        </button>
      </form>

      <p class="login-note">
        Tus credenciales nunca se almacenan en el dispositivo. Solo se guarda un token de sesión cifrado que se elimina al cerrar la pestaña.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'

const { login } = useAuth()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Error desconocido'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Shell ──────────────────────────────────────────────────── */
.login-shell {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  z-index: 9999;
  padding: 20px;
}

/* ── Animated background ────────────────────────────────────── */
.login-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.5;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 100%);
}

.bg-glow {
  position: absolute;
  top: 30%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(ellipse, var(--accent-glow) 0%, transparent 70%);
  animation: glow-pulse 4s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.4; transform: translate(-50%, -50%) scale(1); }
  50%       { opacity: 0.7; transform: translate(-50%, -50%) scale(1.08); }
}

/* ── Card ───────────────────────────────────────────────────── */
.login-card {
  position: relative;
  width: 100%;
  max-width: 400px;
  background: var(--surface-hi);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 36px 32px 28px;
  box-shadow: var(--shadow-lg);
  animation: card-in 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes card-in {
  from { opacity: 0; transform: translateY(16px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* Accent top border */
.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 15%;
  right: 15%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  border-radius: 1px;
}

/* ── Brand ──────────────────────────────────────────────────── */
.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 32px;
}

.brand__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--accent-dim);
  border: 1px solid var(--border-accent);
  border-radius: 14px;
  color: var(--accent);
  flex-shrink: 0;
}

.brand__name {
  font-family: var(--f-display);
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--txt);
  line-height: 1;
}

.brand__sub {
  font-size: 12px;
  color: var(--txt-dim);
  margin-top: 3px;
  font-weight: 500;
}

/* ── Form ───────────────────────────────────────────────────── */
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form__group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form__label {
  font-size: 12px;
  font-weight: 600;
  color: var(--txt-dim);
  letter-spacing: 0.03em;
}

.form__input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.form__icon {
  position: absolute;
  left: 12px;
  color: var(--txt-dim);
  pointer-events: none;
  flex-shrink: 0;
}

.form__input {
  width: 100%;
  padding: 11px 42px 11px 38px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  font-family: var(--f-body);
  font-size: 16px;
  color: var(--txt);
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form__input::placeholder {
  color: var(--txt-dim);
  opacity: 0.6;
}

.form__input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}

.form__input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form__eye {
  position: absolute;
  right: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--txt-dim);
  border-radius: var(--r-sm);
  transition: color 0.15s ease;
}
.form__eye:hover { color: var(--accent); }

/* ── Error ──────────────────────────────────────────────────── */
.form__error {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  color: var(--danger);
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--r-sm);
  padding: 9px 12px;
}

/* ── Submit button ──────────────────────────────────────────── */
.form__submit {
  margin-top: 4px;
  width: 100%;
  padding: 13px;
  background: var(--accent);
  border: none;
  border-radius: var(--r-md);
  font-family: var(--f-body);
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.15s ease, transform 0.12s ease, opacity 0.15s ease;
  letter-spacing: 0.02em;
}

.form__submit:hover:not(:disabled) {
  background: color-mix(in srgb, var(--accent) 85%, white);
  transform: translateY(-1px);
}

.form__submit:active:not(:disabled) {
  transform: translateY(0);
}

.form__submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.submit-spinner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spin {
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Security note ──────────────────────────────────────────── */
.login-note {
  margin-top: 20px;
  font-size: 11px;
  color: var(--txt-dim);
  text-align: center;
  line-height: 1.6;
  padding: 0 4px;
}

/* ── Mobile ─────────────────────────────────────────────────── */
@media (max-width: 440px) {
  .login-card {
    padding: 28px 20px 22px;
    border-radius: 20px;
  }
}
</style>
