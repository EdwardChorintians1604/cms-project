<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import { useAuth } from '@/composables/useAuth'
import { APP_CONFIG } from '@/config'
import { storage } from '@/utils'
import { STORAGE_KEYS } from '@/constants'

const { user } = useAuth()

// Resolusi API Base URL
const apiBaseUrl = computed(() => {
  return APP_CONFIG?.apiBaseUrl || APP_CONFIG?.API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
})

// Status DBMS PostgreSQL
const dbmsStatus = reactive({
  connected: false,
  engine: 'PostgreSQL',
  table: 'church_ministries',
  lastStatus: 'Menghubungkan ke DBMS...',
})

// Konteks Cabang Gereja Aktif
const activeChurch = reactive({
  id: null,
  code: '',
  name: 'Gereja Cabang',
  adminName: 'Admin Gereja',
})

// Helper Auth Token & Headers
const getAuthToken = () => {
  return (
    storage.get(STORAGE_KEYS.AUTH_TOKEN) ||
    localStorage.getItem('cms_auth_token') ||
    localStorage.getItem('gp_auth_token') ||
    localStorage.getItem('token') ||
    ''
  )
}

const getAuthHeaders = () => {
  const token = getAuthToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

// State Data & Tampilan
const isLoading = ref(true)
const isSubmitting = ref(false)
const isSyncing = ref(false)
const viewMode = ref('grid') // 'grid' | 'table'
const selectedCategory = ref('Semua')
const searchQuery = ref('')
const lastSyncTime = ref('-')

// Notification Toast
const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

const showToast = (message, type = 'success') => {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 4500)
}

// Modal State
const isModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const modalMode = ref('create') // 'create' | 'edit'
const selectedMinistry = ref(null)

// Form State
const defaultForm = {
  id: null,
  name: '',
  code: '',
  category: 'Kategorial Usia',
  leader_structure_id: null,
  leader_name: '',
  leader_title: 'Koordinator',
  phone: '',
  email: '',
  member_count: 0,
  meeting_schedule: '',
  location_room: '',
  budget_allocation: '',
  description: '',
  vision_mission: '',
  status: 'Aktif',
  sort_order: 0
}

const formData = reactive({ ...defaultForm })

// Ministry List Data
const ministryList = ref([])
const structureList = ref([])

// Fetch Structure to integrate leader PIC
const fetchStructure = async () => {
  try {
    let url = `${apiBaseUrl.value}/church-structure/`
    if (activeChurch.code && activeChurch.code !== 'DEFAULT') {
      url += `?church_code=${encodeURIComponent(activeChurch.code)}`
    }
    const res = await fetch(url, { headers: getAuthHeaders() })
    if (res.ok) {
      structureList.value = await res.json()
    }
  } catch (err) {
    console.warn('Could not fetch structure for ministry integration:', err)
  }
}

// When leader officer is selected from structure dropdown
const onLeaderSelect = () => {
  if (formData.leader_structure_id) {
    const officer = structureList.value.find(s => s.id === formData.leader_structure_id)
    if (officer) {
      formData.leader_name = officer.name
      formData.leader_title = officer.title || 'Koordinator'
      if (officer.phone) formData.phone = officer.phone
      if (officer.email) formData.email = officer.email
    }
  }
}

// Kategori Pilihan
const categoryOptions = [
  'Semua',
  'Kategorial Usia',
  'Musik & Ibadah',
  'Diakonia & Doa',
  'Misi & Penginjilan',
  'Pembinaan Iman',
  'Operasional & Fasilitas'
]

// Inisialisasi Konteks Cabang Gereja
const initChurchContext = async () => {
  try {
    let userData = user.value || {}

    if (!userData.church_code) {
      const stored = storage.get(STORAGE_KEYS.USER_DATA)
      if (stored) userData = { ...userData, ...stored }
    }

    const token = getAuthToken()
    if (token) {
      try {
        const meRes = await fetch(`${apiBaseUrl.value}/users/me`, {
          headers: getAuthHeaders(),
        })
        if (meRes.ok) {
          const meData = await meRes.json()
          userData = { ...userData, ...meData }
        }
      } catch (e) {
        console.warn('Could not fetch /users/me:', e)
      }
    }

    const adminId = userData.id || userData.church_admin_id
    if (adminId) {
      try {
        const adminRes = await fetch(`${apiBaseUrl.value}/church-admins/${adminId}`, {
          headers: getAuthHeaders(),
        })
        if (adminRes.ok) {
          const adminDetail = await adminRes.json()
          userData = { ...userData, ...adminDetail }
        }
      } catch (e) {
        console.warn('Could not fetch church-admins detail:', e)
      }
    }

    activeChurch.id = userData.church_id || null
    activeChurch.code = userData.church_code || ''
    activeChurch.name = userData.church_name || 'Gereja Cabang'
    activeChurch.adminName = userData.admin_name || userData.name || 'Admin Gereja'
  } catch (err) {
    console.error('Error resolving church context:', err)
  }
}

