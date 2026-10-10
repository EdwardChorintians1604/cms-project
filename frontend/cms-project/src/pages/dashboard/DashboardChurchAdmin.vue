<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { RouterLink } from 'vue-router'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'
import { APP_CONFIG } from '@/config'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import AOS from 'aos'

import imgDashboard from '@/assets/images/manajemen_gereja_1.png'
import imgChurchDigital from '@/assets/images/manajemen_gereja_2.jpg'
import imgKeuanganGereja from '@/assets/images/keuangan_gereja.jpg'
import imgGracePoint from '@/assets/images/GracePoint.png'


const { user } = useAuth()
const { isDark, toggleTheme } = useTheme()

// State data gereja & admin
const isLoading = ref(true)
const isSaving = ref(false)
const saveSuccessMessage = ref('')
const saveErrorMessage = ref('')
const gpsLoading = ref(false)
const searchLoading = ref(false)
const searchQuery = ref('')
const searchResults = ref([])

// Daftar seluruh gereja admin & gereja cabang untuk dropdown / switcher
const allChurchAdmins = ref([])
const selectedAdminId = ref(null)

// Form Geolocation Gereja
const locationForm = reactive({
  church_name: '',
  church_code: '',
  city: '',
  address: '',
  latitude: -6.1824,
  longitude: 106.9856,
  google_maps_url: '',
})

// Leaflet Map & Marker instances
const mapContainer = ref(null)
let leafletMap = null
let churchMarker = null
let otherMarkersLayer = null

// Generate default Google Maps URL from coords
const generateGMapsUrl = (lat, lng) => {
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`
}

// Custom DivIcon for Leaflet (Gereja Aktif & Gereja Lainnya)
const createActivePinIcon = () => {
  return L.divIcon({
    className: 'custom-active-pin',
    html: `
      <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-full">
        <span class="absolute w-8 h-8 rounded-full bg-amber-500/40 animate-ping"></span>
        <div class="w-10 h-10 rounded-full bg-slate-900 border-2 border-amber-400 flex items-center justify-center shadow-xl text-amber-300">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -42]
  })
}

const createOtherPinIcon = (name) => {
  return L.divIcon({
    className: 'custom-other-pin',
    html: `
      <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-full">
        <div class="w-7 h-7 rounded-full bg-cyan-950 border border-cyan-400 flex items-center justify-center shadow-md text-cyan-300 hover:scale-110 transition-transform">
          <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -30]
  })
}

// Inisialisasi Peta Leaflet
const initMap = () => {
  if (!mapContainer.value || leafletMap) return

  const initialLat = Number(locationForm.latitude) || -6.1824
  const initialLng = Number(locationForm.longitude) || 106.9856

  leafletMap = L.map(mapContainer.value, {
    center: [initialLat, initialLng],
    zoom: 14,
    zoomControl: true,
  })

  // CartoDB Styled Tiles (sesuai gaya modern GMaps / Dark HUD)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CartoDB</a>, OpenStreetMap',
    maxZoom: 19,
    subdomains: 'abcd',
  }).addTo(leafletMap)

  // Layer grup untuk gereja cabang lainnya
  otherMarkersLayer = L.layerGroup().addTo(leafletMap)

  // Marker Utama yang Draggable
  churchMarker = L.marker([initialLat, initialLng], {
    icon: createActivePinIcon(),
    draggable: true,
  }).addTo(leafletMap)

  churchMarker.bindPopup(`
    <div class="text-xs p-1">
      <strong class="text-amber-400 text-sm block mb-1 font-serif">${locationForm.church_name || 'Gereja Anda'}</strong>
      <p class="mb-1 opacity-90">${locationForm.address || 'Geser pin untuk menentukan letak koordinat pasti gereja.'}</p>
      <span class="inline-block px-2 py-0.5 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded text-[10px] font-mono">
        ${initialLat.toFixed(5)}, ${initialLng.toFixed(5)}
      </span>
    </div>
  `)

  // Event saat pin digeser oleh admin
  churchMarker.on('dragend', (e) => {
    const position = e.target.getLatLng()
    updateCoords(position.lat, position.lng, true)
  })

  // Klik di sembarang titik peta untuk memindahkan pin
  leafletMap.on('click', (e) => {
    updateCoords(e.latlng.lat, e.latlng.lng, true)
    if (churchMarker) {
      churchMarker.setLatLng(e.latlng)
    }
  })

  renderOtherChurchesMarkers()
}

// Render marker gereja lain di peta
const renderOtherChurchesMarkers = () => {
  if (!leafletMap || !otherMarkersLayer) return
  otherMarkersLayer.clearLayers()

  allChurchAdmins.value.forEach((adm) => {
    if (adm.id === selectedAdminId.value) return // Lewati gereja aktif
    if (adm.latitude && adm.longitude) {
      const lat = Number(adm.latitude)
      const lng = Number(adm.longitude)
      if (isNaN(lat) || isNaN(lng)) return

      const m = L.marker([lat, lng], {
        icon: createOtherPinIcon(adm.church_name),
      })

      m.bindPopup(`
        <div class="text-xs p-1 text-slate-800">
          <strong class="text-cyan-800 block text-sm mb-1">${adm.church_name}</strong>
          <div class="text-slate-600 text-[11px] mb-1">${adm.city || ''} - ${adm.address || ''}</div>
          <a href="${adm.google_maps_url || generateGMapsUrl(lat, lng)}" target="_blank" class="text-sky-600 hover:underline text-[11px] font-semibold flex items-center gap-1">
            Lihat di Google Maps &rarr;
          </a>
        </div>
      `)
      otherMarkersLayer.addLayer(m)
    }
  })
}

// Update koordinat di form & popup
const updateCoords = (lat, lng, fly = false) => {
  const roundedLat = parseFloat(Number(lat).toFixed(6))
  const roundedLng = parseFloat(Number(lng).toFixed(6))
  locationForm.latitude = roundedLat
  locationForm.longitude = roundedLng

  // Perbarui Google Maps URL secara otomatis jika belum di-custom
  locationForm.google_maps_url = generateGMapsUrl(roundedLat, roundedLng)

  if (churchMarker) {
    churchMarker.setLatLng([roundedLat, roundedLng])
    churchMarker.setPopupContent(`
      <div class="text-xs p-1 text-slate-800">
        <strong class="text-amber-700 text-sm block mb-1 font-serif">${locationForm.church_name || 'Gereja Anda'}</strong>
        <p class="mb-1 text-slate-600">${locationForm.address || 'Titik koordinat berhasil diperbarui.'}</p>
        <span class="inline-block px-2 py-0.5 bg-amber-100 text-amber-800 rounded text-[10px] font-mono">
          ${roundedLat}, ${roundedLng}
        </span>
      </div>
    `)
  }

  if (fly && leafletMap) {
    leafletMap.flyTo([roundedLat, roundedLng], Math.max(leafletMap.getZoom(), 15), {
      duration: 1.2
    })
  }
}

// 1. Fitur Deteksi Otomatis Lokasi Saya (GPS Browser / GMaps Geolocation)
const detectCurrentLocation = () => {
  if (!navigator.geolocation) {
    saveErrorMessage.value = 'Browser Anda tidak mendukung Geolocation API.'
    return
  }

  gpsLoading.value = true
  saveErrorMessage.value = ''
  saveSuccessMessage.value = ''

  navigator.geolocation.getCurrentPosition(
    (position) => {
      gpsLoading.value = false
      const lat = position.coords.latitude
      const lng = position.coords.longitude
      const accuracy = position.coords.accuracy ? Math.round(position.coords.accuracy) : null

      updateCoords(lat, lng, true)
      saveSuccessMessage.value = `Lokasi perangkat Anda terdeteksi via GPS (Akurasi: ±${accuracy || 10} meter). Titik pin telah diposisikan.`
      
      // Buka popup
      if (churchMarker) {
        churchMarker.openPopup()
      }
    },
    (error) => {
      gpsLoading.value = false
      switch (error.code) {
        case error.PERMISSION_DENIED:
          saveErrorMessage.value = 'Izin akses lokasi ditolak oleh browser. Silakan aktifkan izin lokasi di pengaturan browser.'
          break
        case error.POSITION_UNAVAILABLE:
          saveErrorMessage.value = 'Informasi lokasi GPS perangkat tidak tersedia.'
          break
        case error.TIMEOUT:
          saveErrorMessage.value = 'Waktu permintaan lokasi habis (timeout). Silakan coba lagi.'
          break
        default:
          saveErrorMessage.value = 'Gagal mendeteksi lokasi: ' + error.message
      }
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  )
}

// 2. Fitur Pencarian Alamat (Geocoding OSM Nominatim)
const searchAddress = async () => {
  if (!searchQuery.value.trim()) return
  searchLoading.value = true
  searchResults.value = []
  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}&countrycodes=id&limit=5`)
    if (res.ok) {
      searchResults.value = await res.json()
    }
  } catch (err) {
    console.warn('Gagal mencari alamat via Nominatim:', err)
  } finally {
    searchLoading.value = false
  }
}

