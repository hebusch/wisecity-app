<template>
  <div class="topbar">
    <div
      class="topbar__left"
      :class="{ 'topbar__left--selectable': deviceCount > 1 }"
      @click="deviceCount > 1 && $emit('toggleDeviceSelector')"
    >
      <span class="plate">{{ plate }}</span>
      <svg v-if="deviceCount > 1" class="chevron" width="12" height="12" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <path d="m6 9 6 6 6-6"/>
      </svg>
      <span v-if="statusLabel" class="badge" :class="statusClass">
        <span class="badge__dot" />
        {{ statusLabel }}
      </span>
    </div>

    <div class="topbar__divider" />

    <div class="topbar__center">
      <span class="speed">
        <span class="speed__val" :class="{ 'speed--moving': speed > 0 }">{{ speed }}</span>
        <span class="speed__unit">km/h</span>
      </span>
    </div>

    <div class="topbar__divider" />

    <div class="topbar__right">
      <button class="icon-btn" title="Actualizar" @click="$emit('refresh')" :disabled="loading">
        <svg :class="{ spin: loading }" width="15" height="15" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M1 4v6h6M23 20v-6h-6"/>
          <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
        </svg>
      </button>
      <button class="icon-btn" title="Modo oscuro" @click="$emit('toggleDark')">
        <svg v-if="darkMode" width="15" height="15" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
      <button v-if="hasTripRoute" class="icon-btn icon-btn--route" title="Limpiar ruta" @click="$emit('clearRoute')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"/>
        </svg>
      </button>
      <button class="icon-btn icon-btn--accent" title="Dashboard" @click="$emit('toggleDashboard')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>
        </svg>
      </button>

      <!-- User menu trigger -->
      <button
        ref="userBtnRef"
        class="icon-btn"
        :class="{ 'icon-btn--active': showMenu }"
        title="Cuenta"
        @click="toggleMenu"
      >
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="8" r="4"/>
          <path d="M4 20c0-3.87 3.58-7 8-7s8 3.13 8 7"/>
        </svg>
      </button>
    </div>
  </div>

  <!-- ── All floating layers (Teleported to avoid stacking context issues) ── -->
  <Teleport to="body">

    <!-- Click-outside scrim -->
    <div v-if="showMenu" class="um-scrim" @click="closeMenu" />

    <!-- ── Desktop dropdown ─────────────────────────────────────────── -->
    <Transition name="dd">
      <div v-if="showMenu && !isMobile" class="um-dropdown" :style="menuPos">
        <template v-if="email">
          <div class="um-head">
            <div class="um-avatar">{{ emailInitial }}</div>
            <span class="um-email">{{ email }}</span>
          </div>
          <div class="um-sep" />
        </template>
        <button class="um-row" @click="openChangePwdModal">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          Cambiar contraseña
        </button>
        <button v-if="hasPasskey" class="um-row um-row--danger" @click="openDeleteModal">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>
          </svg>
          Eliminar passkey
        </button>
        <button class="um-row" @click="doLogout">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2.5" stroke-linecap="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Cerrar sesión
        </button>
      </div>
    </Transition>

    <!-- ── Mobile bottom sheet ──────────────────────────────────────── -->
    <Transition name="sheet">
      <div v-if="showMenu && isMobile" class="um-sheet-wrap" @click="closeMenu">
        <div class="um-sheet" @click.stop>
          <div class="um-handle" />
          <template v-if="email">
            <div class="um-head">
              <div class="um-avatar">{{ emailInitial }}</div>
              <div>
                <div class="um-sheet-label">Cuenta</div>
                <div class="um-email">{{ email }}</div>
              </div>
            </div>
            <div class="um-sep" />
          </template>

          <button class="um-sheet-row" @click="openChangePwdModal">
            <div class="um-sheet-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </div>
            <div class="um-sheet-body">
              <span class="um-sheet-body__label">Cambiar contraseña</span>
              <span class="um-sheet-body__sub">Actualiza tu contraseña de acceso</span>
            </div>
            <svg class="um-sheet-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>

          <button v-if="hasPasskey" class="um-sheet-row um-sheet-row--danger" @click="openDeleteModal">
            <div class="um-sheet-icon um-sheet-icon--danger">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>
              </svg>
            </div>
            <div class="um-sheet-body">
              <span class="um-sheet-body__label">Eliminar passkey</span>
              <span class="um-sheet-body__sub">Elimina tu acceso biométrico</span>
            </div>
            <svg class="um-sheet-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>

          <button class="um-sheet-row" @click="doLogout">
            <div class="um-sheet-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2.5" stroke-linecap="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </div>
            <div class="um-sheet-body">
              <span class="um-sheet-body__label">Cerrar sesión</span>
              <span class="um-sheet-body__sub">Salir de la cuenta</span>
            </div>
            <svg class="um-sheet-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>

          <div class="um-sheet-safe" />
        </div>
      </div>
    </Transition>

    <!-- ── Delete passkey confirmation modal ────────────────────────── -->
    <Transition name="modal">
      <div v-if="showDeleteModal" class="del-backdrop" @click.self="!deleteSuccess && closeDeleteModal()">
        <div class="del-card">
          <Transition name="del-swap" mode="out-in">

            <!-- Normal: form -->
            <div v-if="!deleteSuccess" key="form" class="del-form">
              <div class="del-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  <line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>
                </svg>
              </div>
              <h3 class="del-title">Eliminar acceso biométrico</h3>
              <p class="del-sub">
                Ingresa tu contraseña para confirmar. Podrás activarlo de nuevo cuando quieras.
              </p>
              <input
                ref="deletePwdRef"
                class="del-input"
                type="password"
                placeholder="Contraseña"
                v-model="deletePwd"
                :disabled="deleteLoading"
                @keydown.enter="confirmDelete"
              />
              <p v-if="deleteErr" class="del-error">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2.5" stroke-linecap="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {{ deleteErr }}
              </p>
              <div class="del-actions">
                <button class="del-btn del-btn--ghost" :disabled="deleteLoading" @click="closeDeleteModal">
                  Cancelar
                </button>
                <button class="del-btn del-btn--danger" :disabled="deleteLoading || !deletePwd" @click="confirmDelete">
                  <svg v-if="deleteLoading" class="spin" width="13" height="13" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                    <path d="M21 12a9 9 0 1 1-6.22-8.56"/>
                  </svg>
                  {{ deleteLoading ? 'Eliminando…' : 'Eliminar' }}
                </button>
              </div>
            </div>

            <!-- Success: animated check -->
            <div v-else key="success" class="del-success">
              <div class="del-success-ring">
                <svg width="72" height="72" viewBox="0 0 64 64" fill="none">
                  <circle
                    class="ds-circle"
                    cx="32" cy="32" r="27"
                    stroke="currentColor" stroke-width="2"
                    stroke-linecap="round"
                    stroke-dasharray="170" stroke-dashoffset="170"
                  />
                  <polyline
                    class="ds-check"
                    points="19,33 28,42 45,22"
                    stroke="currentColor" stroke-width="3.5"
                    stroke-linecap="round" stroke-linejoin="round"
                    stroke-dasharray="46" stroke-dashoffset="46"
                  />
                </svg>
              </div>
              <p class="del-success-title">Passkey eliminado</p>
              <p class="del-success-sub">Ya no podrás acceder con biometría</p>
            </div>

          </Transition>
        </div>
      </div>
    </Transition>

    <!-- ── Change password modal ────────────────────────────── -->
    <Transition name="modal">
      <div v-if="showChangePwdModal" class="del-backdrop" @click.self="!changePwdSuccess && closeChangePwdModal()">
        <div class="del-card">
          <Transition name="del-swap" mode="out-in">

            <!-- Normal: form -->
            <div v-if="!changePwdSuccess" key="form" class="del-form">
              <div class="del-icon cp-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </div>
              <h3 class="del-title">Cambiar contraseña</h3>
              <p class="del-sub">Ingresa tu contraseña actual y la nueva contraseña.</p>
              <input
                ref="changePwdCurrentRef"
                class="del-input"
                type="password"
                placeholder="Contraseña actual"
                v-model="changePwdCurrent"
                :disabled="changePwdLoading"
                @keydown.enter="changePwdNewRef?.focus()"
              />
              <input
                ref="changePwdNewRef"
                class="del-input"
                type="password"
                placeholder="Nueva contraseña"
                v-model="changePwdNew"
                :disabled="changePwdLoading"
                @keydown.enter="changePwdConfirmRef?.focus()"
              />
              <input
                ref="changePwdConfirmRef"
                class="del-input"
                type="password"
                placeholder="Confirmar nueva contraseña"
                v-model="changePwdConfirm"
                :disabled="changePwdLoading"
                @keydown.enter="submitChangePwd"
              />
              <p v-if="changePwdErr" class="del-error">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2.5" stroke-linecap="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {{ changePwdErr }}
              </p>
              <div class="del-actions">
                <button class="del-btn del-btn--ghost" :disabled="changePwdLoading" @click="closeChangePwdModal">
                  Cancelar
                </button>
                <button
                  class="del-btn del-btn--primary"
                  :disabled="changePwdLoading || !changePwdCurrent || !changePwdNew || !changePwdConfirm"
                  @click="submitChangePwd"
                >
                  <svg v-if="changePwdLoading" class="spin" width="13" height="13" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                    <path d="M21 12a9 9 0 1 1-6.22-8.56"/>
                  </svg>
                  {{ changePwdLoading ? 'Guardando…' : 'Guardar' }}
                </button>
              </div>
            </div>

            <!-- Success: animated check -->
            <div v-else key="success" class="del-success">
              <div class="del-success-ring">
                <svg width="72" height="72" viewBox="0 0 64 64" fill="none">
                  <circle
                    class="ds-circle"
                    cx="32" cy="32" r="27"
                    stroke="currentColor" stroke-width="2"
                    stroke-linecap="round"
                    stroke-dasharray="170" stroke-dashoffset="170"
                  />
                  <polyline
                    class="ds-check"
                    points="19,33 28,42 45,22"
                    stroke="currentColor" stroke-width="3.5"
                    stroke-linecap="round" stroke-linejoin="round"
                    stroke-dasharray="46" stroke-dashoffset="46"
                  />
                </svg>
              </div>
              <p class="del-success-title">Contraseña actualizada</p>
              <p class="del-success-sub">Tu nueva contraseña está activa</p>
            </div>

          </Transition>
        </div>
      </div>
    </Transition>

  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuth } from '../composables/useAuth'