// Fetch Ministries from PostgreSQL
const fetchMinistries = async (silent = false) => {
  if (!silent) isLoading.value = true
  isSyncing.value = true
  try {
    let url = `${apiBaseUrl.value}/church-ministries/`
    const params = new URLSearchParams()
    
    if (activeChurch.code && activeChurch.code !== 'DEFAULT') {
      params.append('church_code', activeChurch.code)
    }
    if (activeChurch.id) {
      params.append('church_id', activeChurch.id)
    }
    
    const queryString = params.toString()
    if (queryString) {
      url += `?${queryString}`
    }

    const res = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders(),
    })

    if (res.ok) {
      const data = await res.json()
      ministryList.value = Array.isArray(data) ? data : []
      dbmsStatus.connected = true
      dbmsStatus.lastStatus = `Terhubung ke PostgreSQL (${ministryList.value.length} lembaga pelayanan)`
      const now = new Date()
      lastSyncTime.value = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    } else {
      dbmsStatus.connected = false
      dbmsStatus.lastStatus = `HTTP ${res.status}: Gagal memuat data dari PostgreSQL`
      showToast('Gagal memuat data lembaga pelayanan dari server PostgreSQL', 'error')
    }
  } catch (err) {
    console.error('Fetch ministries error:', err)
    dbmsStatus.connected = false
    dbmsStatus.lastStatus = 'Koneksi ke DBMS PostgreSQL terputus'
    showToast('Koneksi terputus saat mengambil data lembaga pelayanan dari DBMS', 'error')
  } finally {
    isLoading.value = false
    isSyncing.value = false
  }
}

// Stats & Metrik
const totalMinistries = computed(() => ministryList.value.length)
const totalVolunteers = computed(() => {
  return ministryList.value.reduce((acc, cur) => acc + (Number(cur.member_count) || 0), 0)
})
const uniqueCategories = computed(() => {
  const set = new Set(ministryList.value.map(i => i.category).filter(Boolean))
  return set.size
})
const activeMinistriesCount = computed(() => {
  return ministryList.value.filter(i => i.status === 'Aktif').length
})

// Filtered List
const filteredMinistries = computed(() => {
  return ministryList.value.filter(item => {
    const matchCat = selectedCategory.value === 'Semua' || item.category === selectedCategory.value
    const q = searchQuery.value.toLowerCase().trim()
    const matchSearch = !q ||
      item.name?.toLowerCase().includes(q) ||
      item.code?.toLowerCase().includes(q) ||
      item.leader_name?.toLowerCase().includes(q) ||
      item.meeting_schedule?.toLowerCase().includes(q) ||
      item.location_room?.toLowerCase().includes(q)
    return matchCat && matchSearch
  })
})

// Buka Modal Tambah
const openCreateModal = () => {
  modalMode.value = 'create'
  Object.assign(formData, defaultForm)
  formData.church_id = activeChurch.id
  formData.church_code = activeChurch.code
  isModalOpen.value = true
}

// Buka Modal Edit
const openEditModal = (item) => {
  modalMode.value = 'edit'
  Object.assign(formData, item)
  isModalOpen.value = true
}

// Buka Detail Modal
const openDetailModal = (item) => {
  selectedMinistry.value = item
  isDetailModalOpen.value = true
}

// Buka Modal Hapus
const confirmDelete = (item) => {
  selectedMinistry.value = item
  isDeleteModalOpen.value = true
}

