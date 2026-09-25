<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import PetaBerandaLayout from '@/layouts/PetaBerandaLayout.vue'
import { APP_CONFIG } from '@/config'
import { useTheme } from '@/composables/useTheme'

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  },
  churches: {
    type: Array,
    default: () => []
  },
  branches: {
    type: Array,
    default: () => []
  }
})

const route = useRoute()
const router = useRouter()

// Cek apakah halaman diakses langsung sebagai route mandiri
const isStandalonePage = computed(() => {
  return !props.embedded && route.path.startsWith('/peta')
})

// Internal data state jika props tidak disediakan (standalone fetch)
const localChurches = ref([])
const localBranches = ref([])
const isLoadingData = ref(false)

const effectiveChurches = computed(() => {
  return (props.churches && props.churches.length > 0) ? props.churches : localChurches.value
})

const effectiveBranches = computed(() => {
  return (props.branches && props.branches.length > 0) ? props.branches : localBranches.value
})

// --- LEAFLET MAP STATE ---
const mapContainerRef = ref(null)
let leafletMap = null
let churchMarkersGroup = null
let userMarker = null
const markerMap = new Map()

// --- USER GEOLOCATION STATE ---
const userCoords = ref(null) // { lat, lng, accuracy }
const isDetectingLocation = ref(false)
const locationSuccessMessage = ref('')
const locationErrorMessage = ref('')

// --- FILTER & SEARCH STATE ---
const searchQuery = ref('')
const selectedCity = ref('all')
const activeChurchId = ref(null)

// Rumus Haversine untuk hitung jarak akurat (km)
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  if (lat1 === null || lon1 === null || lat2 === null || lon2 === null) return null
  const R = 6371 // radius bumi km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return parseFloat((R * c).toFixed(1))
}

// Koleksi data gereja tergeolokasi dari database
const allGeolocatedChurches = computed(() => {
  const result = []
  const seenCodes = new Set()

  // 1. Dari tabel churches (Gereja Induk / Sinode)
  effectiveChurches.value.forEach(c => {
    if (c.latitude && c.longitude) {
      seenCodes.add(c.church_code)
      const lat = Number(c.latitude)
      const lng = Number(c.longitude)
      const dist = userCoords.value ? calculateDistance(userCoords.value.lat, userCoords.value.lng, lat, lng) : null
      result.push({
        id: `church-${c.id}`,
        dbId: c.id,
        category: 'Gereja Utama',
        name: c.church_name,
        code: c.church_code,
        city: c.city || 'Indonesia',
        address: c.address || 'Alamat terdaftar di DBMS',
        lat,
        lng,
        distance: dist,
        gmapsUrl: c.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`,
        directionsUrl: `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`
      })
    }
  })

  // 2. Dari tabel church_admins (Cabang Pelayanan)
  effectiveBranches.value.forEach(b => {
    if (b.latitude && b.longitude && !seenCodes.has(b.church_code)) {
      const lat = Number(b.latitude)
      const lng = Number(b.longitude)
      const dist = userCoords.value ? calculateDistance(userCoords.value.lat, userCoords.value.lng, lat, lng) : null
      result.push({
        id: `branch-${b.id}`,
        dbId: b.id,
        category: 'Cabang Pelayanan',
        name: b.church_name,
        code: b.church_code,
        city: b.city || 'Cabang',
        address: b.address || 'Alamat cabang terdaftar di DBMS',
        lat,
        lng,
        distance: dist,
        gmapsUrl: b.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`,
        directionsUrl: `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`
      })
    }
  })

  // Jika GPS aktif, urutkan otomatis dari yang terdekat
  if (userCoords.value) {
    result.sort((a, b) => (a.distance ?? 99999) - (b.distance ?? 99999))
  }

  return result
})

// Daftar kota untuk pills filter
const availableCities = computed(() => {
  const cities = new Set()
  allGeolocatedChurches.value.forEach(c => {
    if (c.city) cities.add(c.city.trim())
  })
  return Array.from(cities)
})

// Daftar gereja setelah filter kota & pencarian
const filteredChurches = computed(() => {
  return allGeolocatedChurches.value.filter(c => {
    const matchCity = selectedCity.value === 'all' || 
      (c.city && c.city.toLowerCase() === selectedCity.value.toLowerCase())
    const q = searchQuery.value.toLowerCase().trim()
    const matchQuery = !q || c.name.toLowerCase().includes(q) || (c.city && c.city.toLowerCase().includes(q)) || (c.address && c.address.toLowerCase().includes(q))
    return matchCity && matchQuery
  })
})

// Custom Icon Pin Gereja (Emas untuk Induk, Cyan untuk Cabang)
const createChurchPinIcon = (isMain = true) => {
  const borderCol = isMain ? 'border-amber-400' : 'border-cyan-400'
  const textCol = isMain ? 'text-amber-300' : 'text-cyan-300'
  const pingCol = isMain ? 'bg-amber-400/40' : 'bg-cyan-400/40'

  return L.divIcon({
    className: 'custom-church-pin',
    html: `
      <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-full cursor-pointer hover:scale-115 transition-transform duration-200">
        <span class="absolute w-8 h-8 rounded-full ${pingCol} animate-ping"></span>
        <div class="w-9 h-9 rounded-full bg-slate-950 border-2 ${borderCol} flex items-center justify-center shadow-2xl ${textCol}">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -38]
  })
}

// Custom Icon Pin User GPS
const createUserPinIcon = () => {
  return L.divIcon({
    className: 'custom-user-pin',
    html: `
      <div class="relative flex items-center justify-center -translate-x-1/2 -translate-y-1/2">
        <span class="absolute w-10 h-10 rounded-full bg-sky-500/40 animate-ping"></span>
        <div class="w-5 h-5 rounded-full bg-sky-500 border-2 border-white shadow-xl flex items-center justify-center">
          <span class="w-2 h-2 rounded-full bg-white"></span>
        </div>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -14]
  })
}

