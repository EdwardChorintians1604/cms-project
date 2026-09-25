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
    login,
    mainLogin,
    churchLogin,
    setToken,
    fetchUser,
    logout,
  }
}
