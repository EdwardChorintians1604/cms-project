<script setup>
import { ref, computed, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// --- State Data Admin Cabang dari PostgreSQL (tabel church_admins) ---
const admins = ref([])
const churches = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const searchQuery = ref('')
const statusFilter = ref('Semua')
const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const isSubmitting = ref(false)
const showToast = ref(false)
const toastMessage = ref('')

const form = reactive({
  admin_name: '',
  email: '',
  phone: '',
  church_id: null,
  church_code: '',
  church_name: '',
  city: '',
  address: '',
  latitude: null,
  longitude: null,
  google_maps_url: '',
  status: 'Aktif',
  password: ''
})

const mapContainer = ref(null)
const isLocating = ref(false)
const locationFeedback = ref('')
let leafletMap = null
let branchMarker = null

const generateGoogleMapsUrl = (lat, lng) => {
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`
}

const createBranchPinIcon = () => L.divIcon({
  className: 'branch-location-pin',
  html: '<div class="branch-pin-pulse"></div><div class="branch-pin">⌖</div>',
  iconSize: [38, 38],
  iconAnchor: [19, 38],
  popupAnchor: [0, -38]
})

const updateMapPopup = () => {
  if (!branchMarker) return
  branchMarker.setPopupContent(`
    <div class="text-xs text-slate-800">
      <strong class="block text-sm text-amber-700">${form.church_name || 'Lokasi Gereja Cabang'}</strong>
      <span>${Number(form.latitude).toFixed(6)}, ${Number(form.longitude).toFixed(6)}</span>
    </div>
  `)
}

const updateCoordinates = (lat, lng, moveMap = false) => {
  const nextLat = Number(Number(lat).toFixed(6))
  const nextLng = Number(Number(lng).toFixed(6))
  if (!Number.isFinite(nextLat) || !Number.isFinite(nextLng)) return

  form.latitude = nextLat
  form.longitude = nextLng
  form.google_maps_url = generateGoogleMapsUrl(nextLat, nextLng)

  if (branchMarker) {
    branchMarker.setLatLng([nextLat, nextLng])
    updateMapPopup()
  }
  if (moveMap && leafletMap) {
    leafletMap.flyTo([nextLat, nextLng], Math.max(leafletMap.getZoom(), 15), { duration: 0.8 })
  }
}

const initLocationMap = () => {
  if (!mapContainer.value) return
  const initialLat = Number(form.latitude) || -6.1754
  const initialLng = Number(form.longitude) || 106.8415

  if (leafletMap) {
    leafletMap.invalidateSize()
    leafletMap.setView([initialLat, initialLng], 15)
    if (branchMarker) branchMarker.setLatLng([initialLat, initialLng])
    updateMapPopup()
    return
  }

  leafletMap = L.map(mapContainer.value, { center: [initialLat, initialLng], zoom: 14 })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(leafletMap)

  branchMarker = L.marker([initialLat, initialLng], {
    icon: createBranchPinIcon(),
    draggable: true
  }).addTo(leafletMap)
  branchMarker.on('dragend', (event) => {
    const position = event.target.getLatLng()
    updateCoordinates(position.lat, position.lng, true)
  })
  leafletMap.on('click', (event) => updateCoordinates(event.latlng.lat, event.latlng.lng, true))
  updateCoordinates(initialLat, initialLng)
  branchMarker.openPopup()
}

const detectCurrentLocation = () => {
  if (!navigator.geolocation) {
    locationFeedback.value = 'Browser tidak mendukung deteksi lokasi.'
    return
  }
  isLocating.value = true
  locationFeedback.value = 'Mendeteksi lokasi perangkat...'
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      isLocating.value = false
      updateCoordinates(coords.latitude, coords.longitude, true)
      locationFeedback.value = `Lokasi terdeteksi (akurasi ±${Math.round(coords.accuracy || 10)} m).`
    },
    (error) => {
      isLocating.value = false
      locationFeedback.value = error.code === 1
        ? 'Izin lokasi ditolak. Aktifkan izin GPS pada browser.'
        : 'Lokasi perangkat tidak dapat ditentukan.'
    },
    { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
  )
}

// --- 1. Ambil Data Real dari Database PostgreSQL ---
const loadAdmins = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/`)
    if (!res.ok) throw new Error('Gagal memuat data admin cabang dari database.')
    admins.value = await res.json()
  } catch (err) {
    console.error('Load admins error:', err)
    errorMessage.value = err.message || 'Gagal memuat data admin cabang.'
  } finally {
    isLoading.value = false
  }
}

