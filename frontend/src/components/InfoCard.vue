<template>
  <div class="info-card">
    <div class="info-card__header">
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3"/>
      </svg>
      <span>Posición</span>
    </div>
    <div class="info-card__row">
      <span class="label">LAT</span>
      <span class="value">{{ fmt(latitude) }}</span>
    </div>
    <div class="info-card__row">
      <span class="label">LNG</span>
      <span class="value">{{ fmt(longitude) }}</span>
    </div>
    <div v-if="lastFetched" class="info-card__row info-card__row--last">
      <span class="label">SYNC</span>
      <span class="value value--accent">{{ timeAgo }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  latitude: number | null
  longitude: number | null
  lastFetched: Date | null
  darkMode: boolean
}>()

function fmt(n: number | null) {
  return n != null ? n.toFixed(6) : '—'
}

const timeAgo = computed(() => {
  if (!props.lastFetched) return '—'
  const secs = Math.floor((Date.now() - props.lastFetched.getTime()) / 1000)
  if (secs < 60) return `hace ${secs}s`
  if (secs < 3600) return `hace ${Math.floor(secs / 60)}m`
  return `hace ${Math.floor(secs / 3600)}h`
})
</script>

<style scoped>
@media (max-width: 480px) {
  .info-card { display: none; }
}

.info-card {
  position: absolute;
  bottom: 142px;
  right: 16px;
  z-index: 1000;

  background: var(--surface);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  box-shadow: var(--shadow-md);

  padding: 10px 14px 12px;
  min-width: 175px;
  overflow: hidden;
}

/* Accent left border */
.info-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 2px;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}

.info-card__header {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

.info-card__row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding: 3px 0;
}

.info-card__row--last {
  margin-top: 4px;
  padding-top: 6px;
  border-top: 1px solid var(--border);
}

.label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--txt-dim);
  font-family: var(--f-body);
  flex-shrink: 0;
}

.value {
  font-family: var(--f-mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--txt);
  text-align: right;
}

.value--accent {
  color: var(--accent);
  font-family: var(--f-body);
  font-weight: 600;
  font-size: 11px;
}
</style>