// Manajemen Tile Layer Adaptif Tema (Dark / Light)
const { isDark } = useTheme()
let tileLayerInstance = null

const getTileConfig = (dark) => {
  return dark
    ? {
        url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
      }
    : {
        url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
      }
}

const updateMapTile = (dark) => {
  if (!leafletMap) return
  if (tileLayerInstance) {
    leafletMap.removeLayer(tileLayerInstance)
  }
  const config = getTileConfig(dark)
  tileLayerInstance = L.tileLayer(config.url, {
    attribution: config.attribution,
    maxZoom: 19,
    subdomains: 'abcd'
  }).addTo(leafletMap)
}

watch(isDark, (newVal) => {
  updateMapTile(newVal)
})

// Inisialisasi Peta Leaflet dengan Tile Adaptif
const initMap = () => {
  if (!mapContainerRef.value || leafletMap) return

  leafletMap = L.map(mapContainerRef.value, {
    center: [-2.5, 118.0], // Pusat Kepulauan Indonesia
    zoom: 5,
    zoomControl: true,
  })

  updateMapTile(isDark.value)

  churchMarkersGroup = L.layerGroup().addTo(leafletMap)
  renderMarkers()
}

// Render Marker di Peta
const renderMarkers = () => {
  if (!leafletMap || !churchMarkersGroup) return
  churchMarkersGroup.clearLayers()
  markerMap.clear()

  const churches = allGeolocatedChurches.value
  if (churches.length === 0) return

  const bounds = []

  churches.forEach((ch) => {
    const isMain = ch.category === 'Gereja Utama'
    const marker = L.marker([ch.lat, ch.lng], {
      icon: createChurchPinIcon(isMain),
      title: ch.name
    })

    const distHtml = ch.distance !== null 
      ? `<span class="inline-block mt-1 px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded text-[10px] font-semibold font-mono">
           <i class="bi bi-cursor-fill me-1"></i>${ch.distance} km dari Anda
         </span>`
      : ''

    const popupHtml = `
      <div class="p-2 text-xs text-slate-100 max-w-[240px]">
        <span class="text-[9px] uppercase tracking-wider font-bold px-2 py-0.5 rounded ${isMain ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'} inline-block mb-1.5">
          ${ch.category}
        </span>
        <h4 class="font-serif font-bold text-amber-300 text-sm leading-tight mb-1">${ch.name}</h4>
        <p class="text-slate-300 text-[11px] leading-relaxed mb-2">${ch.address}</p>
        <div class="flex items-center gap-1.5 text-slate-400 text-[10px] mb-2 font-mono">
          <i class="bi bi-geo-alt-fill text-amber-400"></i>
          <span>${ch.city} (${ch.lat.toFixed(4)}, ${ch.lng.toFixed(4)})</span>
        </div>
        ${distHtml}
        <div class="pt-2 mt-2 border-t border-slate-700/80 flex items-center gap-2">
          <a 
            href="${ch.directionsUrl}" 
            target="_blank" 
            class="flex-1 py-1.5 px-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-lg text-center text-[10px] uppercase tracking-wider no-underline shadow transition-all block"
          >
            Petunjuk Arah (GMaps) &rarr;
          </a>
        </div>
      </div>
    `

    marker.bindPopup(popupHtml)
    churchMarkersGroup.addLayer(marker)
    bounds.push([ch.lat, ch.lng])
    markerMap.set(ch.id, marker)
  })

  // Fit bounds ke seluruh titik gereja jika belum ada posisi user
  if (bounds.length > 0 && !userCoords.value) {
    leafletMap.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 })
  }
}

// Fokus ke gereja tertentu di peta saat kartu diklik
const focusChurch = (church) => {
  activeChurchId.value = church.id
  if (!leafletMap) return
  leafletMap.flyTo([church.lat, church.lng], 16, { duration: 1.2 })
  const marker = markerMap.get(church.id)
  if (marker) {
    setTimeout(() => {
      marker.openPopup()
    }, 600)
  }
}

// Reset pandangan peta ke seluruh Indonesia
const resetMapBounds = () => {
  if (!leafletMap) return
  const churches = allGeolocatedChurches.value
  if (churches.length > 0) {
    const bounds = churches.map(c => [c.lat, c.lng])
    leafletMap.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 })
  } else {
    leafletMap.setView([-2.5, 118.0], 5)
  }
}

// Deteksi Lokasi Pengguna via Browser GPS
const detectUserLocation = () => {
  if (!navigator.geolocation) {
    locationErrorMessage.value = 'Perangkat atau browser Anda tidak mendukung fitur Geolocation.'
    return
  }

  isDetectingLocation.value = true
  locationErrorMessage.value = ''
  locationSuccessMessage.value = ''

  navigator.geolocation.getCurrentPosition(
    (position) => {
      isDetectingLocation.value = false
      const lat = position.coords.latitude
      const lng = position.coords.longitude
      const acc = position.coords.accuracy ? Math.round(position.coords.accuracy) : null

      userCoords.value = { lat, lng, accuracy: acc }
      locationSuccessMessage.value = `Lokasi Anda terdeteksi via GPS (Akurasi: ±${acc || 10} m). Jarak terdekat ke seluruh gereja telah dihitung!`

      // Buat atau pindahkan user marker
      if (!userMarker && leafletMap) {
        userMarker = L.marker([lat, lng], {
          icon: createUserPinIcon(),
          zIndexOffset: 1000
        }).addTo(leafletMap)
        userMarker.bindPopup(`
          <div class="text-xs p-1 text-slate-900 font-semibold">
            <span class="text-sky-600 block text-sm">Lokasi Anda Saat Ini</span>
            <span class="text-[10px] text-slate-500 font-mono">Akurasi: ±${acc || 10} m</span>
          </div>
        `)
      } else if (userMarker) {
        userMarker.setLatLng([lat, lng])
      }

      // Re-render markers untuk menyertakan info jarak
      renderMarkers()

      // Zoom ke posisi user
      if (leafletMap) {
        leafletMap.flyTo([lat, lng], 13, { duration: 1.2 })
      }
    },
    (err) => {
      isDetectingLocation.value = false
      locationErrorMessage.value = 'Tidak dapat mendeteksi lokasi perangkat. Pastikan izin GPS di browser telah diizinkan.'
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  )
}

// Fetch mandiri jika diakses sebagai halaman terpisah
const fetchStandaloneData = async () => {
  if (props.churches.length > 0 && props.branches.length > 0) return
  isLoadingData.value = true
  try {
    const [resChurches, resBranches] = await Promise.allSettled([
      fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`),
      fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/?limit=200`)
    ])

    if (resChurches.status === 'fulfilled' && resChurches.value.ok) {
      localChurches.value = await resChurches.value.json()
    }
    if (resBranches.status === 'fulfilled' && resBranches.value.ok) {
      localBranches.value = await resBranches.value.json()
    }
  } catch (err) {
    console.error('Gagal mengambil data gereja untuk peta:', err)
  } finally {
    isLoadingData.value = false
    nextTick(() => {
      renderMarkers()
    })
  }
}