const loadChurches = async () => {
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/churches/`)
    if (res.ok) {
      churches.value = await res.json()
    }
  } catch (err) {
    console.warn('Gagal memuat data gereja:', err)
  }
}

onMounted(() => {
  loadAdmins()
  loadChurches()
})

onUnmounted(() => {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
    branchMarker = null
  }
})

// Saat memilih gereja di modal tambah
const onSelectChurch = (event) => {
  const selectedId = Number(event.target.value)
  if (!selectedId) return
  const found = churches.value.find(c => c.id === selectedId)
  if (found) {
    form.church_id = found.id
    form.church_name = found.church_name
    form.city = found.city || ''
    form.address = found.address || ''
    form.latitude = found.latitude !== null && found.latitude !== undefined ? Number(found.latitude) : null
    form.longitude = found.longitude !== null && found.longitude !== undefined ? Number(found.longitude) : null
    form.google_maps_url = found.google_maps_url || ''
    if (!form.church_code) {
      form.church_code = found.church_code
    }
    nextTick(initLocationMap)
  }
}

// --- Computed Filters ---
const filteredAdmins = computed(() => {
  return admins.value.filter(admin => {
    const q = searchQuery.value.toLowerCase()
    const matchesSearch = 
      (admin.admin_name && admin.admin_name.toLowerCase().includes(q)) ||
      (admin.email && admin.email.toLowerCase().includes(q)) ||
      (admin.church_name && admin.church_name.toLowerCase().includes(q)) ||
      (admin.church_code && admin.church_code.toLowerCase().includes(q)) ||
      (admin.city && admin.city.toLowerCase().includes(q))
    
    const matchesStatus = statusFilter.value === 'Semua' || admin.status === statusFilter.value

    return matchesSearch && matchesStatus
  })
})

const totalAdmins = computed(() => admins.value.length)
const activeAdmins = computed(() => admins.value.filter(a => a.status === 'Aktif').length)
const pendingAdmins = computed(() => admins.value.filter(a => a.status === 'Pending').length)
const inactiveAdmins = computed(() => admins.value.filter(a => a.status === 'Nonaktif').length)

// --- Actions CRUD ---
const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  Object.assign(form, {
    admin_name: '',
    email: '',
    phone: '',
    church_id: null,
    church_code: '',
    church_name: '',
    city: '',
    address: '',
    latitude: null,
    longitude: null,
    google_maps_url: '',
    status: 'Aktif',
    password: ''
  })
  isModalOpen.value = true
  nextTick(initLocationMap)
}

const openEditModal = (admin) => {
  isEditing.value = true
  editingId.value = admin.id
  Object.assign(form, {
    admin_name: admin.admin_name,
    email: admin.email,
    phone: admin.phone || '',
    church_id: admin.church_id || null,
    church_code: admin.church_code,
    church_name: admin.church_name,
    city: admin.city || '',
    address: admin.address || '',
    latitude: admin.latitude !== null && admin.latitude !== undefined ? Number(admin.latitude) : null,
    longitude: admin.longitude !== null && admin.longitude !== undefined ? Number(admin.longitude) : null,
    google_maps_url: admin.google_maps_url || '',
    status: admin.status || 'Aktif',
    password: ''
  })
  isModalOpen.value = true
  nextTick(initLocationMap)
}

const saveAdmin = async () => {
  isSubmitting.value = true
  try {
    if (isEditing.value && editingId.value) {
      // Update admin
      const payload = {
        admin_name: form.admin_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || null,
        church_id: form.church_id || null,
        church_code: form.church_code.trim().toUpperCase(),
        church_name: form.church_name.trim(),
        city: form.city.trim() || null,
        address: form.address.trim() || null,
        latitude: form.latitude !== null ? Number(form.latitude) : null,
        longitude: form.longitude !== null ? Number(form.longitude) : null,
        google_maps_url: form.google_maps_url || null,
        status: form.status,
      }
      if (form.password) {
        payload.password = form.password
      }

      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${editingId.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}))
        throw new Error(errJson.detail || 'Gagal memperbarui admin cabang.')
      }

      await loadAdmins()
      triggerToast(`Data admin ${form.admin_name} berhasil diperbarui di database!`)
    } else {
      // Create new admin
      if (!form.password) {
        throw new Error('Kata sandi wajib diisi untuk admin baru.')
      }
      const payload = {
        admin_name: form.admin_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || null,
        church_id: form.church_id || null,
        church_code: form.church_code.trim().toUpperCase(),
        church_name: form.church_name.trim(),
        city: form.city.trim() || null,
        address: form.address.trim() || null,
        latitude: form.latitude !== null ? Number(form.latitude) : null,
        longitude: form.longitude !== null ? Number(form.longitude) : null,
        google_maps_url: form.google_maps_url || null,
        status: form.status,
        password: form.password
      }

      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}))
        throw new Error(errJson.detail || 'Gagal menambahkan admin cabang.')
      }

      await loadAdmins()
      triggerToast(`Admin cabang ${form.admin_name} berhasil ditambahkan ke database!`)
    }
    isModalOpen.value = false
  } catch (err) {
    alert(err.message || 'Terjadi kesalahan.')
  } finally {
    isSubmitting.value = false
  }
}

const toggleStatus = async (admin) => {
  const newStatus = admin.status === 'Aktif' ? 'Nonaktif' : 'Aktif'
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${admin.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    })
    if (!res.ok) throw new Error('Gagal mengubah status admin.')
    admin.status = newStatus
    triggerToast(`Status akun ${admin.admin_name} diubah menjadi ${newStatus}!`)
  } catch (err) {
    alert(err.message || 'Gagal mengubah status akun.')
  }
}

const deleteAdmin = async (id) => {
  if (confirm('Apakah Anda yakin ingin menghapus akun admin cabang ini dari database PostgreSQL?')) {
    try {
      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${id}`, {
        method: 'DELETE'
      })
      if (!res.ok) throw new Error('Gagal menghapus admin.')
      await loadAdmins()
      triggerToast('Akun admin cabang berhasil dihapus dari database!')
    } catch (err) {
      alert(err.message || 'Gagal menghapus admin cabang.')
    }
  }
}

