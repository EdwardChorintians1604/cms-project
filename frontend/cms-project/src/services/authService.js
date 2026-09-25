import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'

export const authService = {
  async register(payload) {
    try {
      const response = await fetch(`${APP_CONFIG.apiBaseUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}))
        throw new Error(errJson.detail || 'Pendaftaran gagal.')
      }

      return response.json()
    } catch (err) {
      console.error('Register error:', err)
      throw err
    }
  },

  // 1. Unified Single Login (Satu Pintu Masuk Cerdas)
  // HANYA 1 request ke server → server deteksi role otomatis (superadmin/church_admin/jemaat)
  // Tidak ada lagi trial-error 3 endpoint yang membuang kuota rate limiter.
  async unifiedLogin(credentials) {
    const formData = new URLSearchParams()
    formData.append('username', credentials.identifier || credentials.email || credentials.username || '')
    formData.append('password', credentials.password || '')
    if (credentials.securityPin) {
      formData.append('security_pin', credentials.securityPin)
    }
    if (credentials.churchCode) {
      formData.append('church_code', credentials.churchCode)
    }

    const response = await fetch(`${APP_CONFIG.apiBaseUrl}/auth/unified-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    })

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({}))
      throw new Error(errJson.detail || 'Email/Username atau kata sandi tidak cocok.')
    }

    const data = await response.json()
    const accessToken = data.access_token
    const detectedRole = data.role || 'jemaat'

    if (accessToken) {
      storage.set(STORAGE_KEYS.AUTH_TOKEN, accessToken)

      // Ambil profil user dari /users/me
      try {
        const userResponse = await fetch(`${APP_CONFIG.apiBaseUrl}/users/me`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        })
        if (userResponse.ok) {
          const userData = await userResponse.json()
          const userWithRole = { ...userData, role: detectedRole }
          storage.set(STORAGE_KEYS.USER_DATA, userWithRole)
          return { user: userWithRole, token: accessToken, role: detectedRole }
        }
      } catch (meError) {
        console.warn('Gagal mengambil profil user:', meError)
      }

      // Fallback minimal jika /users/me gagal
      const fallbackUser = {
        username: credentials.identifier || credentials.email || '',
        role: detectedRole,
      }
      storage.set(STORAGE_KEYS.USER_DATA, fallbackUser)
      return { user: fallbackUser, token: accessToken, role: detectedRole }
    }

    throw new Error('Token tidak diterima dari server.')
  },

  // 2. Login fleksibel dan otomatis mendeteksi peran / endpoint yang sesuai
  async login(credentials, roleHint = null) {
    let targetRole = roleHint || credentials?.role

    if (!targetRole) {
      if (
        credentials?.securityPin !== undefined ||
        (typeof window !== 'undefined' && (window.location.pathname.includes('grace-console-x99') || window.location.pathname.includes('main-login')))
      ) {
        targetRole = 'superadmin'
      } else if (
        credentials?.churchCode !== undefined ||
        (typeof window !== 'undefined' && window.location.pathname.includes('church-login'))
      ) {
        targetRole = 'church_admin'
      } else {
        targetRole = 'jemaat'
      }
    }

    if (targetRole === 'superadmin' || targetRole === 'admin') {
      return this.mainLogin(credentials)
    } else if (targetRole === 'church_admin' || targetRole === 'church') {
      return this.churchLogin(credentials)
    } else {
      return this._loginEndpoint('/auth/jemaat/login', credentials, 'jemaat')
    }
  },

  // 2. Login Admin Utama / Developer (HANYA untuk tabel main_admin)
  async mainLogin(credentials) {
    return this._loginEndpoint('/auth/main-admin/login', credentials, 'superadmin')
  },

  // 3. Login Admin Cabang Gereja (HANYA untuk tabel church_admins)
  async churchLogin(credentials) {
    return this._loginEndpoint('/auth/church-admin/login', credentials, 'church_admin')
  },

  async _loginEndpoint(path, credentials, defaultRole) {
    try {
      const identifier = credentials.identifier || credentials.email || credentials.username || credentials.churchCode
      const password = credentials.password

      const formData = new URLSearchParams()
      formData.append('username', identifier)
      formData.append('password', password)
      if (credentials.churchCode) {
        formData.append('church_code', credentials.churchCode)
      }
      if (credentials.securityPin) {
        formData.append('security_pin', credentials.securityPin)
      }

      const response = await fetch(`${APP_CONFIG.apiBaseUrl}${path}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      })

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}))
        throw new Error(errJson.detail || 'Kredensial tidak valid.')
      }

      const tokenData = await response.json()
      const accessToken = tokenData.access_token

      if (accessToken) {
        storage.set(STORAGE_KEYS.AUTH_TOKEN, accessToken)

        // Fetch user profile from /users/me
        try {
          const userResponse = await fetch(`${APP_CONFIG.apiBaseUrl}/users/me`, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          })
          if (userResponse.ok) {
            const userData = await userResponse.json()
            storage.set(STORAGE_KEYS.USER_DATA, userData)
            return { user: userData, token: accessToken }
          }
        } catch (meError) {
          console.warn('Gagal mengambil profil user:', meError)
        }

        const fallbackUser = { username: identifier, role: defaultRole, full_name: identifier }
        storage.set(STORAGE_KEYS.USER_DATA, fallbackUser)
        return { user: fallbackUser, token: accessToken }
      }

      throw new Error('Token tidak diterima dari server.')
    } catch (err) {
      console.error('Login error:', err)
      throw err
    }
  },

  logout() {
    storage.remove(STORAGE_KEYS.AUTH_TOKEN)
    storage.remove(STORAGE_KEYS.USER_DATA)
    if (typeof window !== 'undefined') {
      localStorage.removeItem('cms_auth_token')
      localStorage.removeItem('cms_user_data')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      sessionStorage.clear()
    }
  },

  getCurrentUser() {
    return storage.get(STORAGE_KEYS.USER_DATA)
  },

  isAuthenticated() {
    return !!storage.get(STORAGE_KEYS.AUTH_TOKEN)
  },

  async getCurrentUserFromApi() {
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    if (!token) return null

    const response = await fetch(`${APP_CONFIG.apiBaseUrl}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (!response.ok) {
      if (response.status === 401) this.logout()
      throw new Error('Sesi login sudah tidak berlaku.')
    }

    const user = await response.json()
    const userWithRole = { ...user, role: user.role || 'jemaat' }
    storage.set(STORAGE_KEYS.USER_DATA, userWithRole)
    return userWithRole
  },
}
