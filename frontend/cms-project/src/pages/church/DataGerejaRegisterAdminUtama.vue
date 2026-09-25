<script setup>
import { nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { apiFetch } from '@/services/api'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()
const isSubmitting = ref(false)
const showSuccessModal = ref(false)
const errorMessage = ref('')

const mapContainer = ref(null)
let leafletMap = null
let churchMarker = null
const isLocating = ref(false)
const locationFeedback = ref('')

// ── Map Search ──
const mapSearchQuery = ref('')
const isSearching = ref(false)
const searchError = ref('')

// Parses lat/lng from various Google Maps URL formats
const parseGoogleMapsUrl = (url) => {
  try {
    // Format: @lat,lng  (most common)
    const atMatch = url.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/)
    if (atMatch) return { lat: parseFloat(atMatch[1]), lng: parseFloat(atMatch[2]) }

    // Format: query=lat,lng  (search/share link)
    const queryMatch = url.match(/[?&]query=(-?\d+\.\d+),(-?\d+\.\d+)/)
    if (queryMatch) return { lat: parseFloat(queryMatch[1]), lng: parseFloat(queryMatch[2]) }

    // Format: ll=lat,lng
    const llMatch = url.match(/[?&]ll=(-?\d+\.\d+),(-?\d+\.\d+)/)
    if (llMatch) return { lat: parseFloat(llMatch[1]), lng: parseFloat(llMatch[2]) }

    // Format: place link with !3d and !4d
    const d3Match = url.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/)
    if (d3Match) return { lat: parseFloat(d3Match[1]), lng: parseFloat(d3Match[2]) }
  } catch {}
  return null
}

// Search by address text (Nominatim) or Google Maps URL
const searchLocation = async () => {
  const query = mapSearchQuery.value.trim()
  if (!query) return

  searchError.value = ''
  isSearching.value = true
  locationFeedback.value = 'Mencari lokasi...'

  // 1️⃣ Coba parsing sebagai Google Maps URL
  if (query.includes('google.com/maps') || query.includes('goo.gl/maps') || query.includes('maps.app.goo.gl')) {
    const parsed = parseGoogleMapsUrl(query)
    if (parsed) {
      updateCoordinates(parsed.lat, parsed.lng, true)
      if (leafletMap) leafletMap.setView([parsed.lat, parsed.lng], 16)
      locationFeedback.value = `✅ Titik dari Google Maps URL: (${parsed.lat.toFixed(5)}, ${parsed.lng.toFixed(5)})`
      isSearching.value = false
      setTimeout(() => { if (locationFeedback.value.startsWith('✅')) locationFeedback.value = '' }, 5000)
      return
    } else {
      searchError.value = 'URL Google Maps tidak mengandung koordinat yang dapat dibaca. Coba salin URL dari bilah alamat browser saat membuka Google Maps.'
      isSearching.value = false
      locationFeedback.value = ''
      return
    }
  }

  // 2️⃣ Geocoding teks alamat via Nominatim (OpenStreetMap, free, no API key)
  try {
    const params = new URLSearchParams({ q: query, format: 'json', limit: '1', addressdetails: '1' })
    const res = await fetch(`https://nominatim.openstreetmap.org/search?${params}`, {
      headers: { 'Accept-Language': 'id,en', 'User-Agent': 'GracePointCMS/1.0' }
    })
    const data = await res.json()
    if (!data || data.length === 0) {
      searchError.value = `Alamat "${query}" tidak ditemukan. Coba tambahkan nama kota atau detail lebih lengkap.`
      locationFeedback.value = ''
      return
    }
    const { lat, lon, display_name } = data[0]
    const numLat = parseFloat(lat)
    const numLon = parseFloat(lon)
    updateCoordinates(numLat, numLon, true)
    if (leafletMap) leafletMap.setView([numLat, numLon], 16)
    locationFeedback.value = `✅ Lokasi ditemukan: ${display_name}`
    setTimeout(() => { if (locationFeedback.value.startsWith('✅')) locationFeedback.value = '' }, 7000)
  } catch {
    searchError.value = 'Gagal menghubungi layanan geocoding. Periksa koneksi internet Anda.'
    locationFeedback.value = ''
  } finally {
    isSearching.value = false
  }
}