const props = defineProps<{
  plate: string
  statusName: string | null
  speed: number
  loading: boolean
  darkMode: boolean
  deviceCount: number
  hasTripRoute: boolean
  email: string
  hasPasskey: boolean
}>()

const emit = defineEmits<{
  refresh: []
  toggleDark: []
  toggleDashboard: []
  toggleDeviceSelector: []
  clearRoute: []
  logout: []
}>()

const { deletePasskey, changePassword } = useAuth()

// ── Status badge ─────────────────────────────────────────────────────────────

const statusClass = computed(() => {
  const s = (props.statusName ?? '').toLowerCase()
  if (s.includes('detenido') || s.includes('parking') || s.includes('stop') || s.includes('reposo')) return 'badge--idle'
  if (s.includes('movimiento') || s.includes('moving') || s.includes('en ruta') || s.includes('activo')) return 'badge--moving'
  return 'badge--unknown'
})

const statusLabel = computed(() => {
  if (!props.statusName) return null
  const cls = statusClass.value
  if (cls === 'badge--idle')   return 'Reposo'
  if (cls === 'badge--moving') return 'Activo'
  return 'Desconocido'
})

// ── User menu ─────────────────────────────────────────────────────────────────

const userBtnRef = ref<HTMLElement | null>(null)
const showMenu   = ref(false)
const isMobile   = ref(window.innerWidth <= 480)
const menuPos    = ref<Record<string, string>>({})

