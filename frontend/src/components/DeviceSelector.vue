<template>
  <Transition name="backdrop-fade">
    <div v-if="visible" class="backdrop" @click.self="$emit('close')">
      <Transition name="sheet-slide" appear>
        <div v-if="visible" class="sheet">
          <div class="sheet__handle" />

          <div class="sheet__header">
            <div class="sheet__header-left">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <rect x="3" y="11" width="18" height="11" rx="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <h2>Mis vehículos</h2>
            </div>
            <span class="sheet__count">{{ devices.length }}</span>
          </div>

          <div class="sheet__list">
            <button
              v-for="device in devices"
              :key="device.id"
              class="device-card"
              :class="{
                'device-card--selected': device.id === selectedId,
                'device-card--moving': isMoving(device),
              }"
              @click="select(device)"
            >
              <div class="device-card__accent" :class="statusClass(device)" />

              <div class="device-card__body">
                <div class="device-card__top">
                  <span class="device-card__plate">{{ device.vehicle.plate ?? device.id }}</span>
                  <span class="device-card__badge" :class="statusClass(device)">
                    <span class="badge-dot" />
                    {{ statusLabel(device) }}
                  </span>
                </div>

                <div class="device-card__mid">
                  <span class="device-card__model">
                    {{ vehicleName(device) }}
                  </span>
                  <span class="device-card__speed" :class="{ 'speed--moving': isMoving(device) }">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                      <path d="M12 2a10 10 0 1 0 10 10"/>
                      <path d="m12 6 4 6-4 2-4-2z"/>
                    </svg>
                    {{ device.speed }} km/h
                  </span>
                </div>

                <div class="device-card__bottom">
                  <span class="device-card__time">{{ timeAgo(device.last_update) }}</span>
                  <svg v-if="device.id === selectedId" class="check-icon" width="14" height="14"
                    viewBox="0 0 24 24" fill="none" stroke="currentColor"
                    stroke-width="2.5" stroke-linecap="round">
                    <path d="M20 6 9 17l-5-5"/>
                  </svg>
                </div>
              </div>
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import type { Device } from '../composables/useDevices'

const props = defineProps<{
  visible: boolean
  devices: Device[]
  selectedId: string | null
}>()

const emit = defineEmits<{
  close: []
  select: [deviceId: string]
}>()

function select(device: Device) {
  emit('select', device.id)
  emit('close')
}

function isMoving(device: Device): boolean {
  const s = (device.status_name ?? '').toLowerCase()
  return s.includes('movimiento') || s.includes('moving') || s.includes('en ruta')
}

function statusLabel(device: Device): string {
  if (!device.status_name) return 'Desconocido'
  const s = device.status_name.toLowerCase()
  if (s.includes('detenido') || s.includes('parking') || s.includes('stop') || s.includes('reposo')) return 'Reposo'
  if (s.includes('movimiento') || s.includes('moving') || s.includes('en ruta')) return 'Activo'
  return 'Desconocido'
}

function statusClass(device: Device): string {
  if (!device.status_name) return 'status--unknown'
  const s = device.status_name.toLowerCase()
  if (s.includes('detenido') || s.includes('parking') || s.includes('stop') || s.includes('reposo')) return 'status--idle'
  if (s.includes('movimiento') || s.includes('moving') || s.includes('en ruta')) return 'status--moving'
  return 'status--unknown'
}

function vehicleName(device: Device): string {
  const { brand, model, year } = device.vehicle
  const parts = [brand, model].filter(Boolean).join(' ')
  return parts ? (year ? `${parts} · ${year}` : parts) : '—'
}

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return 'Sin datos'
  try {
    const secs = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000)
    if (secs < 60) return `hace ${secs}s`
    if (secs < 3600) return `hace ${Math.floor(secs / 60)}m`
    return `hace ${Math.floor(secs / 3600)}h`
  } catch { return '—' }
}
</script>

<style scoped>
/* ── Backdrop ──────────────────────────────────────────────── */
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.backdrop-fade-enter-active,
.backdrop-fade-leave-active { transition: opacity 0.28s ease; }
.backdrop-fade-enter-from,
.backdrop-fade-leave-to     { opacity: 0; }

/* ── Sheet ─────────────────────────────────────────────────── */
.sheet {
  width: 100%;
  max-width: 560px;
  max-height: 82vh;
  background: var(--surface-hi);
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  border: 1px solid var(--border);
  border-bottom: none;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sheet-slide-enter-active,
.sheet-slide-leave-active { transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1); }
.sheet-slide-enter-from,
.sheet-slide-leave-to     { transform: translateY(100%); }

/* ── Handle ─────────────────────────────────────────────────── */
.sheet__handle {
  width: 40px;
  height: 4px;
  background: var(--border);
  border-radius: 99px;
  margin: 12px auto 0;
  flex-shrink: 0;
}

/* ── Header ─────────────────────────────────────────────────── */
.sheet__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.sheet__header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--accent);
}

h2 {
  font-size: 16px;
  font-weight: 700;
  color: var(--txt);
}

.sheet__count {
  font-family: var(--f-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  background: var(--accent-dim);
  border: 1px solid var(--border-accent);
  padding: 2px 9px;
  border-radius: 99px;
}

/* ── Device List ─────────────────────────────────────────────── */
.sheet__list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 14px 28px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ── Device Card ─────────────────────────────────────────────── */
.device-card {
  display: flex;
  align-items: stretch;
  width: 100%;
  text-align: left;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.18s ease, transform 0.14s ease, box-shadow 0.18s ease;
}

.device-card:hover {
  border-color: var(--border-accent);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.device-card--selected {
  border-color: var(--accent);
  background: var(--accent-dim);
  box-shadow: 0 0 0 1px var(--accent), var(--shadow-sm);
}

/* ── Accent stripe ───────────────────────────────────────────── */
.device-card__accent {
  width: 4px;
  flex-shrink: 0;
  border-radius: 0;
}
.status--idle    { background: var(--idle); }
.status--moving  { background: var(--moving); }
.status--unknown { background: var(--warn); }

/* ── Card body ───────────────────────────────────────────────── */
.device-card__body {
  flex: 1;
  padding: 13px 14px 11px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

/* Top row: plate + status */
.device-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.device-card__plate {
  font-family: var(--f-display);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--txt);
  line-height: 1;
}

.device-card__badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: 3px 9px 3px 7px;
  border-radius: 99px;
}
.device-card__badge.status--idle    { background: var(--idle-dim);   color: var(--idle); }
.device-card__badge.status--moving  { background: var(--moving-dim); color: var(--moving); }
.device-card__badge.status--unknown { background: var(--warn-dim);   color: var(--warn); }

.badge-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}
.status--moving .badge-dot {
  animation: pulse-dot 1.4s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.4; transform: scale(0.6); }
}

/* Mid row: model + speed */
.device-card__mid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.device-card__model {
  font-size: 12px;
  color: var(--txt-dim);
  font-weight: 500;
}

.device-card__speed {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--f-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--txt-dim);
  letter-spacing: 0.02em;
}
.device-card__speed.speed--moving {
  color: var(--accent);
}

/* Bottom row: time + check */
.device-card__bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 2px;
}

.device-card__time {
  font-size: 11px;
  color: var(--txt-dim);
}

.check-icon {
  color: var(--accent);
  flex-shrink: 0;
}
</style>
