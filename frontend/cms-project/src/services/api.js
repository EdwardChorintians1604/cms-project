import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'

export async function apiFetch(endpoint, options = {}) {
  const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(`${APP_CONFIG.apiBaseUrl}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.message || `HTTP Error ${response.status}`)
  }

  return response.json()
}
