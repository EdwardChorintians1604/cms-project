<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { APP_CONFIG } from '@/config'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const router = useRouter()

// Form Data selaras 100% dengan kolom tabel PostgreSQL church_admins:
// id, church_id, church_code, church_name, city, address, latitude, longitude, google_maps_url, admin_name, email, phone, password, status
const formData = ref({
  church_id: null,
  church_name: '',
  church_code: '',
  city: '',
  address: '',
  latitude: -6.1824,
  longitude: 106.9856,
  google_maps_url: 'https://www.google.com/maps/search/?api=1&query=-6.1824,106.9856',
  admin_name: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

const churches = ref([])
const isLoadingChurches = ref(false)
const churchLoadError = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// State Geolocation & Leaflet Map
const mapContainer = ref(null)
let leafletMap = null
let churchMarker = null
const isLocating = ref(false)
const locationFeedback = ref('')

// State untuk Fitur Bantuan Gereja Belum Terdaftar (3 Pilihan: Direct Sistem, WhatsApp, Email)
const showUnregisteredModal = ref(false)
const selectedChannel = ref('direct') // 'direct' | 'wa' | 'email'
const isWaitingAdmin = ref(false)
const isSubmittingRequest = ref(false)
const isRefreshingChurches = ref(false)
const modalError = ref('')
const submittedTicketId = ref('')
const isCopiedEmail = ref(false)
const adminMainWhatsApp = ref('6281277895609') // Nomor WhatsApp Admin Utama (dapat disesuaikan)
const adminMainEmail = ref('ambatukam09@gmail.com') // Email resmi Superadmin

const unregisteredForm = ref({
  applicantName: '',
  applicantPhone: '',
  proposedMainChurch: '',
  proposedBranchChurch: '',
  city: '',
  address: '',
  latitude: null,
  longitude: null,
  google_maps_url: '',
  leaderName: '',
  complaintNotes: ''
})

// Pin Emas Khas GracePoint
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

// Update koordinat dan sinkronkan marker & URL GMaps
const updateCoordinates = (lat, lng, pan = false) => {
  const numLat = Number(Number(lat).toFixed(6))
  const numLng = Number(Number(lng).toFixed(6))
  formData.value.latitude = numLat
  formData.value.longitude = numLng
  formData.value.google_maps_url = `https://www.google.com/maps/search/?api=1&query=${numLat},${numLng}`

  if (churchMarker) {
    churchMarker.setLatLng([numLat, numLng])
    churchMarker.setPopupContent(`
      <div style="font-family: sans-serif; font-size: 11px; color: #1e293b; padding: 3px;">
        <strong style="color: #b45309; font-size: 12px; display: block; margin-bottom: 2px;">
          ${formData.value.church_name || 'Lokasi Gereja Cabang'}
        </strong>
        <p style="margin: 2px 0 4px 0; color: #475569; font-size: 10px;">
          ${formData.value.address || 'Titik koordinat akurat gereja'}
        </p>
        <span style="display: inline-block; background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 10px; font-weight: 600;">
          ${numLat}, ${numLng}
        </span>
      </div>
    `)
  }

  if (pan && leafletMap) {
    leafletMap.panTo([numLat, numLng])
  }
}

// Inisialisasi Peta Leaflet
const mapSearchQuery = ref('')
const isSearchingLocation = ref(false)

const searchLocationOnMap = async (customQuery = null) => {
  const q = (typeof customQuery === 'string' && customQuery.trim()) 
    ? customQuery.trim() 
    : (mapSearchQuery.value.trim() || formData.value.address.trim() || formData.value.city.trim() || formData.value.church_name.trim())

  if (!q) {
    locationFeedback.value = '⚠️ Masukkan nama jalan, gereja, atau kota untuk mencari di peta.'
    return
  }

  isSearchingLocation.value = true
  locationFeedback.value = `🔍 Mencari lokasi "${q}" secara akurat di peta...`

  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=1&countrycodes=id`)
    const data = await res.json()
    if (data && data.length > 0) {
      const target = data[0]
      const lat = Number(target.lat)
      const lng = Number(target.lon)
      updateCoordinates(lat, lng, true)
      if (leafletMap) {
        leafletMap.flyTo([lat, lng], 16, { duration: 1.2 })
      }
      locationFeedback.value = `✅ Titik ditemukan & pin dipindahkan: ${target.display_name}`
    } else {
      const resFallback = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=1`)
      const dataFallback = await resFallback.json()
      if (dataFallback && dataFallback.length > 0) {
        const target = dataFallback[0]
        const lat = Number(target.lat)
        const lng = Number(target.lon)
        updateCoordinates(lat, lng, true)
        if (leafletMap) {
          leafletMap.flyTo([lat, lng], 16, { duration: 1.2 })
        }
        locationFeedback.value = `✅ Titik ditemukan & pin dipindahkan: ${target.display_name}`
      } else {
        locationFeedback.value = `⚠️ Lokasi "${q}" tidak ditemukan di database peta. Anda dapat menggeser pin emas ⛪ langsung pada peta.`
      }
    }
  } catch (err) {
    locationFeedback.value = '⚠️ Gagal melakukan pencarian otomatis. Silakan geser pin emas langsung pada peta.'
  } finally {
    isSearchingLocation.value = false
  }
}

const initLeafletMap = () => {
  if (!mapContainer.value || leafletMap) return
  const initialLat = Number(formData.value.latitude) || -6.1824
  const initialLng = Number(formData.value.longitude) || 106.9856

  leafletMap = L.map(mapContainer.value, {
    center: [initialLat, initialLng],
    zoom: 15,
    zoomControl: true,
    attributionControl: false
  })

  // OpenStreetMap clean tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    subdomains: ['a', 'b', 'c'],
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(leafletMap)

  churchMarker = L.marker([initialLat, initialLng], {
    icon: createGoldPinIcon(),
    draggable: true
  }).addTo(leafletMap)

  churchMarker.bindPopup(`
    <div style="font-family: sans-serif; font-size: 11px; color: #1e293b; padding: 3px;">
      <strong style="color: #b45309; font-size: 12px; display: block; margin-bottom: 2px;">
        ${formData.value.church_name || 'Lokasi Gereja Cabang'}
      </strong>
      <span style="display: inline-block; background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 10px; font-weight: 600;">
        ${initialLat}, ${initialLng}
      </span>
    </div>
  `)

  churchMarker.on('dragend', (e) => {
    const { lat, lng } = e.target.getLatLng()
    updateCoordinates(lat, lng, false)
    locationFeedback.value = `📍 Pin berhasil dipindahkan ke: ${formData.value.latitude}, ${formData.value.longitude}`
  })

  leafletMap.on('click', (e) => {
    const { lat, lng } = e.latlng
    updateCoordinates(lat, lng, false)
    locationFeedback.value = `📍 Titik koordinat dipilih: ${formData.value.latitude}, ${formData.value.longitude}`
  })

  // Pastikan render peta aktif segera
  setTimeout(() => {
    if (leafletMap) leafletMap.invalidateSize()
  }, 200)
  setTimeout(() => {
    if (leafletMap) leafletMap.invalidateSize()
  }, 500)
  setTimeout(() => {
    if (leafletMap) leafletMap.invalidateSize()
  }, 1000)
}

// Deteksi Lokasi Sekarang (GPS Browser)
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    locationFeedback.value = '⚠️ Peramban Anda tidak mendukung Geolocation GPS.'
    return
  }
  isLocating.value = true
  locationFeedback.value = '📡 Mengambil titik koordinat GPS perangkat Anda...'

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude
      const lng = pos.coords.longitude
      updateCoordinates(lat, lng, true)
      if (leafletMap) leafletMap.setZoom(16)
      locationFeedback.value = `✅ Koordinat GPS berhasil dideteksi: ${lat.toFixed(6)}, ${lng.toFixed(6)} (Akurasi: ±${Math.round(pos.coords.accuracy)}m)`
      isLocating.value = false
    },
    (err) => {
      let msg = 'Gagal mengakses GPS perangkat.'
      if (err.code === 1) msg = 'Izin akses lokasi ditolak oleh pengguna.'
      else if (err.code === 2) msg = 'Posisi tidak dapat ditentukan.'
      else if (err.code === 3) msg = 'Waktu permintaan lokasi habis (timeout).'
      locationFeedback.value = `⚠️ ${msg}`
      isLocating.value = false
    },
    { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
  )
}

