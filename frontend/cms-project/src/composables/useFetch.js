import { ref, watchEffect } from 'vue'
import { apiFetch } from '@/services/api'

export function useFetch(url) {
  const data = ref(null)
  const error = ref(null)
  const loading = ref(true)

  const fetchData = async () => {
    loading.value = true
    error.value = null
    try {
      data.value = await apiFetch(url)
    } catch (err) {
      error.value = err
    } finally {
      loading.value = false
    }
  }

  watchEffect(() => {
    if (url) fetchData()
  })

  return { data, error, loading, refetch: fetchData }
}