watch(allGeolocatedChurches, () => {
  renderMarkers()
})

onMounted(async () => {
  await fetchStandaloneData()
  nextTick(() => {
    initMap()
  })
})

onUnmounted(() => {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
  }
})

// --- STATE MODAL LAPOR KOREKSI & DENAH GEREJA ---
const isReportModalOpen = ref(false)
const isFloorplanModalOpen = ref(false)
const searchInputRef = ref(null)

const reportForm = ref({
  reporterType: 'jemaat', // 'jemaat' | 'admin_gereja'
  churchId: '',
  category: 'koordinat', // 'koordinat' | 'denah' | 'alamat' | 'fasilitas'
  reporterName: '',
  reporterContact: '',
  suggestedCoords: '',
  description: '',
  submitting: false
})

const reportSubmitSuccess = ref(false)
const selectedFloorplanChurchId = ref(null)

const selectedFloorplanChurch = computed(() => {
  if (selectedFloorplanChurchId.value) {
    const found = allGeolocatedChurches.value.find(c => c.id === selectedFloorplanChurchId.value)
    if (found) return found
  }
  return allGeolocatedChurches.value[0] || null
})

const openReportForChurch = (church = null) => {
  if (church) {
    reportForm.value.churchId = church.id
    if (church.lat && church.lng) {
      reportForm.value.suggestedCoords = `${church.lat}, ${church.lng}`
    }
  } else if (!reportForm.value.churchId && allGeolocatedChurches.value.length > 0) {
    reportForm.value.churchId = allGeolocatedChurches.value[0].id
  }
  isReportModalOpen.value = true
}

const openFloorplanForChurch = (church = null) => {
  if (church) {
    selectedFloorplanChurchId.value = church.id
  } else if (!selectedFloorplanChurchId.value && allGeolocatedChurches.value.length > 0) {
    selectedFloorplanChurchId.value = allGeolocatedChurches.value[0].id
  }
  isFloorplanModalOpen.value = true
}

const focusSearchInput = () => {
  if (searchInputRef.value) {
    searchInputRef.value.focus()
    searchInputRef.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const submitReport = () => {
  if (!reportForm.value.churchId || !reportForm.value.description) return
  reportForm.value.submitting = true

  setTimeout(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('gracepoint_map_reports') || '[]')
      saved.unshift({
        id: Date.now(),
        date: new Date().toISOString(),
        churchId: reportForm.value.churchId,
        churchName: allGeolocatedChurches.value.find(c => c.id === reportForm.value.churchId)?.name || 'Gereja',
        category: reportForm.value.category,
        reporterType: reportForm.value.reporterType,
        reporterName: reportForm.value.reporterName || 'Anonim',
        reporterContact: reportForm.value.reporterContact || '-',
        suggestedCoords: reportForm.value.suggestedCoords || '-',
        description: reportForm.value.description
      })
      localStorage.setItem('gracepoint_map_reports', JSON.stringify(saved))
    } catch (e) {
      console.warn('Gagal menyimpan laporan:', e)
    }

    reportForm.value.submitting = false
    reportSubmitSuccess.value = true

    setTimeout(() => {
      reportSubmitSuccess.value = false
      isReportModalOpen.value = false
      reportForm.value.description = ''
      reportForm.value.suggestedCoords = ''
    }, 2500)
  }, 600)
}
</script>