const applySearchResult = (item) => {
  const lat = parseFloat(item.lat)
  const lon = parseFloat(item.lon)
  updateCoords(lat, lon, true)
  if (!locationForm.address) {
    locationForm.address = item.display_name
  }
  searchResults.value = []
}

// Load data admin & profil gereja dari backend
const loadChurchData = async () => {
  isLoading.value = true
  saveErrorMessage.value = ''
  try {
    // Ambil daftar seluruh admin gereja
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/?limit=100`)
    if (res.ok) {
      const list = await res.json()
      allChurchAdmins.value = list

      // Tentukan admin mana yang sedang aktif
      let currentAdmin = null
      if (user.value) {
        currentAdmin = list.find(a => 
          (user.value.id && Number(a.id) === Number(user.value.id)) ||
          (user.value.email && a.email && a.email.toLowerCase() === user.value.email.toLowerCase()) ||
          (user.value.church_code && a.church_code && a.church_code.toUpperCase() === user.value.church_code.toUpperCase()) ||
          (user.value.church_id && a.church_id && Number(a.church_id) === Number(user.value.church_id))
        )
      }
      
      // Fallback ke admin pertama jika tidak ada sesi spesifik
      if (!currentAdmin && list.length > 0) {
        currentAdmin = list[0]
      }

      if (currentAdmin) {
        selectAdminChurch(currentAdmin)
      }
    }
  } catch (err) {
    console.error('Gagal memuat data gereja:', err)
    saveErrorMessage.value = 'Gagal memuat data admin gereja dari database.'
  } finally {
    isLoading.value = false
    nextTick(() => {
      initMap()
    })
  }
}

// --- Manajemen Informasi Pelayanan Cabang Gereja ---
const branchServices = ref([])
const isBranchServicesLoading = ref(false)
const isServiceModalOpen = ref(false)
const isServiceSubmitting = ref(false)
const serviceSuccessMsg = ref('')
const serviceErrorMsg = ref('')
const editingServiceId = ref(null)
const selectedCategoryFilter = ref('Semua')

const serviceCategories = [
  'Jadwal Ibadah',
  'Pelayanan Pemuda',
  'Diakonia & Sosial',
  'Komunitas Sel',
  'Katekisasi & Pembinaan',
  'Konseling',
  'Musik & Pujian',
  'Lainnya'
]

const filteredBranchServices = computed(() => {
  if (selectedCategoryFilter.value === 'Semua') {
    return branchServices.value
  }
  return branchServices.value.filter(s => s.category === selectedCategoryFilter.value)
})

const emptyServiceForm = () => ({
  service_name: '',
  category: 'Jadwal Ibadah',
  schedule_day: 'Setiap Hari Minggu',
  schedule_time: '09:00 - 11:00 WIB',
  location_room: 'Ruang Ibadah Utama Lt. 1',
  target_audience: 'Semua Jemaat',
  description: '',
  pic_name: '',
  pic_contact: '',
  live_stream_url: '',
  status: 'Aktif'
})

const serviceForm = reactive(emptyServiceForm())

const loadBranchServices = async (churchAdminId) => {
  if (!churchAdminId) return
  isBranchServicesLoading.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/informasi-pelayanan/?church_admin_id=${churchAdminId}`)
    if (res.ok) {
      branchServices.value = await res.json()
    }
  } catch (err) {
    console.warn('Gagal memuat pelayanan cabang:', err)
  } finally {
    isBranchServicesLoading.value = false
  }
}

const openCreateServiceModal = () => {
  editingServiceId.value = null
  Object.assign(serviceForm, emptyServiceForm())
  serviceSuccessMsg.value = ''
  serviceErrorMsg.value = ''
  isServiceModalOpen.value = true
}

