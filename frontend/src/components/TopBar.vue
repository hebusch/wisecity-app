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
      <!-- Clear route button — shown only when a trip route is active -->
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

      <button class="icon-btn" title="Cerrar sesión" @click="$emit('logout')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  plate: string
  statusName: string | null
  speed: number
  loading: boolean
  darkMode: boolean
  deviceCount: number
  hasTripRoute: boolean
}>()

defineEmits<{
  refresh: []
  toggleDark: []
  toggleDashboard: []
  toggleDeviceSelector: []
  clearRoute: []
  logout: []
}>()

const statusClass = computed(() => {
  const s = (props.statusName ?? '').toLowerCase()
  if (s.includes('detenido') || s.includes('parking') || s.includes('stop') || s.includes('reposo')) return 'badge--idle'
  if (s.includes('movimiento') || s.includes('moving') || s.includes('en ruta')) return 'badge--moving'
  return 'badge--unknown'
})

const statusLabel = computed(() => {
  if (!props.statusName) return null
  const cls = statusClass.value
  if (cls === 'badge--idle')    return 'Reposo'
  if (cls === 'badge--moving')  return 'Activo'
  return 'Desconocido'
})
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
  /* Two-row layout: info on top, buttons on bottom */
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

  /* Row 1: plate+badge on left, speed on right */
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

  /* Row 2: buttons spanning full width, evenly spaced */
  .topbar__right {
    grid-column: 1 / -1;
    grid-row: 2;
    /* Override flex layout with grid so buttons share equal width */
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: 1fr;
    width: 100%;
    padding: 6px 4px;
    gap: 4px;
    align-items: center;
  }

  /* Make each button fill its grid cell — bigger tap targets */
  .topbar__right .icon-btn {
    width: 100%;
    height: 48px;
    border-radius: var(--r-sm);
  }

  /* Bigger icons inside buttons */
  .topbar__right .icon-btn svg {
    width: 20px;
    height: 20px;
  }

  /* Hide vertical dividers (rows handle separation now) */
  .topbar__divider {
    display: none;
  }
}

/* Accent stripe on top */
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

.topbar__left--selectable {
  cursor: pointer;
}
.topbar__left--selectable:hover {
  background: var(--accent-dim);
}
.topbar__left--selectable:hover .plate {
  color: var(--accent);
}
.topbar__left--selectable:hover .chevron {
  color: var(--accent);
}

.chevron {
  color: var(--txt-dim);
  flex-shrink: 0;
  transition: color 0.15s ease, transform 0.2s ease;
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

.badge--idle {
  background: var(--idle-dim);
  color: var(--idle);
}
.badge--idle .badge__dot {
  background: var(--idle);
}

.badge--moving {
  background: var(--moving-dim);
  color: var(--moving);
}
.badge--moving .badge__dot {
  background: var(--moving);
  animation: pulse-dot 1.4s ease-in-out infinite;
}

.badge--unknown {
  background: var(--warn-dim);
  color: var(--warn);
}
.badge--unknown .badge__dot {
  background: var(--warn);
}

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

.speed__val.speed--moving {
  color: var(--accent);
}

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
.spin {
  animation: spin 0.9s linear infinite;
  display: block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