<template>
  <component 
    :is="isStandalonePage ? PetaBerandaLayout : 'div'"
    :total-churches="allGeolocatedChurches.length"
    :is-gps-active="!!userCoords"
    :is-detecting-location="isDetectingLocation"
    @detect-location="detectUserLocation"
    @reset-map="resetMapBounds"
    @open-report-modal="openReportForChurch(null)"
    @open-floorplan-modal="openFloorplanForChurch(null)"
    @focus-search="focusSearchInput"
  >
    
    <!-- SEKSI UTAMA PETA GEOLOCATION -->
    <section id="peta-gereja" class="peta-map-page w-full py-8 sm:py-14 px-3 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6 sm:space-y-8">
      
      <!-- Section Header -->
      <div class="text-center max-w-3xl mx-auto space-y-3">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs uppercase tracking-widest font-semibold">
          <i class="bi bi-geo-alt-fill text-amber-400"></i>
          <span>Fitur Geolocation Real-Time & GMaps</span>
        </div>
        <h2 class="text-2xl sm:text-4xl font-serif font-bold text-white tracking-wide">
          Temukan Letak & Lokasi Pasti Gereja
        </h2>
        <p class="text-slate-400 text-xs sm:text-sm leading-relaxed">
          Peta interaktif terhubung langsung ke database DBMS PostgreSQL. Admin gereja telah menandai titik koordinat mereka, memudahkan jemaat mengetahui lokasi pasti serta petunjuk arah navigasi Google Maps secara real-time.
        </p>
      </div>

      <!-- Control Toolbar: GPS Button, Pencarian, & Reset Peta -->
      <div class="p-3.5 sm:p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-md flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 sm:gap-4">
        
        <!-- Tombol Deteksi Lokasi GPS Pengguna -->
        <div class="flex items-center gap-2 flex-wrap sm:flex-nowrap">
          <button 
            type="button"
            @click="detectUserLocation"
            :disabled="isDetectingLocation"
            class="px-3.5 sm:px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50 cursor-pointer"
            title="Deteksi posisi Anda untuk mengurutkan gereja terdekat"
          >
            <span v-if="isDetectingLocation" class="inline-block w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
            <i v-else class="bi bi-crosshair text-sm"></i>
            <span>{{ isDetectingLocation ? 'Mendeteksi Posisi...' : 'Deteksi Lokasi Saya (GPS)' }}</span>
          </button>

          <button 
            type="button"
            @click="resetMapBounds"
            class="px-3 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer"
            title="Tampilkan seluruh peta Indonesia"
          >
            <i class="bi bi-arrows-fullscreen text-amber-400"></i>
            <span class="hidden sm:inline">Reset Peta</span>
          </button>

          <span v-if="userCoords" class="inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 rounded-xl text-xs font-mono">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>GPS Aktif</span>
          </span>
        </div>

        <!-- Input Pencarian Cepat Gereja -->
        <div class="flex-1 max-w-md relative">
          <i class="bi bi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
          <input 
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            placeholder="Cari nama gereja, jalan, atau kota..."
            class="w-full bg-slate-950 border border-slate-700/80 focus:border-amber-400 text-slate-200 text-xs rounded-xl pl-9 pr-8 py-2.5 outline-none transition"
          />
          <button 
            v-if="searchQuery"
            @click="searchQuery = ''"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 text-xs cursor-pointer"
          >
            <i class="bi bi-x-circle-fill"></i>
          </button>
        </div>

      </div>

      <!-- Feedback GPS Alert Message -->
      <div v-if="locationSuccessMessage" class="p-3.5 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs flex items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <i class="bi bi-check-circle-fill text-emerald-400"></i>
          <span>{{ locationSuccessMessage }}</span>
        </div>
        <button @click="locationSuccessMessage = ''" class="text-emerald-400 hover:text-emerald-200 font-bold cursor-pointer">&times;</button>
      </div>

      <div v-if="locationErrorMessage" class="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs flex items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <i class="bi bi-exclamation-circle-fill text-rose-400"></i>
          <span>{{ locationErrorMessage }}</span>
        </div>
        <button @click="locationErrorMessage = ''" class="text-rose-400 hover:text-rose-200 font-bold cursor-pointer">&times;</button>
      </div>

      <!-- Filter Pills Kota -->
      <div class="flex items-center gap-2 overflow-x-auto pb-1 custom-scrollbar text-xs">
        <span class="text-slate-400 font-semibold flex items-center gap-1.5 flex-shrink-0">
          <i class="bi bi-funnel text-amber-400"></i> Filter Kota:
        </span>
        <button 
          @click="selectedCity = 'all'"
          :class="selectedCity === 'all' ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20' : 'bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800'"
          class="px-3 py-1.5 rounded-lg transition flex-shrink-0 cursor-pointer"
        >
          Semua Wilayah ({{ allGeolocatedChurches.length }})
        </button>
        <button 
          v-for="city in availableCities" 
          :key="city"
          @click="selectedCity = city"
          :class="selectedCity === city ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20' : 'bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800'"
          class="px-3 py-1.5 rounded-lg transition flex-shrink-0 cursor-pointer"
        >
          {{ city }}
        </button>
      </div>

      <!-- Kontainer Utama: Peta Interaktif (Kiri) & Daftar Gereja Terdekat (Kanan) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- PETA LEAFLET INTERAKTIF (8 Kolom) -->
        <div class="lg:col-span-8 bg-slate-900/90 border border-amber-500/30 rounded-2xl overflow-hidden shadow-2xl relative">
          
          <div class="relative w-full h-[400px] sm:h-[520px] bg-slate-950">
            <div ref="mapContainerRef" class="w-full h-full z-0"></div>

            <!-- Floating HUD Kiri Bawah -->
            <div class="absolute bottom-3 left-3 bg-slate-950/85 backdrop-blur-md border border-amber-500/40 rounded-xl px-3 py-2 text-[10px] sm:text-[11px] text-slate-300 shadow-xl pointer-events-none z-10 flex items-center gap-2 sm:gap-3">
              <div class="flex items-center gap-1.5 text-amber-400">
                <span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
                <span class="font-bold">{{ allGeolocatedChurches.length }} Titik di DBMS</span>
              </div>
              <span class="text-slate-600">|</span>
              <span class="text-slate-400">Live PostgreSQL Sync</span>
            </div>

            <!-- Floating Legend Kanan Atas -->
            <div class="absolute top-3 right-3 bg-slate-950/85 backdrop-blur-md border border-slate-700/80 rounded-xl p-2 sm:p-2.5 text-[9px] sm:text-[10px] text-slate-300 pointer-events-none z-10 space-y-1 shadow-lg">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                <span>Gereja Induk / Sinode</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                <span>Cabang Pelayanan</span>
              </div>
              <div v-if="userCoords" class="flex items-center gap-2 text-sky-400">
                <span class="w-2.5 h-2.5 rounded-full bg-sky-400 animate-ping"></span>
                <span class="font-bold">Lokasi Anda</span>
              </div>
            </div>
          </div>

        </div>

        <!-- DAFTAR GEREJA TERDEKAT & PETUNJUK ARAH (4 Kolom) -->
        <div id="daftar-rute" class="lg:col-span-4 bg-slate-800/90 border border-slate-800 rounded-2xl p-4 sm:p-5 shadow-2xl flex flex-col h-[420px] sm:h-[520px]">
          
          <!-- Header Daftar -->
          <div class="pb-3 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h3 class="text-sm font-serif font-bold text-white flex items-center gap-2">
                <i class="bi bi-buildings text-amber-400"></i>
                <span>Daftar Gereja & Rute</span>
              </h3>
              <p class="text-[11px] text-slate-400 mt-0.5">
                {{ userCoords ? 'Diurutkan berdasarkan jarak terdekat dari Anda' : 'Klik kartu untuk memperbesar titik pada peta' }}
              </p>
            </div>
            <span class="px-2 py-0.5 rounded bg-slate-800 text-amber-400 font-mono text-xs font-bold">
              {{ filteredChurches.length }}
            </span>
          </div>

          <!-- List Scrollable Gereja -->
          <div class="flex-1 overflow-y-auto space-y-3 py-3 pr-1 custom-scrollbar">
            
            <div v-if="filteredChurches.length === 0" class="p-6 text-center text-slate-500 text-xs">
              <i class="bi bi-search text-2xl block mb-2 text-slate-600"></i>
              <span>Tidak ada gereja yang sesuai dengan filter atau pencarian Anda.</span>
            </div>

            <div 
              v-for="church in filteredChurches" 
              :key="church.id"
              :class="activeChurchId === church.id ? 'border-amber-400 bg-amber-500/10' : 'border-slate-800/80 bg-slate-950/60'"
              class="p-3.5 rounded-xl border transition-all hover:border-amber-500/40 space-y-2.5"
            >
              <div class="flex items-start justify-between gap-2">
                <div>
                  <span 
                    :class="church.category === 'Gereja Utama' ? 'bg-amber-500/15 text-amber-300 border-amber-500/30' : 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'"
                    class="text-[9px] uppercase tracking-wider font-bold px-2 py-0.5 rounded border inline-block mb-1"
                  >
                    {{ church.category }}
                  </span>
                  <h4 class="text-xs font-bold text-slate-100 line-clamp-1 hover:text-amber-300 transition cursor-pointer" @click="focusChurch(church)">
                    {{ church.name }}
                  </h4>
                </div>

                <!-- Distance Badge (Jika GPS Terdeteksi) -->
                <span 
                  v-if="church.distance !== null" 
                  class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono font-bold flex items-center gap-1 flex-shrink-0"
                >
                  <i class="bi bi-cursor-fill text-[9px]"></i>
                  <span>{{ church.distance }} km</span>
                </span>
              </div>

              <!-- Alamat & Kota -->
              <p class="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                {{ church.address }}
              </p>

              <div class="flex items-center gap-1.5 text-[10px] text-slate-500 font-mono">
                <i class="bi bi-geo-alt text-amber-400"></i>
                <span>{{ church.city }}</span>
              </div>

              <!-- Action Buttons: Fokus Peta & Buka Google Maps -->
              <div class="pt-2 border-t border-slate-800/80 flex items-center gap-2">
                <button 
                  type="button"
                  @click="focusChurch(church)"
                  class="flex-1 py-1.5 px-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-[11px] font-semibold text-center transition cursor-pointer flex items-center justify-center gap-1"
                >
                  <i class="bi bi-pin-map text-amber-400"></i>
                  <span>Fokus di Peta</span>
                </button>

                <a 
                  :href="church.directionsUrl" 
                  target="_blank"
                  class="flex-1 py-1.5 px-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-lg text-[11px] text-center no-underline transition shadow flex items-center justify-center gap-1"
                  title="Buka rute langsung di Google Maps"
                >
                  <i class="bi bi-arrow-up-right-square"></i>
                  <span>Rute GMaps</span>
                </a>
              </div>

            </div>

          </div>

          <!-- Bottom Footer Status -->
          <div class="pt-2.5 border-t border-slate-800 text-center text-[10px] text-slate-500">
            Peta Geolocation GracePoint &copy; 2026
          </div>

        </div>

      </div>

    </section>

    <!-- ═══════════════════════════════════════════════════════════════════════
         MODAL 1: LAPOR KOREKSI TITIK KOORDINAT & USULAN DENAH GEREJA
         (Mewadahi laporan dari user / admin gereja yang merancangnya)
         ═══════════════════════════════════════════════════════════════════════ -->
    <Transition name="fade">
      <div 
        v-if="isReportModalOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md overflow-y-auto"
        @click.self="isReportModalOpen = false"
      >
        <div class="bg-slate-900 border border-amber-500/40 rounded-2xl max-w-xl w-full p-5 sm:p-7 shadow-2xl space-y-5 my-8">
          
          <!-- Modal Header -->
          <div class="flex items-start justify-between border-b border-slate-800 pb-3.5">
            <div>
              <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-semibold uppercase tracking-wider mb-1">
                <i class="bi bi-shield-check text-amber-400"></i>
                <span>Partisipasi Data Akurat</span>
              </div>
              <h3 class="font-serif font-bold text-lg sm:text-xl text-white">
                Lapor Koreksi Titik &amp; Denah Gereja
              </h3>
              <p class="text-xs text-slate-400 mt-1">
                Bantu kami menjaga akurasi koordinat GPS dan denah tata ruang gedung gereja di seluruh Indonesia.
              </p>
            </div>
            <button 
              type="button"
              @click="isReportModalOpen = false" 
              class="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer text-xl"
            >
              &times;
            </button>
          </div>

          <!-- Alert Sukses Kirim Laporan -->
          <div v-if="reportSubmitSuccess" class="p-4 rounded-xl bg-emerald-500/20 border border-emerald-500/50 text-emerald-200 text-xs space-y-1 animate__animated animate__fadeIn">
            <div class="flex items-center gap-2 font-bold text-emerald-300">
              <i class="bi bi-check-circle-fill text-base"></i>
              <span>Laporan Berhasil Terkirim &amp; Tersimpan!</span>
            </div>
            <p class="text-[11px] leading-relaxed text-emerald-100/90">
              Terima kasih atas kontribusi Anda. Laporan akan ditinjau oleh tim verifikator DBMS dan admin gereja bersangkutan untuk pembaruan peta dan denah resmi.
            </p>
          </div>

          <!-- Form Input Laporan -->
          <form v-else @submit.prevent="submitReport" class="space-y-4">
            
            <!-- Pilih Peran Pelapor: Jemaat vs Admin Gereja -->
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-slate-300 block">Status Pelapor:</label>
              <div class="grid grid-cols-2 gap-2">
                <label 
                  :class="reportForm.reporterType === 'jemaat' ? 'bg-amber-500/20 border-amber-500/60 text-amber-200' : 'bg-slate-950 border-slate-800 text-slate-400'"
                  class="p-2.5 rounded-xl border flex items-center gap-2 cursor-pointer transition text-xs"
                >
                  <input type="radio" v-model="reportForm.reporterType" value="jemaat" class="hidden">
                  <i class="bi bi-person text-sm text-amber-400"></i>
                  <div>
                    <span class="font-bold block">Jemaat / Pengunjung</span>
                    <span class="text-[10px] opacity-75">Melaporkan ketidaksesuaian</span>
                  </div>
                </label>

                <label 
                  :class="reportForm.reporterType === 'admin_gereja' ? 'bg-cyan-500/20 border-cyan-500/60 text-cyan-200' : 'bg-slate-950 border-slate-800 text-slate-400'"
                  class="p-2.5 rounded-xl border flex items-center gap-2 cursor-pointer transition text-xs"
                >
                  <input type="radio" v-model="reportForm.reporterType" value="admin_gereja" class="hidden">
                  <i class="bi bi-building-gear text-sm text-cyan-400"></i>
                  <div>
                    <span class="font-bold block">Admin Gereja Resmi</span>
                    <span class="text-[10px] opacity-75">Perancang / Pengelola Denah</span>
                  </div>
                </label>
              </div>
            </div>

            <!-- Jika Admin Gereja: Tampilkan Pintasan ke Portal Admin -->
            <div v-if="reportForm.reporterType === 'admin_gereja'" class="p-3 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-cyan-200 text-xs flex items-center justify-between gap-3">
              <div class="flex items-center gap-2">
                <i class="bi bi-info-circle text-cyan-400 text-sm shrink-0"></i>
                <span class="text-[11px]">Sebagai admin gereja terverifikasi, Anda dapat langsung mengedit koordinat &amp; denah di dashboard Anda.</span>
              </div>
              <RouterLink 
                to="/verification-login" 
                class="px-2.5 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-[10px] uppercase tracking-wider shrink-0 transition"
              >
                Masuk Portal
              </RouterLink>
            </div>

            <!-- Pilihan Gereja Terdaftar -->
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-slate-300 block">Gereja yang Dilaporkan / Dikelola: <span class="text-rose-400">*</span></label>
              <select 
                v-model="reportForm.churchId"
                required
                class="w-full bg-slate-950 border border-slate-700/80 focus:border-amber-400 text-slate-200 text-xs rounded-xl px-3 py-2.5 outline-none transition"
              >
                <option value="" disabled>-- Pilih salah satu gereja dari database --</option>
                <option v-for="c in allGeolocatedChurches" :key="c.id" :value="c.id">
                  {{ c.name }} ({{ c.city }}) — {{ c.category }}
                </option>
              </select>
            </div>

            <!-- Kategori Laporan -->
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-slate-300 block">Kategori Pembaruan / Koreksi: <span class="text-rose-400">*</span></label>
              <select 
                v-model="reportForm.category"
                required
                class="w-full bg-slate-950 border border-slate-700/80 focus:border-amber-400 text-slate-200 text-xs rounded-xl px-3 py-2.5 outline-none transition"
              >
                <option value="koordinat">📍 Koreksi Titik Koordinat GPS / Posisi Peta</option>
                <option value="denah">🏛️ Usulan / Pembaruan Denah &amp; Tata Ruang Gedung</option>
                <option value="alamat">🏢 Koreksi Alamat Lengkap &amp; Petunjuk Jalan</option>
                <option value="fasilitas">♿ Pembaruan Fasilitas (Parkir, Ramp Disabilitas, Ruang Anak)</option>
                <option value="lainnya">📝 Koreksi Lainnya</option>
              </select>
            </div>

            <!-- Koordinat Rekomendasi (Opsional) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <label class="text-xs font-semibold text-slate-300 block">Koordinat Baru (Latitude, Longitude):</label>
                <input 
                  v-model="reportForm.suggestedCoords"
                  type="text"
                  placeholder="Contoh: -6.2088, 106.8456"
                  class="w-full bg-slate-950 border border-slate-700/80 focus:border-amber-400 text-slate-200 text-xs rounded-xl px-3 py-2 outline-none font-mono transition"
                />
              </div>

              <div class="space-y-1.5">
                <label class="text-xs font-semibold text-slate-300 block">Nama Anda / Jabatan di Gereja:</label>
                <input 
                  v-model="reportForm.reporterName"
                  type="text"
                  placeholder="Nama pelapor..."
                  class="w-full bg-slate-950 border border-slate-700/80 focus:border-amber-400 text-slate-200 text-xs rounded-xl px-3 py-2 outline-none transition"
                />
              </div>
            </div>

            <!-- Deskripsi / Catatan Perbaikan -->
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-slate-300 block">Rincian Koreksi / Usulan Perancangan Denah: <span class="text-rose-400">*</span></label>
              <textarea 
                v-model="reportForm.description"
                rows="3"
                required
                placeholder="Jelaskan detail letak yang tepat, tata ruang ibadah, pintu masuk utama, kapasitas balkon, atau perubahan denah terkini..."
                class="w-full bg-slate-950 border border-slate-700/80 focus:border-amber-400 text-slate-200 text-xs rounded-xl p-3 outline-none transition leading-relaxed"
              ></textarea>
            </div>

            <!-- Action Buttons -->
            <div class="pt-2 flex items-center justify-end gap-3 border-t border-slate-800">
              <button 
                type="button"
                @click="isReportModalOpen = false" 
                class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition cursor-pointer"
              >
                Batal
              </button>
              <button 
                type="submit"
                :disabled="reportForm.submitting"
                class="px-5 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs uppercase tracking-wider transition shadow-lg shadow-amber-500/20 disabled:opacity-50 cursor-pointer flex items-center gap-2"
              >
                <span v-if="reportForm.submitting" class="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
                <span>{{ reportForm.submitting ? 'Mengirim...' : 'Kirim Laporan' }}</span>
              </button>
            </div>

          </form>

        </div>
      </div>
    </Transition>

    <!-- ═══════════════════════════════════════════════════════════════════════
         MODAL 2: VIEWER DENAH & TATA RUANG FASILITAS GEDUNG GEREJA
         ═══════════════════════════════════════════════════════════════════════ -->
    <Transition name="fade">
      <div 
        v-if="isFloorplanModalOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md overflow-y-auto"
        @click.self="isFloorplanModalOpen = false"
      >
        <div class="bg-slate-900 border border-cyan-500/40 rounded-2xl max-w-2xl w-full p-5 sm:p-7 shadow-2xl space-y-5 my-8">
          
          <!-- Modal Header -->
          <div class="flex items-start justify-between border-b border-slate-800 pb-3.5">
            <div>
              <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 text-[10px] font-semibold uppercase tracking-wider mb-1">
                <i class="bi bi-diagram-3 text-cyan-400"></i>
                <span>Tata Ruang &amp; Arsitektur Pelayanan</span>
              </div>
              <h3 class="font-serif font-bold text-lg sm:text-xl text-white">
                Denah Gedung Gereja &amp; Fasilitas
              </h3>
              <p class="text-xs text-slate-400 mt-1">
                Visualisasi denah ruangan ibadah, jalur evakuasi keselamatan, dan area pastoral.
              </p>
            </div>
            <button 
              type="button"
              @click="isFloorplanModalOpen = false" 
              class="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer text-xl"
            >
              &times;
            </button>
          </div>

          <!-- Selector Gereja untuk Denah -->
          <div class="flex items-center gap-3">
            <label class="text-xs font-semibold text-slate-300 shrink-0">Pilih Gereja:</label>
            <select 
              v-model="selectedFloorplanChurchId"
              class="flex-1 bg-slate-950 border border-slate-700/80 focus:border-cyan-400 text-slate-200 text-xs rounded-xl px-3 py-2 outline-none transition"
            >
              <option v-for="c in allGeolocatedChurches" :key="c.id" :value="c.id">
                {{ c.name }} ({{ c.city }})
              </option>
            </select>
          </div>

          <!-- Denah Schematic Visualization Box -->
          <div v-if="selectedFloorplanChurch" class="space-y-4">
            
            <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div class="flex items-center justify-between text-xs pb-2 border-b border-slate-800">
                <div class="flex items-center gap-2">
                  <i class="bi bi-building text-amber-400"></i>
                  <strong class="text-white">{{ selectedFloorplanChurch.name }}</strong>
                </div>
                <span class="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] font-mono">
                  Denah Standar Tata Ruang
                </span>
              </div>

              <!-- Schematic Interactive Blueprint Box -->
              <div class="w-full bg-slate-900 border border-cyan-500/30 rounded-xl p-4 relative overflow-hidden font-mono text-[11px] text-slate-300">
                
                <!-- Background Grid Blueprint Accent -->
                <div class="absolute inset-0 bg-[radial-gradient(#0284c7_1px,transparent_1px)] [background-size:16px_16px] opacity-15 pointer-events-none"></div>

                <div class="relative z-10 space-y-3">
                  
                  <!-- Area Mimbar & Altar -->
                  <div class="p-3 rounded-lg bg-amber-500/15 border border-amber-500/40 text-center text-amber-200 font-bold">
                    <span class="block text-xs uppercase tracking-wider text-amber-300">✝ Altar &amp; Mimbar Utama</span>
                    <span class="text-[10px] font-normal text-amber-300/80">Ruang Musik • Sound System • Multimedia</span>
                  </div>

                  <!-- Ruang Ibadah Utama (Nave / Sanctuary) -->
                  <div class="p-4 rounded-lg bg-slate-800/80 border border-slate-700 text-center space-y-2">
                    <div class="font-bold text-white uppercase tracking-wider">Sanctuary / Ruang Ibadah Utama</div>
                    <div class="flex justify-center gap-2 text-[10px] text-slate-400">
                      <span>[Baris Kursi Sisi Kiri]</span>
                      <span class="text-cyan-400 font-bold">| Lorong Tengah |</span>
                      <span>[Baris Kursi Sisi Kanan]</span>
                    </div>
                    <div class="pt-2 border-t border-slate-700/60 flex justify-around text-[10px] text-slate-400">
                      <span>Kapasitas: ±400 - 800 Jemaat</span>
                      <span>Pendingin Ruangan (AC)</span>
                      <span>Balkon Lantai 2</span>
                    </div>
                  </div>

                  <!-- Ruang Pelayanan Pendukung (Grid 3 Kolom) -->
                  <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-center text-[10px]">
                    <div class="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700">
                      <span class="block font-bold text-cyan-300">Ruang Pastoral</span>
                      <span class="text-slate-400">Konseling &amp; Ruang Doa</span>
                    </div>
                    <div class="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700">
                      <span class="block font-bold text-emerald-300">Sekolah Minggu</span>
                      <span class="text-slate-400">Kelas Anak &amp; Nursery</span>
                    </div>
                    <div class="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700">
                      <span class="block font-bold text-slate-200">Fasilitas Toilet</span>
                      <span class="text-slate-400">Pria, Wanita, Disabilitas</span>
                    </div>
                  </div>

                  <!-- Pintu Masuk, Jalur Evakuasi & Parkir -->
                  <div class="p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-500/40 flex flex-wrap items-center justify-between gap-2 text-[10px]">
                    <div class="flex items-center gap-1.5 text-emerald-300">
                      <i class="bi bi-door-open-fill"></i>
                      <span>Pintu Masuk Utama (Foyer)</span>
                    </div>
                    <div class="flex items-center gap-1.5 text-rose-400">
                      <i class="bi bi-shield-exclamation"></i>
                      <span>Jalur Evakuasi Darurat (Emergency Exit)</span>
                    </div>
                    <div class="flex items-center gap-1.5 text-amber-300">
                      <i class="bi bi-p-square-fill"></i>
                      <span>Area Parkir Mobil &amp; Motor</span>
                    </div>
                  </div>

                </div>

              </div>

              <!-- Catatan Denah -->
              <p class="text-[11px] text-slate-400 leading-relaxed">
                <i class="bi bi-info-circle text-cyan-400 mr-1"></i>
                Setiap admin gereja dapat mengunggah denah arsitektur resmi yang lebih rinci (blueprint tata ruang, instalasi multimedia, dan protokol keselamatan kebakaran) langsung melalui dashboard admin gereja.
              </p>
            </div>

            <!-- Tombol Aksi di Bawah Denah -->
            <div class="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800">
              <button 
                type="button"
                @click="openReportForChurch(selectedFloorplanChurch); isFloorplanModalOpen = false"
                class="px-3.5 py-2 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/40 text-amber-300 text-xs font-semibold transition cursor-pointer flex items-center gap-1.5"
              >
                <i class="bi bi-pencil-square"></i>
                <span>Laporkan Ketidaksesuaian Denah Ini</span>
              </button>

              <RouterLink 
                to="/verification-login"
                class="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs uppercase tracking-wider transition shadow cursor-pointer flex items-center gap-1.5"
              >
                <i class="bi bi-gear-fill"></i>
                <span>Rancang / Perbarui Denah (Admin Gereja)</span>
              </RouterLink>
            </div>

          </div>

        </div>
      </div>
    </Transition>

  </component>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Playfair+Display:wght@600;700&display=swap');

