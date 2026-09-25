import { authService } from '@/services/authService'

const HONEYPOT_PATHS = [
  '/admin',
  '/superadmin',
  '/admin-utama',
  '/admin-login',
  '/main-login',
  '/main-admin',
  '/super-admin'
]

export function authGuard(to) {
  const currentPath = (to.path || '').toLowerCase()

  // 0. Deteksi Jebakan (Honeypot Intrusion Detection)
  // Jika ada pihak luar yang mencoba menebak rute admin umum:
  if (HONEYPOT_PATHS.includes(currentPath)) {
    console.warn(`[SECURITY ALERT] Upaya akses liar terdeteksi ke rute: ${to.path}`)
    try {
      const threats = JSON.parse(localStorage.getItem('gp_security_threats') || '[]')
      threats.unshift({
        id: Date.now(),
        target: to.path,
        timestamp: new Date().toLocaleString('id-ID'),
        status: 'BLOCKED',
        type: 'Probe Honeypot (Akses Liar Admin Utama Dicegat)',
      })
      localStorage.setItem('gp_security_threats', JSON.stringify(threats.slice(0, 50)))
    } catch (e) {
      // ignore
    }
    // Langsung arahkan ke halaman 404 palsu
    return { name: 'not-found' }
  }

  const requiresAuth = to.matched.some((record) => record.meta && record.meta.requiresAuth)
  const isAuthenticated = authService.isAuthenticated()
  const currentUser = authService.getCurrentUser()
  const userRole = currentUser?.role || 'jemaat'

  // 1. Jika rute mewajibkan autentikasi tapi user belum login
  if (requiresAuth && !isAuthenticated) {
    if (to.meta?.role === 'superadmin') {
      return { name: 'main-login', query: { redirect: to.fullPath } }
    } else if (to.meta?.role === 'church_admin') {
      return { name: 'church-login', query: { redirect: to.fullPath } }
    } else {
      return { name: 'user-login', query: { redirect: to.fullPath } }
    }
  }

  // 2. Jika rute mewajibkan role tertentu dan user sudah login
  if (requiresAuth && isAuthenticated && to.meta?.role) {
    const requiredRole = to.meta.role

    // Superadmin punya akses penuh ke dashboard admin utama
    if (requiredRole === 'superadmin' && userRole !== 'superadmin') {
      if (userRole === 'church_admin') return { name: 'dashboard-church' }
      return { name: 'dashboard-user' }
    }

    // Admin Gereja / Cabang
    if (requiredRole === 'church_admin' && userRole !== 'church_admin' && userRole !== 'superadmin') {
      return { name: 'dashboard-user' }
    }

    // Jemaat
    if (requiredRole === 'jemaat' && userRole !== 'jemaat' && userRole !== 'superadmin') {
      if (userRole === 'church_admin') return { name: 'dashboard-church' }
      return { name: 'dashboard' }
    }
  }


}

