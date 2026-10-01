<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import { useAuth } from '@/composables/useAuth'
import { APP_CONFIG } from '@/config'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const { user, setUser } = useAuth()

// State Data Profil
const isLoading = ref(true)
const isSubmitting = ref(false)
const isModalOpen = ref(false)
const isPasswordModalOpen = ref(false)
const toastMessage = ref('')
const toastType = ref('success') // 'success' | 'error'
const showToast = ref(false)

const profileData = ref({
  id: null,
  church_id: null,
  church_code: '',
  church_name: '',
  city: '',
  admin_name: '',
  email: '',
  phone: '',
  address: '',
  latitude: -6.1824,
  longitude: 106.9856,
  google_maps_url: '',
  status: 'Aktif',
  created_at: null,
  role: 'church_admin',
})

// Form Edit Data
const editForm = reactive({
  admin_name: '',
  email: '',
  phone: '',
  city: '',
  address: '',
  latitude: null,
  longitude: null,
  google_maps_url: '',
})

// Form Ganti Password
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// Leaflet Map State
const miniMapContainer = ref(null)
const editMapContainer = ref(null)
let miniMap = null
let miniMarker = null
let editMap = null
let editMarker = null

const triggerToast = (msg, type = 'success') => {
  toastMessage.value = msg
  toastType.value = type
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 4000)
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}