const openEditServiceModal = (item) => {
  editingServiceId.value = item.id
  Object.assign(serviceForm, {
    service_name: item.service_name,
    category: item.category,
    schedule_day: item.schedule_day || '',
    schedule_time: item.schedule_time || '',
    location_room: item.location_room || '',
    target_audience: item.target_audience || 'Semua Jemaat',
    description: item.description || '',
    pic_name: item.pic_name || '',
    pic_contact: item.pic_contact || '',
    live_stream_url: item.live_stream_url || '',
    status: item.status || 'Aktif'
  })
  serviceSuccessMsg.value = ''
  serviceErrorMsg.value = ''
  isServiceModalOpen.value = true
}

const closeServiceModal = () => {
  if (!isServiceSubmitting.value) {
    isServiceModalOpen.value = false
  }
}

const saveServiceToDatabase = async () => {
  if (!serviceForm.service_name.trim()) {
    serviceErrorMsg.value = 'Nama pelayanan atau ibadah wajib diisi.'
    return
  }

  isServiceSubmitting.value = true
  serviceSuccessMsg.value = ''
  serviceErrorMsg.value = ''

  try {
    const activeAdmin = allChurchAdmins.value.find(a => a.id === selectedAdminId.value)
    const payload = {
      church_admin_id: selectedAdminId.value,
      church_id: activeAdmin?.church_id || null,
      church_name: locationForm.church_name || activeAdmin?.church_name || 'Cabang Gereja',
      church_code: locationForm.church_code || activeAdmin?.church_code || '',
      city: locationForm.city || activeAdmin?.city || '',
      service_name: serviceForm.service_name.trim(),
      category: serviceForm.category,
      schedule_day: serviceForm.schedule_day,
      schedule_time: serviceForm.schedule_time,
      location_room: serviceForm.location_room,
      target_audience: serviceForm.target_audience,
      description: serviceForm.description,
      pic_name: serviceForm.pic_name,
      pic_contact: serviceForm.pic_contact,
      live_stream_url: serviceForm.live_stream_url,
      status: serviceForm.status
    }

    const isEdit = !!editingServiceId.value
    const url = isEdit 
      ? `${APP_CONFIG.apiBaseUrl}/informasi-pelayanan/${editingServiceId.value}`
      : `${APP_CONFIG.apiBaseUrl}/informasi-pelayanan/`
    const method = isEdit ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Gagal menyimpan informasi pelayanan ke basis data.')
    }

    serviceSuccessMsg.value = isEdit 
      ? 'Informasi pelayanan berhasil diperbarui di database!' 
      : 'Informasi pelayanan berhasil diterbitkan ke database dan tampil di InformasiPelayanan.vue!'
    
    isServiceModalOpen.value = false
    await loadBranchServices(selectedAdminId.value)
  } catch (err) {
    serviceErrorMsg.value = err.message || 'Terjadi kesalahan sistem.'
  } finally {
    isServiceSubmitting.value = false
  }
}

const deleteServiceFromDatabase = async (item) => {
  if (!confirm(`Yakin ingin menghapus informasi pelayanan "${item.service_name}" dari database?`)) return
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/informasi-pelayanan/${item.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      await loadBranchServices(selectedAdminId.value)
    }
  } catch (err) {
    alert('Gagal menghapus: ' + err.message)
  }
}

// Pemilihan gereja yang akan diedit lokasinya
const selectAdminChurch = (admin) => {
  selectedAdminId.value = admin.id
  locationForm.church_name = admin.church_name || ''
  locationForm.church_code = admin.church_code || ''
  locationForm.city = admin.city || ''
  locationForm.address = admin.address || ''
  locationForm.latitude = admin.latitude !== null && admin.latitude !== undefined ? Number(admin.latitude) : -6.1824
  locationForm.longitude = admin.longitude !== null && admin.longitude !== undefined ? Number(admin.longitude) : 106.9856
  locationForm.google_maps_url = admin.google_maps_url || generateGMapsUrl(locationForm.latitude, locationForm.longitude)

  if (leafletMap && churchMarker) {
    updateCoords(locationForm.latitude, locationForm.longitude, true)
    renderOtherChurchesMarkers()
  }

  loadBranchServices(admin.id)
}

// 3. Simpan Titik Lokasi & Geolocation Langsung ke Database PostgreSQL
const saveLocationToDatabase = async () => {
  if (!selectedAdminId.value) {
    saveErrorMessage.value = 'Silakan pilih akun admin gereja yang akan diperbarui.'
    return
  }

  isSaving.value = true
  saveSuccessMessage.value = ''
  saveErrorMessage.value = ''

  try {
    const payload = {
      address: locationForm.address,
      city: locationForm.city,
      latitude: Number(locationForm.latitude),
      longitude: Number(locationForm.longitude),
      google_maps_url: locationForm.google_maps_url || generateGMapsUrl(locationForm.latitude, locationForm.longitude)
    }

    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${selectedAdminId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Gagal menyimpan perubahan lokasi ke database.')
    }

    const updated = await res.json()
    saveSuccessMessage.value = `Berhasil! Koordinat dan tautan Google Maps untuk "${locationForm.church_name}" telah tersimpan di DBMS PostgreSQL.`

    // Update data lokal
    const idx = allChurchAdmins.value.findIndex(a => a.id === selectedAdminId.value)
    if (idx !== -1) {
      allChurchAdmins.value[idx] = { ...allChurchAdmins.value[idx], ...payload }
    }

    renderOtherChurchesMarkers()
  } catch (err) {
    console.error('Simpan lokasi error:', err)
    saveErrorMessage.value = err.message || 'Terjadi kesalahan saat menghubungi database server.'
  } finally {
    isSaving.value = false
  }
}

// Buka Google Maps langsung di tab baru untuk verifikasi
const openGoogleMapsTest = () => {
  const url = locationForm.google_maps_url || generateGMapsUrl(locationForm.latitude, locationForm.longitude)
  window.open(url, '_blank')
}

onMounted(() => {
  nextTick(() => {
    try {
      AOS.refresh()
    } catch (e) {
      // safe fallback
    }
  })
  loadChurchData()
})