.font-serif {
  font-family: 'Cinzel', 'Playfair Display', Georgia, serif;
}

.peta-map-page {
  background-color: var(--theme-bg-primary);
  color: var(--theme-text-primary);
}

/* Override utility colors that are intentionally dark in the map's dark palette. */
:global(html[data-theme="light"]) .peta-map-page [class*="bg-slate-900"],
:global(html[data-theme="light"]) .peta-map-page [class*="bg-slate-950"] {
  background-color: var(--theme-bg-card) !important;
}

:global(html[data-theme="light"]) .peta-map-page [class*="border-slate-800"],
:global(html[data-theme="light"]) .peta-map-page [class*="border-slate-700"] {
  border-color: var(--theme-border-soft) !important;
}

:global(html[data-theme="light"]) .peta-map-page [class~="text-white"],
:global(html[data-theme="light"]) .peta-map-page [class~="text-slate-100"],
:global(html[data-theme="light"]) .peta-map-page [class~="text-slate-200"] {
  color: var(--theme-text-primary) !important;
}

:global(html[data-theme="light"]) .peta-map-page [class~="text-slate-300"] {
  color: var(--theme-text-secondary) !important;
}

:global(html[data-theme="light"]) .peta-map-page [class~="text-slate-400"],
:global(html[data-theme="light"]) .peta-map-page [class~="text-slate-500"] {
  color: var(--theme-text-muted) !important;
}

