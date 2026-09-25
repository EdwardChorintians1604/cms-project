<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'

// --- State Data Cabang Gereja & Sinode Induk ---
const branches = ref([])
const churches = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

// Filter & Tampilan
const searchQuery = ref('')
const statusFilter = ref('Semua')
const churchFilter = ref('Semua')
const viewMode = ref('table') // 'table' | 'grid'

// Modal State
const isModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isEditing = ref(false)
const isSubmitting = ref(false)
const branchToDelete = ref(null)
const selectedBranchDetail = ref(null)

// Toast State
const toast = reactive({
  show: false,
  message: '',
  type: 'success' // 'success' | 'error'
})

const showToast = (msg, type = 'success') => {
  toast.message = msg
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3500)
}

// Form State CRUD
const emptyForm = () => ({
  id: null,
  church_id: '',
  church_code: '',
  church_name: '',
  city: '',
  admin_name: '',
  email: '',
  phone: '',
  password: '',
  status: 'Aktif'
})

const form = reactive(emptyForm())

// --- 1. READ: Ambil Data dari API Backend PostgreSQL ---
const loadBranches = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/?limit=200`)
    if (!res.ok) throw new Error('Gagal memuat data cabang gereja dari basis data.')
    branches.value = await res.json()
  } catch (err) {
    console.error('Error loading branches:', err)
    errorMessage.value = err.message || 'Gagal memuat data cabang gereja.'
  } finally {
    isLoading.value = false
  }
}

const loadChurches = async () => {
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`)
    if (res.ok) {
      churches.value = await res.json()
    }
  } catch (err) {
    console.warn('Gagal memuat daftar gereja induk:', err)
  }
}

onMounted(() => {
  loadBranches()
  loadChurches()
})

// Helper nama gereja induk / sinode
const getParentChurchName = (churchId) => {
  if (!churchId) return 'Gereja Mandiri / Non-Sinode'
  const parent = churches.value.find((c) => c.id === churchId)
  return parent ? parent.church_name : 'Gereja Mandiri / Non-Sinode'
}

const getParentChurchCode = (churchId) => {
  if (!churchId) return null
  const parent = churches.value.find((c) => c.id === churchId)
  return parent ? parent.church_code : null
}

// Auto-generate saran kode cabang
const autoGenerateCode = () => {
  const selectedParent = churches.value.find((c) => c.id === Number(form.church_id))
  const prefix = selectedParent?.church_code 
    ? selectedParent.church_code.split('-')[0] 
    : 'CH'
  const cityCode = form.city ? form.city.substring(0, 3).toUpperCase() : 'CAB'
  const count = branches.value.length + 1
  form.church_code = `${prefix}-${cityCode}-${String(count).padStart(2, '0')}`
}

// --- 2. STATISTIK RINGKASAN ---
const statistics = computed(() => {
  const total = branches.value.length
  const active = branches.value.filter((b) => b.status === 'Aktif').length
  const nonactive = branches.value.filter((b) => b.status !== 'Aktif').length
  const uniqueCities = new Set(branches.value.map((b) => b.city).filter(Boolean)).size
  return { total, active, nonactive, uniqueCities }
})

// --- 3. FILTER DATA ---
const filteredBranches = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return branches.value.filter((b) => {
    // Filter status
    const matchStatus = statusFilter.value === 'Semua' || b.status === statusFilter.value
    // Filter church
    const matchChurch = churchFilter.value === 'Semua' || (
      churchFilter.value === 'mandiri' 
        ? !b.church_id 
        : b.church_id === Number(churchFilter.value)
    )
    // Search query
    const matchQuery = !query || [
      b.church_code,
      b.church_name,
      b.city,
      b.admin_name,
      b.email,
      b.phone,
      getParentChurchName(b.church_id)
    ].some((v) => String(v || '').toLowerCase().includes(query))

    return matchStatus && matchChurch && matchQuery
  })
})

// --- 4. CREATE / UPDATE MODAL HANDLER ---
const openCreateModal = () => {
  isEditing.value = false
  Object.assign(form, emptyForm())
  autoGenerateCode()
  isModalOpen.value = true
}

const openEditModal = (branch) => {
  isEditing.value = true
  Object.assign(form, {
    id: branch.id,
    church_id: branch.church_id ? String(branch.church_id) : '',
    church_code: branch.church_code || '',
    church_name: branch.church_name || '',
    city: branch.city || '',
    admin_name: branch.admin_name || '',
    email: branch.email || '',
    phone: branch.phone || '',
    password: '',
    status: branch.status || 'Aktif'
  })
  isModalOpen.value = true
}

const openDetailModal = (branch) => {
  selectedBranchDetail.value = branch
  isDetailModalOpen.value = true
}

