<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import OrgTreeNode from '@/components/Church/OrgTreeNode.vue'
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
  table: 'church_structures',
  lastStatus: 'Menghubungkan ke DBMS...',
})

// Data Gereja Cabang Aktif
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

// State Data
const isLoading = ref(true)
const isSubmitting = ref(false)
const isSyncing = ref(false)
const viewMode = ref('tree') // 'tree' (Tree of Structure) | 'grid' | 'table'
const selectedDepartment = ref('Semua')
const searchQuery = ref('')
const lastSyncTime = ref('-')

// Tree Canvas Controls
const zoomScale = ref(1)
const zoomIn = () => { zoomScale.value = Math.min(Number((zoomScale.value + 0.1).toFixed(2)), 1.5) }
const zoomOut = () => { zoomScale.value = Math.max(Number((zoomScale.value - 0.1).toFixed(2)), 0.5) }
const resetZoom = () => { zoomScale.value = 1 }

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
const modalMode = ref('create') // 'create' | 'edit'
const selectedItem = ref(null)
const selectedParentPreview = ref('')

// Form State
const defaultForm = {
  id: null,
  name: '',
  title: '',
  role_position: '',
  hierarchy_level: 2,
  department: 'BPH',
  parent_id: null,
  ministry_id: null,
  phone: '',
  email: '',
  period: '2024 - 2029',
  photo_url: '',
  notes: '',
  status: 'Aktif',
  sort_order: 0
}

const formData = reactive({ ...defaultForm })

// Structure Data
const structureList = ref([])
const ministriesList = ref([])

// Fetch ministries to cross-link
const fetchMinistries = async () => {
  try {
    let url = `${apiBaseUrl.value}/church-ministries/`
    if (activeChurch.code && activeChurch.code !== 'DEFAULT') {
      url += `?church_code=${encodeURIComponent(activeChurch.code)}`
    }
    const res = await fetch(url, { headers: getAuthHeaders() })
    if (res.ok) {
      ministriesList.value = await res.json()
    }
  } catch (err) {
    console.warn('Could not fetch ministries for cross-link:', err)
  }
}

// Department Options
const departmentOptions = [
  'Semua',
  'Penggembalaan',
  'BPH',
  'Musik & Multimedia',
  'Sekolah Minggu',
  'Pemuda & Remaja',
  'Kaum Bapa (Pria)',
  'Kaum Ibu (Wanita)',
  'Diakonia & Doa',
  'Misi & Penginjilan',
  'Umum & Fasilitas'
]

// Level Definition
const hierarchyLevels = [
  { level: 1, label: 'Tingkat 1 - Gembala Sidang / Pimpinan Jemaat (Pucuk)', badge: 'Pimpinan Utama', color: 'from-amber-500 to-amber-700' },
  { level: 2, label: 'Tingkat 2 - Badan Pengurus Harian (BPH)', badge: 'Pengurus Inti', color: 'from-blue-600 to-indigo-700' },
  { level: 3, label: 'Tingkat 3 - Koordinator Departemen & Seksi', badge: 'Koordinator', color: 'from-emerald-600 to-teal-700' },
  { level: 4, label: 'Tingkat 4 - Staf / Anggota Pelaksana', badge: 'Pelaksana', color: 'from-slate-600 to-gray-700' }
]

// Tree Data: Mengubah array flat database PostgreSQL menjadi Struktur Pohon (Tree of Structure)
const treeData = computed(() => {
  if (!structureList.value || structureList.value.length === 0) return []

  const itemMap = new Map()
  structureList.value.forEach(item => {
    itemMap.set(item.id, { ...item, children: [] })
  })

  const roots = []

  itemMap.forEach(item => {
    if (!item.parent_id) {
      roots.push(item)
    } else if (itemMap.has(item.parent_id)) {
      itemMap.get(item.parent_id).children.push(item)
    } else {
      // Jika parent_id ada tapi tidak ada di list, masukkan sebagai root sekunder
      roots.push(item)
    }
  })

  // Urutkan cabang pohon
  const sortChildren = (node) => {
    if (node.children && node.children.length > 0) {
      node.children.sort((a, b) => (a.hierarchy_level - b.hierarchy_level) || (a.sort_order - b.sort_order) || (a.id - b.id))
      node.children.forEach(sortChildren)
    }
  }

  roots.sort((a, b) => (a.hierarchy_level - b.hierarchy_level) || (a.sort_order - b.sort_order) || (a.id - b.id))
  roots.forEach(sortChildren)

  return roots
})

