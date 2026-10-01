import { reactive, computed } from 'vue'
import { authService } from '@/services/authService'

const state = reactive({
  user: authService.getCurrentUser(),
  token: authService.isAuthenticated(),
  isLoading: false,
})

export const useAuthStore = () => {
  const isAuthenticated = computed(() => !!state.user)
  const user = computed(() => state.user)
  const isLoading = computed(() => state.isLoading)

  const login = async (credentials, roleHint = null) => {
    state.isLoading = true
    try {
      const res = await authService.login(credentials, roleHint)
      state.user = res.user
      state.token = res.token
      return res
    } finally {
      state.isLoading = false
    }
  }

  const mainLogin = async (credentials) => {
    state.isLoading = true
    try {
      const res = await authService.mainLogin(credentials)
      state.user = res.user
      state.token = res.token
      return res
    } finally {
      state.isLoading = false
    }
  }

  const churchLogin = async (credentials) => {
    state.isLoading = true
    try {
      const res = await authService.churchLogin(credentials)
      state.user = res.user
      state.token = res.token
      return res
    } finally {
      state.isLoading = false
    }
  }

  const setUser = (userData) => {
    state.user = userData
    if (userData) {
      storage.set(STORAGE_KEYS.USER_DATA, userData)
    }
  }

  const unifiedLogin = async (credentials) => {
    state.isLoading = true
    try {
      const res = await authService.unifiedLogin(credentials)
      state.user = res.user
      state.token = res.token
      return res
    } finally {
      state.isLoading = false
    }
  }

  const setToken = (token) => {
    state.token = token
  }

  const fetchUser = async () => {
    state.user = await authService.getCurrentUserFromApi()
    return state.user
  }

  const logout = () => {
    authService.logout()
    state.user = null
    state.token = null
  }

  return {
    state,
    user,
    isAuthenticated,
    isLoading,
    setUser,
    unifiedLogin,
    login,
    mainLogin,
    churchLogin,
    setToken,
    fetchUser,
    logout,
  }
}
