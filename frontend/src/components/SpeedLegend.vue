<template>
  <div class="legend">
    <div class="legend__title">Velocidad</div>
    <div v-for="item in items" :key="item.label" class="legend__item">
      <span class="swatch" :style="{ '--sw-color': item.color }" />
      <span class="legend__label">{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ darkMode: boolean }>()

const items = [
  { label: 'Detenido', color: '#6b7280' },
  { label: '< 40 km/h', color: '#22c55e' },
  { label: '40–80 km/h', color: '#f59e0b' },
  { label: '> 80 km/h', color: '#ef4444' },
]
</script>

<style scoped>
.legend {
  position: absolute;
  bottom: 142px;
  left: 16px;
  z-index: 1000;

  background: var(--surface);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  box-shadow: var(--shadow-md);

  padding: 10px 13px 11px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.legend__title {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--txt-dim);
  margin-bottom: 7px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

.legend__item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 3px 0;
}

.swatch {
  display: block;
  width: 3px;
  height: 14px;
  border-radius: 2px;
  background: var(--sw-color);
  flex-shrink: 0;
  box-shadow: 0 0 6px var(--sw-color);
}

.legend__label {
  font-size: 11px;
  font-weight: 500;
  color: var(--txt);
  font-family: var(--f-body);
}
</style>
