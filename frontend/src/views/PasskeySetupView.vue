<template>
  <div class="setup-shell">
    <div class="setup-bg" aria-hidden="true">
      <div class="bg-grid" />
      <div class="bg-glow" />
    </div>

    <div class="setup-card">
      <Transition name="card-swap" mode="out-in">

        <!-- ── Normal state ──────────────────────────────────── -->
        <div v-if="!success" key="form" class="setup-content">
          <div class="setup-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>

          <h2 class="setup-title">Acceso biométrico</h2>
          <p class="setup-sub">
            Activa Face ID, Touch ID o huella para entrar sin contraseña la próxima vez.
          </p>

          <div class="user-chip">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            {{ email }}
          </div>

          <p v-if="errorMsg" class="setup-error">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ errorMsg }}
          </p>

          <button class="activate-btn" :disabled="loading" @click="handleActivate">
            <span v-if="loading" class="spinner-row">
              <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                <path d="M21 12a9 9 0 1 1-6.22-8.56"/>
              </svg>
              Activando…
            </span>
            <span v-else class="btn-row">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
              Activar Passkey
            </span>
          </button>

          <button class="skip-btn" :disabled="loading" @click="handleSkip">
            Ahora no, continuar sin activar
          </button>
        </div>

        <!-- ── Success state ─────────────────────────────────── -->
        <div v-else key="success" class="setup-success">
          <div class="success-ring-wrap">
            <svg class="success-svg" width="96" height="96" viewBox="0 0 64 64" fill="none">
              <circle
                class="s-circle"
                cx="32" cy="32" r="27"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"
                stroke-dasharray="170" stroke-dashoffset="170"
              />
              <polyline
                class="s-check"
                points="19,33 28,42 45,22"
                stroke="currentColor" stroke-width="3.5"
                stroke-linecap="round" stroke-linejoin="round"
                stroke-dasharray="46" stroke-dashoffset="46"
              />
            </svg>
          </div>
          <h2 class="success-title">¡Listo!</h2>
          <p class="success-sub">Acceso biométrico activado</p>
        </div>

      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'

const props = defineProps<{ email: string }>()

const { registerPasskey, confirmLogin } = useAuth()

const loading  = ref(false)
const errorMsg = ref('')
const success  = ref(false)

async function handleActivate() {
  errorMsg.value = ''
  loading.value = true
  try {
    await registerPasskey(props.email)
    success.value = true
    setTimeout(() => confirmLogin(), 1800)
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Error al activar'
  } finally {
    loading.value = false
  }
}

function handleSkip() {
  confirmLogin()
}
</script>

<style scoped>
.setup-shell {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  z-index: 9999;
  padding: 20px;
}

.setup-bg {
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

/* ── Card ───────────────────────────────────────────────── */
.setup-card {
  position: relative;
  width: 100%;
  max-width: 380px;
  background: var(--surface-hi);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 40px 32px 32px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: card-in 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
  overflow: hidden;
}

@keyframes card-in {
  from { opacity: 0; transform: translateY(16px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.setup-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 15%;
  right: 15%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  border-radius: 1px;
}

/* ── Normal state content ───────────────────────────────── */
.setup-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  width: 100%;
}

.setup-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: var(--accent-dim);
  border: 1.5px solid var(--border-accent);
  border-radius: 20px;
  color: var(--accent);
  margin-bottom: 4px;
}

.setup-title {
  font-family: var(--f-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--txt);
  text-align: center;
  line-height: 1.1;
  margin: 0;
}

.setup-sub {
  font-size: 13px;
  color: var(--txt-dim);
  text-align: center;
  line-height: 1.6;
  max-width: 280px;
  margin: 0;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-pill);
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--txt-dim);
}

.setup-error {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  color: var(--danger);
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--r-sm);
  padding: 8px 12px;
  width: 100%;
}

.activate-btn {
  margin-top: 6px;
  width: 100%;
  padding: 14px;
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
  transition: background 0.15s ease, transform 0.12s ease;
  letter-spacing: 0.02em;
}
.activate-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--accent) 85%, white);
  transform: translateY(-1px);
}
.activate-btn:disabled { opacity: 0.65; cursor: not-allowed; }

.skip-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: var(--txt-dim);
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
  padding: 4px;
  transition: color 0.15s ease;
}
.skip-btn:hover:not(:disabled) { color: var(--txt); }
.skip-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-row, .spinner-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Success state ──────────────────────────────────────── */
.setup-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 8px 0 4px;
}

.success-ring-wrap {
  color: var(--accent);
  margin-bottom: 6px;
}

.success-svg {
  display: block;
  overflow: visible;
}

/* Circle draws itself */
.s-circle {
  animation: draw-circle 0.55s cubic-bezier(0.4, 0, 0.2, 1) 0.05s both;
  transform-origin: 32px 32px;
  transform: rotate(-90deg);
}
@keyframes draw-circle {
  to { stroke-dashoffset: 0; }
}

/* Check appears after circle completes */
.s-check {
  animation: draw-check 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.55s both;
}
@keyframes draw-check {
  to { stroke-dashoffset: 0; }
}

.success-title {
  font-family: var(--f-display);
  font-size: 26px;
  font-weight: 800;
  color: var(--txt);
  text-align: center;
  margin: 0;
  animation: fade-up 0.4s ease 0.7s both;
}

.success-sub {
  font-size: 13px;
  color: var(--txt-dim);
  text-align: center;
  margin: 0;
  animation: fade-up 0.4s ease 0.85s both;
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Card content swap transition ───────────────────────── */
.card-swap-enter-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.card-swap-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.card-swap-enter-from   { opacity: 0; transform: scale(0.96) translateY(8px); }
.card-swap-leave-to     { opacity: 0; transform: scale(0.96) translateY(-8px); }

/* ── Misc ───────────────────────────────────────────────── */
.spin { animation: spin 0.9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 440px) {
  .setup-card { padding: 32px 20px 28px; border-radius: 20px; }
}
</style>