function onResize() { isMobile.value = window.innerWidth <= 480 }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

function toggleMenu() {
  if (!showMenu.value) {
    const rect = userBtnRef.value?.getBoundingClientRect()
    if (rect) {
      menuPos.value = {
        top: `${rect.bottom + 8}px`,
        right: `${window.innerWidth - rect.right}px`,
      }
    }
  }
  showMenu.value = !showMenu.value
}

function closeMenu() { showMenu.value = false }

const emailInitial = computed(() => (props.email?.[0] ?? '?').toUpperCase())

function doLogout() {
  closeMenu()
  emit('logout')
}

// ── Change password modal ─────────────────────────────────────────────────────

const showChangePwdModal  = ref(false)
const changePwdSuccess    = ref(false)
const changePwdCurrent    = ref('')
const changePwdNew        = ref('')
const changePwdConfirm    = ref('')
const changePwdErr        = ref('')
const changePwdLoading    = ref(false)
const changePwdCurrentRef = ref<HTMLInputElement | null>(null)
const changePwdNewRef     = ref<HTMLInputElement | null>(null)
const changePwdConfirmRef = ref<HTMLInputElement | null>(null)

function openChangePwdModal() {
  closeMenu()
  changePwdCurrent.value = ''
  changePwdNew.value = ''
  changePwdConfirm.value = ''
  changePwdErr.value = ''
  changePwdSuccess.value = false
  showChangePwdModal.value = true
  nextTick(() => changePwdCurrentRef.value?.focus())
}

