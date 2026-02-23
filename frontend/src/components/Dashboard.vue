<template>
  <Transition name="slide">
    <div v-if="visible" class="dashboard">
      <!-- Header -->
      <div class="dashboard__header">
        <div class="dashboard__header-left">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z"/>
          </svg>
          <div>
            <h2>Estadísticas</h2>
            <p class="dashboard__subtitle">Últimos 30 días</p>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')" title="Cerrar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <path d="M18 6 6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Loading / Error -->
      <div v-if="loading" class="dashboard__loading">
        <div class="loading-dots">
          <span/><span/><span/>
        </div>
        <span>Cargando datos…</span>
      </div>
      <div v-else-if="error" class="dashboard__error">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ error }}
      </div>

      <template v-else>
        <!-- Stats Grid -->
        <div v-if="stats" class="stats-grid">
          <div class="stat-card stat-card--wide">
            <div class="stat-value">{{ stats.total_trips }}</div>
            <div class="stat-label">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M3 12h18M3 6h18M3 18h18"/>
              </svg>
              Viajes totales
            </div>
          </div>
          <div class="stat-card stat-card--wide">
            <div class="stat-value">{{ stats.total_km }}</div>
            <div class="stat-label">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>
              </svg>
              Kilómetros
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_hours }}</div>
            <div class="stat-label">Horas conducidas</div>
          </div>
          <div class="stat-card">
            <div class="stat-value stat-value--accent">{{ stats.avg_speed ?? '—' }}</div>
            <div class="stat-label">Vel. promedio km/h</div>
          </div>
          <div class="stat-card">
            <div class="stat-value stat-value--warn">{{ stats.max_speed ?? '—' }}</div>
            <div class="stat-label">Vel. máxima km/h</div>
          </div>
        </div>

        <!-- Trips -->
        <div class="section-header">
          <span class="section-title">Viajes recientes</span>
          <span v-if="trips.length > 0" class="section-count">
            Mostrando {{ pagedTrips.length }} de {{ trips.length }}
          </span>
        </div>

        <div v-if="trips.length === 0" class="no-data">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          Sin viajes registrados
        </div>
        <div v-else class="trips-list">
          <div v-for="trip in pagedTrips" :key="trip.trip_num" class="trip-item" @click="onTripClick(trip)" title="Ver ruta en el mapa">
            <div class="trip-item__accent" />
            <div class="trip-item__content">
              <div class="trip-item__main">
                <span class="trip-date">{{ fmtDate(trip.start_time) }}</span>
                <span class="trip-dist">{{ trip.distance_km }} km</span>
              </div>
              <div class="trip-item__sub">
                <span class="trip-time">{{ fmtTime(trip.start_time) }} → {{ fmtTime(trip.end_time) }}</span>
                <span class="trip-meta">{{ trip.duration_min }} min &nbsp;·&nbsp; {{ trip.avg_speed ?? '—' }} km/h</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination: pinned to bottom of panel -->
        <div v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="page === 0" @click="page--">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <span class="page-info">{{ page + 1 }} / {{ totalPages }}</span>
          <button class="page-btn" :disabled="page === totalPages - 1" @click="page++">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
        </div>
      </template>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTrips } from '../composables/useTrips'
import type { Trip } from '../composables/useTrips'

const props = defineProps<{
  visible: boolean
  deviceId: string | null
  darkMode: boolean
}>()

const emit = defineEmits<{
  close: []
  showRoute: [payload: { deviceId: string; startTime: string; endTime: string }]
}>()

function onTripClick(trip: Trip) {
  if (!props.deviceId) return
  emit('showRoute', {
    deviceId: props.deviceId,
    startTime: trip.start_time,
    endTime: trip.end_time,
  })
}

const { trips, stats, loading, error, fetchData } = useTrips()

const PAGE_SIZE = 8
const page = ref(0)
const totalPages = computed(() => Math.ceil(trips.value.length / PAGE_SIZE))
const pagedTrips = computed(() => trips.value.slice(page.value * PAGE_SIZE, (page.value + 1) * PAGE_SIZE))

watch(
  () => [props.visible, props.deviceId] as [boolean, string | null],
  ([visible, deviceId]) => {
    if (visible && deviceId) { page.value = 0; fetchData(deviceId) }
  },
  { immediate: true },
)

function fmtDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString('es-CL', { day: '2-digit', month: 'short' })
  } catch { return iso }
}

function fmtTime(iso: string) {
  try {
    return new Date(iso).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })
  } catch { return iso }
}
</script>

<style scoped>
/* ── Panel ──────────────────────────────────────────────── */
.dashboard {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(380px, 100vw);
  z-index: 2000;

  background: var(--surface-hi);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border-left: 1px solid var(--border);
  box-shadow: var(--shadow-lg);

  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: var(--txt);
  font-family: var(--f-body);
}