// 1. AMBIL DAFTAR GEREJA INDUK DARI POSTGRESQL (tabel churches)
const loadChurches = async () => {
  isLoadingChurches.value = true
  churchLoadError.value = ''
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    if (!res.ok) throw new Error('Gagal memuat daftar gereja dari server.')
    const data = await res.json()
    // Hanya ambil gereja induk berstatus Aktif
    churches.value = Array.isArray(data) ? data.filter(c => c.status === 'Aktif') : []
  } catch (err) {
    churchLoadError.value = err.message || 'Tidak dapat terhubung ke database gereja.'
  } finally {
    isLoadingChurches.value = false
  }
}

onMounted(() => {
  loadChurches()
  nextTick(() => {
    initLeafletMap()
  })
  window.addEventListener('resize', () => {
    if (leafletMap) leafletMap.invalidateSize()
  })
})

// Objek gereja induk yang dipilih
const selectedChurch = computed(() => {
  if (!formData.value.church_id) return null
  return churches.value.find(c => c.id === formData.value.church_id) || null
})

// Sinkronisasi saat dropdown gereja induk berubah
const onSelectChurch = (e) => {
  const val = e.target.value
  if (val === 'unregistered') {
    openUnregisteredModal()
    return
  }

  if (val === 'mandiri') {
    formData.value.church_id = null
    autoGenerateCode()
    return
  }

  const id = Number(val)
  formData.value.church_id = id
  autoGenerateCode()
}

// Bantuan buka modal dengan auto-populate data yang sudah diisi di form pendaftaran
const openUnregisteredModal = () => {
  if (!unregisteredForm.value.applicantName && formData.value.admin_name) {
    unregisteredForm.value.applicantName = formData.value.admin_name
  }
  if (!unregisteredForm.value.applicantPhone && formData.value.phone) {
    unregisteredForm.value.applicantPhone = formData.value.phone
  }
  if (!unregisteredForm.value.proposedBranchChurch && formData.value.church_name) {
    unregisteredForm.value.proposedBranchChurch = formData.value.church_name
  }
  if (!unregisteredForm.value.city && formData.value.city) {
    unregisteredForm.value.city = formData.value.city
  }
  if (!unregisteredForm.value.address && formData.value.address) {
    unregisteredForm.value.address = formData.value.address
  }
  if (!unregisteredForm.value.latitude && formData.value.latitude) {
    unregisteredForm.value.latitude = formData.value.latitude
    unregisteredForm.value.longitude = formData.value.longitude
    unregisteredForm.value.google_maps_url = formData.value.google_maps_url
  }
  modalError.value = ''
  showUnregisteredModal.value = true
}

const closeUnregisteredModal = () => {
  showUnregisteredModal.value = false
}

// Validasi Form Pengajuan
const validateUnregisteredForm = () => {
  modalError.value = ''
  if (!unregisteredForm.value.applicantName.trim()) {
    modalError.value = 'Mohon isi nama lengkap pendaftar.'
    return false
  }
  if (!unregisteredForm.value.applicantPhone.trim()) {
    modalError.value = 'Mohon isi nomor WhatsApp pendaftar.'
    return false
  }
  if (!unregisteredForm.value.proposedMainChurch.trim()) {
    modalError.value = 'Mohon isi nama Gereja Induk / Sinode yang ingin didaftarkan.'
    return false
  }
  return true
}

// PILIHAN 1: CHAT WHATSAPP
const sendWhatsAppRequest = () => {
  if (!validateUnregisteredForm()) return

  const text = `Halo Admin Utama GracePoint,

Saya ingin mendaftarkan diri sebagai Admin Gereja, namun nama Gereja Induk / Sinode kami belum terdaftar di database DBMS GracePoint.

Berikut data spesifik pengajuan gereja kami:
• Nama Pendaftar: ${unregisteredForm.value.applicantName.trim()}
• No. WhatsApp Pendaftar: ${unregisteredForm.value.applicantPhone.trim()}
• Nama Gereja Induk / Sinode: ${unregisteredForm.value.proposedMainChurch.trim()}
• Rencana Cabang Lokal: ${unregisteredForm.value.proposedBranchChurch.trim() || '-'}
• Kota / Kabupaten: ${unregisteredForm.value.city.trim() || '-'}
• Alamat Gereja: ${unregisteredForm.value.address.trim() || '-'}
• Pimpinan / Ketua Sinode (BPP): ${unregisteredForm.value.leaderName.trim() || '-'}
(Catatan: Untuk Kode Gereja Induk, kami serahkan kepada Admin Utama untuk menentukannya)

Keluh Kesah & Catatan Pendaftar:
"${unregisteredForm.value.complaintNotes.trim() || 'Nama gereja kami belum tersedia di sistem. Mohon bantuannya untuk menambahkan data ini ke DBMS agar kami bisa menyelesaikan pendaftaran. Terima kasih!'}"

Mohon bantuannya untuk memasukkan data gereja ini. Kami akan menunggu informasi dan konfirmasinya. Terima kasih!`

  const cleanPhone = adminMainWhatsApp.value.replace(/[^0-9]/g, '')
  const whatsappUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(text)}`

  window.open(whatsappUrl, '_blank')
  isWaitingAdmin.value = true
}

// PILIHAN 2: KIRIM LANGSUNG KE SISTEM ADMIN UTAMA
const sendDirectSystemRequest = async () => {
  if (!validateUnregisteredForm()) return

  isSubmittingRequest.value = true
  modalError.value = ''
  try {
    const payload = {
      applicant_name: unregisteredForm.value.applicantName.trim(),
      applicant_phone: unregisteredForm.value.applicantPhone.trim(),
      proposed_main_church: unregisteredForm.value.proposedMainChurch.trim(),
      proposed_branch_church: unregisteredForm.value.proposedBranchChurch.trim() || null,
      city: unregisteredForm.value.city.trim() || null,
      address: unregisteredForm.value.address.trim() || null,
      latitude: unregisteredForm.value.latitude ? Number(unregisteredForm.value.latitude) : (formData.value.latitude ? Number(formData.value.latitude) : null),
      longitude: unregisteredForm.value.longitude ? Number(unregisteredForm.value.longitude) : (formData.value.longitude ? Number(formData.value.longitude) : null),
      google_maps_url: unregisteredForm.value.google_maps_url || formData.value.google_maps_url || null,
      leader_name: unregisteredForm.value.leaderName.trim() || null,
      complaint_notes: unregisteredForm.value.complaintNotes.trim() || null,
      channel: 'direct'
    }

    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/church-requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Gagal mengirim permohonan ke sistem Admin Utama.')
    }

    const data = await res.json()
    submittedTicketId.value = data.request?.id || 'REQ-2026'
    isWaitingAdmin.value = true
  } catch (err) {
    modalError.value = err.message || 'Gagal mengirimkan permohonan ke server.'
  } finally {
    isSubmittingRequest.value = false
  }
}

// PILIHAN 3: KIRIM VIA EMAIL
const generateEmailContent = () => {
  const subject = `[GracePoint] Permohonan Pendaftaran Gereja Baru: ${unregisteredForm.value.proposedMainChurch || 'Gereja Baru'}`
  const coordsInfo = (unregisteredForm.value.latitude && unregisteredForm.value.longitude) 
    ? `\n8. Koordinat Geolocation: ${unregisteredForm.value.latitude}, ${unregisteredForm.value.longitude}\n   Tautan Maps: ${unregisteredForm.value.google_maps_url || '-'}`
    : ''

  const body = `Yth. Admin Utama GracePoint,

Saya ingin mendaftarkan diri sebagai Admin Gereja, namun nama Gereja Induk / Sinode kami belum terdaftar di sistem GracePoint CMS.