// Submit Form (Create / Update)
const handleSubmit = async () => {
  if (!form.church_name.trim() || !form.admin_name.trim() || !form.email.trim()) {
    showToast('Mohon lengkapi seluruh kolom wajib!', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      church_id: form.church_id ? Number(form.church_id) : null,
      church_code: form.church_code ? form.church_code.trim().toUpperCase() : null,
      church_name: form.church_name.trim(),
      city: form.city ? form.city.trim() : null,
      admin_name: form.admin_name.trim(),
      email: form.email.trim().toLowerCase(),
      phone: form.phone ? form.phone.trim() : null,
      status: form.status
    }

    if (isEditing.value) {
      if (form.password && form.password.trim()) {
        payload.password = form.password
      }
      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${form.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || 'Gagal memperbarui data cabang gereja.')
      }
      showToast(`Cabang "${form.church_name}" berhasil diperbarui!`, 'success')
    } else {
      if (!form.password) {
        showToast('Kata sandi wajib diisi untuk cabang baru!', 'error')
        isSubmitting.value = false
        return
      }
      payload.password = form.password
      payload.confirm_password = form.password

      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || 'Gagal menambahkan cabang gereja baru.')
      }
      showToast(`Cabang "${form.church_name}" berhasil didaftarkan ke PostgreSQL!`, 'success')
    }

    isModalOpen.value = false
    await loadBranches()
  } catch (err) {
    console.error('Submit error:', err)
    showToast(err.message || 'Terjadi kesalahan sistem.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Toggle Status Cepat (Aktif / Nonaktif)
const toggleBranchStatus = async (branch) => {
  const newStatus = branch.status === 'Aktif' ? 'Nonaktif' : 'Aktif'
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${branch.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    })
    if (!res.ok) throw new Error('Gagal mengubah status cabang.')
    branch.status = newStatus
    showToast(`Status cabang "${branch.church_name}" diubah ke ${newStatus}`, 'success')
  } catch (err) {
    showToast(err.message || 'Gagal mengubah status', 'error')
  }
}

// --- 5. DELETE MODAL HANDLER ---
const confirmDelete = (branch) => {
  branchToDelete.value = branch
  isDeleteModalOpen.value = true
}

const executeDelete = async () => {
  if (!branchToDelete.value) return
  isSubmitting.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/${branchToDelete.value.id}`, {
      method: 'DELETE'
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Gagal menghapus cabang gereja.')
    }
    showToast(`Cabang "${branchToDelete.value.church_name}" telah dihapus.`, 'success')
    isDeleteModalOpen.value = false
    branchToDelete.value = null
    await loadBranches()
  } catch (err) {
    console.error('Delete error:', err)
    showToast(err.message || 'Gagal menghapus cabang.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Ekspor ke CSV
const exportToCSV = () => {
  if (branches.value.length === 0) {
    showToast('Tidak ada data untuk diekspor', 'error')
    return
  }

  const headers = ['ID', 'Kode Cabang', 'Nama Cabang Gereja', 'Sinode Induk', 'Kota', 'Admin Pengurus', 'Email', 'No Telepon', 'Status']
  const rows = branches.value.map((b) => [
    b.id,
    `"${b.church_code || ''}"`,
    `"${b.church_name || ''}"`,
    `"${getParentChurchName(b.church_id)}"`,
    `"${b.city || ''}"`,
    `"${b.admin_name || ''}"`,
    `"${b.email || ''}"`,
    `"${b.phone || ''}"`,
    `"${b.status || 'Aktif'}"`
  ])

  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `Daftar_Cabang_Gereja_GracePoint_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showToast('Data cabang berhasil diekspor ke format CSV!', 'success')
}
</script>