const triggerToast = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('id-ID', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<template>
  <MainAdminLayout>
    <div class="p-6 max-w-7xl mx-auto font-sans text-slate-100 space-y-6">
      
      <!-- Page Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-amber-500/30">
        <div>
          <h1 class="text-2xl font-bold font-serif text-amber-300 flex items-center gap-2">
            <i class="bi bi-people-fill text-amber-400"></i>
            <span>Manajemen Admin Cabang Gereja</span>
          </h1>
          <p class="text-xs text-slate-300 mt-1">Data resmi pengurus & administrator gereja cabang yang terdaftar di sistem manajemen gereja. </p>
        </div>
      </div>

      <!-- Error Notification -->
      <div v-if="errorMessage" class="p-3 bg-rose-950/80 border border-rose-800 text-rose-200 text-xs rounded-xl flex items-center gap-2">
        <i class="bi bi-exclamation-triangle-fill text-rose-400 text-base"></i>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Metrics Row -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="p-4 rounded-xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-amber-500/30 shadow-lg">
          <span class="text-xs text-slate-400 font-serif uppercase tracking-wider block">Total Admin Terdaftar</span>
          <span class="text-2xl font-bold font-serif text-amber-400 mt-1 block">{{ totalAdmins }} Akun</span>
        </div>

        <div class="p-4 rounded-xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-emerald-500/30 shadow-lg">
          <span class="text-xs text-slate-400 font-serif uppercase tracking-wider block">Status Aktif</span>
          <span class="text-2xl font-bold font-serif text-emerald-400 mt-1 block">{{ activeAdmins }} Akun</span>
        </div>

        <div class="p-4 rounded-xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-amber-500/30 shadow-lg">
          <span class="text-xs text-slate-400 font-serif uppercase tracking-wider block">Menunggu Verifikasi</span>
          <span class="text-2xl font-bold font-serif text-amber-300 mt-1 block">{{ pendingAdmins }} Akun</span>
        </div>

        <div class="p-4 rounded-xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-rose-500/30 shadow-lg">
          <span class="text-xs text-slate-400 font-serif uppercase tracking-wider block">Nonaktif</span>
          <span class="text-2xl font-bold font-serif text-rose-400 mt-1 block">{{ inactiveAdmins }} Akun</span>
        </div>
      </div>

      <!-- Controls & Filter Bar -->
      <div class="p-4 rounded-2xl bg-[#09112b] border border-slate-800 flex flex-col md:flex-row gap-4 items-center justify-between">
        <!-- Search Input -->
        <div class="relative w-full md:w-96">
          <i class="bi bi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Cari nama admin, email, gereja, atau kota..."
            class="w-full pl-10 pr-4 py-2 bg-[#050918] border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
          >
        </div>

        <!-- Filter Dropdown & Refresh -->
        <div class="flex items-center gap-3 w-full md:w-auto">
          <span class="text-xs text-slate-300 font-serif uppercase">Status:</span>
          <select 
            v-model="statusFilter"
            class="px-3 py-2 bg-[#050918] border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-400 cursor-pointer"
          >
            <option value="Semua">Semua Status</option>
            <option value="Aktif">Aktif</option>
            <option value="Pending">Pending</option>
            <option value="Nonaktif">Nonaktif</option>
          </select>

          <button 
            @click="loadAdmins" 
            title="Refresh Data PostgreSQL"
            class="p-2 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-xl transition cursor-pointer border border-slate-700"
          >
            <i class="bi bi-arrow-clockwise" :class="{ 'animate-spin': isLoading }"></i>
          </button>
        </div>
      </div>

      <!-- Table Section -->
      <div class="rounded-2xl bg-gradient-to-br from-[#0c163a] to-[#070d24] border border-amber-500/30 shadow-2xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="bg-[#050918] text-amber-300 font-serif uppercase tracking-wider border-b border-amber-500/20">
                <th class="p-4">Admin & Kontak</th>
                <th class="p-4">Institusi & Cabang</th>
                <th class="p-4">Wilayah / Kota</th>
                <th class="p-4">Status</th>
                <th class="p-4">Tgl Terdaftar</th>
                <th class="p-4 text-center">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800">
              <tr v-if="isLoading" class="text-center">
                <td colspan="6" class="p-8 text-slate-400 font-sans">
                  <i class="bi bi-arrow-clockwise animate-spin text-amber-400 text-xl block mb-2"></i>
                  Memuat data admin cabang dari database PostgreSQL...
                </td>
              </tr>

              <tr v-else-if="filteredAdmins.length === 0" class="text-center">
                <td colspan="6" class="p-8 text-slate-400 font-sans">
                  Tidak ada data admin cabang yang sesuai dengan pencarian.
                </td>
              </tr>

              <tr v-else v-for="admin in filteredAdmins" :key="admin.id" class="hover:bg-slate-900/50 transition">
                
                <!-- Admin Name & Contact -->
                <td class="p-4">
                  <div class="font-bold text-white text-sm font-serif flex items-center gap-2">
                    <div class="w-7 h-7 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 flex items-center justify-center text-xs font-bold">
                      {{ admin.admin_name ? admin.admin_name.charAt(0) : 'A' }}
                    </div>
                    <span>{{ admin.admin_name }}</span>
                  </div>
                  <div class="text-slate-400 font-mono text-[11px] mt-1 flex items-center gap-1.5">
                    <i class="bi bi-envelope text-amber-400/70"></i>
                    <span>{{ admin.email }}</span>
                  </div>
                  <div v-if="admin.phone" class="text-slate-400 text-[11px] mt-0.5 flex items-center gap-1.5">
                    <i class="bi bi-whatsapp text-emerald-400"></i>
                    <span>{{ admin.phone }}</span>
                  </div>
                </td>

                <!-- Church Info -->
                <td class="p-4">
                  <div class="font-bold text-amber-200">{{ admin.church_name }}</div>
                  <span class="inline-block mt-1 font-mono text-[10px] text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                    Kode: {{ admin.church_code }}
                  </span>
                </td>

                <!-- City / Region -->
                <td class="p-4">
                  <span class="text-slate-300 font-medium">
                    {{ admin.city || '-' }}
                  </span>
                </td>

                <!-- Status Badge -->
                <td class="p-4">
                  <span 
                    :class="{
                      'bg-emerald-500/20 text-emerald-300 border-emerald-500/40': admin.status === 'Aktif',
                      'bg-amber-500/20 text-amber-300 border-amber-500/40': admin.status === 'Pending',
                      'bg-rose-500/20 text-rose-300 border-rose-500/40': admin.status === 'Nonaktif'
                    }"
                    class="px-2.5 py-1 rounded-full text-[10px] font-serif uppercase tracking-wider font-bold border"
                  >
                    {{ admin.status }}
                  </span>
                </td>

                <!-- Registered Date -->
                <td class="p-4 text-slate-400 font-mono">
                  {{ formatDate(admin.created_at) }}
                </td>

                <!-- Actions -->
                <td class="p-4 text-center space-x-1.5">
                  <button 
                    @click="openEditModal(admin)" 
                    title="Edit Admin"
                    class="p-1.5 bg-amber-500/10 hover:bg-amber-400 text-amber-300 hover:text-slate-950 border border-amber-500/30 rounded-lg transition cursor-pointer"
                  >
                    <i class="bi bi-pencil-square"></i>
                  </button>

                  <button 
                    @click="toggleStatus(admin)" 
                    :title="admin.status === 'Aktif' ? 'Nonaktifkan Akun' : 'Aktifkan Akun'"
                    class="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition cursor-pointer border border-slate-700"
                  >
                    <i :class="admin.status === 'Aktif' ? 'bi bi-slash-circle text-rose-400' : 'bi bi-check-circle text-emerald-400'"></i>
                  </button>

                  <button 
                    @click="deleteAdmin(admin.id)" 
                    title="Hapus Admin"
                    class="p-1.5 bg-rose-500/10 hover:bg-rose-500 text-rose-400 hover:text-white border border-rose-500/30 rounded-lg transition cursor-pointer"
                  >
                    <i class="bi bi-trash-fill"></i>
                  </button>
                </td>

              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Modal Form Tambah/Edit Admin Cabang -->
    <Teleport to="body">
      <div v-if="isModalOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
        <div class="w-full max-w-3xl max-h-[94vh] overflow-y-auto bg-[#091129] border border-amber-500/40 rounded-2xl p-6 shadow-2xl relative font-sans text-slate-100">
          <button 
            @click="isModalOpen = false" 
            class="absolute top-4 right-4 text-slate-400 hover:text-amber-300 p-1.5 rounded-lg border border-slate-700 hover:bg-[#0b1435] transition cursor-pointer"
          >
            <i class="bi bi-x-lg"></i>
          </button>

          <h3 class="text-xl font-bold font-serif text-amber-300 mb-4 border-b border-amber-500/20 pb-3">
            {{ isEditing ? 'Edit Data Admin Cabang (PostgreSQL)' : 'Tambah Admin Cabang Baru (PostgreSQL)' }}
          </h3>

          <form @submit.prevent="saveAdmin" class="space-y-4 text-xs">
            <div>
              <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Nama Lengkap Admin *</label>
              <input v-model="form.admin_name" type="text" required placeholder="Pdt. / Bp. / Ibu Nama Lengkap" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400">
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Email Login *</label>
                <input v-model="form.email" type="email" required placeholder="admin@gereja.org" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400">
              </div>
              <div>
                <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">No. HP / WhatsApp</label>
                <input v-model="form.phone" type="text" placeholder="0812-xxxx-xxxx" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400">
              </div>
            </div>

            <div v-if="!isEditing && churches.length > 0">
              <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Pilih Gereja Induk Terafiliasi</label>
              <select @change="onSelectChurch" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400 cursor-pointer">
                <option value="">-- Pilih Gereja dari Database (Opsional) --</option>
                <option v-for="c in churches" :key="c.id" :value="c.id">
                  {{ c.church_name }} (Kode: {{ c.church_code }})
                </option>
              </select>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Nama Gereja Cabang *</label>
                <input v-model="form.church_name" type="text" required placeholder="Contoh: GKI Harapan Indah" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400">
              </div>
              <div>
                <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Kode Gereja Cabang *</label>
                <input v-model="form.church_code" type="text" required placeholder="GKI-HARAPAN-01" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white font-mono focus:outline-none focus:border-amber-400 uppercase">
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Kota / Wilayah</label>
                <input v-model="form.city" type="text" placeholder="Contoh: Bekasi" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400">
              </div>
              <div>
                <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Status Akun</label>
                <select v-model="form.status" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400">
                  <option value="Aktif">Aktif</option>
                  <option value="Pending">Pending</option>
                  <option value="Nonaktif">Nonaktif</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Alamat Gereja Cabang</label>
              <textarea v-model="form.address" rows="2" placeholder="Alamat lengkap lokasi gereja cabang" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400 resize-y"></textarea>
            </div>

            <section class="rounded-2xl border border-cyan-500/30 bg-[#050918] p-3 sm:p-4">
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between mb-3">
                <div>
                  <h4 class="font-serif text-sm font-bold text-cyan-300 flex items-center gap-2">
                    <i class="bi bi-geo-alt-fill"></i>
                    Lokasi Gereja Cabang
                  </h4>
                  <p class="text-[10px] text-slate-400 mt-1">Klik peta atau geser pin untuk menentukan titik lokasi yang akurat.</p>
                </div>
                <button
                  type="button"
                  @click="detectCurrentLocation"
                  :disabled="isLocating"
                  class="inline-flex items-center justify-center gap-1.5 rounded-lg border border-cyan-400/40 bg-cyan-500/10 px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-cyan-300 hover:bg-cyan-400 hover:text-slate-950 disabled:opacity-50 transition cursor-pointer"
                >
                  <i class="bi" :class="isLocating ? 'bi-arrow-clockwise animate-spin' : 'bi-crosshair'"></i>
                  {{ isLocating ? 'Mendeteksi...' : 'Gunakan Lokasi Saya' }}
                </button>
              </div>

              <div ref="mapContainer" class="branch-map rounded-xl overflow-hidden border border-slate-700"></div>

              <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px]">
                <div class="rounded-lg border border-slate-700 bg-slate-900/70 px-3 py-2 text-slate-300 font-mono">
                  <span class="text-slate-500">LAT:</span> {{ form.latitude ?? '-' }}
                </div>
                <div class="rounded-lg border border-slate-700 bg-slate-900/70 px-3 py-2 text-slate-300 font-mono">
                  <span class="text-slate-500">LNG:</span> {{ form.longitude ?? '-' }}
                </div>
              </div>
              <p v-if="locationFeedback" class="mt-2 text-[10px] text-cyan-300 flex items-center gap-1.5">
                <i class="bi bi-info-circle"></i>{{ locationFeedback }}
              </p>
              <a v-if="form.google_maps_url" :href="form.google_maps_url" target="_blank" rel="noopener noreferrer" class="mt-2 inline-flex items-center gap-1 text-[10px] text-sky-300 hover:text-sky-200 hover:underline">
                <i class="bi bi-box-arrow-up-right"></i> Buka titik ini di Google Maps
              </a>
            </section>

            <div>
              <label class="block font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">
                {{ isEditing ? 'Kata Sandi Baru (Kosongkan jika tidak diubah)' : 'Kata Sandi Akun *' }}
              </label>
              <input v-model="form.password" :required="!isEditing" type="password" placeholder="••••••••••••" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white focus:outline-none focus:border-amber-400">
            </div>

            <div class="pt-3 border-t border-slate-800 flex justify-end gap-2">
              <button 
                type="button" 
                @click="isModalOpen = false" 
                class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-serif uppercase tracking-wider rounded-xl transition cursor-pointer"
              >
                Batal
              </button>
              <button 
                type="submit" 
                :disabled="isSubmitting"
                class="px-5 py-2 bg-amber-500 hover:bg-amber-400 disabled:bg-amber-500/50 text-slate-950 font-serif font-bold uppercase tracking-wider rounded-xl transition shadow-md cursor-pointer flex items-center gap-2"
              >
                <i v-if="isSubmitting" class="bi bi-arrow-clockwise animate-spin"></i>
                <span>{{ isEditing ? 'Perbarui Data' : 'Simpan ke Database' }}</span>
              </button>
            </div>
          </form>

        </div>
      </div>
    </Teleport>

    <!-- Toast Alert Notification -->
    <Teleport to="body">
      <Transition name="fade-slide">
        <div 
          v-if="showToast"
          class="fixed bottom-6 right-6 z-[10000] px-4 py-3 bg-amber-500 text-slate-950 font-bold font-serif text-xs rounded-xl shadow-2xl border border-amber-300 flex items-center gap-2"
        >
          <i class="bi bi-check-circle-fill text-lg"></i>
          <span>{{ toastMessage }}</span>
        </div>
      </Transition>
    </Teleport>
  </MainAdminLayout>
</template>

<style scoped>
.branch-map {
  height: 300px;
  min-height: 260px;
  z-index: 0;
}

:deep(.branch-location-pin) {
  background: transparent;
  border: 0;
}

:deep(.branch-pin-pulse) {
  position: absolute;
  width: 38px;
  height: 38px;
  border-radius: 9999px;
  background: rgba(34, 211, 238, 0.35);
  animation: branch-pin-ping 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;
}

:deep(.branch-pin) {
  position: absolute;
  left: 5px;
  top: 5px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #cffafe;
  border-radius: 9999px 9999px 9999px 0;
  transform: rotate(-45deg);
  background: #0e7490;
  color: #ecfeff;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
  font-size: 16px;
}

@keyframes branch-pin-ping {
  75%, 100% {
    transform: scale(1.8);
    opacity: 0;
  }
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