function closeChangePwdModal() {
  if (changePwdLoading.value || changePwdSuccess.value) return
  showChangePwdModal.value = false
}

async function submitChangePwd() {
  if (!changePwdCurrent.value || !changePwdNew.value || !changePwdConfirm.value || changePwdLoading.value) return
  if (changePwdNew.value !== changePwdConfirm.value) {
    changePwdErr.value = 'Las contraseñas no coinciden'
    return
  }
  changePwdErr.value = ''
  changePwdLoading.value = true
  try {
    await changePassword(changePwdCurrent.value, changePwdNew.value)
    changePwdSuccess.value = true
    setTimeout(() => {
      showChangePwdModal.value = false
      changePwdSuccess.value = false
    }, 1800)
  } catch (e) {
    changePwdErr.value = e instanceof Error ? e.message : 'Error al cambiar contraseña'
  } finally {
    changePwdLoading.value = false
  }
}

// ── Delete passkey modal ──────────────────────────────────────────────────────

const showDeleteModal = ref(false)
const deleteSuccess   = ref(false)
const deletePwd       = ref('')
const deleteErr       = ref('')
const deleteLoading   = ref(false)
const deletePwdRef    = ref<HTMLInputElement | null>(null)

function openDeleteModal() {
  closeMenu()
  deletePwd.value = ''
  deleteErr.value = ''
  deleteSuccess.value = false
  showDeleteModal.value = true
  nextTick(() => deletePwdRef.value?.focus())
}

function closeDeleteModal() {
  if (deleteLoading.value || deleteSuccess.value) return
  showDeleteModal.value = false
}

async function confirmDelete() {
  if (!deletePwd.value || deleteLoading.value) return
  deleteErr.value = ''
  deleteLoading.value = true
  try {
    await deletePasskey(deletePwd.value)
    deleteSuccess.value = true
    setTimeout(() => {
      showDeleteModal.value = false
      deleteSuccess.value = false
    }, 1800)
  } catch (e) {
    deleteErr.value = e instanceof Error ? e.message : 'Error al eliminar'
  } finally {
    deleteLoading.value = false
  }
}
</script>

<style scoped>
/* ── Shell ──────────────────────────────────────────────── */
.topbar {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;

  display: flex;
  align-items: center;
  gap: 0;

  background: var(--surface);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.08);

  min-width: 340px;
  max-width: 92vw;
  height: 52px;
  padding: 0 6px;
  overflow: hidden;
}