:global(html[data-theme="light"]) .peta-map-page [class~="text-slate-950"] {
  color: var(--theme-text-inverse) !important;
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.35);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(245, 158, 11, 0.6);
}

/* Custom Leaflet Dark Popup Styles */
:deep(.leaflet-popup-content-wrapper) {
  background: #090f22 !important;
  color: #f1f5f9 !important;
  border: 1px solid rgba(245, 158, 11, 0.45) !important;
  border-radius: 14px !important;
  box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.75) !important;
  padding: 2px !important;
}

:deep(.leaflet-popup-tip) {
  background: #090f22 !important;
  border: 1px solid rgba(245, 158, 11, 0.45) !important;
}

:deep(.leaflet-popup-close-button) {
  color: #94a3b8 !important;
  padding: 6px 8px 0 0 !important;
}
:deep(.leaflet-popup-close-button:hover) {
  color: #f59e0b !important;
}

:global(html[data-theme="light"]) .peta-map-page :deep(.leaflet-popup-content-wrapper),
:global(html[data-theme="light"]) .peta-map-page :deep(.leaflet-popup-tip) {
  background: var(--theme-bg-surface) !important;
  color: var(--theme-text-primary) !important;
  border-color: var(--theme-border) !important;
}

:global(html[data-theme="light"]) .peta-map-page :deep(.leaflet-popup-content .text-slate-100),
:global(html[data-theme="light"]) .peta-map-page :deep(.leaflet-popup-content .text-slate-300),
:global(html[data-theme="light"]) .peta-map-page :deep(.leaflet-popup-content .text-slate-400) {
  color: var(--theme-text-secondary) !important;
}
</style>