onUnmounted(() => {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
  }
})
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-10 font-sans pb-10">
      
      <!-- ======================================================== -->
      <!-- 1. GRAND HERO BANNER - ADMIN COMMAND CONSOLE             -->
      <!-- ======================================================== -->
      <section 
        :class="[
          'relative rounded-3xl overflow-hidden shadow-2xl border transition-all duration-300',
          isDark
            ? 'admin-hero-card border-amber-500/30'
            : 'admin-hero-card-light border-amber-300/80 shadow-amber-500/5'
        ]"
      >
        <!-- Deep Ambient Background Layers -->
        <div class="hero-bg-texture"></div>
        <div class="hero-overlay-glow"></div>

        <!-- Top Utility Header Bar (Zonasi Atas: Role/Status Badge & Modern Segmented Switcher Tema Gelap - Terang) -->
        <div
          :class="[
            'relative z-10 flex items-center justify-between gap-4 px-6 py-3.5 sm:px-10 border-b transition-colors',
            isDark ? 'border-amber-500/15 bg-slate-950/40' : 'border-amber-300/40 bg-amber-50/50'
          ]"
        >
          <!-- Badge Status Portal -->
          <div
            :class="[
              'inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold tracking-wider uppercase border transition-colors',
              isDark
                ? 'bg-amber-500/15 border-amber-400/40 text-amber-300'
                : 'bg-amber-100/90 border-amber-300 text-amber-900'
            ]"
          >
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Portal Administrator Cabang Gereja</span>
            <span class="text-amber-500/60">•</span>
            <span :class="isDark ? 'text-slate-300 font-normal' : 'text-slate-600 font-medium'">GracePoint Ecosystem</span>
          </div>

          <!-- Fitur Penggantian Warna Gelap - Terang (Modern Segmented Switcher) -->
          <div class="flex items-center gap-2">
            <span :class="['text-[11px] font-bold hidden sm:inline transition-colors', isDark ? 'text-slate-400' : 'text-slate-600']">
              Tema:
            </span>
            <div
              class="inline-flex items-center overflow-hidden p-0.5 rounded-xl border transition-all duration-300 shadow-2xs"
              :class="isDark ? 'bg-slate-950/80 border-slate-800' : 'bg-white border-amber-300/70'"
              role="group"
              aria-label="Pilihan Tema Gelap atau Terang"
            >
              <button
                @click="!isDark && toggleTheme()"
                type="button"
                id="btn-theme-dark"
                :class="[
                  'px-2.5 py-1 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all duration-200 cursor-pointer',
                  isDark
                    ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 shadow-sm font-extrabold'
                    : 'text-slate-500 hover:text-slate-800'
                ]"
                title="Aktifkan Mode Gelap (Dark Mode)"
              >
                <span>🌙</span>
                <span class="hidden sm:inline">Gelap</span>
              </button>
              <button
                @click="isDark && toggleTheme()"
                type="button"
                id="btn-theme-light"
                :class="[
                  'px-2.5 py-1 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all duration-200 cursor-pointer',
                  !isDark
                    ? 'bg-gradient-to-r from-amber-400 to-amber-500 text-slate-950 shadow-sm font-extrabold'
                    : 'text-slate-400 hover:text-white'
                ]"
                title="Aktifkan Mode Terang (Light Mode)"
              >
                <span>☀️</span>
                <span class="hidden sm:inline">Terang</span>
              </button>
            </div>
          </div>
        </div>

        <div class="relative z-10 p-6 sm:p-10 lg:p-12 flex flex-col lg:flex-row items-center justify-between gap-8">
          
          <!-- Kolom Kiri: Branding & Greeting -->
          <div class="flex-1 text-center lg:text-left space-y-4 max-w-2xl">
            <!-- Title dengan Gaya Cinzel HomeView -->
            <h1 
              :class="[
                'hero-cinzel-title text-2xl sm:text-4xl lg:text-5xl font-bold font-serif tracking-wide leading-tight transition-colors',
                isDark ? 'text-amber-300' : 'text-amber-800'
              ]"
            >
              Selamat Datang di Portal Admin Gereja
            </h1>

            <p :class="['text-sm sm:text-base leading-relaxed transition-colors', isDark ? 'text-slate-300' : 'text-slate-600']">
              Pusat kendali eksekutif untuk pengelolaan titik geolocation gereja di peta publik, sinkronisasi jadwal pelayanan jemaat, manajemen presensi ibadah, serta publikasi warta cabang langsung ke DBMS PostgreSQL.
            </p>

            <!-- Dynamic Active Church Ribbon -->
            <div 
              :class="[
                'p-4 rounded-2xl border backdrop-blur-md flex flex-wrap items-center justify-between gap-3 text-xs transition-colors',
                isDark
                  ? 'bg-slate-950/75 border-amber-500/30 text-white'
                  : 'bg-white/95 border-amber-300/80 text-slate-900 shadow-md shadow-amber-500/5'
              ]"
            >
              <div class="flex items-center gap-3">
                <div 
                  :class="[
                    'w-10 h-10 rounded-xl border flex items-center justify-center text-lg shadow-inner transition-colors',
                    isDark
                      ? 'bg-amber-500/20 border-amber-400/40 text-amber-300'
                      : 'bg-amber-100 border-amber-300 text-amber-800'
                  ]"
                >
                  <i class="bi bi-building"></i>
                </div>
                <div>
                  <div :class="['text-[11px] uppercase tracking-wider font-semibold', isDark ? 'text-slate-400' : 'text-slate-500']">Gereja Dikelola Saat Ini:</div>
                  <div :class="['text-sm font-bold font-serif flex items-center gap-2', isDark ? 'text-white' : 'text-slate-900']">
                    <span>{{ locationForm.church_name || 'Menghubungkan ke Server...' }}</span>
                    <span 
                      v-if="locationForm.church_code" 
                      :class="[
                        'px-2 py-0.5 rounded text-[10px] font-mono border font-bold',
                        isDark
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                          : 'bg-amber-100 text-amber-900 border-amber-300'
                      ]"
                    >
                      {{ locationForm.church_code }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <span 
                  :class="[
                    'px-3 py-1 rounded-lg border font-mono text-[11px] font-bold flex items-center gap-1.5 transition-colors',
                    isDark
                      ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
                      : 'bg-emerald-100 border-emerald-300 text-emerald-800'
                  ]"
                >
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                  Sistem Database Terkoneksi
                </span>
              </div>
            </div>

            <!-- Quick Action CTA Group -->
            <div class="flex flex-wrap items-center justify-center lg:justify-start gap-3 pt-2">
              <a 
                href="#pelayanan-cabang" 
                :class="[
                  'px-4 py-3 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center gap-2 hover:scale-[1.02] transition-all cursor-pointer shadow-lg border',
                  isDark
                    ? 'bg-slate-900/90 hover:bg-slate-800 text-amber-300 border-amber-500/40'
                    : 'bg-amber-100 hover:bg-amber-200 text-amber-900 border-amber-300'
                ]"
              >
                <i class="bi bi-broadcast-pin text-sm"></i>
                <span>Kelola Pelayanan Cabang</span>
              </a>

              <RouterLink 
                to="/church-attendance" 
                :class="[
                  'px-4 py-3 rounded-xl text-xs font-semibold flex items-center gap-2 transition border',
                  isDark
                    ? 'bg-slate-950/80 hover:bg-slate-900 text-slate-300 hover:text-white border-slate-700/80'
                    : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300 shadow-xs'
                ]"
              >
                <i class="bi bi-qr-code text-sm text-sky-400"></i>
                <span>Buatkan Kode QR</span>
              </RouterLink>

              <RouterLink 
                to="/church-members" 
                :class="[
                  'px-4 py-3 rounded-xl text-xs font-semibold flex items-center gap-2 transition border',
                  isDark
                    ? 'bg-slate-950/80 hover:bg-slate-900 text-slate-300 hover:text-white border-slate-700/80'
                    : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300 shadow-xs'
                ]"
              >
                <i class="bi bi-people text-sm text-emerald-400"></i>
                <span>Tampilkan Data Jemaat</span>
              </RouterLink>
            </div>

          </div>

          <!-- Kolom Kanan: Emblem Logo & Sacred Scripture Card -->
          <div class="flex flex-col items-center text-center space-y-4 max-w-xs">
            <div class="relative group">
              <div class="absolute -inset-2 bg-gradient-to-r from-amber-500 to-amber-300 rounded-full blur-xl opacity-30 group-hover:opacity-60 transition duration-500"></div>
              <div 
                :class="[
                  'relative w-36 h-36 sm:w-44 sm:h-44 rounded-full p-2 border-2 shadow-2xl flex items-center justify-center overflow-hidden transition-transform duration-300 hover:scale-105',
                  isDark ? 'bg-slate-950 border-amber-400/60' : 'bg-white border-amber-400/80 shadow-amber-500/10'
                ]"
              >
                <img :src="imgGracePoint" alt="GracePoint Emblem" class="w-28 h-28 sm:w-36 sm:h-36 object-contain drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]">
              </div>
            </div>

            <!-- Scripture Gold Card -->
            <div 
              :class="[
                'p-3.5 rounded-2xl border shadow-xl text-left space-y-1.5 transition-colors',
                isDark
                  ? 'bg-slate-950/80 border-amber-500/25'
                  : 'bg-white/95 border-amber-300/80 shadow-amber-500/5'
              ]"
            >
              <div :class="['flex items-center gap-2 text-xs font-serif font-bold', isDark ? 'text-amber-400' : 'text-amber-800']">
                <i class="bi bi-quote text-base"></i>
                <span>Prinsip Pelayanan Tertib</span>
              </div>
              <p :class="['text-[11px] italic font-serif leading-relaxed', isDark ? 'text-slate-300' : 'text-slate-700']">
                "Tetapi segala sesuatu harus berlangsung dengan sopan dan teratur, sebab Allah kita bukan Allah yang menghendaki kekacauan."
              </p>
              <div :class="['text-[10px] font-mono text-right font-semibold', isDark ? 'text-amber-300/80' : 'text-amber-700']">
                — 1 Korintus 14:33, 40
              </div>
            </div>
          </div>

        </div>
      </section>

      
      <!-- ======================================================== -->
      <!-- 3. EXECUTIVE ADMINISTRATION MODULES (SHOWCASE CARDS)     -->
      <!-- ======================================================== -->
      <section class="space-y-4" id="main_service">
        <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2">
          <div>
            <div class="flex items-center gap-2 text-amber-500 text-xs font-semibold uppercase tracking-wider mb-1">
              <i class="bi bi-grid-fill"></i>
              <span>Modul Operasional Gereja Cabang</span>
            </div>
            <h2 :class="['text-xl sm:text-2xl font-bold font-serif tracking-tight transition-colors', isDark ? 'text-white' : 'text-slate-900']">
              Pusat Akses Layanan & Administrasi
            </h2>
            <p :class="['text-xs sm:text-sm mt-0.5 transition-colors', isDark ? 'text-slate-400' : 'text-slate-600']">
              Pintasan cepat untuk mengelola kehadiran jemaat, permohonan sakramen, serta tata kelola keuangan kas gereja.
            </p>
          </div>
          <span :class="['text-xs font-medium px-3 py-1 rounded-full border self-start sm:self-auto transition-colors', isDark ? 'bg-slate-800/80 text-amber-400 border-amber-500/30' : 'bg-amber-50 text-amber-700 border-amber-200']">
            3 Modul Utama Terintegrasi
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
          
          <!-- Module Card 1: Presensi & Ibadah -->
          <div class="showcase-card group flex flex-col justify-between h-full">
            <div>
              <div class="showcase-card-img-wrapper">
                <img :src="imgDashboard" alt="Presensi Ibadah Real-Time" class="showcase-card-img" />
                <div class="showcase-card-overlay"></div>
                <span class="showcase-card-badge bg-emerald-500/20 text-emerald-300 border-emerald-400/40">
                  <i class="bi bi-qr-code-scan me-1.5"></i> Presensi Jemaat Real-Time
                </span>
              </div>
              <div class="p-5">
                <h3 class="showcase-card-title">Presensi & Rekap Kehadiran Ibadah</h3>
                <p class="showcase-card-desc">
                  Pantau kehadiran jemaat saat ibadah raya, scan barcode kehadiran mandiri, dan integrasi catatan kehadiran rayon secara real-time.
                </p>
              </div>
            </div>
            <div class="px-5 pb-5 pt-0">
              <div :class="['pt-3.5 border-t flex items-center justify-between', isDark ? 'border-slate-800/80' : 'border-slate-200']">
                <span :class="['text-[11px] font-mono flex items-center gap-1.5', isDark ? 'text-slate-400' : 'text-slate-500']">
                  <i class="bi bi-shield-check text-emerald-500"></i>
                  <span>Kode QR Dinamis</span>
                </span>
                <RouterLink 
                  to="/church-attendance" 
                  :class="[
                    'px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 border shadow-sm group-hover:shadow',
                    isDark
                      ? 'bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border-emerald-500/30 hover:border-emerald-500/50'
                      : 'bg-emerald-100 hover:bg-emerald-200 text-emerald-900 border-emerald-300'
                  ]"
                >
                  <span>Buka Presensi</span>
                  <i class="bi bi-arrow-right text-[11px] transition-transform duration-200 group-hover:translate-x-0.5"></i>
                </RouterLink>
              </div>
            </div>
          </div>

          <!-- Module Card 2: Database Jemaat & Rayon -->
          <div class="showcase-card group flex flex-col justify-between h-full">
            <div>
              <div class="showcase-card-img-wrapper">
                <img :src="imgChurchDigital" alt="Database Jemaat & Rayon" class="showcase-card-img" />
                <div class="showcase-card-overlay"></div>
                <span class="showcase-card-badge bg-amber-500/20 text-amber-300 border-amber-400/40">
                  <i class="bi bi-people-fill me-1.5"></i> Database & Sakramen
                </span>
              </div>
              <div class="p-5">
                <h3 class="showcase-card-title">Manajemen Jemaat & Sakramen</h3>
                <p class="showcase-card-desc">
                  Kelola data keanggotaan keluarga jemaat, verifikasi permohonan sakramen pernikahan dan baptisan, serta koordinasi rayon sel.
                </p>
              </div>
            </div>
            <div class="px-5 pb-5 pt-0">
              <div :class="['pt-3.5 border-t flex items-center justify-between', isDark ? 'border-slate-800/80' : 'border-slate-200']">
                <span :class="['text-[11px] font-mono flex items-center gap-1.5', isDark ? 'text-slate-400' : 'text-slate-500']">
                  <i class="bi bi-diagram-3 text-amber-500"></i>
                  <span>Rayon & Keluarga</span>
                </span>
                <RouterLink 
                  to="/church-members" 
                  :class="[
                    'px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 border shadow-sm group-hover:shadow',
                    isDark
                      ? 'bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border-amber-500/30 hover:border-amber-500/50'
                      : 'bg-amber-100 hover:bg-amber-200 text-amber-900 border-amber-300'
                  ]"
                >
                  <span>Kelola Jemaat</span>
                  <i class="bi bi-arrow-right text-[11px] transition-transform duration-200 group-hover:translate-x-0.5"></i>
                </RouterLink>
              </div>
            </div>
          </div>

          <!-- Module Card 3: Manajemen Keuangan Gereja -->
          <div class="showcase-card group flex flex-col justify-between h-full">
            <div>
              <div class="showcase-card-img-wrapper">
                <img :src="imgKeuanganGereja" alt="Manajemen & Kas Keuangan Gereja" class="showcase-card-img" />
                <div class="showcase-card-overlay"></div>
                <span class="showcase-card-badge bg-sky-500/20 text-sky-300 border-sky-400/40">
                  <i class="bi bi-wallet2 me-1.5"></i> Manajemen Keuangan Gereja
                </span>
              </div>
              <div class="p-5">
                <h3 class="showcase-card-title">Manajemen Keuangan Gereja</h3>
                <p class="showcase-card-desc">
                  Dengan adanya sistem ini memungkinkan pihak gereja dapat mengatur pengeluaran dan pendapatan keuangan gereja dalam setiap aktivitasnya.
                </p>
              </div>
            </div>
            <div class="px-5 pb-5 pt-0">
              <div :class="['pt-3.5 border-t flex items-center justify-between', isDark ? 'border-slate-800/80' : 'border-slate-200']">
                <span :class="['text-[11px] font-mono flex items-center gap-1.5', isDark ? 'text-slate-400' : 'text-slate-500']">
                  <i class="bi bi-pie-chart text-sky-500"></i>
                  <span>ChartJS & Laporan</span>
                </span>
                <RouterLink 
                  to="/church-finance" 
                  :class="[
                    'px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 border shadow-sm group-hover:shadow',
                    isDark
                      ? 'bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border-sky-500/30 hover:border-sky-500/50'
                      : 'bg-sky-100 hover:bg-sky-200 text-sky-900 border-sky-300'
                  ]"
                >
                  <span>Cek & Atur Keuangan</span>
                  <i class="bi bi-arrow-right text-[11px] transition-transform duration-200 group-hover:translate-x-0.5"></i>
                </RouterLink>
              </div>
            </div>
          </div>

        </div>
      </section>
    

      <!-- ======================================================== -->
      <!-- MODAL TAMBAH / EDIT INFORMASI PELAYANAN                  -->
      <!-- ======================================================== -->
      <Transition name="fade">
        <div 
          v-if="isServiceModalOpen"
          class="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto"
          @click.self="closeServiceModal"
          @keydown.esc.stop.prevent="closeServiceModal"
          tabindex="-1"
        >
          <div
            :class="['w-full max-w-xl rounded-3xl shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col font-sans animate-scaleUp border transition-colors', isDark ? 'bg-slate-900 border-amber-500/40 text-white' : 'bg-white border-amber-300 text-slate-900']"
            role="dialog"
            aria-modal="true"
            aria-labelledby="service-modal-title"
          >
            <!-- Modal Header -->
            <div :class="['shrink-0 p-5 sm:p-6 border-b flex items-center justify-between transition-colors', isDark ? 'bg-slate-950 border-amber-500/30' : 'bg-amber-50/80 border-amber-200']">
              <div>
                <h3 id="service-modal-title" :class="['font-serif text-lg font-bold', isDark ? 'text-amber-300' : 'text-amber-800']">
                  {{ editingServiceId ? 'Edit Informasi Pelayanan Cabang' : 'Terbitkan Informasi Pelayanan Baru' }}
                </h3>
                <p :class="['text-xs mt-0.5', isDark ? 'text-slate-400' : 'text-slate-600']">Gereja: {{ locationForm.church_name }} ({{ locationForm.city || 'Cabang' }})</p>
              </div>
              <button 
                type="button"
                @click="closeServiceModal"
                :disabled="isServiceSubmitting"
                aria-label="Tutup formulir"
                :class="['w-8 h-8 rounded-full border flex items-center justify-center transition cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed', isDark ? 'bg-slate-900 text-slate-400 hover:text-white border-amber-500/30' : 'bg-white text-slate-500 hover:text-slate-800 border-slate-300']"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>

            <form @submit.prevent="saveServiceToDatabase" class="flex min-h-0 flex-1 flex-col">
            <!-- Modal Form Body -->
            <div class="min-h-0 flex-1 p-6 overflow-y-auto space-y-4 text-xs">
              <div v-if="serviceErrorMsg" role="alert" class="p-3 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-400">
                {{ serviceErrorMsg }}
              </div>

              <!-- Nama Pelayanan -->
              <div>
                <label for="service-field-name" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Nama Ibadah / Pelayanan: *</label>
                <input 
                  id="service-field-name"
                  v-model="serviceForm.service_name"
                  type="text" 
                  required
                  maxlength="150"
                  autocomplete="off"
                  autofocus
                  placeholder="Contoh: Ibadah Raya 1, Persekutuan Doa Fajar, Youth Revival"
                  :class="[
                    'w-full rounded-xl px-3.5 py-2.5 outline-none transition border',
                    isDark
                      ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                      : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                  ]"
                />
              </div>

              <!-- Kategori & Status -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label for="service-field-category" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Kategori: *</label>
                  <select 
                    id="service-field-category"
                    v-model="serviceForm.category"
                    required
                    :class="[
                      'w-full rounded-xl px-3.5 py-2.5 outline-none transition cursor-pointer border',
                      isDark
                        ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                        : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                    ]"
                  >
                    <option v-for="c in serviceCategories" :key="c" :value="c">{{ c }}</option>
                  </select>
                </div>

                <div>
                  <label for="service-field-status" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Status Pelayanan:</label>
                  <select 
                    id="service-field-status"
                    v-model="serviceForm.status"
                    :class="[
                      'w-full rounded-xl px-3.5 py-2.5 outline-none transition cursor-pointer border',
                      isDark
                        ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                        : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                    ]"
                  >
                    <option value="Aktif">Aktif</option>
                    <option value="Akan Datang">Akan Datang</option>
                    <option value="Nonaktif">Nonaktif</option>
                  </select>
                </div>
              </div>

              <!-- Hari & Jam Pelaksanaan -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label for="service-field-day" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Hari Pelaksanaan:</label>
                  <input 
                    id="service-field-day"
                    v-model="serviceForm.schedule_day"
                    type="text" 
                    placeholder="Contoh: Setiap Hari Minggu / Jumat Malam"
                    :class="[
                      'w-full rounded-xl px-3.5 py-2.5 outline-none transition border',
                      isDark
                        ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                        : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                    ]"
                  />
                </div>

                <div>
                  <label for="service-field-time" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Jam Pelaksanaan:</label>
                  <input 
                    id="service-field-time"
                    v-model="serviceForm.schedule_time"
                    type="text" 
                    placeholder="Contoh: 09:00 - 11:00 WIB"
                    :class="[
                      'w-full rounded-xl px-3.5 py-2.5 outline-none transition border',
                      isDark
                        ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                        : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                    ]"
                  />
                </div>
              </div>

              <!-- Ruang & Target -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label for="service-field-location" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Ruangan / Tempat:</label>
                  <input 
                    id="service-field-location"
                    v-model="serviceForm.location_room"
                    type="text" 
                    placeholder="Contoh: Main Sanctuary Lt. 1 / Ruang Serbaguna"
                    :class="[
                      'w-full rounded-xl px-3.5 py-2.5 outline-none transition border',
                      isDark
                        ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                        : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                    ]"
                  />
                </div>

                <div>
                  <label for="service-field-audience" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Target Jemaat:</label>
                  <input 
                    id="service-field-audience"
                    v-model="serviceForm.target_audience"
                    type="text" 
                    placeholder="Contoh: Semua Jemaat / Pemuda & Remaja"
                    :class="[
                      'w-full rounded-xl px-3.5 py-2.5 outline-none transition border',
                      isDark
                        ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                        : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                    ]"
                  />
                </div>
              </div>

              <!-- PIC & Kontak WA -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label for="service-field-pic" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Nama PIC / Pelayan:</label>
                  <input 
                    id="service-field-pic"
                    v-model="serviceForm.pic_name"
                    type="text" 
                    placeholder="Contoh: Pdt. Andreas / Sdr. Kevin"
                    :class="[
                      'w-full rounded-xl px-3.5 py-2.5 outline-none transition border',
                      isDark
                        ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                        : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                    ]"
                  />
                </div>

                <div>
                  <label for="service-field-phone" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Nomor WhatsApp PIC:</label>
                  <input 
                    id="service-field-phone"
                    v-model="serviceForm.pic_contact"
                    type="tel" 
                    autocomplete="tel"
                    placeholder="Contoh: 081234567890"
                    :class="[
                      'w-full rounded-xl px-3.5 py-2.5 outline-none transition border',
                      isDark
                        ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                        : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                    ]"
                  />
                </div>
              </div>

              <!-- Link Live Streaming -->
              <div>
                <label for="service-field-url" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Link Live Streaming / Zoom (Opsional):</label>
                <input 
                  id="service-field-url"
                  v-model="serviceForm.live_stream_url"
                  type="url" 
                  placeholder="https://youtube.com/..."
                  :class="[
                    'w-full rounded-xl px-3.5 py-2.5 outline-none transition border',
                    isDark
                      ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                      : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                  ]"
                />
              </div>

              <!-- Deskripsi -->
              <div>
                <label for="service-field-description" :class="['block font-semibold mb-1', isDark ? 'text-slate-300' : 'text-slate-700']">Deskripsi & Keterangan Pelayanan:</label>
                <textarea 
                  id="service-field-description"
                  v-model="serviceForm.description"
                  rows="3"
                  placeholder="Uraikan informasi mengenai tata ibadah, tema bulanan, atau panduan kehadiran..."
                  :class="[
                    'w-full rounded-xl px-3.5 py-2.5 outline-none resize-none transition border',
                    isDark
                      ? 'bg-slate-950 border-amber-500/30 text-white focus:border-amber-400'
                      : 'bg-slate-50 border-slate-300 text-slate-900 focus:border-amber-500'
                  ]"
                ></textarea>
              </div>
            </div>

            <!-- Modal Footer -->
            <div :class="['shrink-0 p-4 border-t flex items-center justify-end gap-2.5 transition-colors', isDark ? 'bg-slate-950 border-amber-500/30' : 'bg-slate-50 border-slate-200']">
              <button 
                type="button"
                @click="closeServiceModal"
                :disabled="isServiceSubmitting"
                :class="['px-4 py-2 rounded-xl text-xs font-semibold transition cursor-pointer border disabled:opacity-50 disabled:cursor-not-allowed', isDark ? 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-transparent' : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300 shadow-xs']"
              >
                Batal
              </button>

              <button 
                type="submit"
                :disabled="isServiceSubmitting"
                class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 text-xs font-bold uppercase tracking-wider transition flex items-center gap-1.5 shadow-lg shadow-amber-500/20 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <span v-if="isServiceSubmitting" class="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                <span>{{ isServiceSubmitting ? 'Menyimpan...' : editingServiceId ? 'Simpan Perubahan' : 'Terbitkan ke Database' }}</span>
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
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Lato:wght@400;500;700&display=swap');