Berikut rincian data spesifik pengajuan gereja kami:
--------------------------------------------------
1. Nama Pendaftar: ${unregisteredForm.value.applicantName || '-'}
2. No. WhatsApp: ${unregisteredForm.value.applicantPhone || '-'}
3. Nama Gereja Induk / Sinode: ${unregisteredForm.value.proposedMainChurch || '-'}
4. Rencana Cabang Lokal: ${unregisteredForm.value.proposedBranchChurch || '-'}
5. Kota / Kabupaten: ${unregisteredForm.value.city || '-'}
6. Alamat Lengkap: ${unregisteredForm.value.address || '-'}
7. Pimpinan Sinode / BPP: ${unregisteredForm.value.leaderName || '-'}${coordsInfo}
(Kode Gereja Induk: Diserahkan sepenuhnya kepada Admin Utama untuk menentukannya)

Keluh Kesah & Catatan Pendaftar:
"${unregisteredForm.value.complaintNotes || 'Mohon dibantu agar gereja kami dapat dimasukkan ke database sistem GracePoint. Terima kasih!'}"

Mohon kesediaannya untuk menambahkan gereja kami ke DBMS. Kami akan menunggu kabar konfirmasi dari Admin Utama.

Salam hormat,
${unregisteredForm.value.applicantName || 'Calon Admin Gereja'}`

  return { subject, body }
}

const sendEmailRequest = async () => {
  if (!validateUnregisteredForm()) return

  try {
    await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/church-requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        applicant_name: unregisteredForm.value.applicantName.trim(),
        applicant_phone: unregisteredForm.value.applicantPhone.trim(),
        proposed_main_church: unregisteredForm.value.proposedMainChurch.trim(),
        proposed_branch_church: unregisteredForm.value.proposedBranchChurch.trim() || null,
        city: unregisteredForm.value.city.trim() || null,
        address: unregisteredForm.value.address.trim() || null,
        latitude: unregisteredForm.value.latitude ? Number(unregisteredForm.value.latitude) : (formData.value.latitude ? Number(formData.value.latitude) : null),
        longitude: unregisteredForm.value.longitude ? Number(unregisteredForm.value.longitude) : (formData.value.longitude ? Number(formData.value.longitude) : null),
        google_maps_url: unregisteredForm.value.google_maps_url || formData.value.google_maps_url || null,
        leader_name: unregisteredForm.value.leaderName.trim() || null,
        complaint_notes: unregisteredForm.value.complaintNotes.trim() || null,
        channel: 'email'
      })
    })
  } catch (e) {
    console.warn('Sync email request to dashboard:', e)
  }

  const { subject, body } = generateEmailContent()
  const mailtoUrl = `mailto:${adminMainEmail.value}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
  window.location.href = mailtoUrl
  isWaitingAdmin.value = true
}

const copyEmailBody = async () => {
  const { subject, body } = generateEmailContent()
  try {
    await navigator.clipboard.writeText(`Subject: ${subject}\n\n${body}`)
    isCopiedEmail.value = true
    setTimeout(() => { isCopiedEmail.value = false }, 3000)
  } catch (err) {
    alert('Gagal menyalin otomatis. Silakan salin manual teks email.')
  }
}

// Refresh & Cek apakah Gereja Sudah Diinput oleh Admin
const refreshChurchesAndCheck = async () => {
  isRefreshingChurches.value = true
  modalError.value = ''
  try {
    await loadChurches()
    const found = churches.value.find(c => 
      c.church_name.toLowerCase().includes(unregisteredForm.value.proposedMainChurch.trim().toLowerCase())
    )
    if (found) {
      formData.value.church_id = found.id
      autoGenerateCode()
      showUnregisteredModal.value = false
      alert(`🎉 Selamat! Gereja "${found.church_name}" telah ditemukan di database DBMS dan otomatis terpilih! Silakan lanjutkan formulir pendaftaran.`)
    } else {
      modalError.value = `Gereja "${unregisteredForm.value.proposedMainChurch}" belum terdaftar di sistem. Mohon tunggu Admin Utama menginputnya atau hubungi via WhatsApp.`
    }
  } catch (err) {
    modalError.value = 'Gagal memperbarui daftar gereja: ' + (err.message || 'Coba lagi beberapa saat lagi.')
  } finally {
    isRefreshingChurches.value = false
  }
}

// Bantuan auto-generate kode cabang bila belum diisi
const autoGenerateCode = () => {
  if (formData.value.church_code && !formData.value.church_code.startsWith('CH-')) return
  const prefix = selectedChurch.value?.church_code 
    ? selectedChurch.value.church_code.split('-')[0]
    : 'CH'
  const cityCode = formData.value.city ? formData.value.city.substring(0, 3).toUpperCase() : 'CAB'
  formData.value.church_code = `${prefix}-${cityCode}-01`
}

watch(() => formData.value.city, () => {
  if (!formData.value.church_code || formData.value.church_code.includes('-CAB-')) {
    autoGenerateCode()
  }
})

