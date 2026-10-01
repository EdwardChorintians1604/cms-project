import { useAuthStore } from '@/stores/authStore'

export function useAuth() {
  const store = useAuthStore()
  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    setUser: store.setUser,
    unifiedLogin: store.unifiedLogin,
    fetchUser: store.fetchUser,
    login: store.login,
    mainLogin: store.mainLogin,
    churchLogin: store.churchLogin,
    logout: store.logout,
  }
}