.fade-enter-active,
.fade-leave-active {
  transition: opacity 180ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* --- Grand Hero Banner Styling --- */
.admin-hero-card {
  background: linear-gradient(135deg, #050914 0%, #070e24 45%, #0a1435 85%, #0d1a45 100%);
  position: relative;
}

.admin-hero-card-light {
  background: linear-gradient(135deg, #ffffff 0%, #fefce8 35%, #fffbeb 75%, #fef3c7 100%);
  position: relative;
}

.hero-bg-texture {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle at 10% 20%, rgba(245, 158, 11, 0.12) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(56, 189, 248, 0.12) 0%, transparent 45%);
  pointer-events: none;
}

.hero-overlay-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(7, 12, 25, 0.25) 0%, rgba(7, 12, 25, 0.65) 100%);
  pointer-events: none;
}

:global(html[data-theme="light"]) .hero-overlay-glow,
:global(html.theme-light) .hero-overlay-glow,
:global(html.light) .hero-overlay-glow {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, rgba(254, 243, 199, 0.35) 100%) !important;
}

.hero-cinzel-title {
  font-family: 'Cinzel', serif;
  text-shadow: 0 4px 18px rgba(245, 158, 11, 0.3);
}

:global(html[data-theme="light"]) .hero-cinzel-title,
:global(html.theme-light) .hero-cinzel-title,
:global(html.light) .hero-cinzel-title {
  text-shadow: 0 2px 10px rgba(217, 119, 6, 0.2) !important;
}