@media (max-width: 480px) {
  .topbar {
    top: 10px;
    min-width: 0;
    width: calc(100vw - 20px);
    height: auto;
    border-radius: var(--r-md);
    padding: 0;

    display: grid;
    grid-template-columns: 1fr auto;
    grid-template-rows: auto auto;
  }

  .topbar__left {
    grid-column: 1;
    grid-row: 1;
    padding: 10px 12px 8px;
    gap: 7px;
    border-bottom: 1px solid var(--border);
  }

  .topbar__center {
    grid-column: 2;
    grid-row: 1;
    padding: 10px 14px 8px;
    border-bottom: 1px solid var(--border);
    border-left: 1px solid var(--border);
  }

  .topbar__right {
    grid-column: 1 / -1;
    grid-row: 2;
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: 1fr;
    width: 100%;
    padding: 6px 4px;
    gap: 4px;
    align-items: center;
  }

  .topbar__right .icon-btn {
    width: 100%;
    height: 48px;
    border-radius: var(--r-sm);
  }

  .topbar__right .icon-btn svg {
    width: 20px;
    height: 20px;
  }

  .topbar__divider { display: none; }
}

/* Accent stripe */
.topbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 12%;
  right: 12%;
  height: 1.5px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.7;
}

/* ── Sections ───────────────────────────────────────────── */
.topbar__left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 0 10px;
  border-radius: var(--r-md);
  transition: background 0.15s ease;
}

.topbar__left--selectable { cursor: pointer; }
.topbar__left--selectable:hover { background: var(--accent-dim); }
.topbar__left--selectable:hover .plate { color: var(--accent); }
.topbar__left--selectable:hover .chevron { color: var(--accent); }

.chevron {
  color: var(--txt-dim);
  flex-shrink: 0;
  transition: color 0.15s ease;
}

.topbar__center {
  padding: 0 14px;
  flex-shrink: 0;
}

.topbar__right {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  justify-content: flex-end;
  padding: 0 6px;
}

.topbar__divider {
  width: 1px;
  height: 26px;
  background: var(--border);
  flex-shrink: 0;
}

/* ── Plate ──────────────────────────────────────────────── */
.plate {
  font-family: var(--f-display);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--txt);
  line-height: 1;
}

@media (max-width: 480px) {
  .plate { font-size: 24px; }
  .badge { font-size: 12px; padding: 4px 10px 4px 8px; }
  .badge__dot { width: 7px; height: 7px; }
}

/* ── Status Badge ───────────────────────────────────────── */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 3px 9px 3px 7px;
  border-radius: var(--r-pill);
  white-space: nowrap;
}

.badge__dot {
  display: block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.badge--idle { background: var(--idle-dim); color: var(--idle); }
.badge--idle .badge__dot { background: var(--idle); }

.badge--moving { background: var(--moving-dim); color: var(--moving); }
.badge--moving .badge__dot {
  background: var(--moving);
  animation: pulse-dot 1.4s ease-in-out infinite;
}

.badge--unknown { background: var(--warn-dim); color: var(--warn); }
.badge--unknown .badge__dot { background: var(--warn); }

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.4; transform: scale(0.6); }
}

/* ── Speed ──────────────────────────────────────────────── */
.speed {
  display: flex;
  align-items: baseline;
  gap: 3px;
  line-height: 1;
}

.speed__val {
  font-family: var(--f-display);
  font-size: 26px;
  font-weight: 800;
  color: var(--txt);
  letter-spacing: -0.01em;
  transition: color 0.3s ease;
}

.speed__val.speed--moving { color: var(--accent); }

.speed__unit {
  font-family: var(--f-body);
  font-size: 11px;
  font-weight: 500;
  color: var(--txt-dim);
  letter-spacing: 0.02em;
}

@media (max-width: 480px) {
  .speed__val { font-size: 30px; }
  .speed__unit { font-size: 13px; }
}

/* ── Icon Buttons ───────────────────────────────────────── */
.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--r-sm);
  cursor: pointer;
  color: var(--txt-dim);
  transition: background 0.15s ease, color 0.15s ease;
}

