<template>
  <div class="bottombar">
    <svg class="clock-icon" width="12" height="12" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
    </svg>
    <span class="date">{{ formattedDate }}</span>
    <a
      v-if="googleMapsUrl"
      :href="googleMapsUrl"
      target="_blank"
      rel="noopener"
      class="maps-link"
    >
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
        <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
      </svg>
      Abrir en Maps
    </a>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  lastUpdate: string | null
  googleMapsUrl: string | null
  darkMode: boolean
}>()

const formattedDate = computed(() => {
  if (!props.lastUpdate) return 'Sin datos'
  try {
    return new Date(props.lastUpdate).toLocaleString('es-CL', {
      dateStyle: 'medium',
      timeStyle: 'short',
    })
  } catch {
    return props.lastUpdate
  }
})
</script>

<style scoped>
.bottombar {
  position: absolute;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;

  display: flex;
  align-items: center;
  gap: 10px;

  background: var(--surface);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border);
  border-radius: var(--r-pill);
  box-shadow: var(--shadow-md);

  padding: 8px 18px;
  font-size: 12px;
  font-family: var(--f-body);
  color: var(--txt-dim);
  font-weight: 500;
  white-space: nowrap;
}

.clock-icon {
  color: var(--accent);
  flex-shrink: 0;
}

.date {
  color: var(--txt-dim);
}

.maps-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: var(--r-pill);
  border: 1px solid var(--border-accent);
  background: var(--accent-dim);
  transition: background 0.15s ease, color 0.15s ease;
  margin-left: 4px;
}

.maps-link:hover {
  background: var(--accent);
  color: #fff;
  border-color: transparent;
}

/* separator between date and link */
.bottombar .date + .maps-link::before {
  display: none;
}
</style>
