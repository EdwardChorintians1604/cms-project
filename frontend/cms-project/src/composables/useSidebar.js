import { ref } from 'vue'

// State global sidebar - default tertutup agar tidak menutupi halaman saat navigasi / logout
const isSidebarOpen = ref(false)

/**
 * Composable untuk mengelola state global sidebar.
 * Menyediakan state `isSidebarOpen`, `toggleSidebar`, `closeSidebar`, dan `openSidebar`.
 */
export function useSidebar() {
  const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  const closeSidebar = () => {
    isSidebarOpen.value = false
  }

  const openSidebar = () => {
    isSidebarOpen.value = true
  }

  return { isSidebarOpen, toggleSidebar, closeSidebar, openSidebar }
}
