import { ref } from 'vue'
import { useAuth } from './useAuth'

export interface Trip {
  trip_num: number
  start_time: string
  end_time: string
  distance_km: number
  duration_min: number
  avg_speed: number | null
  max_speed: number
}

export interface Stats {
  total_trips: number
  total_km: number
  total_hours: number
  avg_speed: number | null
  max_speed: number | null
}

export interface TripLocation {
  id: number
  latitude: number
  longitude: number
  speed: number
  timestamp: string
}

export function useTrips() {
  const { authFetch } = useAuth()
  const trips = ref<Trip[]>([])
  const stats = ref<Stats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchData(deviceId: string, days = 30) {
    loading.value = true
    error.value = null
    try {
      const [tripsRes, statsRes] = await Promise.all([
        authFetch(`/api/trips?device_id=${encodeURIComponent(deviceId)}&days=${days}`),
        authFetch(`/api/stats?device_id=${encodeURIComponent(deviceId)}&days=${days}`),
      ])
      if (!tripsRes.ok) throw new Error(`Trips: HTTP ${tripsRes.status}`)
      if (!statsRes.ok) throw new Error(`Stats: HTTP ${statsRes.status}`)
      trips.value = await tripsRes.json()
      stats.value = await statsRes.json()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Error fetching trips'
    } finally {
      loading.value = false
    }
  }

  async function fetchTripRoute(
    deviceId: string,
    fromTs: string,
    toTs: string,
  ): Promise<TripLocation[]> {
    const res = await authFetch(
      `/api/locations?device_id=${encodeURIComponent(deviceId)}&from_ts=${encodeURIComponent(fromTs)}&to_ts=${encodeURIComponent(toTs)}`,
    )
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json()
  }

  return { trips, stats, loading, error, fetchData, fetchTripRoute }
}