const form = reactive({
  church_code: '',
  church_name: '',
  established_date: '',
  bpp_general_chairman: '',
  church_description: '',
  address: '',
  city: '',
  latitude: -6.1754,
  longitude: 106.8415,
  google_maps_url: 'https://www.google.com/maps/search/?api=1&query=-6.1754,106.8415',

  // Medsos & Links
  facebook_name: '',
  facebook_link: '',
  instagram_name: '',
  instagram_link: '',
  youtube_name: '',
  youtube_link: '',
  tiktok_name: '',
  tiktok_link: ''
})

const createGoldPinIcon = () => {
  return L.divIcon({
    className: 'custom-church-pin',
    html: `
      <div style="position: relative; display: flex; align-items: center; justify-content: center;">
        <div style="position: absolute; width: 34px; height: 34px; border-radius: 50%; background: rgba(245, 158, 11, 0.35); animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
        <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #fbbf24, #d97706); border-radius: 50% 50% 50% 0; transform: rotate(-45deg); border: 2.5px solid #ffffff; box-shadow: 0 4px 14px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;">
          <span style="transform: rotate(45deg); font-size: 16px; line-height: 1;">⛪</span>
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36]
  })
}

const updateCoordinates = (lat, lng, pan = false) => {
  const numLat = Number(Number(lat).toFixed(6))
  const numLng = Number(Number(lng).toFixed(6))
  form.latitude = numLat
  form.longitude = numLng
  form.google_maps_url = `https://www.google.com/maps/search/?api=1&query=${numLat},${numLng}`

  if (churchMarker) {
    churchMarker.setLatLng([numLat, numLng])
  }

  if (pan && leafletMap) {
    leafletMap.panTo([numLat, numLng])
  }
}

const initLeafletMap = () => {
  if (!mapContainer.value || leafletMap) return
  const initialLat = Number(form.latitude) || -6.1754
  const initialLng = Number(form.longitude) || 106.8415

  leafletMap = L.map(mapContainer.value, {
    center: [initialLat, initialLng],
    zoom: 13,
    zoomControl: true,
    attributionControl: false
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }).addTo(leafletMap)

  churchMarker = L.marker([initialLat, initialLng], {
    icon: createGoldPinIcon(),
    draggable: true
  }).addTo(leafletMap)

  churchMarker.on('dragend', (e) => {
    const pos = e.target.getLatLng()
    updateCoordinates(pos.lat, pos.lng, true)
  })

  leafletMap.on('click', (e) => {
    updateCoordinates(e.latlng.lat, e.latlng.lng, true)
  })
}

const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    locationFeedback.value = 'Browser Anda tidak mendukung fitur deteksi lokasi (Geolocation).'
    return
  }

  isLocating.value = true
  locationFeedback.value = 'Mendeteksi sinyal GPS perangkat Anda...'

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords
      updateCoordinates(latitude, longitude, true)
      if (leafletMap) {
        leafletMap.setView([latitude, longitude], 15)
      }
      isLocating.value = false
      locationFeedback.value = `Lokasi GPS perangkat berhasil didapatkan: (${latitude.toFixed(5)}, ${longitude.toFixed(5)})`
      setTimeout(() => {
        if (locationFeedback.value.startsWith('Lokasi GPS')) locationFeedback.value = ''
      }, 5000)
    },
    (error) => {
      isLocating.value = false
      let msg = 'Gagal mendeteksi lokasi GPS.'
      if (error.code === 1) msg = 'Akses lokasi ditolak. Silakan izinkan akses GPS di browser.'
      else if (error.code === 2) msg = 'Posisi GPS tidak dapat ditentukan.'
      else if (error.code === 3) msg = 'Pencarian lokasi GPS waktu habis (timeout).'
      locationFeedback.value = msg
    },
    { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
  )
}

onMounted(() => {
  nextTick(() => {
    setTimeout(initLeafletMap, 300)
  })
})