/* --- Stat Card Styling (HomeView Design Pattern) --- */
.stat-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1.5rem;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(12, 21, 56, 0.7));
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 1.25rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(12px);
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: rgba(251, 191, 36, 0.5);
  box-shadow: 0 16px 30px -8px rgba(0, 0, 0, 0.55), 0 0 20px rgba(245, 158, 11, 0.15);
}

:global(html[data-theme="light"]) .stat-card,
:global(html.theme-light) .stat-card,
:global(html.light) .stat-card {
  background: linear-gradient(145deg, #ffffff, #f8fafc) !important;
  border: 1px solid rgba(217, 119, 6, 0.25) !important;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06) !important;
}

:global(html[data-theme="light"]) .stat-card:hover,
:global(html.theme-light) .stat-card:hover,
:global(html.light) .stat-card:hover {
  border-color: rgba(217, 119, 6, 0.5) !important;
  box-shadow: 0 10px 25px -5px rgba(217, 119, 6, 0.12), 0 0 15px rgba(217, 119, 6, 0.1) !important;
}

/* --- Showcase Cards Styling (HomeView Design Pattern) --- */
.showcase-card {
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(28, 43, 94, 0.55));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.25rem;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
}

.showcase-card:hover {
  transform: translateY(-5px);
  border-color: rgba(251, 191, 36, 0.5);
  box-shadow: 0 18px 32px -8px rgba(0, 0, 0, 0.5), 0 0 22px rgba(245, 158, 11, 0.18);
}