// Inisialisasi Context Gereja dari Sesi User & Profil DBMS
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

// Fetch Structure from PostgreSQL
const fetchStructure = async (silent = false) => {
  if (!silent) isLoading.value = true
  isSyncing.value = true
  try {
    let url = `${apiBaseUrl.value}/church-structure/`
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
      structureList.value = Array.isArray(data) ? data : []
      dbmsStatus.connected = true
      dbmsStatus.lastStatus = `Terhubung ke PostgreSQL (${structureList.value.length} pejabat terdata)`
      const now = new Date()
      lastSyncTime.value = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    } else {
      dbmsStatus.connected = false
      dbmsStatus.lastStatus = `HTTP ${res.status}: Gagal memuat data dari PostgreSQL`
      showToast('Gagal memuat struktur dari server PostgreSQL', 'error')
    }
  } catch (err) {
    console.error('Fetch structure error:', err)
    dbmsStatus.connected = false
    dbmsStatus.lastStatus = 'Koneksi ke DBMS PostgreSQL terputus'
    showToast('Koneksi terputus saat mengambil data struktur dari DBMS', 'error')
  } finally {
    isLoading.value = false
    isSyncing.value = false
  }
}

// Stats
const totalOfficers = computed(() => structureList.value.length)
const totalLeadership = computed(() => structureList.value.filter(item => item.hierarchy_level <= 2).length)
const uniqueDepartments = computed(() => {
  const set = new Set(structureList.value.map(i => i.department).filter(Boolean))
  return set.size
})
const activePeriod = computed(() => {
  const found = structureList.value.find(i => i.period)
  return found ? found.period : '2024 - 2029'
})

// Filtered List for Table & Grid View
const filteredList = computed(() => {
  return structureList.value.filter(item => {
    const matchDept = selectedDepartment.value === 'Semua' || item.department === selectedDepartment.value
    const q = searchQuery.value.toLowerCase().trim()
    const matchSearch = !q ||
      item.name?.toLowerCase().includes(q) ||
      item.role_position?.toLowerCase().includes(q) ||
      item.title?.toLowerCase().includes(q) ||
      item.phone?.toLowerCase().includes(q) ||
      item.email?.toLowerCase().includes(q)
    return matchDept && matchSearch
  })
})

// Options for Parent Dropdown (Excludes current editing node to avoid circular hierarchy)
const availableParents = computed(() => {
  if (modalMode.value === 'edit' && formData.id) {
    return structureList.value.filter(i => i.id !== formData.id)
  }
  return structureList.value
})

// Helper nama parent
const getParentName = (parentId) => {
  if (!parentId) return 'Pucuk Bagan (Tanpa Atasan)'
  const found = structureList.value.find(i => i.id === parentId)
  return found ? `${found.role_position} - ${found.name}` : `ID: ${parentId}`
}

// Buka Modal Tambah Pejabat Baru Umum (Root / Bebas)
const onMinistrySelect = () => {
  if (formData.ministry_id) {
    const selectedM = ministriesList.value.find(m => m.id === formData.ministry_id)
    if (selectedM) {
      if (!formData.role_position || formData.role_position.startsWith('Koordinator')) {
        formData.role_position = `Koordinator ${selectedM.name}`
      }
      formData.department = selectedM.category || 'Pelayanan'
      formData.hierarchy_level = 3
    }
  }
}

const openCreateModal = () => {
  modalMode.value = 'create'
  Object.assign(formData, defaultForm)
  formData.church_id = activeChurch.id
  formData.church_code = activeChurch.code
  selectedParentPreview.value = ''
  isModalOpen.value = true
}

// Buka Modal Tambah Bawahan Langsung dari Node Bagan (Tree Builder Feature)
const handleAddSubordinate = (parentNode) => {
  modalMode.value = 'create'
  Object.assign(formData, defaultForm)
  formData.church_id = activeChurch.id
  formData.church_code = activeChurch.code
  formData.parent_id = parentNode.id
  formData.hierarchy_level = Math.min((parentNode.hierarchy_level || 1) + 1, 4)
  formData.department = parentNode.department === 'Penggembalaan' ? 'BPH' : parentNode.department
  selectedParentPreview.value = `${parentNode.role_position} — ${parentNode.name}`
  isModalOpen.value = true
}