.icon-btn:hover {
  background: var(--accent-dim);
  color: var(--accent);
}

.icon-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.icon-btn:disabled:hover {
  background: transparent;
  color: var(--txt-dim);
}

.icon-btn--accent {
  background: var(--accent-dim);
  color: var(--accent);
  border: 1px solid var(--border-accent);
}
.icon-btn--accent:hover {
  background: var(--accent);
  color: #fff;
}

.icon-btn--active {
  background: var(--accent-dim);
  color: var(--accent);
}

.icon-btn--route {
  background: rgba(245, 158, 11, 0.12);
  color: var(--warn);
  border: 1px solid rgba(245, 158, 11, 0.3);
}
.icon-btn--route:hover {
  background: var(--warn);
  color: #fff;
  border-color: transparent;
}

/* ── Spinner ────────────────────────────────────────────── */
.spin { animation: spin 0.9s linear infinite; display: block; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ══════════════════════════════════════════════════════════
   USER MENU — shared
   ══════════════════════════════════════════════════════════ */

.um-scrim {
  position: fixed;
  inset: 0;
  z-index: 1999;
}

/* Shared header */
.um-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px 12px;
}

.um-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-dim);
  border: 1px solid var(--border-accent);
  color: var(--accent);
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-family: var(--f-display);
}

.um-email {
  font-size: 12px;
  color: var(--txt-dim);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.um-sheet-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--txt-dim);
  line-height: 1;
  margin-bottom: 3px;
}

.um-sep {
  height: 1px;
  background: var(--border);
}

/* ── Desktop dropdown ───────────────────────────────────── */
.um-dropdown {
  position: fixed;
  z-index: 2000;
  min-width: 210px;
  background: var(--surface-hi);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.05);
  overflow: hidden;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
}

.um-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 16px;
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--f-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--txt);
  text-align: left;
  transition: background 0.12s ease, color 0.12s ease;
}
.um-row:hover {
  background: var(--accent-dim);
  color: var(--accent);
}
.um-row--danger { color: var(--danger); }
.um-row--danger:hover {
  background: rgba(248, 113, 113, 0.1);
  color: var(--danger);
}

/* Dropdown transition */
.dd-enter-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.dd-leave-active { transition: opacity 0.1s ease, transform 0.1s ease; }
.dd-enter-from, .dd-leave-to { opacity: 0; transform: translateY(-6px) scale(0.97); }

/* ── Mobile bottom sheet ────────────────────────────────── */
.um-sheet-wrap {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: flex-end;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.um-sheet {
  width: 100%;
  background: var(--surface-hi);
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  border: 1px solid var(--border);
  border-bottom: none;
  box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.3);
}

.um-handle {
  width: 36px;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  margin: 12px auto 6px;
}

.um-sheet-row {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 14px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--f-body);
  text-align: left;
  transition: background 0.12s ease;
}
.um-sheet-row:hover { background: var(--accent-dim); }
.um-sheet-row--danger:hover { background: rgba(248, 113, 113, 0.08); }

.um-sheet-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--r-md);
  background: var(--surface);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--txt-dim);
  flex-shrink: 0;
}
.um-sheet-icon--danger {
  color: var(--danger);
  background: rgba(248, 113, 113, 0.1);
  border-color: rgba(248, 113, 113, 0.25);
}

.um-sheet-body {
  flex: 1;
  min-width: 0;
}
.um-sheet-body__label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--txt);
}
.um-sheet-row--danger .um-sheet-body__label { color: var(--danger); }

.um-sheet-body__sub {
  display: block;
  font-size: 12px;
  color: var(--txt-dim);
  margin-top: 2px;
}

.um-sheet-chevron { color: var(--txt-dim); flex-shrink: 0; }

.um-sheet-safe { height: env(safe-area-inset-bottom, 16px); }

