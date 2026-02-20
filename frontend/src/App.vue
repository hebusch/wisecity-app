<template>
  <!-- Login screen -->
  <LoginView v-if="!isAuthenticated && !awaitingPasskeySetup" />

  <!-- Intermediate passkey setup (after password login, before map) -->
  <PasskeySetupView
    v-else-if="awaitingPasskeySetup"
    :email="currentEmail ?? ''"
  />

  <!-- Main app -->
  <div v-else class="app-shell">
    <MapView
      :devices="devices"
      :dark-mode="darkMode"
      :selected-device-id="selectedDeviceId"
      :trip-route="tripRoute"
    />

    <TopBar
      :plate="primaryDevice?.vehicle.plate ?? '—'"
      :status-name="primaryDevice?.status_name ?? null"
      :speed="primaryDevice?.speed ?? 0"
      :loading="loading"
      :dark-mode="darkMode"
      :device-count="devices.length"
      :has-trip-route="!!tripRoute"
      :email="currentEmail ?? ''"
      :has-passkey="hasPasskey"
      @refresh="fetchDevices"
      @toggle-dark="toggleDark"
      @toggle-dashboard="showDashboard = !showDashboard"
      @toggle-device-selector="showDeviceSelector = !showDeviceSelector"
      @clear-route="clearTripRoute"
      @logout="handleLogout"
    />

    <BottomBar
      :last-update="primaryDevice?.last_update ?? null"
      :google-maps-url="primaryDevice?.google_maps_url ?? null"
      :dark-mode="darkMode"
    />

    <SpeedLegend :dark-mode="darkMode" />

    <Dashboard
      :visible="showDashboard"
      :device-id="primaryDevice?.id ?? null"
      :dark-mode="darkMode"
      @close="showDashboard = false"
      @show-route="onShowTripRoute"
    />

    <DeviceSelector
      :visible="showDeviceSelector"
      :devices="devices"
      :selected-id="selectedDeviceId"
      @close="showDeviceSelector = false"
      @select="onDeviceSelected"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuth } from './composables/useAuth'
import { useDevices } from './composables/useDevices'
import { useTrips, type TripLocation } from './composables/useTrips'
import LoginView from './views/LoginView.vue'
import PasskeySetupView from './views/PasskeySetupView.vue'
import MapView from './components/MapView.vue'
import TopBar from './components/TopBar.vue'
import BottomBar from './components/BottomBar.vue'
import SpeedLegend from './components/SpeedLegend.vue'
import Dashboard from './components/Dashboard.vue'
import DeviceSelector from './components/DeviceSelector.vue'

const {
  isAuthenticated, awaitingPasskeySetup, sessionExpired, logout,
  currentEmail, hasPasskey,
} = useAuth()
const { fetchTripRoute } = useTrips()
const { devices, loading, fetchDevices } = useDevices()

// Session expired → auto-redirect to login
watch(sessionExpired, (val) => {
  if (val) devices.value = []
})

// Fetch devices immediately after a successful login
watch(isAuthenticated, (val) => {
  if (val) fetchDevices()
})

// Selected device
const selectedDeviceId = ref<string | null>(null)
watch(devices, (devs) => {
  if (!selectedDeviceId.value && devs.length > 0) {
    selectedDeviceId.value = devs[0].id
  }
}, { immediate: true })

const primaryDevice = computed(() =>
  devices.value.find(d => d.id === selectedDeviceId.value) ?? devices.value[0] ?? null
)

function onDeviceSelected(deviceId: string) {
  selectedDeviceId.value = deviceId
  tripRoute.value = null
}

// Trip route on map
const tripRoute = ref<TripLocation[] | null>(null)
const routeLoading = ref(false)

async function onShowTripRoute(payload: { deviceId: string; startTime: string; endTime: string }) {
  routeLoading.value = true
  showDashboard.value = false
  try {
    const locations = await fetchTripRoute(payload.deviceId, payload.startTime, payload.endTime)
    tripRoute.value = locations.length > 0 ? locations : null
  } catch {
    tripRoute.value = null
  } finally {
    routeLoading.value = false
  }
}

function clearTripRoute() {
  tripRoute.value = null
}

// Dark mode
const darkMode = ref(window.matchMedia('(prefers-color-scheme: dark)').matches)
watch(darkMode, (val) => {
  document.documentElement.classList.toggle('dark', val)
}, { immediate: true })

function toggleDark() {
  darkMode.value = !darkMode.value
}

// UI state
const showDashboard = ref(false)
const showDeviceSelector = ref(false)

async function handleLogout() {
  showDashboard.value = false
  showDeviceSelector.value = false
  tripRoute.value = null
  devices.value = []
  selectedDeviceId.value = null
  await logout()
}

</script>

<style scoped>
.app-shell {
  position: relative;
  width: 100%;
  height: 100%;
  background: var(--bg);
  transition: background 0.3s ease;
}
</style>