// 3. SUBMIT PENDAFTARAN ADMIN GEREJA KE POSTGRESQL (tabel church_admins)
const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (formData.value.password !== formData.value.confirmPassword) {
    errorMessage.value = 'Konfirmasi kata sandi tidak cocok!'
    return
  }

  if (!formData.value.church_name || !formData.value.admin_name || !formData.value.email || !formData.value.password) {
    errorMessage.value = 'Mohon lengkapi seluruh kolom wajib yang bertanda bintang (*).'
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      church_id: formData.value.church_id || null,
      church_code: formData.value.church_code ? formData.value.church_code.trim().toUpperCase() : null,
      church_name: formData.value.church_name.trim(),
      city: formData.value.city ? formData.value.city.trim() : null,
      address: formData.value.address ? formData.value.address.trim() : null,
      latitude: formData.value.latitude ? Number(formData.value.latitude) : null,
      longitude: formData.value.longitude ? Number(formData.value.longitude) : null,
      google_maps_url: formData.value.google_maps_url ? formData.value.google_maps_url.trim() : null,
      admin_name: formData.value.admin_name.trim(),
      email: formData.value.email.trim().toLowerCase(),
      phone: formData.value.phone ? formData.value.phone.trim() : null,
      password: formData.value.password,
      confirm_password: formData.value.confirmPassword
    }

    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/auth/church-admin/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Pendaftaran admin gereja gagal diproses di database.')
    }

    const result = await res.json()
    successMessage.value = `Pendaftaran Gereja "${result.church_name}" (Kode: ${result.church_code}) berhasil disimpan ke database PostgreSQL! Mengarahkan ke halaman login...`
    setTimeout(() => router.push({
      path: '/verification-login',
      query: {
        email: result.email,
        churchCode: result.church_code,
      },
    }), 2200)
  } catch (err) {
    errorMessage.value = err.message || 'Gagal melakukan pendaftaran gereja.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="page-root bg-[var(--theme-bg-primary,#070d19)] text-[var(--theme-text-primary,#f8fafc)] flex flex-col justify-between items-center px-3 sm:px-4 font-sans relative overflow-hidden transition-colors duration-300">
    
    <!-- Dynamic Ambient Background Glows -->
    <div aria-hidden="true" class="absolute top-0 left-1/2 -translate-x-1/2 w-[min(750px,120vw)] h-[350px] bg-amber-500/10 dark:bg-amber-500/15 blur-[140px] pointer-events-none rounded-full"></div>
    <div aria-hidden="true" class="absolute bottom-0 right-0 w-[min(450px,90vw)] h-[350px] bg-cyan-500/5 dark:bg-cyan-500/10 blur-[130px] pointer-events-none rounded-full"></div>

    <!-- Top Navigation Header -->
    <header class="w-full max-w-7xl mx-auto px-1 sm:px-6 py-4 flex items-center justify-between gap-3 z-20 relative mb-4">
      <RouterLink 
        to="/" 
        class="brand-link flex items-center gap-3 group cursor-pointer no-underline min-w-0"
        style="text-decoration: none !important;"
      >
        <div class="w-10 h-10 rounded-full border-2 border-slate-400/60 dark:border-amber-500/40 bg-slate-100 dark:bg-slate-900 flex items-center justify-center shadow-lg group-hover:border-amber-400 transition shrink-0 overflow-hidden">
          <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="w-full h-full object-cover">
        </div>
        <div class="flex flex-col min-w-0">
          <span class="truncate font-serif font-bold text-lg text-amber-600 dark:text-amber-300 tracking-wider group-hover:text-amber-500 dark:group-hover:text-amber-200 transition leading-tight">
            GRACEPOINT
          </span>
          <span class="truncate text-[10px] text-slate-500 dark:text-slate-400 font-serif tracking-widest uppercase leading-tight">
            Registrasi Admin Gereja
          </span>
        </div>
      </RouterLink>

      <!-- Header Controls: Theme Toggle & Back Button -->
      <div class="flex items-center gap-2.5 sm:gap-3 shrink-0">
        <ThemeToggleButton />

        <RouterLink 
          to="/" 
          class="text-xs font-medium text-slate-700 dark:text-slate-200 hover:text-amber-600 dark:hover:text-amber-300 flex items-center gap-1.5 px-3 sm:px-3.5 py-2 rounded-xl border border-slate-300 dark:border-slate-700/80 bg-white/90 dark:bg-slate-900/80 hover:bg-slate-50 dark:hover:bg-slate-800 transition shadow-sm cursor-pointer no-underline"
          style="text-decoration: none !important;"
          title="Kembali ke Beranda Utama"
        >
          <svg class="w-4 h-4 text-amber-500 dark:text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          <span class="hidden sm:inline font-sans">Kembali ke Beranda</span>
          <span class="sm:hidden font-sans">Beranda</span>
        </RouterLink>
      </div>
    </header>

    <!-- Main Registration Card -->
    <div class="w-full max-w-4xl bg-white/95 dark:bg-slate-950/90 border border-slate-200 dark:border-amber-500/30 rounded-2xl p-5 sm:p-8 lg:p-10 shadow-2xl backdrop-blur-xl z-10 my-auto transition-colors duration-300">
      
      <!-- Card Header -->
      <div class="text-center pb-6 border-b border-slate-200 dark:border-amber-500/20 mb-6">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/30 dark:border-amber-400/40 text-amber-600 dark:text-amber-300 mb-3 shadow-inner">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
        </div>
        <h1 class="text-2xl sm:text-3xl font-bold font-serif text-amber-600 dark:text-amber-300 tracking-wide">
          Pendaftaran Admin Gereja Baru
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1 font-sans">
          Sesuai skema tabel <code class="px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 font-mono text-[11px]">church_admins</code> PostgreSQL di database GracePoint.
        </p>
      </div>

      <!-- Alert Messages -->
      <div v-if="errorMessage" class="mb-6 p-4 text-xs font-sans bg-rose-50 dark:bg-rose-950/80 border border-rose-300 dark:border-rose-800 text-rose-800 dark:text-rose-200 rounded-xl flex items-center gap-2">
        <span class="text-base">⚠️</span>
        <span>{{ errorMessage }}</span>
      </div>

      <div v-if="successMessage" class="mb-6 p-4 text-xs font-sans bg-emerald-50 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 rounded-xl flex items-center gap-2">
        <span class="text-base">✅</span>
        <span>{{ successMessage }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-6 font-sans text-xs">
        
        <!-- SECTION 1: DATA GEREJA CABANG -->
        <div class="space-y-4">
          <h3 class="section-title text-sm font-serif font-bold text-amber-600 dark:text-amber-300 border-b border-slate-200 dark:border-slate-800 pb-2 uppercase tracking-wider flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
            <span>🏛️ 1. Informasi Gereja Cabang</span>
            <span class="hidden sm:inline text-[10px] text-amber-600/80 dark:text-amber-400/80 font-mono font-normal tracking-normal lowercase">
              Tabel: church_admins
            </span>
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <!-- Kolom: church_name -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Nama Gereja di Daerah Anda <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="formData.church_name" 
                type="text" 
                required 
                placeholder="Contoh: GKI Harapan Indah Bekasi" 
                class="form-control" 
              />
            </div>

            <!-- Kolom: church_id (Gereja Terafiliasi FK ke churches) -->
            <div>
              <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 mb-1.5">
                <label class="block font-medium text-slate-700 dark:text-slate-300">
                  Gereja yang terafiliasi <span class="text-rose-500">*</span>
                </label>
                <div class="flex items-center gap-2">
                  <span v-if="isLoadingChurches" class="text-[10px] text-amber-500 font-mono animate-pulse">
                    Mengambil data...
                  </span>
                  <button 
                    type="button" 
                    @click="openUnregisteredModal" 
                    class="text-[10px] text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 no-underline font-semibold cursor-pointer transition flex items-center gap-1"
                    title="Kirim permohonan ke Admin Utama jika gereja belum terdaftar"
                  >
                    <svg class="w-3 h-3 text-emerald-500 inline" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/>
                    </svg>
                    Belum Ada? Ajukan ke Admin
                  </button>
                </div>
              </div>
              
              <select 
                :value="formData.church_id || (formData.church_id === null ? 'mandiri' : '')" 
                @change="onSelectChurch" 
                class="form-control cursor-pointer"
              >
                <option value="" disabled>-- Pilih Gereja Induk / Sinode Terdaftar --</option>
                <option 
                  v-for="church in churches" 
                  :key="church.id" 
                  :value="church.id"
                >
                  {{ church.church_name }} ({{ church.church_code }})
                </option>
                <option value="mandiri">-- Mandiri / Non-Sinode (Tanpa Afiliasi) --</option>
                <option value="unregistered" class="text-amber-500 font-semibold">
                  ➕ Gereja Belum Terdaftar? (Ajukan ke Admin Utama)
                </option>
              </select>

              <!-- Helper Card Bila Gereja Belum Ada -->
              <div class="mt-2 p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-400 flex items-start gap-2">
                <span class="text-amber-500 text-sm leading-none">💡</span>
                <span>
                  Gereja induk atau cabang belum tercantum di atas? 
                  <button type="button" @click="openUnregisteredModal" class="text-amber-600 dark:text-amber-300 font-semibold no-underline hover:text-amber-500 cursor-pointer">
                    Klik di sini untuk mengirim data ke Admin Utama
                  </button> 
                  agar segera diinput ke sistem DBMS.
                </span>
              </div>

              <!-- Preview Card Gereja Induk Terpilih -->
              <div v-if="selectedChurch" class="mt-2.5 p-3 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-300 dark:border-amber-500/30 text-xs text-amber-900 dark:text-amber-200 space-y-1">
                <div class="flex flex-wrap items-center justify-between gap-2 font-bold text-amber-700 dark:text-amber-300">
                  <span class="flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                    </svg>
                    <span>{{ selectedChurch.church_name }}</span>
                  </span>
                  <span class="font-mono text-[10px] px-2 py-0.5 rounded bg-amber-200 dark:bg-amber-950/80 border border-amber-400 dark:border-amber-500/40 text-amber-900 dark:text-amber-300">
                    {{ selectedChurch.church_code }}
                  </span>
                </div>
                <p v-if="selectedChurch.bpp_general_chairman" class="text-[11px] text-slate-700 dark:text-slate-300">
                  <span class="text-amber-600 dark:text-amber-400 font-semibold">Ketua BPP:</span> {{ selectedChurch.bpp_general_chairman }}
                </p>
                <p v-if="selectedChurch.established_date" class="text-[11px] text-slate-700 dark:text-slate-300">
                  <span class="text-amber-600 dark:text-amber-400 font-semibold">Tgl Berdiri:</span> {{ selectedChurch.established_date }}
                </p>
              </div>

              <div v-else-if="churchLoadError" class="mt-1 text-[11px] text-rose-500">
                {{ churchLoadError }} <button type="button" @click="loadChurches" class="no-underline font-bold text-amber-600 dark:text-amber-400 ml-1">Coba lagi</button>
              </div>
            </div>

            <!-- Kolom: church_code -->
            <div>
              <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 mb-1.5">
                <label class="block font-medium text-slate-700 dark:text-slate-300">
                  Kode Gereja Cabang <span class="text-rose-500">*</span>
                </label>
                <button 
                  type="button" 
                  @click="autoGenerateCode" 
                  class="text-[10px] text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 no-underline font-semibold cursor-pointer"
                  title="Generate otomatis"
                >
                  Saran Kode
                </button>
              </div>
              <input 
                v-model="formData.church_code" 
                type="text" 
                required 
                placeholder="Contoh: GKI-BKS-01" 
                class="form-control font-mono uppercase" 
              />
              <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Kode unik identifikasi cabang gereja (kolom: <code class="text-amber-600 dark:text-amber-300">church_code</code>).</p>
            </div>

            <!-- Kolom: city -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Kota / Kabupaten <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="formData.city" 
                type="text" 
                required 
                placeholder="Contoh: Kota Bekasi, Jawa Barat" 
                class="form-control" 
              />
              <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Wilayah domisili gereja cabang (kolom: <code class="text-amber-600 dark:text-amber-300">city</code>).</p>
            </div>

          </div>
        </div>

        <!-- SECTION 2: LOKASI GEOLOCATION & PETA GEREJA (GMaps) -->
        <div class="space-y-4 pt-2">
          <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-b border-slate-200 dark:border-slate-800 pb-2">
            <h3 class="section-title text-sm font-serif font-bold text-amber-600 dark:text-amber-300 uppercase tracking-wider flex items-center gap-2">
              <span>📍 2. Lokasi Geolocation &amp; Titik Peta Gereja (Peta Interaktif Langsung)</span>
            </h3>
            <span class="hidden sm:inline text-[10px] text-amber-600/80 dark:text-amber-400/80 font-mono font-normal tracking-normal lowercase">
              PostgreSQL: latitude, longitude, address, google_maps_url
            </span>
          </div>

          <!-- Alamat Lengkap Gereja & Tombol Cari Alamat di Peta -->
          <div>
            <div class="flex flex-wrap items-center justify-between gap-2 mb-1.5">
              <label class="block font-medium text-slate-700 dark:text-slate-300">
                Alamat Lengkap Gedung Gereja <span class="text-rose-500">*</span>
              </label>
              <button 
                type="button" 
                @click="searchLocationOnMap(formData.address)"
                :disabled="isSearchingLocation || !formData.address"
                class="text-[11px] font-semibold text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 flex items-center gap-1 cursor-pointer disabled:opacity-50 transition"
                title="Cari lokasi peta berdasarkan teks alamat yang Anda ketik"
              >
                <span>🔍 Cari Alamat Ini di Peta</span>
              </button>
            </div>
            <textarea 
              v-model="formData.address" 
              rows="2" 
              required 
              placeholder="Contoh: Jl. Harapan Indah Boulevard Blok AA No. 1, Medan Satria, Kota Bekasi" 
              class="form-control" 
            ></textarea>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Alamat fisik lengkap gedung gereja cabang (kolom: <code class="text-amber-600 dark:text-amber-300">address</code>).</p>
          </div>

          <!-- Toolbar Geolocation & Pencarian Cepat Peta -->
          <div class="bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-amber-500/20 p-3 sm:p-4 rounded-xl space-y-3">
            
            <!-- Quick Address/City Search on Map -->
            <div class="flex flex-col sm:flex-row items-center gap-2">
              <div class="relative w-full flex-1">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-amber-500">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                  </svg>
                </div>
                <input 
                  v-model="mapSearchQuery" 
                  type="text" 
                  @keydown.enter.prevent="searchLocationOnMap()"
                  placeholder="Ketik nama jalan, komplek, atau kota gereja untuk pencarian cepat..." 
                  class="form-control pl-9 text-xs" 
                />
              </div>

              <button 
                type="button" 
                @click="searchLocationOnMap()"
                :disabled="isSearchingLocation"
                class="w-full sm:w-auto px-4 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-1.5 shadow transition cursor-pointer disabled:opacity-50 shrink-0"
              >
                <svg v-if="isSearchingLocation" class="w-3.5 h-3.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                <span v-else>🔍</span>
                <span>{{ isSearchingLocation ? 'Mencari...' : 'Cari di Peta' }}</span>
              </button>
            </div>

            <!-- GPS Action & Reset Controls -->
            <div class="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-200 dark:border-slate-800">
              <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                <button 
                  type="button" 
                  @click="getCurrentLocation" 
                  :disabled="isLocating"
                  class="px-3.5 py-2.5 rounded-lg bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold text-xs flex flex-1 sm:flex-none items-center justify-center gap-2 shadow-md transition cursor-pointer disabled:opacity-50"
                  title="Ambil koordinat GPS perangkat langsung dari browser"
                >
                  <svg v-if="isLocating" class="w-3.5 h-3.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                  <span v-else class="text-sm">📍</span>
                  <span>{{ isLocating ? 'Mendeteksi GPS...' : 'Ambil Lokasi Saya (GPS Akurat)' }}</span>
                </button>

                <button 
                  type="button" 
                  @click="updateCoordinates(-6.1824, 106.9856, true)"
                  class="px-3 py-2.5 rounded-lg bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 text-xs transition cursor-pointer"
                  title="Reset titik pin ke default"
                >
                  🔄 Reset Pin
                </button>
              </div>

              <div class="flex items-center gap-2 w-full sm:w-auto">
                <a 
                  v-if="formData.latitude && formData.longitude"
                  :href="formData.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${formData.latitude},${formData.longitude}`" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="px-3 py-2.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/80 hover:bg-cyan-100 dark:hover:bg-cyan-900 border border-cyan-300 dark:border-cyan-700/60 text-cyan-800 dark:text-cyan-300 hover:text-cyan-900 dark:hover:text-cyan-200 text-xs font-medium transition flex w-full sm:w-auto items-center justify-center gap-1.5 no-underline"
                  style="text-decoration: none !important;"
                  title="Buka titik koordinat di Google Maps tab baru"
                >
                  <svg class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                  </svg>
                  <span>Buka di Google Maps ↗</span>
                </a>
              </div>
            </div>

          </div>

          <!-- Feedback Status Lokasi -->
          <div v-if="locationFeedback" :class="[
            'p-2.5 rounded-lg text-xs font-mono transition break-words',
            locationFeedback.includes('berhasil') || locationFeedback.includes('ditemukan') ? 'bg-emerald-50 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800' : 'bg-rose-50 dark:bg-rose-950/80 text-rose-800 dark:text-rose-300 border border-rose-300 dark:border-rose-800'
          ]">
            {{ locationFeedback }}
          </div>

          <!-- Leaflet Interactive Map Container (Langsung Muncul & Interaktif) -->
          <div class="gp-map relative h-[360px] sm:h-[420px] w-full rounded-xl overflow-hidden border-2 border-amber-500/50 shadow-2xl bg-slate-100 dark:bg-slate-950">
            <div ref="mapContainer" class="w-full h-full min-h-[360px] sm:min-h-[420px] z-10"></div>
            
            <!-- Live Overlay Floating Badge -->
            <div class="absolute top-3 right-3 z-[400] max-w-[calc(100%-5rem)] bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border border-slate-300 dark:border-amber-500/50 rounded-lg px-3 py-1.5 text-[11px] font-mono text-slate-800 dark:text-amber-300 shadow-lg flex items-center gap-1.5">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span class="font-bold truncate">Pin Aktif: {{ Number(formData.latitude).toFixed(6) }}, {{ Number(formData.longitude).toFixed(6) }}</span>
            </div>

            <!-- Hint overlay in bottom center of map -->
            <div class="absolute bottom-3 left-1/2 -translate-x-1/2 z-[400] bg-slate-950/80 backdrop-blur-sm text-amber-200 border border-amber-500/40 rounded-full px-3 py-1 text-[10px] font-medium shadow-md pointer-events-none hidden sm:flex items-center gap-1.5">
              <span>⛪ Klik pada peta atau geser pin emas untuk memindahkan lokasi gereja</span>
            </div>
          </div>

          <p class="text-[11px] text-slate-500 dark:text-slate-400 italic">
            💡 <strong>Panduan Interaktif:</strong> Peta di atas menampilkan titik lokasi langsung. Anda dapat:
            <span class="text-amber-600 dark:text-amber-400 font-semibold"> (1) Mengetik alamat &amp; klik "Cari di Peta"</span>, 
            <span class="text-amber-600 dark:text-amber-400 font-semibold">(2) Mengklik tombol "Ambil Lokasi Saya" untuk GPS akurat</span>, atau 
            <span class="text-amber-600 dark:text-amber-400 font-semibold">(3) Menggeser pin emas ⛪ langsung</span> ke gedung gereja Anda. Koordinat akan tersimpan otomatis ke PostgreSQL.
          </p>

          <!-- Input Koordinat Presisi -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Latitude (Garis Lintang) <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model.number="formData.latitude" 
                type="number" 
                step="any" 
                required
                @input="updateCoordinates(formData.latitude, formData.longitude, true)"
                placeholder="-6.182400" 
                class="form-control font-mono" 
              />
            </div>

            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Longitude (Garis Bujur) <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model.number="formData.longitude" 
                type="number" 
                step="any" 
                required
                @input="updateCoordinates(formData.latitude, formData.longitude, true)"
                placeholder="106.985600" 
                class="form-control font-mono" 
              />
            </div>

            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Tautan Google Maps URL
              </label>
              <input 
                v-model="formData.google_maps_url" 
                type="text" 
                readonly
                placeholder="https://maps.google.com/..." 
                class="form-control font-mono opacity-80 select-all" 
              />
            </div>
          </div>
        </div>

        <!-- SECTION 3: DATA ADMIN GEREJA -->
        <div class="space-y-4">
          <h3 class="section-title text-sm font-serif font-bold text-amber-600 dark:text-amber-300 border-b border-slate-200 dark:border-slate-800 pb-2 uppercase tracking-wider">
            👤 3. Penanggung Jawab / Admin Cabang
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <!-- Kolom: admin_name -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Nama Admin / Pengurus Cabang <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="formData.admin_name" 
                type="text" 
                required 
                placeholder="Contoh: Pdt. Hendra Setiawan" 
                class="form-control" 
              />
            </div>

            <!-- Kolom: email -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Email Pribadi Admin Gereja <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="formData.email" 
                type="email" 
                required 
                placeholder="hendra.setiawan@gmail.com" 
                class="form-control" 
              />
              <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Email pribadi admin sendiri (bukan email gereja) untuk masuk ke akun sistem.</p>
            </div>

            <!-- Kolom: phone -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                No. HP / WhatsApp <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="formData.phone" 
                type="tel" 
                required 
                placeholder="081234567890" 
                class="form-control" 
              />
            </div>

            <!-- Kolom: password -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Kata Sandi <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="formData.password" 
                type="password" 
                required 
                placeholder="Minimal 6 karakter" 
                class="form-control" 
              />
            </div>

            <!-- Konfirmasi Password -->
            <div class="md:col-span-2">
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Konfirmasi Kata Sandi <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="formData.confirmPassword" 
                type="password" 
                required 
                placeholder="Ulangi kata sandi" 
                class="form-control" 
              />
            </div>
          </div>
        </div>

        <!-- Submit & Footer Actions (Tanpa Garis Bawah) -->
        <div class="pt-6 border-t border-slate-200 dark:border-amber-500/20 flex flex-col-reverse sm:flex-row items-center justify-between gap-4">
          <RouterLink 
            to="/verification-login" 
            class="text-xs font-semibold text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 no-underline transition text-center"
            style="text-decoration: none !important;"
          >
            ← Sudah terdaftar? Masuk di sini
          </RouterLink>

          <button 
            type="submit" 
            :disabled="isSubmitting"
            class="w-full sm:w-auto px-8 py-3 bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-serif font-bold text-xs uppercase tracking-widest rounded-xl shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <span v-if="isSubmitting">Mendaftarkan ke PostgreSQL...</span>
            <span v-else>Daftar Admin Gereja</span>
          </button>
        </div>

      </form>
    </div>

    <!-- Footer Copyright -->
    <footer class="w-full py-4 text-center text-xs text-slate-500 dark:text-slate-400 z-10">
      &copy; 2026 GracePoint — Platform Manajemen &amp; Pelayanan Digital Gereja
    </footer>

    <!-- MODAL PENGAJUAN GEREJA BARU KE ADMIN UTAMA -->
    <div 
      v-if="showUnregisteredModal" 
      class="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-3 sm:p-4 overscroll-contain"
      role="dialog"
      aria-modal="true"
      aria-label="Pengajuan Pendaftaran Gereja Baru"
      @click.self="closeUnregisteredModal"
    >
      <div 
        class="modal-card w-full max-w-2xl bg-white dark:bg-slate-950 border border-slate-300 dark:border-amber-500/40 rounded-2xl shadow-2xl p-5 sm:p-7 relative text-slate-800 dark:text-slate-100 font-sans transition-colors"
      >
        <!-- Close Button -->
        <button 
          type="button" 
          @click="closeUnregisteredModal" 
          class="absolute top-4 right-4 w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 flex items-center justify-center transition cursor-pointer"
          title="Tutup"
          aria-label="Tutup"
        >
          ✕
        </button>

        <!-- Modal Header -->
        <div class="flex items-center gap-3.5 pb-4 pr-9 border-b border-slate-200 dark:border-amber-500/20 mb-4">
          <div class="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/40 text-amber-500 flex items-center justify-center shrink-0 shadow-lg">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <div>
            <h3 class="text-lg sm:text-xl font-bold font-serif text-amber-600 dark:text-amber-300">
              Pengajuan Pendaftaran Gereja Baru
            </h3>
            <p class="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
              Pilih 1 dari 3 metode penyampaian data gereja Anda ke Admin Utama (Superadmin).
            </p>
          </div>
        </div>

        <!-- 3 PILIHAN SALURAN PENGIRIMAN -->
        <div class="mb-4">
          <label class="block text-[11px] font-bold uppercase tracking-wider text-amber-600 dark:text-amber-300 mb-2">
            Pilih Metode Pengajuan:
          </label>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            
            <!-- Pilihan 2: Langsung ke Sistem -->
            <button 
              type="button" 
              @click="selectedChannel = 'direct'"
              :class="[
                'p-3 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between relative overflow-hidden',
                selectedChannel === 'direct' 
                  ? 'bg-amber-500/15 border-amber-500 text-amber-900 dark:text-amber-200 shadow-md ring-1 ring-amber-400' 
                  : 'bg-slate-50 dark:bg-slate-900/80 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700'
              ]"
            >
              <div class="flex items-center gap-1.5 font-bold text-xs text-amber-600 dark:text-amber-300">
                <span class="text-base">🏛️</span>
                <span>Langsung ke Sistem</span>
              </div>
              <p class="text-[10px] mt-1.5 text-slate-600 dark:text-slate-300 leading-snug">
                Masuk ke Notifikasi &amp; Inbox Superadmin di Dashboard secara instan.
              </p>
              <span class="mt-2 text-[9px] font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Rekomendasi ⭐</span>
            </button>

            <!-- Pilihan 1: WhatsApp -->
            <button 
              type="button" 
              @click="selectedChannel = 'wa'"
              :class="[
                'p-3 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between',
                selectedChannel === 'wa' 
                  ? 'bg-emerald-500/15 border-emerald-500 text-emerald-900 dark:text-emerald-200 shadow-md ring-1 ring-emerald-400' 
                  : 'bg-slate-50 dark:bg-slate-900/80 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700'
              ]"
            >
              <div class="flex items-center gap-1.5 font-bold text-xs text-emerald-600 dark:text-emerald-300">
                <span class="text-base">💬</span>
                <span>Chat WhatsApp</span>
              </div>
              <p class="text-[10px] mt-1.5 text-slate-600 dark:text-slate-300 leading-snug">
                Kirim chat terstruktur ke kontak WhatsApp Admin Utama.
              </p>
              <span class="mt-2 text-[9px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Chat Personal</span>
            </button>

            <!-- Pilihan 3: Email -->
            <button 
              type="button" 
              @click="selectedChannel = 'email'"
              :class="[
                'p-3 rounded-xl border text-left transition cursor-pointer flex flex-col justify-between',
                selectedChannel === 'email' 
                  ? 'bg-cyan-500/15 border-cyan-500 text-cyan-900 dark:text-cyan-200 shadow-md ring-1 ring-cyan-400' 
                  : 'bg-slate-50 dark:bg-slate-900/80 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700'
              ]"
            >
              <div class="flex items-center gap-1.5 font-bold text-xs text-cyan-600 dark:text-cyan-300">
                <span class="text-base">✉️</span>
                <span>Kirim via Email</span>
              </div>
              <p class="text-[10px] mt-1.5 text-slate-600 dark:text-slate-300 leading-snug">
                Buka email client &amp; kirim surat resmi ke Superadmin.
              </p>
              <span class="mt-2 text-[9px] font-semibold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider">Format Resmi</span>
            </button>

          </div>
        </div>

        <!-- Error in Modal -->
        <div v-if="modalError" class="mb-4 p-3 text-xs bg-rose-50 dark:bg-rose-950/80 border border-rose-300 dark:border-rose-800 text-rose-800 dark:text-rose-200 rounded-lg">
          ⚠️ {{ modalError }}
        </div>

        <!-- Waiting / Info Status Card -->
        <div v-if="isWaitingAdmin" class="mb-4 p-4 rounded-xl bg-emerald-50 dark:bg-slate-900 border border-emerald-300 dark:border-emerald-500/40 text-xs space-y-3">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center gap-2 text-emerald-700 dark:text-emerald-300 font-bold text-sm">
              <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
              <span>Permohonan Telah Diteruskan ke Admin Utama!</span>
            </div>
            <span v-if="submittedTicketId" class="px-2.5 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-mono text-[11px] font-bold">
              Tiket: {{ submittedTicketId }}
            </span>
          </div>

          <p class="text-slate-700 dark:text-slate-300 leading-relaxed">
            Data spesifik &amp; keluh kesah Anda telah berhasil dicatat. 
            Admin Utama akan memeriksa dan menginputkan data gereja Anda ke database DBMS. 
            <span class="text-amber-700 dark:text-amber-300 font-medium">Mohon tunggu selama beberapa menit</span>, kemudian klik tombol di bawah untuk memeriksa ketersediaan gereja di sistem:
          </p>

          <div class="flex flex-col sm:flex-row items-center gap-2.5 pt-1">
            <button 
              type="button" 
              @click="refreshChurchesAndCheck" 
              :disabled="isRefreshingChurches"
              class="w-full sm:w-auto px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs flex items-center justify-center gap-2 transition cursor-pointer disabled:opacity-50 shadow-lg"
            >
              <svg :class="{'animate-spin': isRefreshingChurches}" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span>{{ isRefreshingChurches ? 'Mengecek Database...' : '🔄 Refresh & Cek Daftar Gereja Sekarang' }}</span>
            </button>
          </div>
        </div>

        <!-- Formulir Detail Pengajuan Gereja Baru -->
        <div class="space-y-3.5">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-medium text-[11px] mb-1">
                Nama Lengkap Anda (Pendaftar) <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="unregisteredForm.applicantName" 
                type="text" 
                placeholder="Pdt. / Bpk. / Ibu" 
                class="form-control text-xs" 
              />
            </div>

            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-medium text-[11px] mb-1">
                No. WhatsApp Anda <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="unregisteredForm.applicantPhone" 
                type="tel" 
                placeholder="0812xxxxxxxx" 
                class="form-control text-xs" 
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-medium text-[11px] mb-1">
                Nama Gereja Induk / Sinode yang Diajukan <span class="text-rose-500">*</span>
              </label>
              <input 
                v-model="unregisteredForm.proposedMainChurch" 
                type="text" 
                placeholder="Contoh: Gereja Bethel Indonesia (GBI)" 
                class="form-control text-xs" 
              />
            </div>

            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-medium text-[11px] mb-1">
                Rencana Nama Cabang Lokal Anda
              </label>
              <input 
                v-model="unregisteredForm.proposedBranchChurch" 
                type="text" 
                placeholder="Contoh: GBI Glow Fellowship Karawaci" 
                class="form-control text-xs" 
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-medium text-[11px] mb-1">Kota / Kabupaten</label>
              <input 
                v-model="unregisteredForm.city" 
                type="text" 
                placeholder="Contoh: Tangerang, Banten" 
                class="form-control text-xs" 
              />
            </div>

            <div>
              <label class="block text-slate-700 dark:text-slate-300 font-medium text-[11px] mb-1">Pimpinan Sinode / BPP (Jika Tahu)</label>
              <input 
                v-model="unregisteredForm.leaderName" 
                type="text" 
                placeholder="Contoh: Pdt. Dr. Rubin Adi Abraham" 
                class="form-control text-xs" 
              />
            </div>
          </div>

          <div>
            <label class="block text-slate-700 dark:text-slate-300 font-medium text-[11px] mb-1">Alamat Lengkap Gereja</label>
            <input 
              v-model="unregisteredForm.address" 
              type="text" 
              placeholder="Alamat jalan, nomor, kelurahan, kecamatan" 
              class="form-control text-xs" 
            />
          </div>

          <div>
            <label class="block text-slate-700 dark:text-slate-300 font-medium text-[11px] mb-1">
              Catatan / Keluh Kesah Anda Mengenai Gereja yang Belum Terdaftar
            </label>
            <textarea 
              v-model="unregisteredForm.complaintNotes" 
              rows="2" 
              placeholder="Ceritakan kendala atau informasi tambahan perihal sinode gereja Anda..." 
              class="form-control text-xs"
            ></textarea>
          </div>

          <!-- Info Email Tujuan jika jalur Email dipilih -->
          <div v-if="selectedChannel === 'email'" class="p-3 rounded-xl bg-cyan-50 dark:bg-cyan-950/40 border border-cyan-300 dark:border-cyan-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <p class="text-cyan-800 dark:text-cyan-300 font-semibold text-xs">Email Tujuan Resmi Superadmin:</p>
              <code class="text-amber-700 dark:text-amber-300 font-mono text-[11px] break-all">{{ adminMainEmail }}</code>
            </div>
            <button 
              type="button" 
              @click="copyEmailBody" 
              class="px-3 py-1.5 rounded-lg bg-cyan-100 dark:bg-cyan-900/60 hover:bg-cyan-200 dark:hover:bg-cyan-800 text-cyan-900 dark:text-cyan-200 border border-cyan-300 dark:border-cyan-700/60 text-xs font-medium transition cursor-pointer flex w-full sm:w-auto shrink-0 items-center justify-center gap-1.5"
            >
              <span>{{ isCopiedEmail ? '✅ Tersalin!' : '📋 Salin Teks Email' }}</span>
            </button>
          </div>

        </div>

        <!-- Modal Footer Actions Sesuai Channel Terpilih -->
        <div class="modal-footer bg-white dark:bg-slate-950 mt-5 pt-4 border-t border-slate-200 dark:border-slate-800 flex flex-col-reverse sm:flex-row items-center justify-between gap-3">
          <button 
            type="button" 
            @click="closeUnregisteredModal" 
            class="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900 text-xs font-medium transition cursor-pointer"
          >
            Tutup / Batal
          </button>

          <div class="flex items-center gap-2 w-full sm:w-auto">
            
            <!-- Tombol Action untuk Channel 2: Langsung ke Sistem -->
            <button 
              v-if="selectedChannel === 'direct'"
              type="button" 
              @click="sendDirectSystemRequest" 
              :disabled="isSubmittingRequest"
              class="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:brightness-110 text-slate-950 font-bold text-xs rounded-xl shadow-lg hover:shadow-amber-500/20 transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              <svg :class="{'animate-spin': isSubmittingRequest}" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
              <span>{{ isSubmittingRequest ? 'Mengirimkan ke Sistem...' : '🏛️ Kirim Langsung ke Sistem Admin Utama' }}</span>
            </button>

            <!-- Tombol Action untuk Channel 1: WhatsApp -->
            <button 
              v-else-if="selectedChannel === 'wa'"
              type="button" 
              @click="sendWhatsAppRequest" 
              class="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-emerald-600 via-emerald-500 to-emerald-600 hover:from-emerald-500 hover:to-emerald-500 text-white font-bold text-xs rounded-xl shadow-lg hover:shadow-emerald-500/25 transition flex items-center justify-center gap-2 cursor-pointer"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/>
              </svg>
              <span>Kirim Chat WhatsApp ke Admin Utama</span>
            </button>

            <!-- Tombol Action untuk Channel 3: Email -->
            <button 
              v-else-if="selectedChannel === 'email'"
              type="button" 
              @click="sendEmailRequest" 
              class="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-cyan-600 via-cyan-500 to-cyan-600 hover:from-cyan-500 hover:to-cyan-500 text-white font-bold text-xs rounded-xl shadow-lg hover:shadow-cyan-500/25 transition flex items-center justify-center gap-2 cursor-pointer"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <span>✉️ Luncurkan Email Client</span>
            </button>

          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