// Simpan Data (Create / Update)
const handleSubmit = async () => {
  if (!formData.name) {
    showToast('Nama Lembaga / Departemen Pelayanan wajib diisi!', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const isEdit = modalMode.value === 'edit'
    const url = isEdit
      ? `${apiBaseUrl.value}/church-ministries/${formData.id}`
      : `${apiBaseUrl.value}/church-ministries/`
    const method = isEdit ? 'PUT' : 'POST'

    const payload = {
      ...formData,
      church_code: activeChurch.code || formData.church_code || null,
      church_id: activeChurch.id || formData.church_id || null,
      member_count: Number(formData.member_count) || 0,
    }

    const res = await fetch(url, {
      method,
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })

    if (res.ok) {
      showToast(isEdit ? 'Data lembaga pelayanan berhasil diperbarui di PostgreSQL!' : 'Lembaga pelayanan baru berhasil didaftarkan!', 'success')
      isModalOpen.value = false
      await fetchMinistries(true)
    } else {
      const err = await res.json().catch(() => ({}))
      showToast(err.detail || 'Gagal menyimpan perubahan ke server', 'error')
    }
  } catch (err) {
    console.error('Submit error:', err)
    showToast('Terjadi kesalahan jaringan saat menyimpan', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Eksekusi Hapus Data
const executeDelete = async () => {
  if (!selectedMinistry.value) return
  isSubmitting.value = true
  try {
    const url = `${apiBaseUrl.value}/church-ministries/${selectedMinistry.value.id}`
    const res = await fetch(url, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    })

    if (res.ok) {
      showToast(`Lembaga "${selectedMinistry.value.name}" berhasil dihapus dari basis data`, 'success')
      isDeleteModalOpen.value = false
      selectedMinistry.value = null
      await fetchMinistries(true)
    } else {
      showToast('Gagal menghapus data dari PostgreSQL', 'error')
    }
  } catch (err) {
    console.error('Delete error:', err)
    showToast('Terjadi kesalahan saat menghapus data', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Seed Default Template Lembaga Pelayanan
const seedDefaultMinistries = async () => {
  if (ministryList.value.length > 0) {
    if (!confirm('Daftar lembaga sudah memiliki data. Apakah Anda tetap ingin menambahkan template standar lembaga pelayanan cabang?')) {
      return
    }
  }
  isSyncing.value = true
  try {
    const codeParam = activeChurch.code ? encodeURIComponent(activeChurch.code) : ''
    const url = `${apiBaseUrl.value}/church-ministries/seed-default${codeParam ? `?church_code=${codeParam}` : ''}`
    const res = await fetch(url, {
      method: 'POST',
      headers: getAuthHeaders(),
    })
    if (res.ok) {
      showToast('Template lembaga pelayanan baku jemaat berhasil dimuat ke DBMS!', 'success')
      await fetchMinistries(true)
    } else {
      showToast('Gagal memuat template lembaga pelayanan', 'error')
    }
  } catch (err) {
    console.error('Seed error:', err)
    showToast('Gagal memproses inisialisasi lembaga pelayanan', 'error')
  } finally {
    isSyncing.value = false
  }
}

// Cetak Laporan
const printReport = () => {
  window.print()
}

// Helper Inisial Avatar
const getInitials = (name) => {
  if (!name) return 'LP'
  return name.split(' ').map(n => n[0]).filter(Boolean).slice(0, 2).join('').toUpperCase()
}

// Helper Warna Kategori
const getCategoryBadgeClass = (category) => {
  switch (category) {
    case 'Kategorial Usia':
      return 'bg-purple-500/15 text-purple-300 border-purple-500/30'
    case 'Musik & Ibadah':
      return 'bg-amber-500/15 text-amber-300 border-amber-500/30'
    case 'Diakonia & Doa':
      return 'bg-rose-500/15 text-rose-300 border-rose-500/30'
    case 'Misi & Penginjilan':
      return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
    case 'Pembinaan Iman':
      return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
    case 'Operasional & Fasilitas':
      return 'bg-blue-500/15 text-blue-300 border-blue-500/30'
    default:
      return 'bg-slate-700 text-slate-300 border-slate-600'
  }
}

onMounted(async () => {
  await initChurchContext()
  await fetchMinistries()
  await fetchStructure()
})
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6 pb-12 print:p-0 print:space-y-4">
      
      <!-- Toast Alert -->
      <transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-4 opacity-0" enter-to-class="transform translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0 opacity-100" leave-to-class="transform -translate-y-4 opacity-0">
        <div v-if="toast.show" class="fixed top-5 right-5 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-2xl border backdrop-blur-md"
             :class="toast.type === 'success' ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-200' : 'bg-rose-950/90 border-rose-500/50 text-rose-200'">
          <svg v-if="toast.type === 'success'" class="w-5 h-5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-5 h-5 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      </transition>

      <!-- Header Section -->
      <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl relative overflow-hidden shadow-xl">
        <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div class="flex flex-wrap items-center gap-3 mb-2">
              <!-- DBMS Status Indicator -->
              <div class="flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-semibold"
                   :class="dbmsStatus.connected 
                     ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
                     : 'bg-rose-500/10 border-rose-500/30 text-rose-400'">
                <span class="w-2 h-2 rounded-full"
                      :class="dbmsStatus.connected ? 'bg-emerald-400 animate-ping' : 'bg-rose-400'"></span>
                {{ dbmsStatus.connected ? 'PostgreSQL Live Sync' : 'Koneksi DBMS Terputus' }}
              </div>

              <!-- Church Branch Info -->
              <div class="px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold">
                {{ activeChurch.code || 'Cabang Aktif' }} • {{ activeChurch.name }}
              </div>
              <span class="text-xs text-slate-400">Sinkron: {{ lastSyncTime }}</span>
            </div>

            <h1 class="text-2xl lg:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
              <svg class="w-8 h-8 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Lembaga Pelayanan Cabang & Departemen Jemaat
            </h1>
            <p class="text-sm text-slate-400 mt-1 max-w-2xl">
              Pusat kendali dan administrasi seluruh komisi kategorial, departemen ibadah, diakonia, dan sayap pelayanan jemaat cabang gereja yang tersinkronisasi langsung ke DBMS PostgreSQL (<code class="text-cyan-400/80 font-mono text-xs">tabel church_ministries</code>).
            </p>
          </div>

          <!-- Quick Action Buttons -->
          <div class="flex flex-wrap items-center gap-3 print:hidden">
            <button 
              @click="fetchMinistries(false)"
              :disabled="isSyncing"
              class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl border border-slate-700 flex items-center gap-2 transition disabled:opacity-50">
              <svg class="w-4 h-4 text-slate-400" :class="{'animate-spin': isSyncing}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Sinkron Ulang
            </button>

            <button 
              v-if="ministryList.length === 0"
              @click="seedDefaultMinistries"
              :disabled="isSyncing"
              class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition">
              <svg class="w-4 h-4 text-indigo-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Gunakan Template Baku
            </button>

            <button 
              @click="printReport"
              class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl border border-slate-700 flex items-center gap-2 transition">
              <svg class="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              Cetak Laporan
            </button>

            <button 
              @click="openCreateModal"
              class="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-sm rounded-xl shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition transform active:scale-95">
              <svg class="w-5 h-5 text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
              </svg>
              + Tambah Lembaga Pelayanan
            </button>
          </div>
        </div>

        <!-- Metrics Bar -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-800/80">
          <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-800/60">
            <div class="text-xs font-medium text-slate-400">Total Lembaga & Komisi</div>
            <div class="text-2xl font-black text-cyan-400 mt-1 flex items-baseline gap-2">
              {{ totalMinistries }}
              <span class="text-xs font-normal text-slate-400">departemen</span>
            </div>
          </div>
          <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-800/60">
            <div class="text-xs font-medium text-slate-400">Total Relawan & Pelayan</div>
            <div class="text-2xl font-black text-amber-400 mt-1 flex items-baseline gap-2">
              {{ totalVolunteers }}
              <span class="text-xs font-normal text-slate-400">orang jemaat</span>
            </div>
          </div>
          <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-800/60">
            <div class="text-xs font-medium text-slate-400">Sektor / Kategori Pelayanan</div>
            <div class="text-2xl font-black text-purple-400 mt-1 flex items-baseline gap-2">
              {{ uniqueCategories }}
              <span class="text-xs font-normal text-slate-400">sektor aktif</span>
            </div>
          </div>
          <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-800/60">
            <div class="text-xs font-medium text-slate-400">Status Keaktifan Cabang</div>
            <div class="text-2xl font-black text-emerald-400 mt-1 flex items-baseline gap-2">
              {{ activeMinistriesCount }}/{{ totalMinistries }}
              <span class="text-xs font-normal text-slate-400">aktif melayani</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Controls & Filter Switcher -->
      <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800 print:hidden">
        <!-- Tabs Mode -->
        <div class="flex items-center gap-1 bg-slate-950/60 p-1 rounded-lg border border-slate-800">
          <button 
            @click="viewMode = 'grid'"
            class="flex items-center gap-2 px-4 py-2 rounded-md text-xs font-bold transition"
            :class="viewMode === 'grid' ? 'bg-cyan-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Kartu Lembaga Pelayanan
          </button>
          <button 
            @click="viewMode = 'table'"
            class="flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition"
            :class="viewMode === 'table' ? 'bg-cyan-500 text-slate-950 font-bold shadow-md' : 'text-slate-400 hover:text-white'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Tabel Data DBMS
          </button>
        </div>

        <!-- Filters & Search -->
        <div class="flex flex-wrap items-center gap-3">
          <!-- Category Filter -->
          <div class="relative">
            <select 
              v-model="selectedCategory"
              class="bg-slate-950/80 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 pr-8 focus:ring-1 focus:ring-cyan-500 focus:outline-none">
              <option v-for="cat in categoryOptions" :key="cat" :value="cat">
                Sektor: {{ cat }}
              </option>
            </select>
          </div>

          <!-- Search Input -->
          <div class="relative min-w-[240px]">
            <input 
              v-model="searchQuery"
              type="text"
              placeholder="Cari lembaga, kode, ketua, jadwal..."
              class="w-full bg-slate-950/80 border border-slate-700 text-slate-200 text-xs rounded-lg pl-8 pr-3 py-2 focus:ring-1 focus:ring-cyan-500 focus:outline-none placeholder:text-slate-500" />
            <svg class="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="py-20 flex flex-col items-center justify-center space-y-4">
        <div class="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
        <p class="text-sm text-slate-400">Menghubungkan ke DBMS PostgreSQL & mengambil daftar lembaga pelayanan...</p>
      </div>

      <!-- Connection Broken State -->
      <div v-else-if="!dbmsStatus.connected" class="py-12 bg-rose-950/20 border border-rose-500/30 rounded-2xl flex flex-col items-center justify-center text-center p-6">
        <div class="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-3">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 class="text-base font-bold text-white">Koneksi DBMS PostgreSQL Terputus</h3>
        <p class="text-xs text-rose-300/80 max-w-md mt-1 mb-4">
          {{ dbmsStatus.lastStatus }}. Pastikan backend FastAPI di port 8000 dan basis data PostgreSQL aktif.
        </p>
        <button 
          @click="fetchMinistries(false)" 
          class="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-rose-600/20 flex items-center gap-2 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Coba Hubungkan Ulang Sekarang
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="ministryList.length === 0" class="py-16 bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center text-center p-6">
        <div class="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white">Belum Ada Lembaga Pelayanan Terdaftar</h3>
        <p class="text-sm text-slate-400 max-w-md mt-1 mb-6">
          Cabang ini belum memiliki data departemen lembaga pelayanan. Anda dapat memuat 7 lembaga pelayanan baku jemaat atau menambahkannya secara mandiri.
        </p>
        <div class="flex flex-wrap items-center justify-center gap-3">
          <button 
            @click="seedDefaultMinistries" 
            class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Terapkan 7 Lembaga Pelayanan Baku Gereja
          </button>
          <button 
            @click="openCreateModal" 
            class="px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm rounded-xl shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Tambah Lembaga Pertama
          </button>
        </div>
      </div>

      <!-- VIEW MODE 1: GRID KARTU LEMBAGA PELAYANAN -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="item in filteredMinistries" 
          :key="item.id"
          class="bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 hover:border-cyan-500/50 rounded-2xl p-5 shadow-xl transition-all duration-300 flex flex-col justify-between group relative overflow-hidden">
          
          <!-- Top Accent Light -->
          <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500"></div>

          <div>
            <!-- Top Badges -->
            <div class="flex items-start justify-between gap-2 mb-3 pt-1">
              <div class="flex flex-wrap items-center gap-2">
                <span v-if="item.code" class="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono text-[10px] font-bold border border-slate-700">
                  {{ item.code }}
                </span>
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold border" :class="getCategoryBadgeClass(item.category)">
                  {{ item.category }}
                </span>
              </div>
              <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold"
                    :class="item.status === 'Aktif' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-rose-500/15 text-rose-300'">
                {{ item.status }}
              </span>
            </div>

            <!-- Title & Description -->
            <h3 class="text-base font-bold text-white group-hover:text-cyan-300 transition leading-snug">
              {{ item.name }}
            </h3>
            <p v-if="item.description" class="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
              {{ item.description }}
            </p>

            <!-- Leader / PIC Box -->
            <div class="mt-4 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 space-y-2">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 flex items-center justify-center font-bold text-xs shrink-0">
                  {{ getInitials(item.leader_name) }}
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex items-center justify-between gap-1">
                    <span class="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">
                      {{ item.leader_title || 'Ketua / PIC' }}
                    </span>
                    <RouterLink 
                      to="/church-structure" 
                      class="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 hover:bg-amber-500/20 transition flex items-center gap-0.5" 
                      title="Lihat di Bagan Struktur">
                      <span>🌳</span> Bagan
                    </RouterLink>
                  </div>
                  <p class="text-xs font-bold text-white truncate" :title="item.leader_name">
                    {{ item.leader_name || 'Belum Ditetapkan' }}
                  </p>
                </div>
              </div>

              <!-- Quick Contact Links -->
              <div v-if="item.phone || item.email" class="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
                <div class="flex items-center gap-2">
                  <a v-if="item.phone" :href="'https://wa.me/' + item.phone.replace(/[^0-9]/g, '')" target="_blank" class="p-1 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition" title="WhatsApp PIC">
                    <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.664-.698c.969.584 1.961.913 2.796.914h.005c3.18 0 5.767-2.587 5.768-5.766 0-3.181-2.587-5.767-5.768-5.767zm0 10.536h-.004c-.868 0-1.748-.242-2.545-.715l-.182-.108-1.58.414.422-1.541-.118-.188c-.521-.83-.796-1.794-.795-2.784.001-2.628 2.14-4.767 4.77-4.767 2.628 0 4.767 2.139 4.768 0 2.628-2.139 4.768-4.768 4.768z"/></svg>
                  </a>
                  <a v-if="item.email" :href="'mailto:' + item.email" class="p-1 rounded bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 transition" title="Email Departemen">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                  </a>
                  <span class="text-[11px] text-slate-400 font-mono">{{ item.phone || item.email }}</span>
                </div>
              </div>
            </div>

            <!-- Schedule & Member Count -->
            <div class="mt-3 grid grid-cols-2 gap-2 text-xs">
              <div class="bg-slate-950/40 p-2 rounded-lg border border-slate-800/40">
                <span class="text-[10px] text-slate-500 block">Pelayan / Relawan</span>
                <span class="font-bold text-amber-400">{{ item.member_count || 0 }} Orang</span>
              </div>
              <div class="bg-slate-950/40 p-2 rounded-lg border border-slate-800/40 truncate">
                <span class="text-[10px] text-slate-500 block">Jadwal Rutin</span>
                <span class="font-medium text-slate-300 truncate block" :title="item.meeting_schedule">
                  {{ item.meeting_schedule || 'Kondisional' }}
                </span>
              </div>
            </div>

            <div v-if="item.location_room" class="mt-2 text-[11px] text-slate-400 flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5 text-slate-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span class="truncate">{{ item.location_room }}</span>
            </div>
          </div>

          <!-- Bottom Actions -->
          <div class="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
            <button 
              @click="openDetailModal(item)"
              class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium rounded-lg transition flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
              Detail
            </button>

            <div class="flex items-center gap-1.5">
              <button 
                @click="openEditModal(item)"
                class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-semibold rounded-lg border border-slate-700 flex items-center gap-1.5 transition">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                Edit
              </button>
              <button 
                @click="confirmDelete(item)"
                class="p-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded-lg border border-rose-500/30 transition"
                title="Hapus Lembaga">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- VIEW MODE 2: TABEL DATA DBMS -->
      <div v-else-if="viewMode === 'table'" class="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th class="py-3.5 px-4">No</th>
                <th class="py-3.5 px-4">Kode & Lembaga Pelayanan</th>
                <th class="py-3.5 px-4">Kategori Sektor</th>
                <th class="py-3.5 px-4">Ketua / PIC Lembaga</th>
                <th class="py-3.5 px-4">Anggota</th>
                <th class="py-3.5 px-4">Jadwal & Ruangan</th>
                <th class="py-3.5 px-4">Status</th>
                <th class="py-3.5 px-4 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              <tr v-for="(item, index) in filteredMinistries" :key="item.id" class="hover:bg-slate-800/40 transition">
                <td class="py-3.5 px-4 text-slate-400">{{ index + 1 }}</td>
                <td class="py-3.5 px-4">
                  <div>
                    <div class="flex items-center gap-2">
                      <span v-if="item.code" class="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono text-[10px] font-bold border border-slate-700">
                        {{ item.code }}
                      </span>
                      <strong class="text-white block">{{ item.name }}</strong>
                    </div>
                    <span v-if="item.budget_allocation" class="text-[11px] text-slate-500 mt-0.5 block">
                      Kas: {{ item.budget_allocation }}
                    </span>
                  </div>
                </td>
                <td class="py-3.5 px-4">
                  <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold border" :class="getCategoryBadgeClass(item.category)">
                    {{ item.category }}
                  </span>
                </td>
                <td class="py-3.5 px-4">
                  <div class="font-bold text-slate-200">{{ item.leader_name || '-' }}</div>
                  <div class="text-[11px] text-cyan-400">{{ item.phone || item.email || '-' }}</div>
                </td>
                <td class="py-3.5 px-4">
                  <span class="px-2 py-0.5 rounded bg-slate-800 text-amber-400 font-bold">
                    {{ item.member_count || 0 }} orang
                  </span>
                </td>
                <td class="py-3.5 px-4 text-slate-300">
                  <div class="font-medium">{{ item.meeting_schedule || 'Kondisional' }}</div>
                  <div class="text-[11px] text-slate-500">{{ item.location_room || '-' }}</div>
                </td>
                <td class="py-3.5 px-4">
                  <span class="px-2 py-0.5 rounded-full font-medium text-[11px]"
                        :class="item.status === 'Aktif' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-slate-700 text-slate-300'">
                    {{ item.status }}
                  </span>
                </td>
                <td class="py-3.5 px-4 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <button @click="openDetailModal(item)" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition" title="Lihat Detail">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    </button>
                    <button @click="openEditModal(item)" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-300 transition" title="Edit">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                    </button>
                    <button @click="confirmDelete(item)" class="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition" title="Hapus">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- MODAL TAMBAH / EDIT LEMBAGA PELAYANAN (RESPONSIVE STICKY FOOTER) -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-start sm:items-center justify-center overflow-y-auto bg-slate-950/80 px-3 py-4 backdrop-blur-sm sm:p-6">
      <div class="my-auto flex max-h-[calc(100dvh-2rem)] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl sm:max-h-[calc(100dvh-3rem)]">
        
        <!-- Modal Header -->
        <div class="flex shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-4 py-4 sm:px-6">
          <div>
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              {{ modalMode === 'create' ? 'Tambah Lembaga Pelayanan Baru' : 'Edit Lembaga Pelayanan' }}
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">
              Kelola komisi kategorial, departemen ibadah, dan unit pelayanan cabang jemaat.
            </p>
          </div>
          <button @click="isModalOpen = false" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Form Scrollable Body -->
        <form @submit.prevent="handleSubmit" class="min-h-0 flex-1 space-y-4 overflow-y-auto overscroll-contain p-4 sm:p-6">
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Kode Singkatan -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Kode / Singkatan</label>
              <input 
                v-model="formData.code" 
                type="text" 
                placeholder="Contoh: KPR-YOUTH"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white uppercase focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>

            <!-- Nama Lembaga -->
            <div class="md:col-span-2">
              <label class="block text-xs font-semibold text-slate-300 mb-1">Nama Lembaga / Departemen *</label>
              <input 
                v-model="formData.name" 
                type="text" 
                required
                placeholder="Contoh: Komisi Pelayanan Pemuda & Remaja"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Kategori Pelayanan -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Kategori Sektor Pelayanan</label>
              <select 
                v-model="formData.category"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none">
                <option v-for="cat in categoryOptions.filter(c => c !== 'Semua')" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
            </div>

            <!-- Status Lembaga -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Status Keaktifan</label>
              <select 
                v-model="formData.status"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none">
                <option value="Aktif">Aktif Melayani</option>
                <option value="Non-Aktif">Non-Aktif</option>
                <option value="Reorganisasi">Dalam Masa Reorganisasi</option>
              </select>
            </div>
          </div>

          <!-- Pilihan Ketua Terintegrasi dengan Bagan Struktur Organisasi -->
          <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>👑</span> Hubungkan Ketua / PIC dari Pejabat Struktur Organisasi
              </label>
              <span class="text-[10px] text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                Tersinkronisasi Otomatis
              </span>
            </div>
            <select 
              v-model="formData.leader_structure_id"
              @change="onLeaderSelect"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none">
              <option :value="null">-- Input Nama Baru (Otomatis Dibuatkan di Bagan Struktur) --</option>
              <option v-for="officer in structureList" :key="officer.id" :value="officer.id">
                {{ officer.name }} — {{ officer.role_position }} (Lvl {{ officer.hierarchy_level }}, {{ officer.department }})
              </option>
            </select>
            <p class="text-[11px] text-slate-400">
              Pilih pejabat dari bagan organisasi untuk menyalin data otomatis, atau ketik nama baru untuk dimasukkan ke struktur kepemimpinan secara instan.
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Gelar / Jabatan PIC -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Jabatan PIC</label>
              <input 
                v-model="formData.leader_title" 
                type="text" 
                placeholder="Ketua Komisi / Koordinator"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>

            <!-- Nama Ketua / Koordinator -->
            <div class="md:col-span-2">
              <label class="block text-xs font-semibold text-slate-300 mb-1">Nama Ketua / Koordinator PIC</label>
              <input 
                v-model="formData.leader_name" 
                type="text" 
                placeholder="Contoh: Daniel Pratama, S.Kom"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Kontak WhatsApp -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">WhatsApp / No HP PIC</label>
              <input 
                v-model="formData.phone" 
                type="tel" 
                placeholder="081234567890"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>

            <!-- Email Departemen -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Email Departemen</label>
              <input 
                v-model="formData.email" 
                type="email" 
                placeholder="lembaga@gracepoint.or.id"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>

            <!-- Jumlah Anggota Pelayan -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Jumlah Anggota Pelayan</label>
              <input 
                v-model.number="formData.member_count" 
                type="number" 
                min="0"
                placeholder="25"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Jadwal Rutin -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Jadwal Pertemuan / Ibadah Rutin</label>
              <input 
                v-model="formData.meeting_schedule" 
                type="text" 
                placeholder="Contoh: Setiap Sabtu, 18:30 WIB"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>

            <!-- Ruang / Tempat Kegiatan -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Ruang / Tempat Kegiatan</label>
              <input 
                v-model="formData.location_room" 
                type="text" 
                placeholder="Contoh: Ruang Youth Hall Lt. 3"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
            </div>
          </div>

          <!-- Alokasi Anggaran -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Alokasi Kas / Anggaran Pelayanan</label>
            <input 
              v-model="formData.budget_allocation" 
              type="text" 
              placeholder="Contoh: Kas Anggaran Rutin Cabang / Kas Diakonia"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none" />
          </div>

          <!-- Deskripsi & Program Utama -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Deskripsi & Ruang Lingkup Pelayanan</label>
            <textarea 
              v-model="formData.description" 
              rows="2" 
              placeholder="Jelaskan bidang pelayanan, program rutin, dan tanggung jawab lembaga ini..."
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none"></textarea>
          </div>

          <!-- Visi & Misi Pelayanan -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Visi & Misi Pelayanan</label>
            <textarea 
              v-model="formData.vision_mission" 
              rows="2" 
              placeholder="Visi kerohanian dan sasaran pelayanan jemaat..."
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none"></textarea>
          </div>

          <!-- Sticky Action Footer -->
          <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
            <button 
              type="button"
              @click="isModalOpen = false"
              class="w-full rounded-xl bg-slate-800 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-slate-700 sm:w-auto">
              Batal
            </button>
            <button 
              type="submit"
              :disabled="isSubmitting"
              class="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-2.5 text-sm font-bold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 sm:w-auto">
              <svg v-if="isSubmitting" class="w-4 h-4 animate-spin text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ isSubmitting ? 'Menyimpan ke PostgreSQL...' : (modalMode === 'create' ? 'Daftarkan Lembaga' : 'Simpan Perubahan') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL DETAIL LEMBAGA PELAYANAN -->
    <div v-if="isDetailModalOpen && selectedMinistry" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4 my-8">
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span v-if="selectedMinistry.code" class="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono text-xs font-bold border border-slate-700">
                {{ selectedMinistry.code }}
              </span>
              <span class="px-2.5 py-0.5 rounded-full text-xs font-bold border" :class="getCategoryBadgeClass(selectedMinistry.category)">
                {{ selectedMinistry.category }}
              </span>
            </div>
            <h3 class="text-lg font-bold text-white">{{ selectedMinistry.name }}</h3>
          </div>
          <button @click="isDetailModalOpen = false" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div class="space-y-3 text-xs bg-slate-950/50 p-4 rounded-xl border border-slate-800">
          <div class="flex justify-between">
            <span class="text-slate-500">Ketua / PIC:</span>
            <span class="font-bold text-white">{{ selectedMinistry.leader_name }} ({{ selectedMinistry.leader_title }})</span>
          </div>
          <div v-if="selectedMinistry.phone" class="flex justify-between">
            <span class="text-slate-500">WhatsApp:</span>
            <a :href="'https://wa.me/' + selectedMinistry.phone.replace(/[^0-9]/g, '')" target="_blank" class="text-emerald-400 hover:underline">
              {{ selectedMinistry.phone }}
            </a>
          </div>
          <div v-if="selectedMinistry.email" class="flex justify-between">
            <span class="text-slate-500">Email:</span>
            <span class="text-cyan-400">{{ selectedMinistry.email }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">Jumlah Relawan:</span>
            <span class="font-bold text-amber-400">{{ selectedMinistry.member_count }} orang</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">Jadwal Pertemuan:</span>
            <span class="text-slate-200">{{ selectedMinistry.meeting_schedule || 'Kondisional' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">Ruangan:</span>
            <span class="text-slate-200">{{ selectedMinistry.location_room || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">Status Keaktifan:</span>
            <span class="px-2 py-0.5 rounded text-[11px] font-semibold" :class="selectedMinistry.status === 'Aktif' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-700 text-slate-300'">
              {{ selectedMinistry.status }}
            </span>
          </div>
        </div>

        <div v-if="selectedMinistry.description" class="space-y-1">
          <h5 class="text-xs font-bold text-slate-300">Deskripsi Pelayanan:</h5>
          <p class="text-xs text-slate-400 leading-relaxed">{{ selectedMinistry.description }}</p>
        </div>

        <div v-if="selectedMinistry.vision_mission" class="space-y-1">
          <h5 class="text-xs font-bold text-slate-300">Visi & Misi:</h5>
          <p class="text-xs text-slate-400 leading-relaxed italic">"{{ selectedMinistry.vision_mission }}"</p>
        </div>

        <div class="pt-3 border-t border-slate-800 flex justify-end">
          <button @click="isDetailModalOpen = false" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl transition">
            Tutup
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL CONFIRM DELETE -->
    <div v-if="isDeleteModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 shadow-2xl">
        <div class="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 class="text-center text-lg font-bold text-white">Hapus Lembaga Pelayanan?</h3>
        <p class="text-center text-sm text-slate-400 mt-2">
          Apakah Anda yakin ingin menghapus <strong class="text-white">{{ selectedMinistry?.name }}</strong> dari daftar lembaga pelayanan di basis data PostgreSQL?
        </p>

        <div class="flex items-center justify-center gap-3 mt-6">
          <button 
            @click="isDeleteModalOpen = false"
            class="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition">
            Batal
          </button>
          <button 
            @click="executeDelete"
            :disabled="isSubmitting"
            class="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-sm font-bold shadow-lg shadow-rose-600/30 flex items-center gap-2 transition disabled:opacity-50">
            <svg v-if="isSubmitting" class="w-4 h-4 animate-spin text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ isSubmitting ? 'Menghapus...' : 'Ya, Hapus Sekarang' }}
          </button>
        </div>
      </div>
    </div>

  </ChurchAdminLayout>
</template>
