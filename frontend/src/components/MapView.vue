<template>
  <div class="map-wrapper">
    <div ref="mapEl" class="map-container" />
    <div class="center-wrap">
      <button
        class="center-btn"
        :class="{ 'center-btn--flying': flying }"
        :disabled="!hasVehicle"
        @click="centerOnVehicle"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>
          <circle cx="12" cy="12" r="8" stroke-dasharray="2 3" stroke-width="1.2" opacity="0.4"/>
        </svg>
      </button>

      <!-- Coords tooltip — always visible -->
      <div class="coords-tooltip">
        <div class="coords-row">
          <span class="coords-label">LAT</span>
          <span class="coords-val">{{ fmtCoord(selectedDevice?.location.latitude) }}</span>
        </div>
        <div class="coords-row">
          <span class="coords-label">LNG</span>
          <span class="coords-val">{{ fmtCoord(selectedDevice?.location.longitude) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import L from 'leaflet'
import type { Device } from '../composables/useDevices'
import type { TripLocation } from '../composables/useTrips'

const props = defineProps<{
  devices: Device[]
  darkMode: boolean
  selectedDeviceId: string | null
  tripRoute: TripLocation[] | null
}>()

const mapEl = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let tileLayer: L.TileLayer | null = null
const markerMap = new Map<string, L.Marker>()
const flying = ref(false)
let hasInitiallyPanned = false

function fmtCoord(n: number | null | undefined): string {
  return n != null ? n.toFixed(6) : '—'
}

// Route and accuracy layers
let routeLayer: L.LayerGroup | null = null
let accuracyCircle: L.Circle | null = null
let accuracyPulse: L.Circle | null = null
let routeGeneration = 0
let matchController: AbortController | null = null

// ── Selected device ──────────────────────────────────────────

const selectedDevice = computed(() =>
  props.devices.find(d => d.id === props.selectedDeviceId) ?? props.devices[0] ?? null
)

const hasVehicle = computed(() =>
  selectedDevice.value?.location.latitude != null &&
  selectedDevice.value?.location.longitude != null
)

// ── Speed colors ─────────────────────────────────────────────

function speedColor(speed: number): string {
  if (speed === 0) return '#6b7280'
  if (speed < 40) return '#22c55e'
  if (speed < 80) return '#f59e0b'
  return '#ef4444'
}

// ── Vehicle icon ─────────────────────────────────────────────

function buildIcon(speed: number): L.DivIcon {
  const color = speedColor(speed)
  const isMoving = speed > 0
  const pulse = isMoving
    ? `<div style="position:absolute;inset:-6px;border-radius:50%;border:2px solid ${color};opacity:.5;animation:pulse 2s infinite"></div>`
    : ''

  return L.divIcon({
    className: '',
    html: `
      <div style="position:relative;width:28px;height:28px">
        ${pulse}
        <div style="
          width:28px;height:28px;border-radius:50%;
          background:${color};border:3px solid white;
          box-shadow:0 2px 8px rgba(0,0,0,.4);
          display:flex;align-items:center;justify-content:center;
          font-size:13px
        ">🚗</div>
      </div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  })
}

// ── GPS Accuracy circle (≤5 m) ───────────────────────────────

function updateAccuracyCircle() {
  if (!map || !selectedDevice.value) return
  const { latitude, longitude } = selectedDevice.value.location
  if (latitude == null || longitude == null) return

  const latlng: L.LatLngExpression = [latitude, longitude]

  if (accuracyCircle) {
    accuracyCircle.setLatLng(latlng)
    accuracyPulse?.setLatLng(latlng)
  } else {
    // Outer pulsing ring
    accuracyPulse = L.circle(latlng, {
      radius: 5,
      color: '#00c2cb',
      fillColor: '#00c2cb',
      fillOpacity: 0.08,
      weight: 1,
      opacity: 0.3,
      className: 'accuracy-pulse',
    }).addTo(map)

    // Inner solid circle
    accuracyCircle = L.circle(latlng, {
      radius: 5,
      color: '#00c2cb',
      fillColor: '#00c2cb',
      fillOpacity: 0.15,
      weight: 1.5,
      opacity: 0.6,
      className: 'accuracy-ring',
    }).addTo(map)
  }
}

function removeAccuracyCircle() {
  accuracyCircle?.remove()
  accuracyPulse?.remove()
  accuracyCircle = null
  accuracyPulse = null
}

// ── Trip route polyline ──────────────────────────────────────

async function fetchMapMatchedRoute(locations: TripLocation[]): Promise<L.LatLngExpression[] | null> {
  // Route API accepts up to 25 waypoints; sample evenly keeping start and end
  const MAX = 25
  let pts = locations
  if (pts.length > MAX) {
    const step = Math.ceil((pts.length - 2) / (MAX - 2))
    const sampled: TripLocation[] = [pts[0]]
    for (let i = step; i < pts.length - 1; i += step) sampled.push(pts[i])
    sampled.push(pts[pts.length - 1])
    pts = sampled
  }

  matchController?.abort()
  matchController = new AbortController()

  const coords = pts.map(p => `${p.longitude},${p.latitude}`).join(';')

  try {
    const url = `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`
    const res = await fetch(url, { signal: matchController.signal })
    if (!res.ok) {
      console.warn('[OSRM] route failed:', res.status)
      return null
    }
    const data = await res.json()
    if (data.code !== 'Ok' || !data.routes?.length) {
      console.warn('[OSRM] no route:', data.code, data.message)
      return null
    }

    return (data.routes[0].geometry.coordinates as [number, number][])
      .map(([lng, lat]) => [lat, lng] as L.LatLngExpression)
  } catch (e) {
    if ((e as Error).name !== 'AbortError') console.warn('[OSRM] fetch error:', e)
    return null
  }
}

function nearestSpeed(lat: number, lng: number, locations: TripLocation[]): number {
  let minDist = Infinity
  let speed = 0
  for (const loc of locations) {
    const d = (loc.latitude - lat) ** 2 + (loc.longitude - lng) ** 2
    if (d < minDist) { minDist = d; speed = loc.speed }
  }
  return speed
}

async function drawTripRoute(locations: TripLocation[]) {
  const gen = ++routeGeneration
  if (!map) return
  clearRouteLayer()
  if (locations.length < 2) return

  routeLayer = L.layerGroup().addTo(map)

  const matched = await fetchMapMatchedRoute(locations)
  if (gen !== routeGeneration) return  // a newer route was requested while waiting

  if (matched) {
    // Draw road-following route with interpolated speed colors
    for (let i = 1; i < matched.length; i++) {
      const [lat, lng] = matched[i] as [number, number]
      L.polyline([matched[i - 1], matched[i]], {
        color: speedColor(nearestSpeed(lat, lng, locations)),
        weight: 5,
        opacity: 0.85,
        lineCap: 'round',
        lineJoin: 'round',
      }).addTo(routeLayer!)
    }
  } else {
    // Fallback: straight lines between GPS points
    for (let i = 1; i < locations.length; i++) {
      const prev = locations[i - 1]
      const curr = locations[i]
      L.polyline(
        [[prev.latitude, prev.longitude], [curr.latitude, curr.longitude]],
        { color: speedColor(curr.speed), weight: 5, opacity: 0.85, lineCap: 'round', lineJoin: 'round' },
      ).addTo(routeLayer!)
    }
  }

  // Start marker (green)
  const first = locations[0]
  L.circleMarker([first.latitude, first.longitude], {
    radius: 8, color: '#fff', weight: 2.5, fillColor: '#22c55e', fillOpacity: 1,
  }).bindTooltip('Inicio', { direction: 'top' }).addTo(routeLayer!)

  // End marker (red)
  const last = locations[locations.length - 1]
  L.circleMarker([last.latitude, last.longitude], {
    radius: 8, color: '#fff', weight: 2.5, fillColor: '#ef4444', fillOpacity: 1,
  }).bindTooltip('Fin', { direction: 'top' }).addTo(routeLayer!)

  // Fit map to the route
  const bounds = L.latLngBounds(locations.map(l => [l.latitude, l.longitude] as L.LatLngExpression))
  map.fitBounds(bounds, { padding: [60, 60], maxZoom: 17 })
}

function clearRouteLayer() {
  matchController?.abort()
  routeLayer?.remove()
  routeLayer = null
}

// ── Tiles ────────────────────────────────────────────────────

const TILES = {
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
  dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
}
const ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'

function updateTiles() {
  if (!map) return
  tileLayer?.remove()
  tileLayer = L.tileLayer(props.darkMode ? TILES.dark : TILES.light, {
    attribution: ATTRIBUTION,
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map)
}

// ── Markers ──────────────────────────────────────────────────

function updateMarkers() {
  if (!map) return

  const seen = new Set<string>()

  for (const device of props.devices) {
    const { latitude, longitude } = device.location
    if (latitude == null || longitude == null) continue

    seen.add(device.id)
    const latlng: L.LatLngExpression = [latitude, longitude]
    const icon = buildIcon(device.speed)

    const tooltipHtml = `
      <div style="font-size:12px;line-height:1.7;min-width:180px">
        <strong style="font-size:14px;letter-spacing:.04em">${device.vehicle.plate ?? device.id}</strong><br/>
        <span style="opacity:.8">${device.status_name ?? '—'} &bull; ${device.speed} km/h</span><br/>
        <span style="opacity:.6;font-size:11px">Lat: ${fmtCoord(latitude)} &nbsp; Lng: ${fmtCoord(longitude)}</span><br/>
        <span style="opacity:.5;font-size:10px">${device.last_update ?? ''}</span>
      </div>`

    if (markerMap.has(device.id)) {
      const m = markerMap.get(device.id)!
      m.setLatLng(latlng)
      m.setIcon(icon)
      m.setTooltipContent(tooltipHtml)
    } else {
      const m = L.marker(latlng, { icon })
        .bindTooltip(tooltipHtml, { permanent: false, direction: 'top', offset: [0, -16] })
        .addTo(map)
      markerMap.set(device.id, m)
    }
  }

  // Remove stale markers
  for (const [id, marker] of markerMap) {
    if (!seen.has(id)) {
      marker.remove()
      markerMap.delete(id)
    }
  }

  // Pan to selected device only on first load
  if (!hasInitiallyPanned && selectedDevice.value?.location.latitude != null) {
    map.setView(
      [selectedDevice.value.location.latitude!, selectedDevice.value.location.longitude!],
      15,
    )
    hasInitiallyPanned = true
  }

  // Update accuracy circle position
  updateAccuracyCircle()
}

// ── Center on vehicle ─────────────────────────────────────────

function centerOnVehicle() {
  if (!map || !hasVehicle.value || !selectedDevice.value) return

  flying.value = true
  map.flyTo(
    [selectedDevice.value.location.latitude!, selectedDevice.value.location.longitude!],
    16,
    { duration: 1.4, easeLinearity: 0.2 },
  )
  setTimeout(() => { flying.value = false }, 1600)
}

// ── Lifecycle ─────────────────────────────────────────────────

onMounted(() => {
  if (!mapEl.value) return
  map = L.map(mapEl.value, { zoomControl: false, preferCanvas: false }).setView([-33.45, -70.65], 13)
  L.control.zoom({ position: 'bottomleft' }).addTo(map)
  updateTiles()
  updateMarkers()
})

onUnmounted(() => {
  removeAccuracyCircle()
  clearRouteLayer()
  map?.remove()
  map = null
})

// ── Watchers ──────────────────────────────────────────────────

watch(() => props.darkMode, updateTiles)
watch(() => props.devices, updateMarkers, { deep: true })

watch(() => props.selectedDeviceId, (newId) => {
  if (!map || !newId) return
  clearRouteLayer()
  const device = props.devices.find(d => d.id === newId)
  if (device?.location.latitude != null && device?.location.longitude != null) {
    map.flyTo([device.location.latitude, device.location.longitude], 16, {
      duration: 1.2,
      easeLinearity: 0.25,
    })
  }
})

watch(() => props.tripRoute, (route) => {
  if (route && route.length > 0) {
    drawTripRoute(route)
  } else {
    clearRouteLayer()
  }
})
</script>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.map-container {
  width: 100%;
  height: 100%;
}

/* ── Center Button + Tooltip wrapper ────────────────────────── */
.center-wrap {
  position: absolute;
  bottom: 90px;
  right: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

/* Tooltip — always visible */
.coords-tooltip {
  background: var(--surface);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border-accent);
  border-radius: var(--r-sm);
  box-shadow: var(--shadow-md);
  padding: 7px 11px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  pointer-events: none;
}

.coords-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coords-label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--txt-dim);
  font-family: var(--f-body);
  width: 22px;
  flex-shrink: 0;
}

.coords-val {
  font-family: var(--f-mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--txt);
  white-space: nowrap;
}

/* ── Center Button ─────────────────────────────────────────── */
.center-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--surface);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 2px solid var(--border-accent);
  border-radius: var(--r-sm);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  color: var(--accent);
  transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
}
.center-btn:hover {
  background: var(--accent);
  color: #fff;
  border-color: transparent;
  transform: scale(1.06);
}
.center-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.center-btn:disabled:hover {
  background: var(--surface);
  color: var(--accent);
  transform: none;
}
.center-btn--flying {
  animation: spin-locate 1.4s ease-in-out;
}
@keyframes spin-locate {
  0%   { transform: scale(1) rotate(0deg); }
  30%  { transform: scale(1.12) rotate(180deg); }
  100% { transform: scale(1) rotate(360deg); }
}
</style>

<style>
/* ── Pulse animation for vehicle marker ─────────────────────── */
@keyframes pulse {
  0%   { transform: scale(1);   opacity: .5; }
  50%  { transform: scale(1.4); opacity: .15; }
  100% { transform: scale(1);   opacity: .5; }
}

/* ── GPS accuracy circle animations ─────────────────────────── */
.accuracy-ring path {
  transition: all 0.5s ease;
}

.accuracy-pulse path {
  animation: accuracy-expand 3s ease-in-out infinite;
}

@keyframes accuracy-expand {
  0%   { opacity: 0.3; transform-origin: center; transform: scale(1); }
  50%  { opacity: 0.1; transform: scale(1.4); }
  100% { opacity: 0.3; transform: scale(1); }
}
</style>