<template>
  <MainAdminLayout>
    <div class="space-y-6 text-[#EDE6D6] pb-12">
      
      <!-- ======================================================= -->
      <!-- HEADER UTAMA                                            -->
      <!-- ======================================================= -->
      <div class="relative overflow-hidden bg-[#123138]/80 border border-amber-500/20 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
        <div class="absolute inset-0 opacity-[0.06] pointer-events-none" style="background-image:radial-gradient(#EDE6D6 1px, transparent 1px); background-size:20px 20px;"></div>

        <div class="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div class="flex items-center gap-4 sm:gap-5">
            <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-amber-500/20 to-amber-600/5 border border-amber-400/30 flex items-center justify-center text-amber-300 shadow-inner shrink-0">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="text-[10px] uppercase tracking-[0.25em] text-amber-400 font-bold">Modul Multi-Tenant &middot; DBMS GracePoint</span>
                <span class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 font-mono">church_admins</span>
              </div>
              <h1 class="font-serif text-2xl sm:text-3xl font-bold text-[#F5EFE0] tracking-tight">Manajemen Cabang Gereja</h1>
              <p class="text-xs sm:text-sm text-[#8AA0A4] mt-1 max-w-2xl leading-relaxed">
                Pusat data cabang gereja lokal di seluruh Indonesia. Kelola integrasi sinode, kode unik identifikasi cabang, akun admin penanggung jawab, serta status keaktifan.
              </p>
            </div>
          </div>

          <!-- Tombol Aksi Header -->
          <div class="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
            <button 
              @click="loadBranches" 
              :disabled="isLoading"
              class="px-3.5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-amber-300 border border-amber-500/30 text-xs font-semibold flex items-center gap-2 transition cursor-pointer disabled:opacity-50"
              title="Muat ulang data dari PostgreSQL"
            >
              <svg :class="{'animate-spin': isLoading}" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span>{{ isLoading ? 'Memuat...' : 'Segarkan' }}</span>
            </button>

            <button 
              @click="exportToCSV"
              class="px-3.5 py-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer"
              title="Unduh data dalam format CSV"
            >
              <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <span>Ekspor CSV</span>
            </button>

            
          </div>
        </div>
      </div>

      <!-- ======================================================= -->
      <!-- KARTU STATISTIK METRIK RINGKASAN                        -->
      <!-- ======================================================= -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Card 1: Total Cabang -->
        <div class="p-4 sm:p-5 rounded-2xl bg-[#123138]/70 border border-white/5 backdrop-blur-md relative overflow-hidden flex flex-col justify-between">
          <div class="flex items-center justify-between text-xs text-[#8AA0A4] mb-2 font-medium">
            <span>Total Cabang Gereja</span>
            <span class="w-2 h-2 rounded-full bg-amber-400"></span>
          </div>
          <div class="font-serif text-2xl sm:text-3xl font-bold text-[#F5EFE0] tracking-tight">
            {{ statistics.total }}
          </div>
          <p class="text-[11px] text-amber-300/80 mt-1">Terdaftar di seluruh database</p>
        </div>

        <!-- Card 2: Aktif -->
        <div class="p-4 sm:p-5 rounded-2xl bg-[#123138]/70 border border-white/5 backdrop-blur-md relative overflow-hidden flex flex-col justify-between">
          <div class="flex items-center justify-between text-xs text-[#8AA0A4] mb-2 font-medium">
            <span>Cabang Berstatus Aktif</span>
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          </div>
          <div class="font-serif text-2xl sm:text-3xl font-bold text-emerald-400 tracking-tight">
            {{ statistics.active }}
          </div>
          <p class="text-[11px] text-emerald-300/80 mt-1">Dapat login & beroperasi normal</p>
        </div>

        <!-- Card 3: Nonaktif -->
        <div class="p-4 sm:p-5 rounded-2xl bg-[#123138]/70 border border-white/5 backdrop-blur-md relative overflow-hidden flex flex-col justify-between">
          <div class="flex items-center justify-between text-xs text-[#8AA0A4] mb-2 font-medium">
            <span>Cabang Nonaktif</span>
            <span class="w-2 h-2 rounded-full bg-rose-400"></span>
          </div>
          <div class="font-serif text-2xl sm:text-3xl font-bold text-rose-400 tracking-tight">
            {{ statistics.nonactive }}
          </div>
          <p class="text-[11px] text-rose-300/80 mt-1">Akses portal sementara dibatasi</p>
        </div>

        <!-- Card 4: Persebaran Wilayah -->
        <div class="p-4 sm:p-5 rounded-2xl bg-[#123138]/70 border border-white/5 backdrop-blur-md relative overflow-hidden flex flex-col justify-between">
          <div class="flex items-center justify-between text-xs text-[#8AA0A4] mb-2 font-medium">
            <span>Wilayah Kota / Kab</span>
            <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
          </div>
          <div class="font-serif text-2xl sm:text-3xl font-bold text-cyan-300 tracking-tight">
            {{ statistics.uniqueCities }} Kota
          </div>
          <p class="text-[11px] text-cyan-300/80 mt-1">Persebaran domisili jemaat</p>
        </div>
      </div>

      <!-- ======================================================= -->
      <!-- FILTER, PENCARIAN, & TOGGLE VIEW                        -->
      <!-- ======================================================= -->
      <div class="p-4 sm:p-5 rounded-2xl bg-[#123138]/70 border border-white/5 backdrop-blur-md space-y-3.5">
        <div class="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
          
          <!-- Search input -->
          <div class="relative flex-1">
            <svg class="w-4 h-4 text-[#8AA0A4] absolute left-3.5 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Cari nama cabang, kode cabang, kota, admin, atau sinode..." 
              class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-slate-100 text-xs rounded-xl pl-10 pr-4 py-2.5 outline-none transition" 
            />
            <button 
              v-if="searchQuery" 
              @click="searchQuery = ''"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white text-xs cursor-pointer"
            >✕</button>
          </div>

          <!-- Controls: Filters & Views -->
          <div class="flex flex-wrap items-center gap-2.5">
            <!-- Filter Sinode Induk -->
            <select 
              v-model="churchFilter" 
              class="bg-[#0B2027] border border-white/10 focus:border-amber-400 text-slate-200 text-xs rounded-xl px-3 py-2.5 outline-none cursor-pointer"
            >
              <option value="Semua">Semua Sinode Induk</option>
              <option value="mandiri">Non-Sinode / Mandiri</option>
              <option v-for="c in churches" :key="c.id" :value="String(c.id)">
                {{ c.church_name }} ({{ c.church_code }})
              </option>
            </select>

            <!-- Filter Status -->
            <select 
              v-model="statusFilter" 
              class="bg-[#0B2027] border border-white/10 focus:border-amber-400 text-slate-200 text-xs rounded-xl px-3 py-2.5 outline-none cursor-pointer"
            >
              <option value="Semua">Semua Status</option>
              <option value="Aktif">Status: Aktif</option>
              <option value="Nonaktif">Status: Nonaktif</option>
            </select>

            <!-- Toggle View Mode (Table vs Grid) -->
            <div class="flex items-center bg-[#0B2027] border border-white/10 rounded-xl p-0.5">
              <button 
                @click="viewMode = 'table'"
                :class="['p-2 rounded-lg transition cursor-pointer', viewMode === 'table' ? 'bg-amber-400 text-slate-950 font-bold' : 'text-slate-400 hover:text-slate-200']"
                title="Tampilan Tabel"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
                </svg>
              </button>
              <button 
                @click="viewMode = 'grid'"
                :class="['p-2 rounded-lg transition cursor-pointer', viewMode === 'grid' ? 'bg-amber-400 text-slate-950 font-bold' : 'text-slate-400 hover:text-slate-200']"
                title="Tampilan Kartu Grid"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
                </svg>
              </button>
            </div>

          </div>

        </div>

        <!-- Info Hasil Pencarian -->
        <div class="flex items-center justify-between text-[11px] text-[#8AA0A4] pt-1">
          <span>Menampilkan <strong>{{ filteredBranches.length }}</strong> dari total {{ branches.length }} cabang gereja</span>
          <span v-if="searchQuery || statusFilter !== 'Semua' || churchFilter !== 'Semua'" class="text-amber-400/90 font-medium">
            (Filter Aktif)
          </span>
        </div>
      </div>

      <!-- ======================================================= -->
      <!-- TAMPILAN TABEL DATA CABANG GEREJA                       -->
      <!-- ======================================================= -->
      <div v-if="viewMode === 'table'" class="bg-[#123138]/70 border border-white/5 rounded-2xl shadow-xl backdrop-blur-md overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-200">
            <thead class="bg-[#0B2027]/90 text-amber-300 font-bold uppercase tracking-wider text-[10px] border-b border-white/10">
              <tr>
                <th class="py-3.5 px-4 w-12 text-center">No</th>
                <th class="py-3.5 px-4">Kode Cabang</th>
                <th class="py-3.5 px-4">Nama Cabang Gereja</th>
                <th class="py-3.5 px-4">Sinode Induk</th>
                <th class="py-3.5 px-4">Kota / Domisili</th>
                <th class="py-3.5 px-4">Penanggung Jawab</th>
                <th class="py-3.5 px-4">Status</th>
                <th class="py-3.5 px-4 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
              <tr v-if="isLoading" class="text-center">
                <td colspan="8" class="py-12 text-[#8AA0A4]">
                  <div class="flex items-center justify-center gap-2">
                    <svg class="animate-spin w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                    </svg>
                    <span>Memuat data cabang gereja dari PostgreSQL...</span>
                  </div>
                </td>
              </tr>

              <tr v-else-if="filteredBranches.length === 0" class="text-center">
                <td colspan="8" class="py-12 text-[#8AA0A4]">
                  <p class="text-2xl mb-1">🏛️</p>
                  <p class="text-xs">Tidak ada data cabang gereja yang sesuai dengan kriteria pencarian.</p>
                </td>
              </tr>

              <tr 
                v-for="(b, idx) in filteredBranches" 
                :key="b.id"
                class="hover:bg-white/[0.03] transition duration-150 group"
              >
                <!-- No -->
                <td class="py-3.5 px-4 text-center font-mono text-slate-400 text-[11px]">
                  {{ idx + 1 }}
                </td>

                <!-- Kode Cabang -->
                <td class="py-3.5 px-4 font-mono font-bold text-amber-300">
                  <span class="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-[11px]">
                    {{ b.church_code || '-' }}
                  </span>
                </td>

                <!-- Nama Cabang -->
                <td class="py-3.5 px-4">
                  <p class="font-bold text-slate-100 text-sm group-hover:text-amber-300 transition">
                    {{ b.church_name }}
                  </p>
                  <p class="text-[11px] text-slate-400">
                    ID Akun: #{{ b.id }} &middot; {{ b.email }}
                  </p>
                </td>

                <!-- Sinode Induk -->
                <td class="py-3.5 px-4">
                  <span 
                    class="px-2.5 py-1 rounded-full text-[10px] font-semibold border inline-flex items-center gap-1.5"
                    :class="b.church_id ? 'bg-amber-500/15 text-amber-300 border-amber-500/30' : 'bg-slate-800/80 text-slate-400 border-slate-700'"
                  >
                    <span>🏛️</span>
                    <span>{{ getParentChurchName(b.church_id) }}</span>
                  </span>
                </td>

                <!-- Kota -->
                <td class="py-3.5 px-4 text-slate-300">
                  <span class="flex items-center gap-1">
                    <span class="text-cyan-400">📍</span>
                    <span>{{ b.city || '-' }}</span>
                  </span>
                </td>

                <!-- Admin / Penanggung Jawab -->
                <td class="py-3.5 px-4">
                  <p class="font-medium text-slate-200">{{ b.admin_name }}</p>
                  <p v-if="b.phone" class="text-[11px] text-emerald-400 font-mono">
                    WA: {{ b.phone }}
                  </p>
                </td>

                <!-- Status & Quick Toggle -->
                <td class="py-3.5 px-4">
                  <button 
                    type="button" 
                    @click="toggleBranchStatus(b)"
                    :class="[
                      'px-2.5 py-1 rounded-full text-[10px] font-bold border transition cursor-pointer flex items-center gap-1.5',
                      b.status === 'Aktif' 
                        ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/25' 
                        : 'bg-rose-500/15 border-rose-500/40 text-rose-300 hover:bg-rose-500/25'
                    ]"
                    title="Klik untuk mengubah status"
                  >
                    <span class="w-1.5 h-1.5 rounded-full" :class="b.status === 'Aktif' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'"></span>
                    <span>{{ b.status || 'Aktif' }}</span>
                  </button>
                </td>

                <!-- Aksi -->
                <td class="py-3.5 px-4 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <!-- Detail -->
                    <button 
                      @click="openDetailModal(b)"
                      class="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-cyan-300 border border-white/10 hover:border-cyan-500/40 transition cursor-pointer"
                      title="Lihat Detail Cabang"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                    </button>

                    <!-- Edit -->
                    <button 
                      @click="openEditModal(b)"
                      class="p-1.5 rounded-lg bg-white/5 hover:bg-amber-500/20 text-amber-300 border border-white/10 hover:border-amber-500/40 transition cursor-pointer"
                      title="Edit Data Cabang"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                    </button>

                    <!-- Delete -->
                    <button 
                      @click="confirmDelete(b)"
                      class="p-1.5 rounded-lg bg-white/5 hover:bg-rose-500/20 text-rose-300 border border-white/10 hover:border-rose-500/40 transition cursor-pointer"
                      title="Hapus Cabang Gereja"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </div>
                </td>

              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ======================================================= -->
      <!-- TAMPILAN KARTU GRID DATA CABANG GEREJA                  -->
      <!-- ======================================================= -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div 
          v-for="b in filteredBranches" 
          :key="b.id"
          class="bg-[#123138]/70 border border-white/10 rounded-2xl p-5 shadow-xl backdrop-blur-md flex flex-col justify-between hover:border-amber-500/40 transition duration-200"
        >
          <div>
            <div class="flex items-center justify-between border-b border-white/5 pb-2.5 mb-3">
              <span class="px-2.5 py-0.5 rounded font-mono text-[11px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
                {{ b.church_code || '-' }}
              </span>
              <span 
                :class="[
                  'px-2 py-0.5 rounded-full text-[10px] font-bold border',
                  b.status === 'Aktif' ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/15 border-rose-500/30 text-rose-300'
                ]"
              >
                {{ b.status }}
              </span>
            </div>

            <h3 class="font-serif font-bold text-base text-[#F5EFE0] mb-1">
              {{ b.church_name }}
            </h3>
            
            <p class="text-xs text-amber-300/90 flex items-center gap-1 mb-2">
              <span>🏛️ Sinode:</span>
              <span class="font-semibold">{{ getParentChurchName(b.church_id) }}</span>
            </p>

            <div class="space-y-1 text-xs text-slate-300">
              <p class="flex items-center gap-1.5">
                <span class="text-cyan-400">📍</span>
                <span>Kota: <strong>{{ b.city || '-' }}</strong></span>
              </p>
              <p class="flex items-center gap-1.5">
                <span class="text-amber-400">👤</span>
                <span>Admin: <strong>{{ b.admin_name }}</strong></span>
              </p>
              <p class="flex items-center gap-1.5">
                <span class="text-slate-400">✉️</span>
                <span class="truncate">{{ b.email }}</span>
              </p>
              <p v-if="b.phone" class="flex items-center gap-1.5 text-emerald-400 font-mono">
                <span>📱</span>
                <span>{{ b.phone }}</span>
              </p>
            </div>
          </div>

          <div class="pt-4 border-t border-white/5 mt-4 flex items-center justify-between gap-2">
            <a 
              v-if="b.phone"
              :href="`https://wa.me/${b.phone.replace(/[^0-9]/g, '')}`" 
              target="_blank"
              class="px-2.5 py-1.5 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/40 text-xs font-semibold flex items-center gap-1 transition"
            >
              <span>💬 WA</span>
            </a>
            <span v-else></span>

            <div class="flex items-center gap-1.5">
              <button 
                @click="openDetailModal(b)" 
                class="px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-cyan-300 text-xs font-semibold transition cursor-pointer"
              >
                Detail
              </button>
              <button 
                @click="openEditModal(b)" 
                class="px-2.5 py-1.5 rounded-lg bg-amber-400 hover:bg-amber-300 text-slate-950 text-xs font-bold transition cursor-pointer"
              >
                Edit
              </button>
              <button 
                @click="confirmDelete(b)" 
                class="p-1.5 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 text-xs transition cursor-pointer"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ======================================================= -->
    <!-- MODAL CREATE & EDIT CABANG GEREJA                       -->
    <!-- ======================================================= -->
    <Transition name="modal">
      <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/85 backdrop-blur-md overflow-y-auto">
        <div class="bg-[#123138] border border-amber-500/30 rounded-2xl p-5 sm:p-7 w-full max-w-xl shadow-2xl space-y-4 my-auto text-slate-100 font-sans text-xs">
          
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-300 flex items-center justify-center font-bold">
                🏛️
              </div>
              <h3 class="font-serif text-base sm:text-lg font-bold text-[#F5EFE0]">
                {{ isEditing ? 'Edit Data Cabang Gereja' : 'Pendaftaran Cabang Gereja Baru' }}
              </h3>
            </div>
            <button @click="isModalOpen = false" class="text-slate-400 hover:text-white cursor-pointer text-sm">✕</button>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <!-- Gereja Induk / Sinode -->
              <div class="sm:col-span-2">
                <label class="block font-medium text-slate-300 mb-1">
                  Gereja Induk / Sinode Terafiliasi
                </label>
                <select 
                  v-model="form.church_id" 
                  @change="autoGenerateCode"
                  class="w-full px-3 py-2 bg-[#0B2027] border border-white/10 rounded-xl text-slate-100 text-xs focus:border-amber-400 outline-none cursor-pointer"
                >
                  <option value="">-- Mandiri / Non-Sinode (Tanpa Afiliasi) --</option>
                  <option v-for="c in churches" :key="c.id" :value="String(c.id)">
                    {{ c.church_name }} ({{ c.church_code }})
                  </option>
                </select>
              </div>

              <!-- Nama Cabang Gereja -->
              <div class="sm:col-span-2">
                <label class="block font-medium text-slate-300 mb-1">
                  Nama Cabang Gereja di Daerah <span class="text-rose-400">*</span>
                </label>
                <input 
                  v-model="form.church_name" 
                  type="text" 
                  required 
                  placeholder="Contoh: GSJA Rayon 10 Padang" 
                  class="w-full px-3 py-2 bg-[#0B2027] border border-white/10 rounded-xl text-slate-100 text-xs focus:border-amber-400 outline-none" 
                />
              </div>

              <!-- Kota / Kabupaten -->
              <div>
                <label class="block font-medium text-slate-300 mb-1">
                  Kota / Kabupaten Domisili
                </label>
                <input 
                  v-model="form.city" 
                  type="text" 
                  placeholder="Contoh: Kota Padang" 
                  @input="!isEditing && autoGenerateCode()"
                  class="w-full px-3 py-2 bg-[#0B2027] border border-white/10 rounded-xl text-slate-100 text-xs focus:border-amber-400 outline-none" 
                />
              </div>

              <!-- Kode Cabang Gereja -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="font-medium text-slate-300">
                    Kode Cabang Gereja <span class="text-rose-400">*</span>
                  </label>
                  <button 
                    type="button" 
                    @click="autoGenerateCode" 
                    class="text-[10px] text-amber-400 hover:underline cursor-pointer"
                  >
                    Saran Kode
                  </button>
                </div>
                <input 
                  v-model="form.church_code" 
                  type="text" 
                  required 
                  placeholder="Contoh: GSJA-PDG-01" 
                  class="w-full px-3 py-2 bg-[#0B2027] border border-white/10 rounded-xl text-amber-300 font-mono font-bold text-xs uppercase focus:border-amber-400 outline-none" 
                />
              </div>

              <!-- Nama Admin Cabang -->
              <div>
                <label class="block font-medium text-slate-300 mb-1">
                  Nama Penanggung Jawab / Admin <span class="text-rose-400">*</span>
                </label>
                <input 
                  v-model="form.admin_name" 
                  type="text" 
                  required 
                  placeholder="Contoh: Pdt. Hendra Setiawan" 
                  class="w-full px-3 py-2 bg-[#0B2027] border border-white/10 rounded-xl text-slate-100 text-xs focus:border-amber-400 outline-none" 
                />
              </div>

              <!-- WhatsApp / HP -->
              <div>
                <label class="block font-medium text-slate-300 mb-1">
                  No. WhatsApp / HP Cabang
                </label>
                <input 
                  v-model="form.phone" 
                  type="tel" 
                  placeholder="081234567890" 
                  class="w-full px-3 py-2 bg-[#0B2027] border border-white/10 rounded-xl text-slate-100 text-xs focus:border-amber-400 outline-none" 
                />
              </div>

              <!-- Email Admin Cabang -->
              <div>
                <label class="block font-medium text-slate-300 mb-1">
                  Email Akun Admin <span class="text-rose-400">*</span>
                </label>
                <input 
                  v-model="form.email" 
                  type="email" 
                  required 
                  placeholder="admin.cabang@gmail.com" 
                  class="w-full px-3 py-2 bg-[#0B2027] border border-white/10 rounded-xl text-slate-100 text-xs focus:border-amber-400 outline-none" 
                />
              </div>

              <!-- Kata Sandi -->
              <div>
                <label class="block font-medium text-slate-300 mb-1">
                  Kata Sandi <span v-if="!isEditing" class="text-rose-400">*</span>
                  <span v-else class="text-[10px] text-slate-400 font-normal">(Kosongkan jika tidak diubah)</span>
                </label>
                <input 
                  v-model="form.password" 
                  type="password" 
                  :required="!isEditing"
                  placeholder="Minimal 6 karakter" 
                  class="w-full px-3 py-2 bg-[#0B2027] border border-white/10 rounded-xl text-slate-100 text-xs focus:border-amber-400 outline-none" 
                />
              </div>

              <!-- Status -->
              <div class="sm:col-span-2">
                <label class="block font-medium text-slate-300 mb-1">Status Keaktifan Akun Cabang</label>
                <div class="flex items-center gap-4 pt-1">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="radio" v-model="form.status" value="Aktif" class="text-amber-400 focus:ring-0">
                    <span class="text-emerald-300 font-semibold">Aktif (Dapat Login & Operasional)</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="radio" v-model="form.status" value="Nonaktif" class="text-amber-400 focus:ring-0">
                    <span class="text-rose-300 font-semibold">Nonaktif (Akses Ditutup Sementara)</span>
                  </label>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-end gap-2.5 pt-3 border-t border-white/10">
              <button 
                type="button" 
                @click="isModalOpen = false" 
                class="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-semibold transition cursor-pointer"
              >
                Batal
              </button>
              <button 
                type="submit" 
                :disabled="isSubmitting"
                class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:brightness-110 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition cursor-pointer disabled:opacity-50"
              >
                {{ isSubmitting ? 'Menyimpan...' : (isEditing ? 'Simpan Perubahan' : 'Daftarkan Cabang') }}
              </button>
            </div>

          </form>

        </div>
      </div>
    </Transition>

    <!-- ======================================================= -->
    <!-- MODAL DETAIL CABANG GEREJA                              -->
    <!-- ======================================================= -->
    <Transition name="modal">
      <div v-if="isDetailModalOpen && selectedBranchDetail" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
        <div class="bg-[#123138] border border-amber-500/30 rounded-2xl p-6 w-full max-w-lg shadow-2xl space-y-4 my-auto text-slate-100 text-xs">
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 class="font-serif text-base font-bold text-amber-300">Rincian Data Cabang Gereja</h3>
            <button @click="isDetailModalOpen = false" class="text-slate-400 hover:text-white cursor-pointer">✕</button>
          </div>

          <div class="space-y-3">
            <div class="flex items-center justify-between p-3 rounded-xl bg-[#0B2027]/70 border border-white/5">
              <div>
                <p class="text-[10px] text-slate-400 uppercase tracking-wider">Kode Cabang</p>
                <p class="font-mono text-sm font-bold text-amber-300">{{ selectedBranchDetail.church_code }}</p>
              </div>
              <span class="px-2.5 py-0.5 rounded-full text-xs font-bold" :class="selectedBranchDetail.status === 'Aktif' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'">
                {{ selectedBranchDetail.status }}
              </span>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <p class="text-[10px] text-slate-400">Nama Cabang</p>
                <p class="font-bold text-sm text-slate-100">{{ selectedBranchDetail.church_name }}</p>
              </div>
              <div>
                <p class="text-[10px] text-slate-400">Sinode Induk</p>
                <p class="font-bold text-xs text-amber-300">{{ getParentChurchName(selectedBranchDetail.church_id) }}</p>
              </div>
              <div>
                <p class="text-[10px] text-slate-400">Kota / Domisili</p>
                <p class="text-slate-200">{{ selectedBranchDetail.city || '-' }}</p>
              </div>
              <div>
                <p class="text-[10px] text-slate-400">Nama Admin</p>
                <p class="text-slate-200 font-semibold">{{ selectedBranchDetail.admin_name }}</p>
              </div>
              <div>
                <p class="text-[10px] text-slate-400">Email Akun</p>
                <p class="text-slate-200 font-mono">{{ selectedBranchDetail.email }}</p>
              </div>
              <div>
                <p class="text-[10px] text-slate-400">WhatsApp / HP</p>
                <p class="text-emerald-400 font-mono">{{ selectedBranchDetail.phone || '-' }}</p>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-2 pt-3 border-t border-white/10">
            <button @click="isDetailModalOpen = false" class="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-semibold cursor-pointer">
              Tutup
            </button>
            <button @click="isDetailModalOpen = false; openEditModal(selectedBranchDetail)" class="px-4 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 text-xs font-bold cursor-pointer">
              Edit Data Ini
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ======================================================= -->
    <!-- MODAL KONFIRMASI HAPUS                                  -->
    <!-- ======================================================= -->
    <Transition name="modal">
      <div v-if="isDeleteModalOpen && branchToDelete" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
        <div class="bg-[#123138] border border-rose-500/30 rounded-2xl p-6 w-full max-w-md shadow-2xl space-y-4 my-auto text-slate-100 text-xs text-center">
          <div class="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 mx-auto flex items-center justify-center text-xl">
            ⚠️
          </div>
          <div>
            <h3 class="font-serif text-base font-bold text-rose-300">Hapus Cabang Gereja?</h3>
            <p class="text-slate-300 mt-2">
              Anda yakin ingin menghapus cabang gereja: <br>
              <strong class="text-white text-sm">"{{ branchToDelete.church_name }}"</strong> <br>
              <span class="font-mono text-amber-300 text-[11px]">(Kode: {{ branchToDelete.church_code }})</span>?
            </p>
            <p class="text-[11px] text-rose-300/80 mt-2">
              Tindakan ini akan menghapus akun admin cabang dari database PostgreSQL dan tidak dapat dibatalkan.
            </p>
          </div>

          <div class="flex items-center justify-center gap-3 pt-2">
            <button @click="isDeleteModalOpen = false" class="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-semibold cursor-pointer">
              Batal
            </button>
            <button 
              @click="executeDelete" 
              :disabled="isSubmitting"
              class="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs transition cursor-pointer disabled:opacity-50"
            >
              {{ isSubmitting ? 'Menghapus...' : 'Ya, Hapus Cabang' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ======================================================= -->
    <!-- TOAST NOTIFIKASI FEEDBACK                               -->
    <!-- ======================================================= -->
    <div 
      v-if="toast.show" 
      class="fixed bottom-5 right-5 z-50 p-4 rounded-xl shadow-2xl border flex items-center gap-3 text-xs font-semibold animate__animated animate__fadeInUp"
      :class="toast.type === 'success' ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-200' : 'bg-rose-950/90 border-rose-500/50 text-rose-200'"
    >
      <span class="text-base">{{ toast.type === 'success' ? '✅' : '⚠️' }}</span>
      <span>{{ toast.message }}</span>
    </div>

  </MainAdminLayout>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }
</style>