// Buka Modal Edit Pejabat
const openEditModal = (item) => {
  modalMode.value = 'edit'
  Object.assign(formData, item)
  if (item.parent_id) {
    const p = structureList.value.find(i => i.id === item.parent_id)
    selectedParentPreview.value = p ? `${p.role_position} — ${p.name}` : `ID: ${item.parent_id}`
  } else {
    selectedParentPreview.value = 'Pucuk Pimpinan / Gembala Sidang (Root)'
  }
  isModalOpen.value = true
}

// Buka Modal Konfirmasi Hapus
const confirmDelete = (item) => {
  selectedItem.value = item
  isDeleteModalOpen.value = true
}

// Hitung berapa bawahan yang terdampak jika dihapus
const subordinateCount = computed(() => {
  if (!selectedItem.value) return 0
  return structureList.value.filter(i => i.parent_id === selectedItem.value.id).length
})

// Simpan Data (Create / Update)
const handleSubmit = async () => {
  if (!formData.name || !formData.role_position) {
    showToast('Nama Lengkap dan Jabatan Struktural wajib diisi!', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const isEdit = modalMode.value === 'edit'
    const url = isEdit
      ? `${apiBaseUrl.value}/church-structure/${formData.id}`
      : `${apiBaseUrl.value}/church-structure/`
    const method = isEdit ? 'PUT' : 'POST'

    const payload = {
      ...formData,
      church_code: activeChurch.code || formData.church_code || null,
      church_id: activeChurch.id || formData.church_id || null,
    }

    const res = await fetch(url, {
      method,
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })

    if (res.ok) {
      showToast(isEdit ? 'Data pejabat dan relasi hierarki berhasil diperbarui!' : 'Pejabat baru berhasil ditambahkan ke dalam bagan pohon!', 'success')
      isModalOpen.value = false
      await fetchStructure(true)
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

// Eksekusi Hapus Pejabat
const executeDelete = async () => {
  if (!selectedItem.value) return
  isSubmitting.value = true
  try {
    const url = `${apiBaseUrl.value}/church-structure/${selectedItem.value.id}`
    const res = await fetch(url, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    })

    if (res.ok) {
      showToast(`Pejabat ${selectedItem.value.name} berhasil dihapus dari struktur`, 'success')
      isDeleteModalOpen.value = false
      selectedItem.value = null
      await fetchStructure(true)
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

// Seed Default Template
const seedDefaultStructure = async () => {
  if (structureList.value.length > 0) {
    if (!confirm('Struktur sudah memiliki data. Apakah Anda tetap ingin menambahkan template struktur baku gereja?')) {
      return
    }
  }
  isSyncing.value = true
  try {
    const codeParam = activeChurch.code ? encodeURIComponent(activeChurch.code) : ''
    const url = `${apiBaseUrl.value}/church-structure/seed-default${codeParam ? `?church_code=${codeParam}` : ''}`
    const res = await fetch(url, {
      method: 'POST',
      headers: getAuthHeaders(),
    })
    if (res.ok) {
      showToast('Template bagan struktur gereja berhasil dimuat ke DBMS!', 'success')
      await fetchStructure(true)
    } else {
      showToast('Gagal menginisialisasi template struktur baku', 'error')
    }
  } catch (err) {
    console.error('Seed error:', err)
    showToast('Gagal memproses inisialisasi struktur', 'error')
  } finally {
    isSyncing.value = false
  }
}

// Cetak Bagan
const printChart = () => {
  window.print()
}

// Initials helper
const getInitials = (name) => {
  if (!name) return 'PG'
  return name.split(' ').map(n => n[0]).filter(Boolean).slice(0, 2).join('').toUpperCase()
}

onMounted(async () => {
  await initChurchContext()
  await fetchStructure()
  await fetchMinistries()
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
        <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
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
              <div class="px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold">
                {{ activeChurch.code || 'Cabang Aktif' }} • {{ activeChurch.name }}
              </div>
              <span class="text-xs text-slate-400">Sinkron: {{ lastSyncTime }}</span>
            </div>

            <h1 class="text-2xl lg:text-3xl font-bold text-white tracking-tight flex items-center gap-3">
              <svg class="w-8 h-8 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              Perancang Bagan Struktur Kepemimpinan Gereja
            </h1>
            <p class="text-sm text-slate-400 mt-1 max-w-2xl">
              Rancang dan kelola pohon struktur organisasi (<em>Tree of Structure</em>) gereja secara interaktif. Tambahkan bawahan, ubah atasan, dan pantau jalur penggembalaan langsung di database PostgreSQL.
            </p>
          </div>

          <!-- Quick Action Buttons -->
          <div class="flex flex-wrap items-center gap-3 print:hidden">
            <button 
              @click="fetchStructure(false)"
              :disabled="isSyncing"
              class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl border border-slate-700 flex items-center gap-2 transition disabled:opacity-50">
              <svg class="w-4 h-4 text-slate-400" :class="{'animate-spin': isSyncing}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Sinkron Ulang
            </button>

            <button 
              v-if="structureList.length === 0"
              @click="seedDefaultStructure"
              :disabled="isSyncing"
              class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition">
              <svg class="w-4 h-4 text-indigo-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Gunakan Template Baku
            </button>

            <button 
              @click="printChart"
              class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl border border-slate-700 flex items-center gap-2 transition">
              <svg class="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              Cetak Bagan
            </button>

            <button 
              @click="openCreateModal"
              class="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-sm rounded-xl shadow-lg shadow-amber-500/20 flex items-center gap-2 transition transform active:scale-95">
              <svg class="w-5 h-5 text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
              </svg>
              + Tambah Pejabat Pucuk (Root)
            </button>
          </div>
        </div>

        <!-- Metrics Bar -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-800/80">
          <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-800/60">
            <div class="text-xs font-medium text-slate-400">Total Pejabat Terdaftar</div>
            <div class="text-2xl font-black text-amber-400 mt-1 flex items-baseline gap-2">
              {{ totalOfficers }}
              <span class="text-xs font-normal text-slate-400">orang</span>
            </div>
          </div>
          <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-800/60">
            <div class="text-xs font-medium text-slate-400">Penggembalaan & BPH</div>
            <div class="text-2xl font-black text-blue-400 mt-1 flex items-baseline gap-2">
              {{ totalLeadership }}
              <span class="text-xs font-normal text-slate-400">pejabat</span>
            </div>
          </div>
          <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-800/60">
            <div class="text-xs font-medium text-slate-400">Bidang & Seksi Pelayanan</div>
            <div class="text-2xl font-black text-emerald-400 mt-1 flex items-baseline gap-2">
              {{ uniqueDepartments }}
              <span class="text-xs font-normal text-slate-400">departemen</span>
            </div>
          </div>
          <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-800/60">
            <div class="text-xs font-medium text-slate-400">Masa Bakti Kepengurusan</div>
            <div class="text-xl font-bold text-slate-200 mt-1 truncate">
              {{ activePeriod }}
            </div>
          </div>
        </div>
      </div>

      <!-- Controls & View Mode Switcher -->
      <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800 print:hidden">
        <!-- Tabs Mode -->
        <div class="flex items-center gap-1 bg-slate-950/60 p-1 rounded-lg border border-slate-800">
          <button 
            @click="viewMode = 'tree'"
            class="flex items-center gap-2 px-4 py-2 rounded-md text-xs font-bold transition"
            :class="viewMode === 'tree' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            🌳 Bagan Pohon (Tree of Structure)
          </button>
          <button 
            @click="viewMode = 'grid'"
            class="flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition"
            :class="viewMode === 'grid' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-400 hover:text-white'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Kartu Departemen
          </button>
          <button 
            @click="viewMode = 'table'"
            class="flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition"
            :class="viewMode === 'table' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-400 hover:text-white'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Tabel Data DBMS
          </button>
        </div>

        <!-- Filters & Search (for Grid & Table) -->
        <div v-if="viewMode !== 'tree'" class="flex flex-wrap items-center gap-3">
          <!-- Department Filter -->
          <div class="relative">
            <select 
              v-model="selectedDepartment"
              class="bg-slate-950/80 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 pr-8 focus:ring-1 focus:ring-amber-500 focus:outline-none">
              <option v-for="dept in departmentOptions" :key="dept" :value="dept">
                Departemen: {{ dept }}
              </option>
            </select>
          </div>

          <!-- Search Input -->
          <div class="relative min-w-[220px]">
            <input 
              v-model="searchQuery"
              type="text"
              placeholder="Cari nama, jabatan, kontak..."
              class="w-full bg-slate-950/80 border border-slate-700 text-slate-200 text-xs rounded-lg pl-8 pr-3 py-2 focus:ring-1 focus:ring-amber-500 focus:outline-none placeholder:text-slate-500" />
            <svg class="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Quick Designer Helper Alert for Admin -->
      <div v-if="viewMode === 'tree'" class="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-center justify-between gap-4 text-xs text-amber-200 print:hidden">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center shrink-0 text-amber-400 font-bold">
            💡
          </div>
          <div>
            <strong class="font-bold text-amber-300 block mb-0.5">Cara Merancang Bagan Struktur:</strong>
            <span>Gunakan tombol <code class="bg-amber-500/20 px-1.5 py-0.5 rounded font-bold text-amber-300">+ Bawahan</code> pada tiap kartu pejabat untuk menyusun rantai komando dari Gembala Sidang ke BPH, lalu ke Koordinator Seksi/Departemen.</span>
          </div>
        </div>
        <button 
          @click="openCreateModal"
          class="shrink-0 px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg transition shadow">
          + Pucuk Baru
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="py-20 flex flex-col items-center justify-center space-y-4">
        <div class="w-12 h-12 border-4 border-amber-500/20 border-t-amber-500 rounded-full animate-spin"></div>
        <p class="text-sm text-slate-400">Menghubungkan ke DBMS PostgreSQL & merakit bagan pohon struktur...</p>
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
          @click="fetchStructure(false)" 
          class="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-rose-600/20 flex items-center gap-2 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Coba Hubungkan Ulang Sekarang
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="structureList.length === 0" class="py-16 bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl flex flex-col items-center justify-center text-center p-6">
        <div class="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white">Bagan Struktur Gereja Belum Dirancang</h3>
        <p class="text-sm text-slate-400 max-w-md mt-1 mb-6">
          Cabang ini belum memiliki data struktur kepemimpinan. Anda dapat memuat bagan baku struktur gereja atau mulai menambahkan pimpinan puncak secara mandiri.
        </p>
        <div class="flex flex-wrap items-center justify-center gap-3">
          <button 
            @click="seedDefaultStructure" 
            class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Terapkan Template Bagan Baku Gereja
          </button>
          <button 
            @click="openCreateModal" 
            class="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm rounded-xl shadow-lg shadow-amber-500/20 flex items-center gap-2 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Tambah Gembala Sidang (Pucuk)
          </button>
        </div>
      </div>

      <!-- VIEW MODE 1: INTERACTIVE TREE OF STRUCTURE BUILDER -->
      <div v-else-if="viewMode === 'tree'" class="relative">
        <div class="absolute right-3 top-3 z-10 flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900/95 p-1.5 shadow-xl backdrop-blur sm:right-4 sm:top-4">
          <button
            @click="zoomOut"
            :disabled="zoomScale <= 0.5"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-700 bg-slate-800 text-slate-200 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
            title="Perkecil bagan"
            aria-label="Perkecil bagan">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/></svg>
          </button>
          <span class="w-12 text-center font-mono text-xs font-bold text-amber-400" aria-live="polite">{{ Math.round(zoomScale * 100) }}%</span>
          <button
            @click="zoomIn"
            :disabled="zoomScale >= 1.5"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-700 bg-slate-800 text-slate-200 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
            title="Perbesar bagan"
            aria-label="Perbesar bagan">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          </button>
          <button
            @click="resetZoom"
            class="rounded-lg px-2.5 py-2 text-xs font-semibold text-slate-300 transition hover:bg-slate-800 hover:text-white"
            title="Kembalikan zoom ke 100%">
            Reset
          </button>
        </div>

        <!-- Canvas Container with Blueprint Dot Grid -->
        <div 
          class="relative mx-auto h-[min(70vh,640px)] min-h-[360px] max-h-[640px] w-full max-w-6xl overflow-auto rounded-2xl border border-slate-800/80 bg-slate-950/70 p-4 pt-16 shadow-2xl sm:p-8 sm:pt-16"
          style="background-image: radial-gradient(rgba(245, 158, 11, 0.08) 1.5px, transparent 1.5px); background-size: 28px 28px;">
          
          <!-- Zoom Transform Layer -->
          <div 
            class="flex flex-col items-center min-w-max pb-16 transition-transform duration-200 origin-top"
            :style="{ transform: `scale(${zoomScale})` }">
            
            <!-- Root Nodes Row -->
            <div class="flex items-start justify-center gap-16">
              <div 
                v-for="rootNode in treeData" 
                :key="rootNode.id"
                class="flex flex-col items-center">
                <OrgTreeNode 
                  :node="rootNode" 
                  :level="1"
                  :ministries="ministriesList"
                  @add-child="handleAddSubordinate"
                  @edit="openEditModal"
                  @delete="confirmDelete" />
              </div>
            </div>

          </div>
        </div>
      </div>

      <!-- VIEW MODE 2: CARDS GRID PER DEPARTEMEN -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div 
          v-for="item in filteredList" 
          :key="item.id"
          class="bg-slate-900/80 border border-slate-800 hover:border-amber-500/50 rounded-2xl p-5 shadow-lg transition flex flex-col justify-between group">
          <div>
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-indigo-500/20 border border-slate-700 text-amber-300 flex items-center justify-center font-bold text-sm shrink-0 overflow-hidden">
                  <img v-if="item.photo_url" :src="item.photo_url" alt="Foto" class="w-full h-full object-cover" />
                  <span v-else>{{ getInitials(item.name) }}</span>
                </div>
                <div>
                  <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-amber-300 border border-slate-700">
                    {{ item.department }}
                  </span>
                  <h4 class="text-sm font-bold text-white mt-1 leading-snug">
                    {{ item.title ? `${item.title} ` : '' }}{{ item.name }}
                  </h4>
                </div>
              </div>
              <span class="text-[10px] px-2 py-0.5 rounded-full font-medium"
                    :class="item.status === 'Aktif' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-rose-500/15 text-rose-300'">
                {{ item.status }}
              </span>
            </div>

            <div class="mt-4 space-y-1.5 text-xs text-slate-300 bg-slate-950/40 p-3 rounded-xl border border-slate-800/60">
              <div class="flex justify-between">
                <span class="text-slate-500">Jabatan:</span>
                <span class="font-semibold text-amber-400">{{ item.role_position }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">Atasan:</span>
                <span class="font-medium text-slate-300 truncate max-w-[180px]">{{ getParentName(item.parent_id) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">Tingkat:</span>
                <span>Tingkat {{ item.hierarchy_level }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">Periode:</span>
                <span>{{ item.period }}</span>
              </div>
              <div v-if="item.phone" class="flex justify-between">
                <span class="text-slate-500">WhatsApp:</span>
                <a :href="'https://wa.me/' + item.phone.replace(/[^0-9]/g, '')" target="_blank" class="text-emerald-400 hover:underline">
                  {{ item.phone }}
                </a>
              </div>
              <div v-if="item.email" class="flex justify-between">
                <span class="text-slate-500">Email:</span>
                <span class="text-blue-400 truncate max-w-[160px]">{{ item.email }}</span>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
            <button 
              @click="handleAddSubordinate(item)" 
              class="px-2.5 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 text-xs font-semibold rounded-lg border border-amber-500/30 flex items-center gap-1 transition">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/></svg>
              + Bawahan
            </button>
            <div class="flex items-center gap-1.5">
              <button @click="openEditModal(item)" class="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg transition" title="Edit">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
              </button>
              <button @click="confirmDelete(item)" class="p-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 text-xs rounded-lg transition" title="Hapus">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- VIEW MODE 3: DATA TABLE MANAGEMENT -->
      <div v-else-if="viewMode === 'table'" class="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th class="py-3.5 px-4">No</th>
                <th class="py-3.5 px-4">Pejabat & Gelar</th>
                <th class="py-3.5 px-4">Jabatan Struktural</th>
                <th class="py-3.5 px-4">Atasan Langsung (Parent)</th>
                <th class="py-3.5 px-4">Departemen</th>
                <th class="py-3.5 px-4">Tingkat</th>
                <th class="py-3.5 px-4">Kontak</th>
                <th class="py-3.5 px-4">Status</th>
                <th class="py-3.5 px-4 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              <tr v-for="(item, index) in filteredList" :key="item.id" class="hover:bg-slate-800/40 transition">
                <td class="py-3 px-4 text-slate-400">{{ index + 1 }}</td>
                <td class="py-3 px-4">
                  <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-300 flex items-center justify-center font-bold text-xs shrink-0 overflow-hidden">
                      <img v-if="item.photo_url" :src="item.photo_url" class="w-full h-full object-cover" />
                      <span v-else>{{ getInitials(item.name) }}</span>
                    </div>
                    <div>
                      <span class="font-bold text-white block">{{ item.name }}</span>
                      <span v-if="item.title" class="text-[11px] text-slate-400">Gelar: {{ item.title }}</span>
                    </div>
                  </div>
                </td>
                <td class="py-3 px-4 font-semibold text-amber-400">{{ item.role_position }}</td>
                <td class="py-3 px-4 text-slate-300">
                  <span class="px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/80 text-[11px]">
                    {{ getParentName(item.parent_id) }}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
                    {{ item.department }}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <span class="px-2 py-0.5 rounded font-bold text-[11px]"
                        :class="item.hierarchy_level === 1 ? 'bg-amber-500/20 text-amber-300' : item.hierarchy_level === 2 ? 'bg-blue-500/20 text-blue-300' : 'bg-emerald-500/20 text-emerald-300'">
                    Level {{ item.hierarchy_level }}
                  </span>
                </td>
                <td class="py-3 px-4 text-slate-300">
                  <div>{{ item.phone || '-' }}</div>
                  <div class="text-[11px] text-slate-500">{{ item.email }}</div>
                </td>
                <td class="py-3 px-4">
                  <span class="px-2 py-0.5 rounded-full font-medium text-[11px]"
                        :class="item.status === 'Aktif' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-slate-700 text-slate-300'">
                    {{ item.status }}
                  </span>
                </td>
                <td class="py-3 px-4 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <button @click="handleAddSubordinate(item)" class="p-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 transition" title="Tambah Bawahan">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/></svg>
                    </button>
                    <button @click="openEditModal(item)" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition" title="Edit">
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

    <!-- MODAL TAMBAH / EDIT PEJABAT STRUKTUR (GUIDED TREE BUILDER MODAL) -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-start sm:items-center justify-center overflow-y-auto bg-slate-950/80 px-3 py-4 backdrop-blur-sm sm:p-6">
      <div class="my-auto flex max-h-[calc(100dvh-2rem)] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl sm:max-h-[calc(100dvh-3rem)]">
        <div class="flex shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950/50 px-4 py-4 sm:px-6">
          <div>
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              {{ modalMode === 'create' ? 'Tambah Pejabat ke Bagan Pohon' : 'Edit Pejabat & Posisi Hierarki' }}
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">
              {{ formData.parent_id ? `Menambahkan bawahan di bawah ${selectedParentPreview}` : 'Menetapkan pucuk kepemimpinan / pimpinan utama jemaat' }}
            </p>
          </div>
          <button @click="isModalOpen = false" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="min-h-0 flex-1 space-y-4 overflow-y-auto overscroll-contain p-4 sm:p-6">
          
                    <!-- Parent Selection & Ministry Cross-Link (Integrasi Dua Arah) -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-950/80 p-3.5 rounded-xl border border-slate-800">
            <div>
              <label class="block text-xs font-bold text-amber-300 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <span>🌳</span> Atasan Langsung (Parent)
              </label>
              <select 
                v-model="formData.parent_id"
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:ring-1 focus:ring-amber-500 focus:outline-none">
                <option :value="null">-- Pucuk Pimpinan / Gembala --</option>
                <option v-for="parentItem in availableParents" :key="parentItem.id" :value="parentItem.id">
                  {{ parentItem.role_position }} — {{ parentItem.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-cyan-300 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <span>🏛️</span> Pimpin Lembaga Pelayanan
              </label>
              <select 
                v-model="formData.ministry_id"
                @change="onMinistrySelect"
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:ring-1 focus:ring-cyan-500 focus:outline-none">
                <option :value="null">-- Tidak Memimpin Lembaga --</option>
                <option v-for="m in ministriesList" :key="m.id" :value="m.id">
                  [{{ m.code || 'DEP' }}] {{ m.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Jabatan Struktural -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Jabatan Struktural Gereja *</label>
              <input 
                v-model="formData.role_position" 
                type="text" 
                required
                placeholder="Contoh: Gembala Sidang, Sekretaris, Koordinator Musik"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none" />
            </div>

            <!-- Departemen / Seksi -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Departemen / Bidang</label>
              <select 
                v-model="formData.department"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none">
                <option v-for="dept in departmentOptions.filter(d => d !== 'Semua')" :key="dept" :value="dept">
                  {{ dept }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Tingkat Hierarki -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Tingkat Kedudukan Bagan</label>
              <select 
                v-model.number="formData.hierarchy_level"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none">
                <option v-for="hl in hierarchyLevels" :key="hl.level" :value="hl.level">
                  {{ hl.label }}
                </option>
              </select>
            </div>

            <!-- Periode Jabatan -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Periode Masa Tugas</label>
              <input 
                v-model="formData.period" 
                type="text" 
                placeholder="Contoh: 2024 - 2029"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Nomor Telepon/WhatsApp -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Nomor WhatsApp / HP</label>
              <input 
                v-model="formData.phone" 
                type="tel" 
                placeholder="081234567890"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none" />
            </div>

            <!-- Email -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Email Pejabat</label>
              <input 
                v-model="formData.email" 
                type="email" 
                placeholder="pejabat@gereja.org"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- URL Foto Profil -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">URL Foto Pejabat (Opsional)</label>
              <input 
                v-model="formData.photo_url" 
                type="url" 
                placeholder="https://example.com/foto.jpg"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none" />
            </div>

            <!-- Status Pejabat -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Status Keaktifan</label>
              <select 
                v-model="formData.status"
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none">
                <option value="Aktif">Aktif Bertugas</option>
                <option value="Cuti">Cuti Pelayanan</option>
                <option value="Demisioner">Demisioner / Purna Tugas</option>
              </select>
            </div>
          </div>

          <!-- Catatan / Tugas Khusus -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Deskripsi / Tugas Tambahan</label>
            <textarea 
              v-model="formData.notes" 
              rows="2" 
              placeholder="Catatan kewenangan atau deskripsi pelayanan..."
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:ring-1 focus:ring-amber-500 focus:outline-none"></textarea>
          </div>

          <!-- Actions -->
          <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col gap-2 border-t border-slate-800 bg-slate-900/95 px-4 py-3 shadow-[0_-12px_24px_rgba(2,6,23,0.35)] backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:items-center sm:justify-end sm:gap-3 sm:px-6 sm:py-4">
            <button 
              type="button"
              @click="isModalOpen = false"
              class="min-h-11 w-full rounded-lg border border-slate-700 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-slate-600 hover:bg-slate-800 sm:w-auto">
              Batal
            </button>
            <button 
              type="submit"
              :disabled="isSubmitting"
              class="flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-amber-500 px-5 py-2.5 text-sm font-bold text-slate-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto">
              <svg v-if="isSubmitting" class="w-4 h-4 animate-spin text-slate-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ isSubmitting ? 'Menyimpan ke PostgreSQL...' : (modalMode === 'create' ? 'Tautkan ke Bagan' : 'Perbarui Perubahan') }}
            </button>
          </div>
        </form>
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
        <h3 class="text-center text-lg font-bold text-white">Hapus dari Bagan Organisasi?</h3>
        <p class="text-center text-sm text-slate-400 mt-2">
          Apakah Anda yakin ingin menghapus <strong class="text-white">{{ selectedItem?.name }}</strong> ({{ selectedItem?.role_position }}) dari struktur gereja di PostgreSQL?
        </p>

        <div v-if="subordinateCount > 0" class="mt-4 p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-300">
          ⚠️ <strong>Perhatian:</strong> Pejabat ini memiliki <strong>{{ subordinateCount }} bawahan langsung</strong>. Jika dihapus, bawahan akan terlepas dari atasan ini.
        </div>

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