const handleSubmit = async () => {
  errorMessage.value = ''
  isSubmitting.value = true

  try {
    const payload = {
      ...form,
      established_date: form.established_date || null,
      city: form.city ? form.city.trim() : null,
      latitude: form.latitude ? Number(form.latitude) : null,
      longitude: form.longitude ? Number(form.longitude) : null,
      google_maps_url: form.google_maps_url || null
    }

    await apiFetch('/churches/', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    showSuccessModal.value = true
  } catch (err) {
    errorMessage.value = err.message || 'Terjadi kesalahan saat menyimpan data.'
  } finally {
    isSubmitting.value = false
  }
}

const goToDataGereja = () => {
  showSuccessModal.value = false
  router.push('/data-gereja')
}
</script>

<template>
  <MainAdminLayout>
    <div class="p-6 max-w-4xl mx-auto font-sans text-slate-100">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-amber-500/30">
        <div>
          <h1 class="text-2xl font-bold font-serif text-amber-300">Registrasi Data Gereja Baru</h1>
          <p class="text-xs text-slate-300 mt-1">Formulir pendaftaran institusi gereja baru oleh Admin Utama System GracePoint.</p>
        </div>
        <button 
          @click="router.push('/data-gereja')"
          class="px-4 py-2 text-xs font-serif uppercase tracking-wider bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg transition flex items-center gap-2 cursor-pointer"
        >
          <i class="bi bi-arrow-left"></i>
          <span>Kembali ke Daftar Gereja</span>
        </button>
      </div>

      <!-- Form Card -->
      <form @submit.prevent="handleSubmit" class="p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-[#0c163a] to-[#070d24] border border-amber-500/30 shadow-2xl space-y-8">
        
        <!-- Error Alert -->
        <div v-if="errorMessage" class="p-4 bg-rose-950/80 border border-rose-800 text-rose-200 rounded-xl text-xs flex items-center gap-2">
          <i class="bi bi-exclamation-triangle-fill text-base text-rose-400"></i>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Section 1: Profil & Alamat Gereja -->
        <div class="space-y-4">
          <h3 class="text-sm font-bold font-serif text-amber-400 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-2">
            <i class="bi bi-building font-bold"></i>
            <span>1. Informasi Profil Gereja</span>
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Kode Gereja *</label>
              <input v-model="form.church_code" type="text" required placeholder="Contoh: GP-005" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white font-mono text-sm focus:outline-none focus:border-amber-400">
            </div>

            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Nama Resmi Gereja *</label>
              <input v-model="form.church_name" type="text" required placeholder="Contoh: Gereja Bethel Indonesia / Gereja Kristen Protestan Mentawai" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white text-sm focus:outline-none focus:border-amber-400">
            </div>

            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Tanggal Berdiri / Lahir Gereja *</label>
              <input v-model="form.established_date" type="date" required class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white text-sm focus:outline-none focus:border-amber-400">
            </div>

            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Ketua Umum BPP Tiap Gereja *</label>
              <input v-model="form.bpp_general_chairman" type="text" required placeholder="Contoh: Pdt. Dr. Rubin Adi Abraham / Ephorus..." class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white text-sm focus:outline-none focus:border-amber-400">
            </div>

            <div class="md:col-span-2">
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Kota / Wilayah Domisili Gereja Pusat</label>
              <input v-model="form.city" type="text" placeholder="Contoh: Jakarta Pusat, DKI Jakarta" class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white text-sm focus:outline-none focus:border-amber-400">
            </div>
          </div>

          <div>
            <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Alamat Lengkap Gedung Gereja *</label>
            <textarea v-model="form.address" rows="2" required placeholder="Jl. Diponegoro No. 25, Menteng..." class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white text-sm focus:outline-none focus:border-amber-400"></textarea>
          </div>
        </div>

        <!-- Section 2: Geolocation & Titik Peta Gereja Pusat (Admin Utama) -->
        <div class="space-y-4 pt-2">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 class="text-sm font-bold font-serif text-amber-400 uppercase tracking-wider flex items-center gap-2">
              <i class="bi bi-geo-alt-fill text-amber-400"></i>
              <span>2. Titik Geolocation & Peta Gereja Pusat (GMaps)</span>
            </h3>
            <span class="text-[10px] text-amber-400/80 font-mono">Tabel: churches</span>
          </div>

          <!-- Toolbar Geolocation -->
          <div class="bg-[#050918] border border-amber-500/20 p-3 rounded-xl space-y-3">

            <!-- Search Bar: Alamat atau URL Google Maps -->
            <div class="space-y-1.5">
              <label class="text-[10px] uppercase tracking-widest text-amber-300/70 font-bold flex items-center gap-1.5">
                <i class="bi bi-search"></i>
                Cari Lokasi via Alamat atau Tempel Link Google Maps
              </label>
              <div class="flex gap-2">
                <div class="relative flex-1">
                  <i class="bi bi-geo-alt absolute left-3 top-1/2 -translate-y-1/2 text-amber-400/60 text-sm pointer-events-none"></i>
                  <input
                    v-model="mapSearchQuery"
                    type="text"
                    placeholder="Ketik alamat (cth: Jl. Sudirman No.5 Jakarta) atau tempel link Google Maps..."
                    class="w-full pl-9 pr-3 py-2.5 bg-[#0a1128] border border-amber-500/30 focus:border-amber-400 rounded-xl text-white text-xs font-mono outline-none transition placeholder:text-slate-600"
                    @keydown.enter.prevent="searchLocation"
                  />
                </div>
                <button
                  type="button"
                  @click="searchLocation"
                  :disabled="isSearching || !mapSearchQuery.trim()"
                  class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-md transition cursor-pointer disabled:opacity-50 shrink-0"
                >
                  <i v-if="isSearching" class="bi bi-arrow-repeat animate-spin"></i>
                  <i v-else class="bi bi-search"></i>
                  <span>{{ isSearching ? 'Mencari...' : 'Cari' }}</span>
                </button>
              </div>
              <!-- Error pencarian -->
              <div v-if="searchError" class="flex items-start gap-2 p-2.5 rounded-lg bg-rose-950/60 border border-rose-800/60 text-rose-300 text-[11px]">
                <i class="bi bi-exclamation-triangle-fill shrink-0 mt-0.5"></i>
                <span>{{ searchError }}</span>
              </div>
              <p class="text-[10px] text-slate-500">
                💡 Tempel link Google Maps untuk akurasi tepat, atau ketik alamat untuk pencarian otomatis via OpenStreetMap.
              </p>
            </div>

            <!-- Divider -->
            <div class="border-t border-slate-800"></div>

            <!-- GPS & Reset Buttons -->
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <button 
                  type="button" 
                  @click="getCurrentLocation" 
                  :disabled="isLocating"
                  class="px-3.5 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 border border-slate-600 font-semibold text-xs flex items-center gap-2 shadow-md transition cursor-pointer disabled:opacity-50"
                >
                  <i v-if="isLocating" class="bi bi-arrow-repeat animate-spin text-amber-400"></i>
                  <i v-else class="bi bi-geo-fill text-amber-400"></i>
                  <span>{{ isLocating ? 'Mendeteksi GPS...' : 'Ambil Lokasi GPS Saya' }}</span>
                </button>

                <button 
                  type="button" 
                  @click="updateCoordinates(-6.1754, 106.8415, true); mapSearchQuery = ''; searchError = ''"
                  class="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 border border-slate-700 text-xs transition cursor-pointer"
                >
                  Reset
                </button>
              </div>

              <a 
                v-if="form.latitude && form.longitude"
                :href="form.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${form.latitude},${form.longitude}`" 
                target="_blank" 
                rel="noopener noreferrer"
                class="px-3 py-2 rounded-lg bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-700/60 text-cyan-300 text-xs flex items-center gap-1.5 no-underline"
              >
                <i class="bi bi-box-arrow-up-right"></i>
                <span>Buka di Google Maps ↗</span>
              </a>
            </div>
          </div>

          <!-- Feedback Status Lokasi -->
          <div v-if="locationFeedback" class="p-2.5 rounded-lg text-xs font-mono bg-emerald-950/80 text-emerald-300 border border-emerald-800">
            {{ locationFeedback }}
          </div>

          <!-- Peta Leaflet -->
          <div class="relative rounded-xl overflow-hidden border border-amber-500/40 shadow-2xl bg-[#050918]">
            <div ref="mapContainer" class="w-full h-[250px] z-10"></div>
            <div class="absolute top-3 right-3 z-[400] bg-slate-900/90 border border-amber-500/50 rounded-lg px-2.5 py-1 text-[10px] font-mono text-amber-300 shadow">
              Titik: {{ Number(form.latitude).toFixed(5) }}, {{ Number(form.longitude).toFixed(5) }}
            </div>
          </div>

          <!-- Input Koordinat Presisi -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Latitude *</label>
              <input 
                v-model.number="form.latitude" 
                type="number" 
                step="any"
                required
                @input="updateCoordinates(form.latitude, form.longitude, true)"
                class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white font-mono text-xs focus:outline-none focus:border-amber-400" 
              />
            </div>

            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Longitude *</label>
              <input 
                v-model.number="form.longitude" 
                type="number" 
                step="any"
                required
                @input="updateCoordinates(form.latitude, form.longitude, true)"
                class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white font-mono text-xs focus:outline-none focus:border-amber-400" 
              />
            </div>

            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1 font-semibold">Google Maps URL</label>
              <div class="flex gap-2">
                <input 
                  v-model="mapSearchQuery"
                  type="text"
                  placeholder="Tempel link Google Maps di sini lalu tekan Enter..."
                  class="flex-1 px-3 py-2 bg-[#050918] border border-amber-500/20 focus:border-amber-400 rounded-xl text-amber-200 font-mono text-xs outline-none transition placeholder:text-slate-700"
                  @keydown.enter.prevent="searchLocation"
                />
                <button
                  type="button"
                  @click="searchLocation"
                  :disabled="isSearching || !mapSearchQuery.trim()"
                  class="px-3 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 text-amber-300 text-xs font-bold transition cursor-pointer disabled:opacity-40"
                >
                  <i v-if="isSearching" class="bi bi-arrow-repeat animate-spin"></i>
                  <i v-else class="bi bi-geo-alt-fill"></i>
                </button>
              </div>
              <p class="text-[10px] text-slate-600 mt-1 font-mono">Auto-generated: {{ form.google_maps_url }}</p>
            </div>
          </div>
        </div>

        <!-- Section 3: Deskripsi & Sejarah Sekilas Gereja -->
        <div class="space-y-4 pt-2">
          <h3 class="text-sm font-bold font-serif text-amber-400 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-2">
            <i class="bi bi-journal-text font-bold"></i>
            <span>3. Deskripsi & Sejarah Sekilas Gereja</span>
          </h3>

          <div>
            <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-2 font-semibold">Deskripsi Profil / Sejarah Perjalanan Gereja</label>
            <textarea 
              v-model="form.church_description" 
              rows="4" 
              placeholder="Tuliskan deskripsi sekilas, visi misi pelayanan, atau latar belakang sejarah berdirinya gereja ini..." 
              class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white text-sm focus:outline-none focus:border-amber-400"
            ></textarea>
          </div>
        </div>

        <!-- Section 4: Media Sosial & Link URL -->
        <div class="space-y-4">
          <h3 class="text-sm font-bold font-serif text-amber-400 uppercase tracking-wider flex items-center gap-2 border-b border-slate-800 pb-2">
            <i class="bi bi-share-fill font-bold"></i>
            <span>3. Akun Media Sosial & Tautan (Link)</span>
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <!-- Instagram -->
            <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div class="flex items-center gap-2 text-xs font-bold text-pink-400 font-serif pb-1 border-b border-slate-800/80">
                <i class="bi bi-instagram text-base"></i>
                <span>Instagram Gereja</span>
              </div>
              <div class="space-y-3 pt-1">
                <div>
                  <label class="block text-[11px] font-semibold text-slate-400 mb-1">Nama Akun / Username</label>
                  <input v-model="form.instagram_name" type="text" placeholder="cth: @gracepoint_church" class="w-full px-3.5 py-2.5 bg-[#050918] border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-pink-400">
                </div>
                <div>
                  <label class="block text-[11px] font-semibold text-slate-400 mb-1">Tautan / Link URL</label>
                  <input v-model="form.instagram_link" type="url" placeholder="cth: https://instagram.com/gracepoint_church" class="w-full px-3.5 py-2.5 bg-[#050918] border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-pink-400 font-mono">
                </div>
              </div>
            </div>

            <!-- Facebook -->
            <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div class="flex items-center gap-2 text-xs font-bold text-blue-400 font-serif pb-1 border-b border-slate-800/80">
                <i class="bi bi-facebook text-base"></i>
                <span>Facebook Halaman / Fanpage</span>
              </div>
              <div class="space-y-3 pt-1">
                <div>
                  <label class="block text-[11px] font-semibold text-slate-400 mb-1">Nama Halaman / Fanpage</label>
                  <input v-model="form.facebook_name" type="text" placeholder="cth: GracePoint Church Official" class="w-full px-3.5 py-2.5 bg-[#050918] border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-blue-400">
                </div>
                <div>
                  <label class="block text-[11px] font-semibold text-slate-400 mb-1">Tautan / Link URL</label>
                  <input v-model="form.facebook_link" type="url" placeholder="cth: https://facebook.com/gracepoint.official" class="w-full px-3.5 py-2.5 bg-[#050918] border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-blue-400 font-mono">
                </div>
              </div>
            </div>

            <!-- YouTube -->
            <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div class="flex items-center gap-2 text-xs font-bold text-red-400 font-serif pb-1 border-b border-slate-800/80">
                <i class="bi bi-youtube text-base"></i>
                <span>YouTube Channel Live Streaming</span>
              </div>
              <div class="space-y-3 pt-1">
                <div>
                  <label class="block text-[11px] font-semibold text-slate-400 mb-1">Nama Channel YouTube</label>
                  <input v-model="form.youtube_name" type="text" placeholder="cth: GracePoint Church Live" class="w-full px-3.5 py-2.5 bg-[#050918] border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-red-400">
                </div>
                <div>
                  <label class="block text-[11px] font-semibold text-slate-400 mb-1">Tautan / Link URL Channel</label>
                  <input v-model="form.youtube_link" type="url" placeholder="cth: https://youtube.com/@GracePointLive" class="w-full px-3.5 py-2.5 bg-[#050918] border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-red-400 font-mono">
                </div>
              </div>
            </div>

            <!-- TikTok -->
            <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div class="flex items-center gap-2 text-xs font-bold text-slate-300 font-serif pb-1 border-b border-slate-800/80">
                <i class="bi bi-tiktok text-base"></i>
                <span>TikTok Official</span>
              </div>
              <div class="space-y-3 pt-1">
                <div>
                  <label class="block text-[11px] font-semibold text-slate-400 mb-1">Nama Username TikTok</label>
                  <input v-model="form.tiktok_name" type="text" placeholder="cth: @gracepoint.official" class="w-full px-3.5 py-2.5 bg-[#050918] border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-slate-400">
                </div>
                <div>
                  <label class="block text-[11px] font-semibold text-slate-400 mb-1">Tautan / Link URL TikTok</label>
                  <input v-model="form.tiktok_link" type="url" placeholder="cth: https://tiktok.com/@gracepoint.official" class="w-full px-3.5 py-2.5 bg-[#050918] border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:border-slate-400 font-mono">
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Button -->
        <div class="pt-4 border-t border-slate-800 flex justify-end gap-3">
          <button 
            type="button" 
            @click="router.push('/data-gereja')"
            class="px-5 py-3 text-xs font-serif uppercase tracking-wider bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition"
          >
            Batal
          </button>

          <button 
            type="submit" 
            :disabled="isSubmitting"
            class="px-6 py-3 text-xs font-serif font-bold uppercase tracking-wider bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 rounded-xl transition shadow-lg shadow-amber-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <i v-if="isSubmitting" class="bi bi-arrow-repeat animate-spin text-base"></i>
            <i v-else class="bi bi-check-circle-fill text-base"></i>
            <span>{{ isSubmitting ? 'Menyimpan...' : 'Daftarkan Gereja Sekarang' }}</span>
          </button>
        </div>

      </form>
    </div>

    <!-- Success Modal -->
    <Teleport to="body">
      <div v-if="showSuccessModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
        <div class="w-full max-w-md bg-[#091129] border border-amber-500/40 rounded-2xl p-6 shadow-2xl text-center space-y-4 font-sans text-slate-100">
          <div class="w-14 h-14 mx-auto rounded-full bg-emerald-500/20 border border-emerald-400 text-emerald-400 flex items-center justify-center text-2xl">
            <i class="bi bi-check-lg"></i>
          </div>
          <h3 class="text-xl font-bold font-serif text-amber-300">Registrasi Gereja Berhasil!</h3>
          <p class="text-xs text-slate-300">Data gereja <strong>{{ form.church_name }}</strong> dengan kode <strong>{{ form.church_code }}</strong> berhasil ditambahkan ke dalam sistem.</p>
          <button 
            @click="goToDataGereja"
            class="w-full py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-serif font-bold text-xs uppercase tracking-wider rounded-xl transition cursor-pointer"
          >
            Kembali ke Daftar Gereja
          </button>
        </div>
      </div>
    </Teleport>
  </MainAdminLayout>
</template>