// Inisialisasi Peta Tampilan (Read-only Mini Map)
const initMiniMap = () => {
  if (!miniMapContainer.value) return
  const lat = Number(profileData.value.latitude) || -6.1824
  const lng = Number(profileData.value.longitude) || 106.9856

  if (miniMap) {
    miniMap.invalidateSize()
    miniMap.setView([lat, lng], 15)
    if (miniMarker) miniMarker.setLatLng([lat, lng])
    return
  }

  miniMap = L.map(miniMapContainer.value, {
    center: [lat, lng],
    zoom: 15,
    zoomControl: true,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(miniMap)

  const pinIcon = L.divIcon({
    className: 'custom-pin',
    html: `
      <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-full">
        <span class="absolute w-8 h-8 rounded-full bg-amber-500/40 animate-ping"></span>
        <div class="w-10 h-10 rounded-full bg-slate-900 border-2 border-amber-400 flex items-center justify-center shadow-xl text-amber-300 font-bold">
          ⛪
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
  })

  miniMarker = L.marker([lat, lng], { icon: pinIcon }).addTo(miniMap)
  miniMarker.bindPopup(`
    <div class="text-xs p-1">
      <strong class="text-amber-600 block text-sm font-serif mb-1">${profileData.value.church_name || 'Gereja Cabang'}</strong>
      <p class="text-slate-600 mb-1">${profileData.value.address || 'Alamat Cabang'}</p>
      <span class="text-[10px] text-slate-500 font-mono">${lat.toFixed(5)}, ${lng.toFixed(5)}</span>
    </div>
  `)
}

// Inisialisasi Peta Modal Edit (Interactive Map)
const initEditMap = () => {
  if (!editMapContainer.value) return
  const lat = Number(editForm.latitude) || -6.1824
  const lng = Number(editForm.longitude) || 106.9856

  if (editMap) {
    editMap.invalidateSize()
    editMap.setView([lat, lng], 15)
    if (editMarker) editMarker.setLatLng([lat, lng])
    return
  }

  editMap = L.map(editMapContainer.value, {
    center: [lat, lng],
    zoom: 14,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(editMap)

  const editPinIcon = L.divIcon({
    className: 'custom-edit-pin',
    html: `
      <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-full">
        <div class="w-8 h-8 rounded-full bg-amber-500 border-2 border-slate-900 flex items-center justify-center shadow-lg text-slate-950 font-bold text-xs">
          📍
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  })

  editMarker = L.marker([lat, lng], { icon: editPinIcon, draggable: true }).addTo(editMap)

  editMarker.on('dragend', (e) => {
    const pos = e.target.getLatLng()
    editForm.latitude = parseFloat(pos.lat.toFixed(6))
    editForm.longitude = parseFloat(pos.lng.toFixed(6))
    editForm.google_maps_url = `https://www.google.com/maps/search/?api=1&query=${editForm.latitude},${editForm.longitude}`
  })

  editMap.on('click', (e) => {
    const lat = parseFloat(e.latlng.lat.toFixed(6))
    const lng = parseFloat(e.latlng.lng.toFixed(6))
    editForm.latitude = lat
    editForm.longitude = lng
    editForm.google_maps_url = `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`
    if (editMarker) editMarker.setLatLng([lat, lng])
  })
}

// 1. READ: Ambil Data Akun Admin Gereja yang Sedang Login
const loadProfile = async () => {
  isLoading.value = true
  try {
    const token = localStorage.getItem('gp_auth_token')
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!res.ok) {
      throw new Error('Gagal mengambil data profil admin gereja.')
    }

    const data = await res.json()
    profileData.value = {
      ...profileData.value,
      ...data,
      admin_name: data.admin_name || data.full_name || 'Admin Gereja',
    }

    // Jika admin_id tersedia, pastikan data sinkron dari tabel church-admins
    if (data.id) {
      const detailRes = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${data.id}`)
      if (detailRes.ok) {
        const detail = await detailRes.json()
        profileData.value = {
          ...profileData.value,
          ...detail,
        }
      }
    }

    nextTick(() => {
      initMiniMap()
    })
  } catch (err) {
    console.error('Error load profile:', err)
    triggerToast(err.message || 'Gagal memuat data profil.', 'error')
  } finally {
    isLoading.value = false
  }
}

// Buka Modal Edit
const openEditModal = () => {
  editForm.admin_name = profileData.value.admin_name || ''
  editForm.email = profileData.value.email || ''
  editForm.phone = profileData.value.phone || ''
  editForm.city = profileData.value.city || ''
  editForm.address = profileData.value.address || ''
  editForm.latitude = profileData.value.latitude || -6.1824
  editForm.longitude = profileData.value.longitude || 106.9856
  editForm.google_maps_url = profileData.value.google_maps_url || ''

  isModalOpen.value = true
  nextTick(() => {
    initEditMap()
  })
}

// Buka Modal Ganti Password
const openPasswordModal = () => {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  isPasswordModalOpen.value = true
}

// 2. UPDATE: Simpan Perubahan Data Profil Admin
const handleSaveProfile = async () => {
  if (!editForm.admin_name.trim()) {
    triggerToast('Nama lengkap admin tidak boleh kosong.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      admin_name: editForm.admin_name.trim(),
      phone: editForm.phone.trim(),
      city: editForm.city.trim(),
      address: editForm.address.trim(),
      latitude: editForm.latitude ? parseFloat(editForm.latitude) : null,
      longitude: editForm.longitude ? parseFloat(editForm.longitude) : null,
      google_maps_url: editForm.google_maps_url || undefined,
    }

    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${profileData.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Gagal memperbarui profil.')
    }

    const updated = await res.json()
    profileData.value = {
      ...profileData.value,
      ...updated,
    }

    // Perbarui reaktif user di AuthStore & LocalStorage
    const updatedUserStore = {
      ...user.value,
      ...profileData.value,
      full_name: updated.admin_name,
      admin_name: updated.admin_name,
      name: updated.admin_name,
    }
    setUser(updatedUserStore)

    triggerToast('Profil admin cabang gereja berhasil diperbarui!')
    isModalOpen.value = false

    nextTick(() => {
      initMiniMap()
    })
  } catch (err) {
    console.error('Update error:', err)
    triggerToast(err.message || 'Terjadi kesalahan saat menyimpan data.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 3. UPDATE: Ganti Kata Sandi Admin
const handleSavePassword = async () => {
  if (!passwordForm.new_password) {
    triggerToast('Silakan masukkan kata sandi baru.', 'error')
    return
  }
  if (passwordForm.new_password.length < 6) {
    triggerToast('Kata sandi baru minimal 6 karakter.', 'error')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    triggerToast('Konfirmasi kata sandi tidak cocok.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      password: passwordForm.new_password,
    }

    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${profileData.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Gagal mengubah kata sandi.')
    }

    triggerToast('Kata sandi berhasil diperbarui! Silakan gunakan kata sandi baru pada login berikutnya.')
    isPasswordModalOpen.value = false
  } catch (err) {
    console.error('Password change error:', err)
    triggerToast(err.message || 'Gagal mengubah kata sandi.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Ambil Geolocation Browser
const detectCurrentLocation = () => {
  if (!navigator.geolocation) {
    triggerToast('Browser tidak mendukung pendeteksi lokasi GPS.', 'error')
    return
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = parseFloat(pos.coords.latitude.toFixed(6))
      const lng = parseFloat(pos.coords.longitude.toFixed(6))
      editForm.latitude = lat
      editForm.longitude = lng
      editForm.google_maps_url = `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`
      if (editMap) {
        editMap.setView([lat, lng], 16)
        if (editMarker) editMarker.setLatLng([lat, lng])
      }
      triggerToast('Titik koordinat berhasil diambil dari GPS perangkat Anda!')
    },
    (err) => {
      console.warn('Geolocation error:', err)
      triggerToast('Gagal mendeteksi lokasi GPS: ' + err.message, 'error')
    }
  )
}

onMounted(() => {
  loadProfile()
})
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6 max-w-6xl mx-auto pb-12 font-sans">

      <!-- Toast Notification -->
      <Transition name="slide-down">
        <div
          v-if="showToast"
          :class="[
            'fixed top-20 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-2xl text-xs font-semibold backdrop-blur-xl border transition-all duration-300',
            toastType === 'success'
              ? 'bg-emerald-950/90 text-emerald-200 border-emerald-500/40 shadow-emerald-500/10'
              : 'bg-rose-950/90 text-rose-200 border-rose-500/40 shadow-rose-500/10'
          ]"
        >
          <span class="text-base">{{ toastType === 'success' ? '✓' : '⚠️' }}</span>
          <span>{{ toastMessage }}</span>
          <button @click="showToast = false" class="ml-2 text-slate-400 hover:text-white cursor-pointer">&times;</button>
        </div>
      </Transition>

      <!-- Loading State -->
      <div v-if="isLoading" class="p-12 text-center text-slate-400 space-y-3">
        <div class="inline-block w-8 h-8 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-xs font-semibold">Memuat profil dan akun cabang gereja...</p>
      </div>

      <template v-else>
        <!-- Header Banner & Hero Card -->
        <div class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#0b1329] via-[#0f172a] to-[#1c1917] border border-amber-500/30 p-6 sm:p-8 shadow-2xl">
          <!-- Background Glow Effect -->
          <div class="absolute -right-20 -top-20 w-80 h-80 rounded-full bg-amber-500/10 blur-3xl pointer-events-none"></div>
          <div class="absolute -left-20 -bottom-20 w-60 h-60 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none"></div>

          <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <!-- Left Info -->
            <div class="flex items-start sm:items-center gap-4 sm:gap-6">
              <!-- Avatar Inisial -->
              <div class="relative shrink-0">
                <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gradient-to-tr from-amber-600 via-amber-500 to-yellow-300 p-0.5 shadow-xl shadow-amber-500/20">
                  <div class="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center font-black text-amber-400 text-2xl sm:text-3xl tracking-tighter">
                    {{ profileData.admin_name?.charAt(0) || 'A' }}
                  </div>
                </div>
                <div class="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-slate-900 shadow" title="Akun Aktif"></div>
              </div>

              <!-- Main Title & Branch -->
              <div class="space-y-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-extrabold uppercase tracking-widest border border-amber-500/30">
                    Administrator Cabang
                  </span>
                  <span class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-bold border border-emerald-500/30 flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    {{ profileData.status || 'Aktif' }}
                  </span>
                  <span v-if="profileData.church_code" class="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-[10px] font-mono font-bold border border-cyan-500/30">
                    {{ profileData.church_code }}
                  </span>
                </div>

                <h1 class="text-xl sm:text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
                  {{ profileData.admin_name }}
                </h1>

                <p class="text-xs sm:text-sm text-amber-400/90 font-medium flex items-center gap-1.5">
                  <span class="text-base">⛪</span>
                  <strong class="text-white">{{ profileData.church_name }}</strong>
                  <span v-if="profileData.city" class="text-slate-400">({{ profileData.city }})</span>
                </p>
              </div>
            </div>

            <!-- Action Buttons (CRUD Controls) -->
            <div class="flex items-center gap-2.5 shrink-0 flex-wrap sm:flex-nowrap">
              <button
                @click="openEditModal"
                id="btn-edit-church-profile"
                class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-extrabold text-xs shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all duration-200 cursor-pointer hover:scale-[1.02] active:scale-[0.98]"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                </svg>
                <span>Edit Profil &amp; Cabang</span>
              </button>

              <button
                @click="openPasswordModal"
                id="btn-change-password"
                class="px-4 py-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700 hover:border-amber-500/40 font-bold text-xs flex items-center gap-2 transition-all duration-200 cursor-pointer shadow"
              >
                <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <span>Ubah Sandi</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Detail Cards Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <!-- Col 1: Informasi Personal Pengurus & Akun -->
          <div class="space-y-6">
            <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-4">
              <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                <div class="flex items-center gap-2 text-amber-400 font-extrabold text-sm uppercase tracking-wider">
                  <span>👤</span>
                  <h2>Informasi Pribadi Admin</h2>
                </div>
                <span class="text-[10px] text-slate-500 font-mono">ID: #{{ profileData.id }}</span>
              </div>

              <div class="space-y-3.5 text-xs">
                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Nama Lengkap Pengurus</span>
                  <p class="font-extrabold text-slate-100 text-sm mt-0.5">{{ profileData.admin_name }}</p>
                </div>

                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Alamat Email Terdaftar</span>
                  <p class="font-mono text-amber-300 font-semibold mt-0.5">{{ profileData.email }}</p>
                </div>

                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Nomor Telepon / WhatsApp</span>
                  <p class="font-semibold text-slate-200 mt-0.5 flex items-center gap-1.5">
                    <span class="text-emerald-400">📱</span> {{ profileData.phone || 'Belum diisi' }}
                  </p>
                </div>

                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Peran Sistem (Role)</span>
                  <div class="mt-1 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-300 font-bold text-[11px]">
                    <span>🛡️</span> Church Administrator Cabang
                  </div>
                </div>

                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Tanggal Akun Didaftarkan</span>
                  <p class="text-slate-400 mt-0.5 text-[11px]">{{ formatDate(profileData.created_at) }}</p>
                </div>
              </div>
            </div>

            <!-- Card Keamanan & Sesi Login -->
            <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3.5 text-xs">
              <div class="flex items-center gap-2 text-emerald-400 font-extrabold text-sm uppercase tracking-wider pb-3 border-b border-slate-800">
                <span>🔒</span>
                <h2>Status Keamanan Akun</h2>
              </div>

              <div class="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-slate-400 font-medium">Enkripsi Kata Sandi:</span>
                  <span class="text-emerald-400 font-bold">Argon2id Active</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-slate-400 font-medium">Sesi Login:</span>
                  <span class="text-amber-400 font-bold font-mono">JWT Bearer Auth</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-slate-400 font-medium">Status Akun:</span>
                  <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">Terverifikasi</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Col 2 & 3: Informasi Cabang Gereja & Mini Map (2 Kolom) -->
          <div class="lg:col-span-2 space-y-6">
            <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-lg space-y-4">
              <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                <div class="flex items-center gap-2 text-amber-400 font-extrabold text-sm uppercase tracking-wider">
                  <span>⛪</span>
                  <h2>Data Lembaga &amp; Cabang Gereja</h2>
                </div>
                <span class="px-2 py-0.5 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-mono font-bold">
                  {{ profileData.church_code || 'CABANG' }}
                </span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Nama Institusi Cabang</span>
                  <p class="font-extrabold text-white text-sm mt-0.5">{{ profileData.church_name }}</p>
                </div>

                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Kode Registrasi Unik</span>
                  <p class="font-mono text-cyan-300 font-bold text-sm mt-0.5">{{ profileData.church_code }}</p>
                </div>

                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Kota / Wilayah Domisili</span>
                  <p class="font-semibold text-slate-200 mt-0.5">{{ profileData.city || 'Belum diisi' }}</p>
                </div>

                <div>
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Tautan Peta Eksternal</span>
                  <a
                    v-if="profileData.google_maps_url"
                    :href="profileData.google_maps_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-sky-400 hover:text-sky-300 underline font-semibold mt-0.5 inline-flex items-center gap-1"
                  >
                    <span>Buka Google Maps</span>
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                    </svg>
                  </a>
                  <span v-else class="text-slate-500 mt-0.5 block">Belum ada tautan peta</span>
                </div>

                <div class="sm:col-span-2">
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Alamat Lengkap Sekretariat Gereja</span>
                  <p class="text-slate-300 font-medium mt-0.5 leading-relaxed">{{ profileData.address || 'Alamat gereja belum dicatat secara lengkap.' }}</p>
                </div>
              </div>

              <!-- Titik Koordinat & Peta Mini Leaflet -->
              <div class="space-y-2 pt-2">
                <div class="flex items-center justify-between text-xs">
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Titik Geolocation GPS Cabang
                  </span>
                  <span class="font-mono text-amber-400 text-[11px] font-bold">
                    {{ Number(profileData.latitude).toFixed(6) }}, {{ Number(profileData.longitude).toFixed(6) }}
                  </span>
                </div>

                <!-- Leaflet Mini Map Container -->
                <div class="relative w-full h-56 rounded-xl overflow-hidden border border-slate-800 shadow-inner">
                  <div ref="miniMapContainer" class="w-full h-full z-10"></div>
                </div>
              </div>

            </div>
          </div>

        </div>

      </template>

      <!-- MODAL 1: EDIT PROFIL & DATA CABANG GEREJA -->
      <Transition name="fade">
        <div
          v-if="isModalOpen"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md overflow-y-auto"
        >
          <div class="relative w-full max-w-2xl bg-slate-900 border border-amber-500/30 rounded-3xl shadow-2xl overflow-hidden text-xs my-8">

            <!-- Modal Header -->
            <div class="px-6 py-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center font-bold">
                  ✎
                </div>
                <div>
                  <h3 class="font-extrabold text-white text-sm">Edit Data Akun &amp; Cabang Gereja</h3>
                  <p class="text-[10px] text-slate-400">Perbarui identitas pengurus, kontak, dan alamat gereja</p>
                </div>
              </div>
              <button
                @click="isModalOpen = false"
                class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer"
              >
                ✕
              </button>
            </div>

            <!-- Modal Body Form -->
            <form @submit.prevent="handleSaveProfile" class="p-6 space-y-4 max-h-[75vh] overflow-y-auto">

              <!-- Grid 2 Kolom -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                    Nama Lengkap Pengurus / Admin *
                  </label>
                  <input
                    v-model="editForm.admin_name"
                    type="text"
                    required
                    class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-amber-400 focus:ring-1 focus:ring-amber-400 text-white placeholder-slate-600 outline-none transition font-medium"
                    placeholder="Contoh: Pdt. Yohanes Sitorus, S.Th"
                  />
                </div>

                <div>
                  <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                    Nomor WhatsApp / Telepon
                  </label>
                  <input
                    v-model="editForm.phone"
                    type="text"
                    class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-amber-400 focus:ring-1 focus:ring-amber-400 text-white placeholder-slate-600 outline-none transition font-medium"
                    placeholder="Contoh: 081234567890"
                  />
                </div>

                <div>
                  <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                    Kota / Wilayah Domisili
                  </label>
                  <input
                    v-model="editForm.city"
                    type="text"
                    class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-amber-400 focus:ring-1 focus:ring-amber-400 text-white placeholder-slate-600 outline-none transition font-medium"
                    placeholder="Contoh: Padang, Sumatera Barat"
                  />
                </div>

                <div>
                  <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                    Alamat Email (Akun Login)
                  </label>
                  <input
                    :value="editForm.email"
                    type="email"
                    disabled
                    class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/50 border border-slate-800 text-slate-500 font-mono cursor-not-allowed"
                    title="Alamat email tidak dapat diubah langsung untuk menjaga keamanan sesi."
                  />
                </div>
              </div>

              <!-- Alamat Lengkap -->
              <div>
                <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Alamat Lengkap Sekretariat / Gedung Gereja
                </label>
                <textarea
                  v-model="editForm.address"
                  rows="2"
                  class="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 focus:border-amber-400 focus:ring-1 focus:ring-amber-400 text-white placeholder-slate-600 outline-none transition font-medium"
                  placeholder="Nama jalan, nomor gedung, kelurahan, kecamatan..."
                ></textarea>
              </div>

              <!-- Map Picker Koordinat -->
              <div class="space-y-2 pt-2 border-t border-slate-800">
                <div class="flex items-center justify-between">
                  <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Titik Koordinat Geolocation Cabang (Peta Interaktif)
                  </label>
                  <button
                    type="button"
                    @click="detectCurrentLocation"
                    class="px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/30 text-[10px] font-bold flex items-center gap-1 cursor-pointer transition"
                  >
                    <span>📡</span> Deteksi GPS Saya
                  </button>
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <span class="text-[9px] text-slate-500 font-mono">Latitude:</span>
                    <input
                      v-model="editForm.latitude"
                      type="number"
                      step="0.000001"
                      class="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-amber-300 font-mono text-xs outline-none"
                    />
                  </div>
                  <div>
                    <span class="text-[9px] text-slate-500 font-mono">Longitude:</span>
                    <input
                      v-model="editForm.longitude"
                      type="number"
                      step="0.000001"
                      class="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-amber-300 font-mono text-xs outline-none"
                    />
                  </div>
                </div>

                <div class="relative w-full h-44 rounded-xl overflow-hidden border border-slate-800 shadow-inner">
                  <div ref="editMapContainer" class="w-full h-full z-10"></div>
                </div>
                <p class="text-[10px] text-slate-500 italic">Geser pin di peta untuk menyesuaikan letak koordinat gedung cabang gereja secara presisi.</p>
              </div>

              <!-- Modal Footer -->
              <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  @click="isModalOpen = false"
                  class="px-4 py-2 rounded-xl text-slate-400 hover:text-white font-semibold cursor-pointer"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  :disabled="isSubmitting"
                  class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-extrabold shadow-lg shadow-amber-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <span v-if="isSubmitting" class="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                  <span>{{ isSubmitting ? 'Menyimpan...' : 'Simpan Perubahan' }}</span>
                </button>
              </div>

            </form>

          </div>
        </div>
      </Transition>

      <!-- MODAL 2: GANTI KATA SANDI -->
      <Transition name="fade">
        <div
          v-if="isPasswordModalOpen"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md"
        >
          <div class="relative w-full max-w-md bg-slate-900 border border-amber-500/30 rounded-3xl shadow-2xl overflow-hidden text-xs">

            <div class="px-6 py-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center font-bold">
                  🔒
                </div>
                <div>
                  <h3 class="font-extrabold text-white text-sm">Ganti Kata Sandi</h3>
                  <p class="text-[10px] text-slate-400">Pastikan menggunakan kombinasi sandi yang aman</p>
                </div>
              </div>
              <button
                @click="isPasswordModalOpen = false"
                class="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form @submit.prevent="handleSavePassword" class="p-6 space-y-4">
              <div>
                <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Kata Sandi Baru *
                </label>
                <input
                  v-model="passwordForm.new_password"
                  type="password"
                  required
                  minlength="6"
                  class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-amber-400 focus:ring-1 focus:ring-amber-400 text-white placeholder-slate-600 outline-none transition font-medium"
                  placeholder="Minimal 6 karakter"
                />
              </div>

              <div>
                <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Konfirmasi Kata Sandi Baru *
                </label>
                <input
                  v-model="passwordForm.confirm_password"
                  type="password"
                  required
                  minlength="6"
                  class="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 focus:border-amber-400 focus:ring-1 focus:ring-amber-400 text-white placeholder-slate-600 outline-none transition font-medium"
                  placeholder="Ulangi kata sandi baru"
                />
              </div>

              <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  @click="isPasswordModalOpen = false"
                  class="px-4 py-2 rounded-xl text-slate-400 hover:text-white font-semibold cursor-pointer"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  :disabled="isSubmitting"
                  class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-extrabold shadow-lg shadow-amber-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <span v-if="isSubmitting" class="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                  <span>{{ isSubmitting ? 'Menyimpan...' : 'Perbarui Sandi' }}</span>
                </button>
              </div>
            </form>

          </div>
        </div>
      </Transition>

    </div>
  </ChurchAdminLayout>
</template>

<style scoped>
.custom-pin, .custom-edit-pin {
  background: transparent !important;
  border: none !important;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