@media (max-width: 640px) {
  .dashboard {
    width: 100vw;
    border-left: none;
    border-top: 1px solid var(--border);
  }
}

/* Subtle accent top strip */
.dashboard::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent) 40%, var(--accent) 60%, transparent);
  opacity: 0.6;
  z-index: 1;
}

/* ── Slide Transition ───────────────────────────────────── */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.32s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* ── Header ─────────────────────────────────────────────── */
.dashboard__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 18px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.dashboard__header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--accent);
}

.dashboard__header-left svg {
  flex-shrink: 0;
}

h2 {
  font-size: 15px;
  font-weight: 700;
  color: var(--txt);
  line-height: 1.1;
}

.dashboard__subtitle {
  font-size: 11px;
  color: var(--txt-dim);
  font-weight: 500;
  margin-top: 1px;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  cursor: pointer;
  color: var(--txt-dim);
  transition: all 0.15s ease;
}
.close-btn:hover {
  background: var(--danger);
  border-color: var(--danger);
  color: #fff;
}

/* ── Loading ─────────────────────────────────────────────── */
.dashboard__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 48px 20px;
  color: var(--txt-dim);
  font-size: 13px;
}

.loading-dots {
  display: flex;
  gap: 6px;
}
.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  animation: bounce-dot 1.2s ease-in-out infinite;
}
.loading-dots span:nth-child(2) { animation-delay: 0.15s; }
.loading-dots span:nth-child(3) { animation-delay: 0.30s; }

@keyframes bounce-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%           { transform: scale(1);   opacity: 1; }
}

/* ── Error ───────────────────────────────────────────────── */
.dashboard__error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 18px;
  margin: 16px;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--r-sm);
  color: var(--danger);
  font-size: 13px;
}

/* ── Stats Grid ──────────────────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  padding: 16px 16px 10px;
  flex-shrink: 0;
}

.stat-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 12px 10px 10px;
  text-align: center;
  transition: border-color 0.15s ease;
}
.stat-card:hover {
  border-color: var(--border-accent);
}

.stat-card--wide {
  grid-column: span 1;
}

.stat-value {
  font-family: var(--f-display);
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1;
  color: var(--txt);
}
.stat-value--accent { color: var(--accent); }
.stat-value--warn   { color: var(--warn); }

.stat-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 600;
  color: var(--txt-dim);
  margin-top: 4px;
  letter-spacing: 0.01em;
}

/* ── Section Header ──────────────────────────────────────── */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 18px 8px;
  flex-shrink: 0;
}

.section-title {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--txt-dim);
}

.section-count {
  font-family: var(--f-mono);
  font-size: 10px;
  font-weight: 600;
  color: var(--accent);
  background: var(--accent-dim);
  padding: 1px 7px;
  border-radius: var(--r-pill);
  border: 1px solid var(--border-accent);
}

/* ── Empty State ─────────────────────────────────────────── */
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 40px 20px;
  color: var(--txt-dim);
  font-size: 13px;
}

/* ── Trips List ──────────────────────────────────────────── */
.trips-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0 14px;
  padding-bottom: 60px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* ── Pagination ──────────────────────────────────────────── */
.pagination {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 10px 14px 16px;
  background: var(--surface-hi);
  border-top: 1px solid var(--border);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  color: var(--txt-dim);
  cursor: pointer;
  transition: all 0.15s ease;
}
.page-btn:hover:not(:disabled) {
  background: var(--accent-dim);
  border-color: var(--border-accent);
  color: var(--accent);
}
.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-info {
  font-family: var(--f-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--txt-dim);
  min-width: 48px;
  text-align: center;
}

.trip-item {
  flex-shrink: 0;
  display: flex;
  align-items: stretch;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.15s ease, transform 0.12s ease, box-shadow 0.15s ease;
}
.trip-item:hover {
  border-color: var(--border-accent);
  transform: translateX(-2px);
  box-shadow: 2px 0 0 0 var(--accent);
}

.trip-item__accent {
  width: 3px;
  flex-shrink: 0;
  background: linear-gradient(to bottom, var(--accent), var(--moving));
  opacity: 0.6;
}

.trip-item__content {
  flex: 1;
  padding: 10px 13px;
}

.trip-item__main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trip-date {
  font-size: 13px;
  font-weight: 600;
  color: var(--txt);
}

.trip-dist {
  font-family: var(--f-display);
  font-size: 16px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.01em;
}

.trip-item__sub {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  gap: 8px;
}

.trip-time {
  font-size: 11px;
  color: var(--txt-dim);
  font-family: var(--f-mono);
}

.trip-meta {
  font-size: 11px;
  color: var(--txt-dim);
  text-align: right;
  white-space: nowrap;
}
</style>