:global(html[data-theme="light"]) .showcase-card,
:global(html.theme-light) .showcase-card,
:global(html.light) .showcase-card {
  background: #ffffff !important;
  border: 1px solid rgba(15, 23, 42, 0.1) !important;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06) !important;
}

:global(html[data-theme="light"]) .showcase-card:hover,
:global(html.theme-light) .showcase-card:hover,
:global(html.light) .showcase-card:hover {
  border-color: rgba(217, 119, 6, 0.45) !important;
  box-shadow: 0 12px 28px -6px rgba(217, 119, 6, 0.15) !important;
}

.showcase-card-img-wrapper {
  position: relative;
  width: 100%;
  height: 160px;
  overflow: hidden;
}

.showcase-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.showcase-card:hover .showcase-card-img {
  transform: scale(1.08);
}

.showcase-card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.25) 60%, transparent 100%);
}

.showcase-card-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.3rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid;
  backdrop-filter: blur(8px);
  z-index: 2;
}

.showcase-card-content {
  padding: 1.25rem;
  text-align: left;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.showcase-card-title {
  font-family: 'Cinzel', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 0.4rem;
  line-height: 1.35;
}

:global(html[data-theme="light"]) .showcase-card-title,
:global(html.theme-light) .showcase-card-title,
:global(html.light) .showcase-card-title {
  color: #0f172a !important;
}

.showcase-card-desc {
  font-family: 'Lato', sans-serif;
  font-size: 0.825rem;
  color: #94a3b8;
  line-height: 1.55;
  margin: 0;
}

:global(html[data-theme="light"]) .showcase-card-desc,
:global(html.theme-light) .showcase-card-desc,
:global(html.light) .showcase-card-desc {
  color: #475569 !important;
}

/* Animations */
@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scaleUp {
  animation: scaleUp 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Leaflet custom popup styling */
:deep(.leaflet-popup-content-wrapper) {
  background: var(--theme-bg-surface, #0f172a);
  color: var(--theme-text-primary, #f1f5f9);
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
}

:deep(.leaflet-popup-tip) {
  background: var(--theme-bg-surface, #0f172a);
  border: 1px solid rgba(245, 158, 11, 0.4);
}

:deep(.leaflet-popup-close-button) {
  color: #f59e0b !important;
}

:global(html[data-theme="light"]) :deep(.leaflet-popup-content-wrapper),
:global(html.theme-light) :deep(.leaflet-popup-content-wrapper),
:global(html.light) :deep(.leaflet-popup-content-wrapper) {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: rgba(217, 119, 6, 0.35) !important;
}

:global(html[data-theme="light"]) :deep(.leaflet-popup-tip),
:global(html.theme-light) :deep(.leaflet-popup-tip),
:global(html.light) :deep(.leaflet-popup-tip) {
  background: #ffffff !important;
}
</style>
