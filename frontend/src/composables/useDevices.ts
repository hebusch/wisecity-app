import { ref, onMounted, onUnmounted } from 'vue'
import { useAuth } from './useAuth'

export interface DeviceLocation {
  latitude: number | null
  longitude: number | null
}

export interface DeviceVehicle {
  plate: string | null
  brand: string | null
  model: string | null
  year: number | null
}

export interface Device {
  id: string
  name: string | null
  vehicle: DeviceVehicle
  location: DeviceLocation
  status_name: string | null
  speed: number
  last_update: string | null
  locked: boolean
  google_maps_url: string | null
}

export function useDevices() {
  const { authFetch } = useAuth()
  const devices = ref<Device[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetched = ref<Date | null>(null)

  let intervalId: ReturnType<typeof setInterval> | null = null

  async function fetchDevices() {
    loading.value = true
    error.value = null
    try {
      const res = await authFetch('/api/devices')
      if (res.status === 401) return  // useAuth handles clearing token
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      devices.value = await res.json()
      lastFetched.value = new Date()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Error fetching devices'
    } finally {
      loading.value = false
    }
  }

  function startPolling(intervalMs = 60_000) {
    fetchDevices()
    intervalId = setInterval(fetchDevices, intervalMs)
  }

  function stopPolling() {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  onMounted(() => startPolling())
  onUnmounted(() => stopPolling())

  return { devices, loading, error, lastFetched, fetchDevices }
}
