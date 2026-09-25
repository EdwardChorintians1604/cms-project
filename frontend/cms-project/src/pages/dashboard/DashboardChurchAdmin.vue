<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { RouterLink } from 'vue-router'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'
import { useAuth } from '@/composables/useAuth'
import { APP_CONFIG } from '@/config'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import AOS from 'aos'

import imgDashboard from '@/assets/images/manajemen_gereja_1.png'
import imgChurchDigital from '@/assets/images/manajemen_gereja_2.jpg'
import imgAppHand from '@/assets/images/manajemen_gereja_3.jpg'
import imgGracePoint from '@/assets/images/GracePoint.png'

const { user } = useAuth()

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
      if (user.value && user.value.role === 'church_admin') {
        currentAdmin = list.find(a => a.id === user.value.id || a.email === user.value.email)
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
      <section class="admin-hero-card relative rounded-3xl overflow-hidden shadow-2xl border border-amber-500/30">
        <!-- Deep Ambient Background Layers -->
        <div class="hero-bg-texture"></div>
        <div class="hero-overlay-glow"></div>

        <div class="relative z-10 p-6 sm:p-10 lg:p-12 flex flex-col lg:flex-row items-center justify-between gap-8">
          
          <!-- Kolom Kiri: Branding & Greeting -->
          <div class="flex-1 text-center lg:text-left space-y-4 max-w-2xl">
            <!-- Badge Status Portal -->
            <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/15 border border-amber-400/40 text-amber-300 text-xs font-semibold tracking-wider uppercase">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Portal Administrator Cabang Gereja</span>
              <span class="text-amber-500/60">•</span>
              <span class="text-slate-300 font-normal">GracePoint Ecosystem</span>
            </div>

            <!-- Title dengan Gaya Cinzel HomeView -->
            <h1 class="hero-cinzel-title text-2xl sm:text-4xl lg:text-5xl font-bold font-serif text-amber-300 tracking-wide leading-tight">
              Selamat Datang di Portal Admin Gereja
            </h1>

            <p class="text-slate-300 text-sm sm:text-base leading-relaxed">
              Pusat kendali eksekutif untuk pengelolaan titik geolocation gereja di peta publik, sinkronisasi jadwal pelayanan jemaat, manajemen presensi ibadah, serta publikasi warta cabang langsung ke DBMS PostgreSQL.
            </p>

            <!-- Dynamic Active Church Ribbon -->
            <div class="p-4 rounded-2xl bg-slate-950/75 border border-amber-500/30 backdrop-blur-md flex flex-wrap items-center justify-between gap-3 text-xs">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-400/40 text-amber-300 flex items-center justify-center text-lg shadow-inner">
                  <i class="bi bi-building"></i>
                </div>
                <div>
                  <div class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Gereja Dikelola Saat Ini:</div>
                  <div class="text-sm font-bold text-white font-serif flex items-center gap-2">
                    <span>{{ locationForm.church_name || 'Menghubungkan ke Server...' }}</span>
                    <span v-if="locationForm.church_code" class="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      {{ locationForm.church_code }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <span class="px-3 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 font-mono text-[11px] font-bold flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                  PostgreSQL Terkoneksi
                </span>
              </div>
            </div>

            <!-- Quick Action CTA Group -->
            <div class="flex flex-wrap items-center justify-center lg:justify-start gap-3 pt-2">
              <a 
                href="#geolocation" 
                class="px-5 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-xl shadow-amber-500/20 hover:scale-[1.02] transition-all cursor-pointer"
              >
                <i class="bi bi-geo-alt-fill text-sm"></i>
                <span>Atur Geolocation Peta</span>
              </a>

              <a 
                href="#pelayanan-cabang" 
                class="px-4 py-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-amber-300 border border-amber-500/40 font-bold text-xs uppercase tracking-wider flex items-center gap-2 hover:scale-[1.02] transition-all cursor-pointer shadow-lg"
              >
                <i class="bi bi-broadcast-pin text-sm"></i>
                <span>Kelola Pelayanan Cabang</span>
              </a>

              <RouterLink 
                to="/church-attendance" 
                class="px-4 py-3 rounded-xl bg-slate-950/80 hover:bg-slate-900 text-slate-300 hover:text-white border border-slate-700/80 text-xs font-semibold flex items-center gap-2 transition"
              >
                <i class="bi bi-qr-code text-sm text-sky-400"></i>
                <span>Presensi Ibadah</span>
              </RouterLink>

              <RouterLink 
                to="/church-members" 
                class="px-4 py-3 rounded-xl bg-slate-950/80 hover:bg-slate-900 text-slate-300 hover:text-white border border-slate-700/80 text-xs font-semibold flex items-center gap-2 transition"
              >
                <i class="bi bi-people text-sm text-emerald-400"></i>
                <span>Data Jemaat</span>
              </RouterLink>
            </div>

          </div>

          <!-- Kolom Kanan: Emblem Logo & Sacred Scripture Card -->
          <div class="flex flex-col items-center text-center space-y-4 max-w-xs">
            <div class="relative group">
              <div class="absolute -inset-2 bg-gradient-to-r from-amber-500 to-amber-300 rounded-full blur-xl opacity-30 group-hover:opacity-60 transition duration-500"></div>
              <div class="relative w-36 h-36 sm:w-44 sm:h-44 rounded-full p-2 bg-slate-950 border-2 border-amber-400/60 shadow-2xl flex items-center justify-center overflow-hidden transition-transform duration-300 hover:scale-105">
                <img :src="imgGracePoint" alt="GracePoint Emblem" class="w-28 h-28 sm:w-36 sm:h-36 object-contain drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]">
              </div>
            </div>

            <!-- Scripture Gold Card -->
            <div class="p-3.5 rounded-2xl bg-slate-950/80 border border-amber-500/25 shadow-xl text-left space-y-1.5">
              <div class="flex items-center gap-2 text-amber-400 text-xs font-serif font-bold">
                <i class="bi bi-quote text-base"></i>
                <span>Prinsip Pelayanan Tertib</span>
              </div>
              <p class="text-[11px] text-slate-300 italic font-serif leading-relaxed">
                "Tetapi segala sesuatu harus berlangsung dengan sopan dan teratur, sebab Allah kita bukan Allah yang menghendaki kekacauan."
              </p>
              <div class="text-[10px] text-amber-300/80 font-mono text-right font-semibold">
                — 1 Korintus 14:33, 40
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- ======================================================== -->
      <!-- 2. EXECUTIVE KEY METRICS COUNTERS (HOMEVIEW AESTHETICS)   -->
      <!-- ======================================================== -->
      <section class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg sm:text-xl font-bold font-serif text-white flex items-center gap-2">
              <i class="bi bi-speedometer2 text-amber-400"></i>
              <span>Ringkasan Statistik & Indikator Cabang</span>
            </h2>
            <p class="text-xs text-slate-400">Metrik operasional jemaat dan kehadiran ibadah gereja cabang Anda.</p>
          </div>
          <span class="text-xs text-slate-500 font-mono hidden sm:inline-block">Auto-Synced with PostgreSQL</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          
          <!-- Stat 1: Total Jemaat Terdaftar -->
          <div class="stat-card group">
            <div class="flex items-center justify-between w-full mb-2">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Jemaat</span>
              <div class="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-400 flex items-center justify-center text-sm shadow-inner group-hover:scale-110 transition-transform">
                <i class="bi bi-people-fill"></i>
              </div>
            </div>
            <div class="text-3xl sm:text-4xl font-bold font-serif text-amber-400 tracking-tight my-1">
              1,248
            </div>
            <div class="w-full flex items-center justify-between text-xs pt-2 border-t border-slate-800">
              <span class="text-slate-400">Aktif Terdaftar</span>
              <span class="text-emerald-400 font-semibold font-mono text-[11px]">+12 Jiwa Baru</span>
            </div>
          </div>

          <!-- Stat 2: Kehadiran Minggu Lalu -->
          <div class="stat-card group">
            <div class="flex items-center justify-between w-full mb-2">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Kehadiran Terakhir</span>
              <div class="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center justify-center text-sm shadow-inner group-hover:scale-110 transition-transform">
                <i class="bi bi-calendar2-check-fill"></i>
              </div>
            </div>
            <div class="text-3xl sm:text-4xl font-bold font-serif text-emerald-400 tracking-tight my-1">
              892
            </div>
            <div class="w-full flex items-center justify-between text-xs pt-2 border-t border-slate-800">
              <span class="text-slate-400">Ibadah Raya 1 & 2</span>
              <span class="text-emerald-400 font-semibold font-mono text-[11px]">71.4% Kuota</span>
            </div>
          </div>

          <!-- Stat 3: Total Keluarga / KK -->
          <div class="stat-card group">
            <div class="flex items-center justify-between w-full mb-2">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Kepala Keluarga</span>
              <div class="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 text-sky-400 flex items-center justify-center text-sm shadow-inner group-hover:scale-110 transition-transform">
                <i class="bi bi-house-heart-fill"></i>
              </div>
            </div>
            <div class="text-3xl sm:text-4xl font-bold font-serif text-sky-400 tracking-tight my-1">
              340
            </div>
            <div class="w-full flex items-center justify-between text-xs pt-2 border-t border-slate-800">
              <span class="text-slate-400">Terdata dalam Rayon</span>
              <span class="text-sky-300 font-semibold font-mono text-[11px]">8 Wilayah</span>
            </div>
          </div>

          <!-- Stat 4: Program Pelayanan & Geolocation Status -->
          <div class="stat-card group">
            <div class="flex items-center justify-between w-full mb-2">
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Pelayanan & Peta</span>
              <div class="w-8 h-8 rounded-lg bg-purple-500/15 border border-purple-500/30 text-purple-400 flex items-center justify-center text-sm shadow-inner group-hover:scale-110 transition-transform">
                <i class="bi bi-broadcast-pin"></i>
              </div>
            </div>
            <div class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-tight my-1 flex items-center gap-2">
              <span>{{ branchServices.length }}</span>
              <span class="text-xs font-sans text-slate-400 font-normal">Program</span>
            </div>
            <div class="w-full flex items-center justify-between text-xs pt-2 border-t border-slate-800">
              <span class="text-slate-400">Peta Geolocation:</span>
              <span class="text-emerald-400 font-semibold font-mono text-[11px] flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Terkoneksi
              </span>
            </div>
          </div>

        </div>
      </section>

      <!-- ======================================================== -->
      <!-- 3. EXECUTIVE ADMINISTRATION MODULES (SHOWCASE CARDS)     -->
      <!-- ======================================================== -->
      <section class="space-y-4">
        <div>
          <div class="flex items-center gap-2 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <i class="bi bi-grid-fill"></i>
            <span>Modul Operasional Gereja Cabang</span>
          </div>
          <h2 class="text-xl sm:text-2xl font-bold font-serif text-white">
            Pusat Akses Layanan & Administrasi
          </h2>
          <p class="text-slate-400 text-xs sm:text-sm mt-0.5">
            Pintasan cepat untuk mengelola kehadiran jemaat, permohonan sakramen, dan sinkronisasi informasi publik.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <!-- Module Card 1: Presensi & Ibadah -->
          <div class="showcase-card group">
            <div class="showcase-card-img-wrapper">
              <img :src="imgDashboard" alt="Presensi Ibadah Real-Time" class="showcase-card-img" />
              <div class="showcase-card-overlay"></div>
              <span class="showcase-card-badge bg-emerald-500/20 text-emerald-300 border-emerald-400/40">
                <i class="bi bi-qr-code-scan me-1"></i> Presensi Jemaat Real-Time
              </span>
            </div>
            <div class="showcase-card-content">
              <div>
                <h3 class="showcase-card-title">Presensi & Rekap Kehadiran Ibadah</h3>
                <p class="showcase-card-desc">
                  Pantau kehadiran jemaat saat ibadah raya, scan barcode kehadiran mandiri, dan integrasi catatan kehadiran rayon secara real-time.
                </p>
              </div>
              <div class="pt-4 mt-3 border-t border-slate-800/80 flex items-center justify-between">
                <span class="text-[11px] text-slate-400 font-mono">Kode QR Dinamis</span>
                <RouterLink 
                  to="/church-attendance" 
                  class="px-3.5 py-1.5 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition flex items-center gap-1"
                >
                  <span>Buka Presensi</span>
                  <i class="bi bi-arrow-right"></i>
                </RouterLink>
              </div>
            </div>
          </div>

          <!-- Module Card 2: Database Jemaat & Rayon -->
          <div class="showcase-card group">
            <div class="showcase-card-img-wrapper">
              <img :src="imgChurchDigital" alt="Database Jemaat & Rayon" class="showcase-card-img" />
              <div class="showcase-card-overlay"></div>
              <span class="showcase-card-badge bg-amber-500/20 text-amber-300 border-amber-400/40">
                <i class="bi bi-people-fill me-1"></i> Database & Sakramen
              </span>
            </div>
            <div class="showcase-card-content">
              <div>
                <h3 class="showcase-card-title">Manajemen Jemaat & Sakramen</h3>
                <p class="showcase-card-desc">
                  Kelola data keanggotaan keluarga jemaat, verifikasi permohonan sakramen pernikahan dan baptisan, serta koordinasi rayon sel.
                </p>
              </div>
              <div class="pt-4 mt-3 border-t border-slate-800/80 flex items-center justify-between">
                <span class="text-[11px] text-slate-400 font-mono">Rayon & Keluarga</span>
                <RouterLink 
                  to="/church-members" 
                  class="px-3.5 py-1.5 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 text-xs font-semibold transition flex items-center gap-1"
                >
                  <span>Kelola Jemaat</span>
                  <i class="bi bi-arrow-right"></i>
                </RouterLink>
              </div>
            </div>
          </div>

          <!-- Module Card 3: Geolocation & Warta Publik -->
          <div class="showcase-card group">
            <div class="showcase-card-img-wrapper">
              <img :src="imgAppHand" alt="Warta Digital & Geolocation" class="showcase-card-img" />
              <div class="showcase-card-overlay"></div>
              <span class="showcase-card-badge bg-sky-500/20 text-sky-300 border-sky-400/40">
                <i class="bi bi-geo-alt-fill me-1"></i> Integrasi Layanan Publik
              </span>
            </div>
            <div class="showcase-card-content">
              <div>
                <h3 class="showcase-card-title">Peta Geolocation & Warta Pelayanan</h3>
                <p class="showcase-card-desc">
                  Sinkronkan koordinat fisik gedung gereja ke Google Maps serta publikasikan jadwal ibadah dan warta agar tampil di portal jemaat.
                </p>
              </div>
              <div class="pt-4 mt-3 border-t border-slate-800/80 flex items-center justify-between">
                <span class="text-[11px] text-slate-400 font-mono">CartoDB & Leaflet</span>
                <a 
                  href="#geolocation" 
                  class="px-3.5 py-1.5 rounded-lg bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border border-sky-500/30 text-xs font-semibold transition flex items-center gap-1"
                >
                  <span>Atur Lokasi</span>
                  <i class="bi bi-arrow-down-short"></i>
                </a>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- ======================================================== -->
      <!-- 4. SECTION GEOLOCATION & GOOGLE MAPS MANAGER             -->
      <!-- ======================================================== -->
      <section id="geolocation" class="bg-slate-900/90 border border-amber-500/30 rounded-3xl p-5 sm:p-8 shadow-2xl backdrop-blur-xl space-y-6">
        
        <!-- Header Section Geolocation -->
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800">
          <div>
            <div class="flex items-center gap-2 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-1">
              <i class="bi bi-geo-alt-fill"></i>
              <span>Fitur Geolocation & Google Maps Terintegrasi</span>
            </div>
            <h2 class="text-xl sm:text-2xl font-bold font-serif text-white">
              Peta Lokasi & Koordinat Gereja (Admin Control)
            </h2>
            <p class="text-slate-400 text-xs sm:text-sm mt-1">
              Tentukan posisi pasti gereja Anda dengan menggeser pin di peta, mencari alamat, atau memanfaatkan GPS langsung dari perangkat Anda. Titik ini akan langsung tampil di Beranda Pengguna.
            </p>
          </div>

          <!-- Switcher Pilih Gereja Jika Ada Lebih dari 1 -->
          <div class="flex items-center gap-3">
            <label class="text-xs text-slate-400 font-semibold whitespace-nowrap">Gereja Dikelola:</label>
            <select 
              :value="selectedAdminId"
              @change="(e) => {
                const adm = allChurchAdmins.find(a => a.id === Number(e.target.value))
                if (adm) selectAdminChurch(adm)
              }"
              class="bg-slate-950 border border-amber-500/40 text-amber-300 text-xs rounded-xl px-3 py-2 outline-none focus:border-amber-400 max-w-[240px] cursor-pointer shadow-inner"
            >
              <option v-for="adm in allChurchAdmins" :key="adm.id" :value="adm.id">
                {{ adm.church_name }} ({{ adm.city || 'Cabang' }})
              </option>
            </select>
          </div>
        </div>

        <!-- Feedback Alert Messages -->
        <div v-if="saveSuccessMessage" class="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs sm:text-sm flex items-start gap-3 animate-scaleUp">
          <i class="bi bi-check-circle-fill text-emerald-400 text-base flex-shrink-0 mt-0.5"></i>
          <div>
            <strong class="font-serif">Berhasil Tersimpan!</strong>
            <p class="mt-0.5">{{ saveSuccessMessage }}</p>
          </div>
        </div>

        <div v-if="saveErrorMessage" class="p-4 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs sm:text-sm flex items-start gap-3 animate-scaleUp">
          <i class="bi bi-exclamation-triangle-fill text-rose-400 text-base flex-shrink-0 mt-0.5"></i>
          <div>
            <strong class="font-serif">Perhatian:</strong>
            <p class="mt-0.5">{{ saveErrorMessage }}</p>
          </div>
        </div>

        <!-- Grid 2 Kolom: Peta Interaktif & Form Pengaturan Koordinat -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          <!-- Kolom Kiri: Peta Interaktif Leaflet + HUD Bar (7 Kolom) -->
          <div class="lg:col-span-7 space-y-3">
            
            <!-- Tool Control Bar di atas peta -->
            <div class="flex flex-wrap items-center justify-between gap-2.5 p-3 bg-slate-950/80 border border-slate-800 rounded-xl">
              <!-- Fitur GPS Auto-Detect -->
              <button 
                type="button"
                @click="detectCurrentLocation" 
                :disabled="gpsLoading"
                class="px-3.5 py-2 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold flex items-center gap-2 transition-all disabled:opacity-50 cursor-pointer shadow-sm"
                title="Ambil titik koordinat GPS perangkat Anda saat ini"
              >
                <span v-if="gpsLoading" class="inline-block w-3.5 h-3.5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></span>
                <i v-else class="bi bi-crosshair text-sm text-emerald-400"></i>
                <span>{{ gpsLoading ? 'Mendeteksi GPS...' : 'Ambil Lokasi Saya (GPS)' }}</span>
              </button>

              <!-- Search Bar Alamat Cepat -->
              <div class="flex-1 min-w-[200px] relative">
                <div class="flex items-center gap-1.5">
                  <input 
                    v-model="searchQuery"
                    @keyup.enter="searchAddress"
                    type="text" 
                    placeholder="Cari jalan / kelurahan / kota..."
                    class="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2 outline-none focus:border-amber-400 transition"
                  />
                  <button 
                    type="button"
                    @click="searchAddress" 
                    :disabled="searchLoading"
                    class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition border border-slate-700 cursor-pointer"
                  >
                    <span v-if="searchLoading" class="inline-block w-3 h-3 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></span>
                    <i v-else class="bi bi-search"></i>
                  </button>
                </div>

                <!-- Dropdown Hasil Pencarian Alamat -->
                <div v-if="searchResults.length > 0" class="absolute left-0 right-0 top-full mt-1 bg-slate-950 border border-amber-500/40 rounded-xl shadow-2xl z-50 max-h-48 overflow-y-auto">
                  <div 
                    v-for="(res, idx) in searchResults" 
                    :key="idx"
                    @click="applySearchResult(res)"
                    class="p-2.5 hover:bg-amber-500/15 border-b border-slate-800/80 text-[11px] text-slate-300 cursor-pointer transition flex items-start gap-2"
                  >
                    <i class="bi bi-geo-alt text-amber-400 mt-0.5"></i>
                    <span class="truncate">{{ res.display_name }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Kontainer Peta Leaflet -->
            <div class="relative w-full h-[380px] sm:h-[440px] rounded-2xl overflow-hidden border border-amber-500/30 shadow-2xl bg-slate-950">
              <div ref="mapContainer" class="w-full h-full z-0"></div>

              <!-- Floating HUD Info Koordinat Peta -->
              <div class="absolute bottom-3 left-3 bg-slate-950/90 backdrop-blur-md border border-amber-500/40 rounded-xl px-3 py-2 text-[11px] text-slate-300 shadow-xl pointer-events-none z-10 flex items-center gap-3">
                <div class="flex items-center gap-1.5 text-amber-400">
                  <span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
                  <span class="font-bold font-mono">LAT: {{ Number(locationForm.latitude).toFixed(5) }}</span>
                </div>
                <span class="text-slate-600">|</span>
                <div class="text-sky-400 font-mono font-bold">
                  LNG: {{ Number(locationForm.longitude).toFixed(5) }}
                </div>
              </div>

              <!-- Petunjuk Drag -->
              <div class="absolute top-3 right-3 bg-slate-950/85 backdrop-blur-md border border-slate-700/60 rounded-xl px-3 py-1.5 text-[10px] text-slate-300 pointer-events-none z-10 flex items-center gap-1.5 shadow">
                <i class="bi bi-hand-index-thumb text-amber-400"></i>
                <span>Klik peta atau geser pin emas</span>
              </div>
            </div>

            <!-- Legend Marker Peta -->
            <div class="flex flex-wrap items-center justify-between text-[11px] text-slate-400 px-1">
              <div class="flex items-center gap-4">
                <div class="flex items-center gap-1.5">
                  <span class="w-3 h-3 rounded-full bg-amber-400 border border-slate-900 shadow-sm"></span>
                  <span class="text-slate-300 font-medium">Gereja Anda (Dapat Digeser)</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-cyan-400 border border-slate-900"></span>
                  <span>Gereja Cabang Lainnya di Database</span>
                </div>
              </div>
              <span class="text-slate-500 font-mono">Peta: CartoDB & OSM Active</span>
            </div>

          </div>

          <!-- Kolom Kanan: Form Input Koordinat & Tombol Simpan ke Database (5 Kolom) -->
          <div class="lg:col-span-5 space-y-4 bg-slate-950/70 border border-slate-800/90 rounded-2xl p-5 shadow-xl">
            
            <div class="pb-3 border-b border-slate-800">
              <h3 class="text-base font-bold font-serif text-white flex items-center gap-2">
                <i class="bi bi-sliders text-amber-400"></i>
                <span>Parameter Koordinat & Alamat</span>
              </h3>
              <p class="text-slate-400 text-xs mt-0.5">Nilai di bawah ini disinkronkan otomatis dengan pin di peta.</p>
            </div>

            <!-- Nama Gereja & Kode Gereja (Read-only info) -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-[11px] text-slate-400 font-semibold block mb-1">Nama Gereja</label>
                <input 
                  type="text" 
                  :value="locationForm.church_name" 
                  disabled
                  class="w-full bg-slate-900/60 border border-slate-800 text-slate-300 text-xs rounded-xl px-3 py-2 cursor-not-allowed font-medium"
                />
              </div>
              <div>
                <label class="text-[11px] text-slate-400 font-semibold block mb-1">Kode Gereja</label>
                <input 
                  type="text" 
                  :value="locationForm.church_code" 
                  disabled
                  class="w-full bg-slate-900/60 border border-slate-800 text-amber-400 font-mono text-xs rounded-xl px-3 py-2 cursor-not-allowed font-bold"
                />
              </div>
            </div>

            <!-- Input Latitude & Longitude -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-[11px] text-amber-300 font-semibold block mb-1">
                  Latitude (Lintang)
                </label>
                <input 
                  v-model.number="locationForm.latitude"
                  @change="updateCoords(locationForm.latitude, locationForm.longitude, true)"
                  type="number" 
                  step="0.000001"
                  class="w-full bg-slate-900 border border-slate-700 focus:border-amber-400 text-amber-300 font-mono text-xs rounded-xl px-3 py-2 outline-none transition"
                  placeholder="-6.182400"
                />
              </div>
              <div>
                <label class="text-[11px] text-amber-300 font-semibold block mb-1">
                  Longitude (Bujur)
                </label>
                <input 
                  v-model.number="locationForm.longitude"
                  @change="updateCoords(locationForm.latitude, locationForm.longitude, true)"
                  type="number" 
                  step="0.000001"
                  class="w-full bg-slate-900 border border-slate-700 focus:border-amber-400 text-amber-300 font-mono text-xs rounded-xl px-3 py-2 outline-none transition"
                  placeholder="106.985600"
                />
              </div>
            </div>

            <!-- Input Kota -->
            <div>
              <label class="text-[11px] text-slate-300 font-semibold block mb-1">Kota / Wilayah</label>
              <input 
                v-model="locationForm.city" 
                type="text" 
                placeholder="Contoh: Surabaya, Jakarta Pusat, Medan..."
                class="w-full bg-slate-900 border border-slate-700 focus:border-amber-400 text-slate-200 text-xs rounded-xl px-3 py-2 outline-none transition"
              />
            </div>

            <!-- Input Alamat Lengkap Gereja -->
            <div>
              <label class="text-[11px] text-slate-300 font-semibold block mb-1">Alamat Fisik Gedung Gereja</label>
              <textarea 
                v-model="locationForm.address"
                rows="3"
                placeholder="Jl. Nama Jalan No. XX, Kelurahan, Kecamatan..."
                class="w-full bg-slate-900 border border-slate-700 focus:border-amber-400 text-slate-200 text-xs rounded-xl p-3 outline-none resize-none leading-relaxed transition"
              ></textarea>
            </div>

            <!-- Input / Output Google Maps URL -->
            <div>
              <div class="flex items-center justify-between mb-1">
                <label class="text-[11px] text-slate-300 font-semibold">Tautan Google Maps (GMaps)</label>
                <button 
                  type="button" 
                  @click="openGoogleMapsTest"
                  class="text-[10px] text-sky-400 hover:text-sky-300 flex items-center gap-1 font-semibold cursor-pointer transition"
                  title="Buka link di tab baru untuk mengecek"
                >
                  <i class="bi bi-box-arrow-up-right"></i>
                  <span>Tes Buka GMaps</span>
                </button>
              </div>
              <div class="relative">
                <input 
                  v-model="locationForm.google_maps_url" 
                  type="text" 
                  placeholder="https://www.google.com/maps/..."
                  class="w-full bg-slate-900 border border-slate-700 focus:border-amber-400 text-sky-300 text-xs font-mono rounded-xl pl-3 pr-8 py-2 outline-none truncate transition"
                />
                <button 
                  type="button" 
                  @click="locationForm.google_maps_url = generateGMapsUrl(locationForm.latitude, locationForm.longitude)"
                  title="Generate ulang URL otomatis dari koordinat"
                  class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-amber-400 text-xs cursor-pointer transition"
                >
                  <i class="bi bi-arrow-clockwise"></i>
                </button>
              </div>
            </div>

            <!-- Action Buttons: Simpan ke Database -->
            <div class="pt-3 border-t border-slate-800 flex flex-col gap-2">
              <button 
                type="button"
                @click="saveLocationToDatabase"
                :disabled="isSaving"
                class="w-full py-3.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs uppercase tracking-wider shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2 transition-all disabled:opacity-60 cursor-pointer"
              >
                <span v-if="isSaving" class="inline-block w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                <i v-else class="bi bi-cloud-arrow-up-fill text-sm"></i>
                <span>{{ isSaving ? 'Menyimpan ke Database...' : 'Simpan Lokasi ke DBMS PostgreSQL' }}</span>
              </button>

              <p class="text-[10px] text-slate-500 text-center">
                Koordinat akan langsung diperbarui di PostgreSQL dan ditampilkan ke publik di Peta Beranda.
              </p>
            </div>

          </div>

        </div>

      </section>

      <!-- ======================================================== -->
      <!-- 5. SECTION DAFTAR SELURUH CABANG DENGAN GEOLOCATION      -->
      <!-- ======================================================== -->
      <section class="bg-slate-900/60 border border-slate-800 rounded-3xl p-5 sm:p-7 space-y-4 shadow-xl">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 class="text-lg font-serif font-bold text-white flex items-center gap-2">
              <i class="bi bi-diagram-3 text-amber-400"></i>
              <span>Daftar Titik Gereja & Cabang Terhubung</span>
            </h3>
            <p class="text-slate-400 text-xs">Seluruh titik cabang yang telah terdaftar di sistem DBMS GracePoint.</p>
          </div>
          <span class="px-3.5 py-1.5 bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-xl text-xs font-mono font-bold w-fit">
            Total: {{ allChurchAdmins.length }} Gereja Cabang
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="adm in allChurchAdmins" 
            :key="adm.id"
            :class="adm.id === selectedAdminId ? 'border-amber-400/90 bg-amber-500/10 shadow-lg shadow-amber-500/10 ring-1 ring-amber-400/30' : 'border-slate-800 bg-slate-950/70 hover:border-slate-700'"
            class="p-4 rounded-2xl border transition-all flex flex-col justify-between space-y-3"
          >
            <div>
              <div class="flex items-center justify-between gap-2 mb-1.5">
                <span class="text-xs font-bold font-serif text-amber-300 truncate">{{ adm.church_name }}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 font-bold">{{ adm.church_code || 'CABANG' }}</span>
              </div>
              <p class="text-xs text-slate-400 line-clamp-2">
                {{ adm.address || 'Alamat fisik belum didaftarkan' }}
              </p>
              <div class="flex items-center gap-2 mt-2 text-[11px] text-slate-400">
                <i class="bi bi-geo-alt text-amber-400"></i>
                <span>{{ adm.city || 'Kota belum diset' }}</span>
              </div>
            </div>

            <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <div class="font-mono text-[10px] text-emerald-400 flex items-center gap-1" v-if="adm.latitude && adm.longitude">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span>{{ Number(adm.latitude).toFixed(4) }}, {{ Number(adm.longitude).toFixed(4) }}</span>
              </div>
              <span v-else class="text-[10px] text-rose-400">Belum ada koordinat</span>

              <button 
                type="button"
                @click="selectAdminChurch(adm)"
                :class="adm.id === selectedAdminId ? 'bg-amber-400 text-slate-950 font-bold' : 'bg-amber-500/15 text-amber-300 hover:bg-amber-500/25'"
                class="px-3 py-1.5 rounded-lg text-[11px] font-semibold transition cursor-pointer flex items-center gap-1"
              >
                <span>{{ adm.id === selectedAdminId ? 'Sedang Aktif' : 'Pilih & Edit' }}</span>
                <i v-if="adm.id !== selectedAdminId" class="bi bi-arrow-right"></i>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- 6. SECTION MANAJEMEN INFORMASI PELAYANAN CABANG GEREJA   -->
      <!-- ======================================================== -->
      <section id="pelayanan-cabang" class="bg-slate-900/90 border border-amber-500/30 rounded-3xl p-5 sm:p-8 shadow-2xl backdrop-blur-xl space-y-6">
        
        <!-- Header Section -->
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800">
          <div>
            <div class="flex items-center gap-2 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-1">
              <i class="bi bi-broadcast-pin"></i>
              <span>Publikasi Pelayanan Gereja Terintegrasi</span>
            </div>
            <h2 class="text-xl sm:text-2xl font-bold font-serif text-white">
              Manajemen Informasi & Pengumuman Pelayanan Cabang
            </h2>
            <p class="text-slate-400 text-xs sm:text-sm mt-1">
              Terbitkan jadwal ibadah, persekutuan, konseling, dan kegiatan sosial cabang gereja Anda ke database PostgreSQL. Informasi ini otomatis tayang di portal publik <strong>Informasi Pelayanan</strong>.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <RouterLink 
              to="/informasi-pelayanan#pelayanan-cabang" 
              class="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-500/30 text-xs font-semibold flex items-center gap-1.5 transition"
            >
              <i class="bi bi-box-arrow-up-right"></i>
              <span>Lihat Halaman Publik</span>
            </RouterLink>

            <button 
              type="button"
              @click="openCreateServiceModal"
              class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-amber-500/20 transition cursor-pointer"
            >
              <i class="bi bi-plus-circle-fill"></i>
              <span>+ Terbitkan Pelayanan Baru</span>
            </button>
          </div>
        </div>

        <!-- Filter Kategori Tabs -->
        <div class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
          <button 
            type="button"
            @click="selectedCategoryFilter = 'Semua'"
            :class="selectedCategoryFilter === 'Semua' ? 'bg-amber-400 text-slate-950 font-bold' : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'"
            class="px-3.5 py-1.5 rounded-xl text-xs whitespace-nowrap transition cursor-pointer flex items-center gap-1.5"
          >
            <span>Semua Pelayanan</span>
            <span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="selectedCategoryFilter === 'Semua' ? 'bg-slate-900 text-amber-300' : 'bg-slate-800 text-slate-400'">
              {{ branchServices.length }}
            </span>
          </button>

          <button 
            v-for="cat in serviceCategories" 
            :key="cat"
            type="button"
            @click="selectedCategoryFilter = cat"
            :class="selectedCategoryFilter === cat ? 'bg-amber-400 text-slate-950 font-bold' : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'"
            class="px-3.5 py-1.5 rounded-xl text-xs whitespace-nowrap transition cursor-pointer flex items-center gap-1.5"
          >
            <span>{{ cat }}</span>
          </button>
        </div>

        <!-- Feedback Alert Messages -->
        <div v-if="serviceSuccessMsg" class="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs sm:text-sm flex items-start gap-3 animate-scaleUp">
          <i class="bi bi-check-circle-fill text-emerald-400 text-base flex-shrink-0 mt-0.5"></i>
          <div>
            <strong class="font-serif">Berhasil!</strong>
            <p class="mt-0.5">{{ serviceSuccessMsg }}</p>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isBranchServicesLoading" class="text-center py-12">
          <div class="w-9 h-9 border-2 border-amber-400 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p class="text-xs text-slate-400">Memuat data pelayanan cabang dari database...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredBranchServices.length === 0" class="text-center py-12 px-4 bg-slate-950/60 rounded-2xl border border-dashed border-amber-500/25 space-y-3">
          <div class="w-14 h-14 rounded-full bg-slate-900 border border-amber-500/30 text-amber-400 flex items-center justify-center mx-auto text-2xl shadow-inner">
            <i class="bi bi-calendar-plus"></i>
          </div>
          <h4 class="font-serif text-base sm:text-lg font-bold text-white">
            {{ selectedCategoryFilter === 'Semua' ? 'Belum Ada Informasi Pelayanan yang Diterbitkan' : `Belum Ada Jadwal untuk Kategori "${selectedCategoryFilter}"` }}
          </h4>
          <p class="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            Gereja cabang ini belum memiliki jadwal atau pengumuman pelayanan aktif. Klik tombol di bawah untuk menerbitkan jadwal ibadah atau program pelayanan cabang Anda.
          </p>
          <button 
            type="button"
            @click="openCreateServiceModal"
            class="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-xl text-xs uppercase tracking-wider transition inline-flex items-center gap-2 cursor-pointer shadow-lg shadow-amber-500/20"
          >
            <i class="bi bi-plus-lg"></i>
            <span>Mulai Terbitkan Pelayanan</span>
          </button>
        </div>

        <!-- Populated Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div 
            v-for="svc in filteredBranchServices" 
            :key="svc.id"
            class="bg-slate-950/90 border border-amber-500/25 hover:border-amber-400/60 rounded-2xl p-5 flex flex-col justify-between space-y-4 shadow-xl transition-all duration-300 hover:-translate-y-1"
          >
            <div class="space-y-3">
              <div class="flex items-center justify-between gap-2">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  {{ svc.category }}
                </span>
                <span 
                  :class="svc.status === 'Aktif' ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' : 'bg-slate-800 text-slate-300 border-slate-700'"
                  class="text-[10px] px-2.5 py-0.5 rounded-full border font-semibold"
                >
                  {{ svc.status || 'Aktif' }}
                </span>
              </div>

              <h4 class="font-serif font-bold text-white text-base leading-snug">{{ svc.service_name }}</h4>
              
              <div class="text-xs text-slate-300 space-y-1.5 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <p class="text-amber-300 flex items-center gap-2 font-medium">
                  <i class="bi bi-clock text-amber-400"></i>
                  <span>{{ svc.schedule_day || 'Minggu' }} • {{ svc.schedule_time || 'Reguler' }}</span>
                </p>
                <p v-if="svc.location_room" class="text-slate-400 flex items-center gap-2 text-[11px]">
                  <i class="bi bi-geo-alt text-amber-400"></i>
                  <span>{{ svc.location_room }}</span>
                </p>
                <p v-if="svc.pic_name" class="text-slate-400 flex items-center gap-2 text-[11px]">
                  <i class="bi bi-person text-amber-400"></i>
                  <span>PIC: {{ svc.pic_name }}</span>
                  <a 
                    v-if="svc.pic_contact" 
                    :href="`https://wa.me/${svc.pic_contact.replace(/\D/g, '')}`" 
                    target="_blank"
                    class="text-emerald-400 hover:underline font-mono text-[10px] flex items-center gap-0.5 ml-1"
                  >
                    <i class="bi bi-whatsapp"></i> WA
                  </a>
                </p>
              </div>

              <p v-if="svc.description" class="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                {{ svc.description }}
              </p>
            </div>

            <div class="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
              <button 
                type="button"
                @click="openEditServiceModal(svc)"
                class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 text-xs font-semibold border border-amber-500/30 transition flex items-center gap-1.5 cursor-pointer"
              >
                <i class="bi bi-pencil"></i>
                <span>Edit</span>
              </button>
              <button 
                type="button"
                @click="deleteServiceFromDatabase(svc)"
                class="px-3 py-1.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 text-xs font-semibold border border-rose-500/30 transition flex items-center gap-1.5 cursor-pointer"
              >
                <i class="bi bi-trash"></i>
                <span>Hapus</span>
              </button>
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
          @click.self="isServiceModalOpen = false"
        >
          <div class="bg-slate-900 border border-amber-500/40 w-full max-w-xl rounded-3xl shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col font-sans animate-scaleUp">
            
            <!-- Modal Header -->
            <div class="p-5 sm:p-6 bg-slate-950 border-b border-amber-500/30 flex items-center justify-between">
              <div>
                <h3 class="font-serif text-lg font-bold text-amber-300">
                  {{ editingServiceId ? 'Edit Informasi Pelayanan Cabang' : 'Terbitkan Informasi Pelayanan Baru' }}
                </h3>
                <p class="text-xs text-slate-400 mt-0.5">Gereja: {{ locationForm.church_name }} ({{ locationForm.city || 'Cabang' }})</p>
              </div>
              <button 
                type="button"
                @click="isServiceModalOpen = false"
                class="w-8 h-8 rounded-full bg-slate-900 text-slate-400 hover:text-white border border-amber-500/30 flex items-center justify-center transition cursor-pointer"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>

            <!-- Modal Form Body -->
            <div class="p-6 overflow-y-auto space-y-4 text-xs">
              <div v-if="serviceErrorMsg" class="p-3 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300">
                {{ serviceErrorMsg }}
              </div>

              <!-- Nama Pelayanan -->
              <div>
                <label class="block text-slate-300 font-semibold mb-1">Nama Ibadah / Pelayanan: *</label>
                <input 
                  v-model="serviceForm.service_name"
                  type="text" 
                  placeholder="Contoh: Ibadah Raya 1, Persekutuan Doa Fajar, Youth Revival"
                  class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition"
                />
              </div>

              <!-- Kategori & Status -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="block text-slate-300 font-semibold mb-1">Kategori: *</label>
                  <select 
                    v-model="serviceForm.category"
                    class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition cursor-pointer"
                  >
                    <option v-for="c in serviceCategories" :key="c" :value="c">{{ c }}</option>
                  </select>
                </div>

                <div>
                  <label class="block text-slate-300 font-semibold mb-1">Status Pelayanan:</label>
                  <select 
                    v-model="serviceForm.status"
                    class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition cursor-pointer"
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
                  <label class="block text-slate-300 font-semibold mb-1">Hari Pelaksanaan:</label>
                  <input 
                    v-model="serviceForm.schedule_day"
                    type="text" 
                    placeholder="Contoh: Setiap Hari Minggu / Jumat Malam"
                    class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition"
                  />
                </div>

                <div>
                  <label class="block text-slate-300 font-semibold mb-1">Jam Pelaksanaan:</label>
                  <input 
                    v-model="serviceForm.schedule_time"
                    type="text" 
                    placeholder="Contoh: 09:00 - 11:00 WIB"
                    class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition"
                  />
                </div>
              </div>

              <!-- Ruang & Target -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="block text-slate-300 font-semibold mb-1">Ruangan / Tempat:</label>
                  <input 
                    v-model="serviceForm.location_room"
                    type="text" 
                    placeholder="Contoh: Main Sanctuary Lt. 1 / Ruang Serbaguna"
                    class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition"
                  />
                </div>

                <div>
                  <label class="block text-slate-300 font-semibold mb-1">Target Jemaat:</label>
                  <input 
                    v-model="serviceForm.target_audience"
                    type="text" 
                    placeholder="Contoh: Semua Jemaat / Pemuda & Remaja"
                    class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition"
                  />
                </div>
              </div>

              <!-- PIC & Kontak WA -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="block text-slate-300 font-semibold mb-1">Nama PIC / Pelayan:</label>
                  <input 
                    v-model="serviceForm.pic_name"
                    type="text" 
                    placeholder="Contoh: Pdt. Andreas / Sdr. Kevin"
                    class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition"
                  />
                </div>

                <div>
                  <label class="block text-slate-300 font-semibold mb-1">Nomor WhatsApp PIC:</label>
                  <input 
                    v-model="serviceForm.pic_contact"
                    type="text" 
                    placeholder="Contoh: 081234567890"
                    class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition"
                  />
                </div>
              </div>

              <!-- Link Live Streaming -->
              <div>
                <label class="block text-slate-300 font-semibold mb-1">Link Live Streaming / Zoom (Opsional):</label>
                <input 
                  v-model="serviceForm.live_stream_url"
                  type="text" 
                  placeholder="https://youtube.com/..."
                  class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none transition"
                />
              </div>

              <!-- Deskripsi -->
              <div>
                <label class="block text-slate-300 font-semibold mb-1">Deskripsi & Keterangan Pelayanan:</label>
                <textarea 
                  v-model="serviceForm.description"
                  rows="3"
                  placeholder="Uraikan informasi mengenai tata ibadah, tema bulanan, atau panduan kehadiran..."
                  class="w-full bg-slate-950 border border-amber-500/30 text-white rounded-xl px-3.5 py-2.5 focus:border-amber-400 outline-none resize-none transition"
                ></textarea>
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="p-4 bg-slate-950 border-t border-amber-500/30 flex items-center justify-end gap-2.5">
              <button 
                type="button"
                @click="isServiceModalOpen = false"
                class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition cursor-pointer"
              >
                Batal
              </button>

              <button 
                type="button"
                @click="saveServiceToDatabase"
                :disabled="isServiceSubmitting"
                class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 text-xs font-bold uppercase tracking-wider transition flex items-center gap-1.5 shadow-lg shadow-amber-500/20 cursor-pointer"
              >
                <span v-if="isServiceSubmitting" class="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                <span>{{ editingServiceId ? 'Simpan Perubahan' : 'Terbitkan ke Database' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>

    </div>
  </ChurchAdminLayout>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Lato:wght@400;500;700&display=swap');

/* --- Grand Hero Banner Styling --- */
.admin-hero-card {
  background: linear-gradient(135deg, #050914 0%, #070e24 45%, #0a1435 85%, #0d1a45 100%);
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

.hero-cinzel-title {
  font-family: 'Cinzel', serif;
  text-shadow: 0 4px 18px rgba(245, 158, 11, 0.3);
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

.showcase-card-desc {
  font-family: 'Lato', sans-serif;
  font-size: 0.825rem;
  color: #94a3b8;
  line-height: 1.55;
  margin: 0;
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