/* Sheet transition */
.sheet-enter-active { transition: opacity 0.25s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.sheet-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.sheet-enter-from, .sheet-leave-to { opacity: 0; transform: translateY(100%); }

/* ══════════════════════════════════════════════════════════
   DELETE PASSKEY MODAL
   ══════════════════════════════════════════════════════════ */

.del-backdrop {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.del-card {
  width: 100%;
  max-width: 360px;
  background: var(--surface-hi);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 32px 28px 28px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.del-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgba(248, 113, 113, 0.12);
  border: 1.5px solid rgba(248, 113, 113, 0.3);
  color: var(--danger);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.del-title {
  font-family: var(--f-display);
  font-size: 18px;
  font-weight: 700;
  color: var(--txt);
  text-align: center;
  line-height: 1.2;
  margin: 0;
}

.del-sub {
  font-size: 13px;
  color: var(--txt-dim);
  text-align: center;
  line-height: 1.6;
  max-width: 280px;
  margin: 0;
}

.del-input {
  width: 100%;
  padding: 11px 14px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  font-family: var(--f-body);
  font-size: 16px;
  color: var(--txt);
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  margin-top: 4px;
}
.del-input:focus {
  border-color: var(--danger);
  box-shadow: 0 0 0 3px rgba(248, 113, 113, 0.15);
}
.del-input::placeholder { color: var(--txt-dim); opacity: 0.6; }
.del-input:disabled { opacity: 0.5; cursor: not-allowed; }

.del-error {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--danger);
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--r-sm);
  padding: 7px 12px;
  width: 100%;
}

.del-actions {
  display: flex;
  gap: 8px;
  width: 100%;
  margin-top: 4px;
}

.del-btn {
  flex: 1;
  padding: 11px;
  border-radius: var(--r-md);
  font-family: var(--f-body);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.15s ease;
}
.del-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.del-btn--ghost {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--txt-dim);
}
.del-btn--ghost:hover:not(:disabled) {
  background: var(--accent-dim);
  color: var(--txt);
}

.del-btn--danger {
  background: rgba(248, 113, 113, 0.12);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: var(--danger);
}
.del-btn--danger:hover:not(:disabled) {
  background: var(--danger);
  color: #fff;
  border-color: transparent;
}

.del-btn--primary {
  background: var(--accent-dim);
  border: 1px solid var(--border-accent);
  color: var(--accent);
}
.del-btn--primary:hover:not(:disabled) {
  background: var(--accent);
  color: #fff;
  border-color: transparent;
}

.cp-icon {
  background: var(--accent-dim);
  border-color: var(--border-accent);
  color: var(--accent);
}

/* Modal transition */
.modal-enter-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.modal-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }

/* ── Delete modal form wrapper ──────────────────────────── */
.del-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
}

/* ── Delete modal success state ─────────────────────────── */
.del-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 12px 0 8px;
}

.del-success-ring {
  color: var(--accent);
  margin-bottom: 4px;
}

/* Circle draws itself */
.ds-circle {
  animation: ds-draw-circle 0.55s cubic-bezier(0.4, 0, 0.2, 1) 0.05s both;
  transform-origin: 32px 32px;
  transform: rotate(-90deg);
}
@keyframes ds-draw-circle {
  to { stroke-dashoffset: 0; }
}

/* Check appears after circle */
.ds-check {
  animation: ds-draw-check 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.55s both;
}
@keyframes ds-draw-check {
  to { stroke-dashoffset: 0; }
}

.del-success-title {
  font-family: var(--f-display);
  font-size: 17px;
  font-weight: 700;
  color: var(--txt);
  margin: 0;
  animation: ds-fade-up 0.35s ease 0.7s both;
}

.del-success-sub {
  font-size: 12px;
  color: var(--txt-dim);
  margin: 0;
  animation: ds-fade-up 0.35s ease 0.85s both;
}

@keyframes ds-fade-up {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Swap transition inside the modal card */
.del-swap-enter-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.del-swap-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.del-swap-enter-from   { opacity: 0; transform: scale(0.96); }
.del-swap-leave-to     { opacity: 0; transform: scale(0.96); }
</style>