.font-serif {
  font-family: 'Cinzel', 'Playfair Display', Georgia, 'Times New Roman', serif;
}

/* Hilangkan semua garis bawah pada teks tautan secara mutlak */
a,
a:hover,
a:focus,
a:active,
a:visited,
.brand-link,
.brand-link * {
  text-decoration: none !important;
}

/* ===== Tata letak halaman ===== */
/* 100dvh mengikuti tinggi layar sebenarnya di HP (bar alamat naik/turun), 100vh sebagai cadangan */
.page-root {
  min-height: 100vh;
  min-height: 100dvh;
  padding-top: 1.5rem;
  padding-bottom: max(1.5rem, env(safe-area-inset-bottom, 0px));
}

h1,
h3 {
  text-wrap: balance;
}

/* Penanda judul seksi: garis emas di kiri */
.section-title {
  padding-left: 0.75rem;
  box-shadow: inset 3px 0 0 0 #f59e0b;
}

/* Fokus keyboard yang jelas untuk tautan & tombol */
a:focus-visible,
button:focus-visible {
  outline: 2px solid #f59e0b;
  outline-offset: 2px;
}

/* ===== Kontrol form: satu sumber warna lewat variabel, otomatis mengikuti tema ===== */
.form-control {
  --fc-bg: var(--theme-bg-primary, #ffffff);
  --fc-border: rgba(148, 163, 184, 0.4);
  --fc-text: var(--theme-text-primary, #0f172a);
  --fc-placeholder: #94a3b8;
  --fc-chevron: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");

  display: block;
  width: 100%;
  min-height: 2.75rem; /* target sentuh nyaman di HP */
  padding: 0.625rem 0.875rem;
  font-size: 1rem; /* 16px mencegah auto-zoom di iOS saat input difokuskan */
  line-height: 1.4;
  border-radius: 0.75rem;
  border: 1px solid;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
  background-color: var(--fc-bg) !important;
  border-color: var(--fc-border) !important;
  color: var(--fc-text) !important;
}

@media (min-width: 640px) {
  .form-control {
    font-size: 0.875rem;
  }
}

/* Tema gelap */
html[data-theme="dark"] .form-control,
html.dark .form-control {
  --fc-bg: #0f172a;
  --fc-border: rgba(71, 85, 105, 0.8);
  --fc-text: #f8fafc;
  --fc-placeholder: #64748b;
  --fc-chevron: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  color-scheme: dark; /* ikon kalender, scrollbar, & dropdown ikut gelap */
}

/* Tema terang */
html[data-theme="light"] .form-control,
html.light .form-control {
  --fc-bg: #ffffff;
  --fc-border: #cbd5e1;
  --fc-text: #0f172a;
  --fc-placeholder: #94a3b8;
  --fc-chevron: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  color-scheme: light;
}

.form-control::placeholder {
  color: var(--fc-placeholder);
  opacity: 1;
}

/* Dropdown: panah kustom yang konsisten di semua peramban */
select.form-control {
  -webkit-appearance: none;
  appearance: none;
  padding-right: 2.5rem;
  background-image: var(--fc-chevron);
  background-repeat: no-repeat;
  background-position: right 0.875rem center;
  background-size: 1rem;
  cursor: pointer;
  text-overflow: ellipsis;
}

.form-control option {
  background-color: var(--fc-bg);
}

/* Input tanggal: tidak melebar di iOS */
.form-control[type="date"] {
  -webkit-appearance: none;
  appearance: none;
  min-width: 0;
}

.form-control[type="date"]::-webkit-date-and-time-value {
  text-align: left;
}

textarea.form-control {
  resize: vertical;
}

.form-control:focus {
  outline: none;
  border-color: #f59e0b !important;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.25);
}

/* Tanda salah isi baru muncul setelah pengguna berinteraksi (tanpa JS) */
@supports selector(:user-invalid) {
  .form-control:user-invalid {
    border-color: #f43f5e !important;
  }

  .form-control:user-invalid:focus {
    box-shadow: 0 0 0 3px rgba(244, 63, 94, 0.22);
  }
}

/* Isi otomatis peramban (autofill) tetap terbaca di mode gelap */
.form-control:-webkit-autofill,
.form-control:-webkit-autofill:hover {
  -webkit-text-fill-color: var(--fc-text);
  caret-color: var(--fc-text);
  box-shadow: 0 0 0 1000px var(--fc-bg) inset;
  transition: background-color 9999s ease-out 0s;
}

.form-control:-webkit-autofill:focus {
  -webkit-text-fill-color: var(--fc-text);
  caret-color: var(--fc-text);
  box-shadow: 0 0 0 1000px var(--fc-bg) inset, 0 0 0 3px rgba(245, 158, 11, 0.25);
}

.form-control[readonly] {
  cursor: default;
}

.form-control:disabled,
select.form-control:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ===== Peta Leaflet ===== */
.gp-map {
  height: 380px !important;
  min-height: 380px !important;
  position: relative !important;
}

@media (min-width: 640px) {
  .gp-map {
    height: 440px !important;
    min-height: 440px !important;
  }
}

:deep(.leaflet-container) {
  width: 100% !important;
  height: 100% !important;
  min-height: 380px !important;
  border-radius: 0.75rem;
  font-family: inherit;
  z-index: 10;
}

:deep(.leaflet-tile) {
  max-width: none !important;
  max-height: none !important;
}

@media (min-width: 640px) {
  :deep(.leaflet-container) {
    min-height: 440px !important;
  }
}

.gp-map :deep(.leaflet-control-zoom) {
  border: 0 !important;
  border-radius: 0.625rem;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
}

.gp-map :deep(.leaflet-bar a) {
  width: 2.25rem;
  height: 2.25rem;
  line-height: 2.25rem;
}

/* Peta ikut gelap di mode gelap (hanya lapisan ubin; pin & popup tetap normal) */
html[data-theme="dark"] .gp-map :deep(.leaflet-tile-pane),
html.dark .gp-map :deep(.leaflet-tile-pane) {
  filter: invert(1) hue-rotate(180deg) brightness(0.95) contrast(0.9);
}

html[data-theme="dark"] .gp-map :deep(.leaflet-bar a),
html.dark .gp-map :deep(.leaflet-bar a) {
  background-color: #0f172a;
  color: #e2e8f0;
  border-bottom-color: #334155;
}

/* ===== Modal pengajuan: seluruh kartu bisa di-scroll, tombol aksi menempel di bawah ===== */
.modal-card {
  max-height: calc(100vh - 1.5rem);
  max-height: calc(100dvh - 1.5rem);
  overflow-y: auto;
  overscroll-behavior: contain;
}

.modal-footer {
  position: sticky;
  bottom: 0;
  z-index: 5;
  margin-left: -1.25rem;
  margin-right: -1.25rem;
  padding-left: 1.25rem;
  padding-right: 1.25rem;
  padding-bottom: 0.25rem;
}

@media (min-width: 640px) {
  .modal-card {
    max-height: calc(100vh - 2rem);
    max-height: calc(100dvh - 2rem);
  }

  .modal-footer {
    margin-left: -1.75rem;
    margin-right: -1.75rem;
    padding-left: 1.75rem;
    padding-right: 1.75rem;
  }
}

/* Hormati pengaturan "kurangi gerakan" dari sistem */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>