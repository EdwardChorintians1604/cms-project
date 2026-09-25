<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { apiFetch } from '@/services/api'

const router = useRouter()

const emptyChurchForm = () => ({
  id: null,
  church_code: '',
  church_name: '',
  established_date: '',
  bpp_general_chairman: '',
  address: '',
  city: '',
  latitude: null,
  longitude: null,
  google_maps_url: '',
  church_description: '',
  status: 'Aktif',
  facebook_name: '',
  facebook_link: '',
  instagram_name: '',
  instagram_link: '',
  youtube_name: '',
  youtube_link: '',
  tiktok_name: '',
  tiktok_link: ''
})

const churches = ref([])
const isLoading = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const statusOptions = ['Aktif', 'Pending', 'Nonaktif']

const searchQuery = ref('')
const statusFilter = ref('Semua')
const isModalOpen = ref(false)
const modalMode = ref('create')
const modalTab = ref('info') // 'info' | 'medsos' | 'relasi'
const selectedChurch = ref(null)
const form = reactive(emptyChurchForm())

const statusMeta = {
  Aktif: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/25',
  Pending: 'bg-amber-500/15 text-amber-300 border-amber-500/30 hover:bg-amber-500/25',
  Nonaktif: 'bg-rose-500/15 text-rose-300 border-rose-500/30 hover:bg-rose-500/25'
}

// 1. READ: Ambil data live dari PostgreSQL
const loadChurches = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(`${APP_CONFIG.apiBaseUrl}/churches/`)
    if (!response.ok) throw new Error('Data gereja gagal dimuat dari database server.')
    const data = await response.json()
    churches.value = data
  } catch (error) {
    console.error('Load churches error:', error)
    errorMessage.value = error.message || 'Gagal memuat data gereja.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadChurches)

// 2. FILTER SEARCH
const filteredChurches = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  return churches.value.filter((church) => {
    const matchesStatus = statusFilter.value === 'Semua' || church.status === statusFilter.value
    const matchesQuery = !query || [
      church.church_code,
      church.church_name,
      church.bpp_general_chairman,
      church.established_date,
      church.address,
      church.city
    ].some((value) => String(value || '').toLowerCase().includes(query))

    return matchesStatus && matchesQuery
  })
})

// 3. STATISTIK SUMMARY
const summary = computed(() => ({
  total: churches.value.length,
  active: churches.value.filter((c) => c.status === 'Aktif').length,
  pending: churches.value.filter((c) => c.status === 'Pending').length,
  nonactive: churches.value.filter((c) => c.status === 'Nonaktif').length
}))

const resetForm = () => {
  Object.assign(form, emptyChurchForm())
}

const openCreateModal = () => {
  modalMode.value = 'create'
  modalTab.value = 'info'
  selectedChurch.value = null
  resetForm()
  form.church_code = `GP-${String(churches.value.length + 1).padStart(3, '0')}`
  isModalOpen.value = true
}

const openEditModal = (church) => {
  modalMode.value = 'edit'
  modalTab.value = 'info'
  selectedChurch.value = church
  resetForm()
  Object.assign(form, {
    id: church.id,
    church_code: church.church_code,
    church_name: church.church_name,
    established_date: church.established_date || '',
    bpp_general_chairman: church.bpp_general_chairman || '',
    address: church.address,
    city: church.city || '',
    latitude: church.latitude,
    longitude: church.longitude,
    google_maps_url: church.google_maps_url || '',
    church_description: church.church_description || '',
    status: church.status || 'Aktif',
    facebook_name: church.facebook_name || '',
    facebook_link: church.facebook_link || '',
    instagram_name: church.instagram_name || '',
    instagram_link: church.instagram_link || '',
    youtube_name: church.youtube_name || '',
    youtube_link: church.youtube_link || '',
    tiktok_name: church.tiktok_name || '',
    tiktok_link: church.tiktok_link || ''
  })
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  selectedChurch.value = null
  resetForm()
}

// 4. CREATE / UPDATE DATA GEREJA KE POSTGRESQL
const saveChurch = async () => {
  if (!form.church_code || !form.church_name || !form.address) {
    alert('Harap lengkapi Kode Gereja, Nama Gereja, dan Alamat Lengkap.')
    return
  }

  isSubmitting.value = true
  const isEdit = modalMode.value === 'edit' && selectedChurch.value

  const payload = {
    church_code: form.church_code,
    church_name: form.church_name,
    established_date: form.established_date || null,
    bpp_general_chairman: form.bpp_general_chairman || null,
    address: form.address,
    city: form.city ? form.city.trim() : null,
    latitude: form.latitude ? Number(form.latitude) : null,
    longitude: form.longitude ? Number(form.longitude) : null,
    google_maps_url: form.google_maps_url || null,
    church_description: form.church_description || null,
    status: form.status || 'Aktif',
    facebook_name: form.facebook_name || null,
    facebook_link: form.facebook_link || null,
    instagram_name: form.instagram_name || null,
    instagram_link: form.instagram_link || null,
    youtube_name: form.youtube_name || null,
    youtube_link: form.youtube_link || null,
    tiktok_name: form.tiktok_name || null,
    tiktok_link: form.tiktok_link || null
  }

  try {
    const url = isEdit
      ? `${APP_CONFIG.apiBaseUrl}/churches/${selectedChurch.value.id}`
      : `${APP_CONFIG.apiBaseUrl}/churches/`
    
    await apiFetch(url.replace(APP_CONFIG.apiBaseUrl, ''), {
      method: isEdit ? 'PUT' : 'POST',
      body: JSON.stringify(payload)
    })

    await loadChurches()
    closeModal()
  } catch (error) {
    alert(error.message || 'Gagal menyimpan data gereja.')
  } finally {
    isSubmitting.value = false
  }
}

// 5. DELETE GEREJA DARI POSTGRESQL
const deleteChurch = async (church) => {
  const confirmed = window.confirm(
    `Apakah Anda yakin ingin menghapus data gereja "${church.church_name}" (${church.church_code}) secara permanen dari PostgreSQL?`
  )
  if (!confirmed) return

  try {
    await apiFetch(`/churches/${church.id}`, {
      method: 'DELETE'
    })
    await loadChurches()
  } catch (error) {
    alert(error.message || 'Gagal menghapus data gereja.')
  }
}

// 6. TOGGLE STATUS AKTIF / NONAKTIF
const toggleStatus = async (church) => {
  const nextStatus = church.status === 'Aktif' ? 'Nonaktif' : 'Aktif'
  try {
    await apiFetch(`/churches/${church.id}`, {
      method: 'PUT',
      body: JSON.stringify({ status: nextStatus })
    })
    church.status = nextStatus
  } catch (error) {
    console.error('Toggle status error:', error)
  }
}
</script>

<template>
  <MainAdminLayout>
    <div class="relative space-y-6 text-[#EDE6D6]">
      <div class="pointer-events-none fixed inset-0 -z-10 bg-[#0B2027]"></div>

      <!-- Header Section -->
      <section class="relative overflow-hidden rounded-2xl border border-amber-500/20 bg-[#123138]/80 p-5 sm:p-6 shadow-2xl backdrop-blur-xl">
        <div class="absolute inset-0 opacity-[0.06] pointer-events-none" style="background-image: radial-gradient(#EDE6D6 1px, transparent 1px); background-size: 22px 22px;"></div>
        <div class="relative z-10 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-[10px] font-bold uppercase tracking-[0.25em] text-amber-300/80">Registry Tenant Gereja</span>
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                ● PostgreSQL Live
              </span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl font-bold tracking-tight text-[#F5EFE0]">Manajemen Data Gereja</h1>
            <p class="mt-1 max-w-2xl text-xs sm:text-sm leading-relaxed text-[#B8C4C2]">
              Sinkronisasi data tabel <code class="px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-300 font-mono text-[11px]">churches</code>: Tanggal Berdiri, Ketua Umum BPP, Alamat Gedung, dan Media Sosial.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2.5">
            <button
              @click="loadChurches"
              :disabled="isLoading"
              class="inline-flex items-center gap-1.5 rounded-xl border border-amber-500/30 bg-white/5 px-3.5 py-2.5 text-xs font-bold text-amber-300 transition hover:bg-white/10 cursor-pointer disabled:opacity-50"
              title="Refresh Data dari Database"
            >
              <svg class="h-4 w-4" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Refresh</span>
            </button>

            <button
              @click="openCreateModal"
              class="inline-flex items-center justify-center gap-1.5 rounded-xl bg-amber-400 px-4 py-2.5 text-xs font-bold text-[#0B2027] shadow-lg shadow-amber-500/20 transition hover:bg-amber-300 cursor-pointer"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
              </svg>
              <span>+ Tambah Gereja</span>
            </button>

            <router-link
              to="/register-gereja"
              class="inline-flex items-center justify-center gap-1.5 rounded-xl border border-amber-400/50 bg-amber-500/10 px-4 py-2.5 text-xs font-bold text-amber-300 transition hover:bg-amber-500/20"
            >
              <span>Form Registrasi Lengkap &rarr;</span>
            </router-link>
          </div>
        </div>
      </section>

      <!-- Summary Stats Cards -->
      <section class="grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-4">
        <div class="rounded-xl border border-amber-500/20 bg-[#123138]/70 p-4 shadow-lg">
          <div class="flex items-center justify-between text-[#8AA0A4]">
            <p class="text-[10px] font-bold uppercase tracking-wider">Total Gereja</p>
            <i class="bi bi-building text-sm text-amber-400"></i>
          </div>
          <p class="mt-2 font-serif text-2xl sm:text-3xl font-bold text-amber-300">{{ summary.total }}</p>
          <p class="mt-0.5 text-[10px] text-[#8AA0A4]">Tercatat di PostgreSQL</p>
        </div>

        <div class="rounded-xl border border-emerald-500/20 bg-[#123138]/70 p-4 shadow-lg">
          <div class="flex items-center justify-between text-[#8AA0A4]">
            <p class="text-[10px] font-bold uppercase tracking-wider">Gereja Aktif</p>
            <i class="bi bi-check-circle text-sm text-emerald-400"></i>
          </div>
          <p class="mt-2 font-serif text-2xl sm:text-3xl font-bold text-emerald-300">{{ summary.active }}</p>
          <p class="mt-0.5 text-[10px] text-[#8AA0A4]">Status operasional aktif</p>
        </div>

        <div class="rounded-xl border border-amber-500/20 bg-[#123138]/70 p-4 shadow-lg">
          <div class="flex items-center justify-between text-[#8AA0A4]">
            <p class="text-[10px] font-bold uppercase tracking-wider">Status Pending</p>
            <i class="bi bi-clock-history text-sm text-amber-400"></i>
          </div>
          <p class="mt-2 font-serif text-2xl sm:text-3xl font-bold text-amber-300">{{ summary.pending }}</p>
          <p class="mt-0.5 text-[10px] text-[#8AA0A4]">Menunggu konfirmasi</p>
        </div>

        <div class="rounded-xl border border-rose-500/20 bg-[#123138]/70 p-4 shadow-lg">
          <div class="flex items-center justify-between text-[#8AA0A4]">
            <p class="text-[10px] font-bold uppercase tracking-wider">Nonaktif</p>
            <i class="bi bi-dash-circle text-sm text-rose-400"></i>
          </div>
          <p class="mt-2 font-serif text-2xl sm:text-3xl font-bold text-rose-300">{{ summary.nonactive }}</p>
          <p class="mt-0.5 text-[10px] text-[#8AA0A4]">Tidak beroperasi</p>
        </div>
      </section>

      <!-- Main Table Section -->
      <section class="rounded-2xl border border-white/10 bg-[#123138]/70 p-4 sm:p-5 shadow-2xl backdrop-blur-md">
        
        <!-- Error Banner -->
        <div v-if="errorMessage" class="mb-4 flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-200">
          <i class="bi bi-exclamation-triangle-fill text-rose-400"></i>
          <span>{{ errorMessage }}</span>
          <button type="button" class="ml-auto font-bold text-rose-300 underline cursor-pointer" @click="loadChurches">Coba lagi</button>
        </div>

        <!-- Filter & Search Bar -->
        <div class="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 class="font-serif text-lg sm:text-xl font-bold text-[#F5EFE0]">Daftar Institusi Gereja (Tabel: churches)</h2>
            <p class="mt-0.5 text-xs text-[#8AA0A4]">
              {{ isLoading ? 'Sedang memuat data dari PostgreSQL...' : `${filteredChurches.length} gereja ditampilkan (Total: ${churches.length} gereja)` }}
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2.5">
            <div class="relative flex-1 sm:w-64">
              <svg class="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#8AA0A4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z" />
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Cari kode, nama, ketua BPP..."
                class="h-9 w-full rounded-xl border border-white/10 bg-[#0B2027]/70 py-1.5 pl-8 pr-3 text-xs text-[#EDE6D6] outline-none transition focus:border-amber-400"
              />
            </div>

            <select v-model="statusFilter" class="h-9 rounded-xl border border-white/10 bg-[#0B2027]/70 px-3 text-xs text-[#EDE6D6] outline-none transition focus:border-amber-400 cursor-pointer">
              <option value="Semua">Semua Status</option>
              <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
            </select>
          </div>
        </div>

        <!-- Loading Spinner -->
        <div v-if="isLoading" class="py-16 text-center text-amber-300">
          <svg class="mx-auto h-8 w-8 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <p class="mt-3 text-xs font-serif tracking-wider">Menghubungkan & memuat data dari PostgreSQL...</p>
        </div>

        <!-- Table Data -->
        <div v-else class="overflow-x-auto rounded-xl border border-white/10">
          <table class="w-full text-left text-xs">
            <thead class="border-b border-amber-500/20 bg-[#0B2027]/90 text-[10px] font-bold uppercase tracking-wider text-amber-300">
              <tr>
                <th class="px-4 py-3 whitespace-nowrap">Kode Gereja</th>
                <th class="px-4 py-3 min-w-[220px]">Nama Resmi & Ketua Umum BPP</th>
                <th class="px-4 py-3 whitespace-nowrap">Tanggal Berdiri</th>
                <th class="px-4 py-3 min-w-[200px]">Alamat Lengkap Gedung</th>
                <th class="px-3 py-3 text-center whitespace-nowrap">Status</th>
                <th class="px-4 py-3 text-right whitespace-nowrap">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5 text-[#C6D2D0]">
              <tr v-for="church in filteredChurches" :key="church.id" class="align-middle transition hover:bg-white/[0.03]">
                
                <!-- Kode Gereja -->
                <td class="px-4 py-3.5 font-mono font-bold text-amber-300 whitespace-nowrap">
                  <span class="inline-block px-2.5 py-1 bg-amber-950/60 border border-amber-500/30 rounded text-[11px] shadow-sm">
                    {{ church.church_code }}
                  </span>
                </td>

                <!-- Nama Gereja & Ketua Umum BPP -->
                <td class="px-4 py-3.5">
                  <p class="font-bold text-[#F5EFE0] text-[13px] leading-tight">{{ church.church_name }}</p>
                  <div class="mt-1 flex items-center gap-1.5 text-[11px] text-amber-200/90">
                    <i class="bi bi-award-fill text-amber-400 text-xs"></i>
                    <span>Ketua BPP: <strong class="text-amber-300">{{ church.bpp_general_chairman || '-' }}</strong></span>
                  </div>
                  <!-- Social Links Badges (if any) -->
                  <div v-if="church.facebook_link || church.instagram_link || church.youtube_link || church.tiktok_link" class="mt-1.5 flex items-center gap-2.5 text-xs text-slate-400">
                    <a v-if="church.facebook_link" :href="church.facebook_link" target="_blank" rel="noopener noreferrer" class="hover:text-blue-400" title="Facebook">
                      <i class="bi bi-facebook"></i>
                    </a>
                    <a v-if="church.instagram_link" :href="church.instagram_link" target="_blank" rel="noopener noreferrer" class="hover:text-pink-400" title="Instagram">
                      <i class="bi bi-instagram"></i>
                    </a>
                    <a v-if="church.youtube_link" :href="church.youtube_link" target="_blank" rel="noopener noreferrer" class="hover:text-red-400" title="YouTube">
                      <i class="bi bi-youtube"></i>
                    </a>
                    <a v-if="church.tiktok_link" :href="church.tiktok_link" target="_blank" rel="noopener noreferrer" class="hover:text-teal-400" title="TikTok">
                      <i class="bi bi-tiktok"></i>
                    </a>
                  </div>
                </td>

                <!-- Tanggal Berdiri / Lahir -->
                <td class="px-4 py-3.5 whitespace-nowrap">
                  <div v-if="church.established_date" class="flex items-center gap-1.5 text-[#EDE6D6] font-medium text-[11px]">
                    <i class="bi bi-calendar3 text-amber-400"></i>
                    <span>{{ church.established_date }}</span>
                  </div>
                  <span v-else class="text-slate-500 italic text-[11px]">-</span>
                </td>

                <!-- Alamat Lengkap Gedung & Geolocation -->
                <td class="px-4 py-3.5">
                  <p class="text-[11px] text-[#B8C4C2] leading-snug line-clamp-2" :title="church.address">
                    {{ church.address }}
                  </p>
                  <div class="mt-1 flex flex-wrap items-center gap-1.5 text-[10px]">
                    <span v-if="church.city" class="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                      🏙️ {{ church.city }}
                    </span>
                    <a 
                      v-if="church.latitude && church.longitude" 
                      :href="church.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${church.latitude},${church.longitude}`" 
                      target="_blank" 
                      class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-500/15 border border-amber-500/30 text-amber-300 hover:text-amber-200 transition font-mono"
                      title="Buka titik Google Maps"
                    >
                      <span>📍 {{ Number(church.latitude).toFixed(3) }}, {{ Number(church.longitude).toFixed(3) }}</span>
                      <i class="bi bi-box-arrow-up-right text-[9px]"></i>
                    </a>
                    <span v-else class="text-slate-500 italic">Belum ada pin</span>
                  </div>
                </td>

                <!-- Status -->
                <td class="px-3 py-3.5 text-center whitespace-nowrap">
                  <button
                    @click="toggleStatus(church)"
                    class="rounded-full border px-2.5 py-0.5 text-[10px] font-bold transition cursor-pointer"
                    :class="statusMeta[church.status] || statusMeta['Aktif']"
                    title="Klik untuk mengubah status Aktif / Nonaktif"
                  >
                    {{ church.status }}
                  </button>
                </td>

                <!-- Aksi (Edit & Hapus) -->
                <td class="px-4 py-3.5 text-right whitespace-nowrap">
                  <div class="flex items-center justify-end gap-1.5">
                    <button 
                      @click="openEditModal(church)" 
                      class="inline-flex items-center gap-1 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-1 text-[11px] font-bold text-cyan-300 transition hover:bg-cyan-500/20 cursor-pointer"
                      title="Edit Data Gereja"
                    >
                      <i class="bi bi-pencil-square"></i>
                      <span>Edit</span>
                    </button>
                    <button 
                      @click="deleteChurch(church)" 
                      class="inline-flex items-center gap-1 rounded-lg border border-rose-500/30 bg-rose-500/10 px-2.5 py-1 text-[11px] font-bold text-rose-300 transition hover:bg-rose-500/20 cursor-pointer"
                      title="Hapus Data Gereja"
                    >
                      <i class="bi bi-trash3"></i>
                      <span>Hapus</span>
                    </button>
                  </div>
                </td>
              </tr>

              <!-- Empty State -->
              <tr v-if="filteredChurches.length === 0">
                <td colspan="6" class="px-4 py-12 text-center text-[#8AA0A4]">
                  <i class="bi bi-search text-3xl text-slate-600 block mb-2"></i>
                  <p class="font-semibold text-slate-400">Tidak ada data gereja yang sesuai pencarian atau filter.</p>
                  <button @click="openCreateModal" class="mt-3 text-xs text-amber-400 hover:underline cursor-pointer">
                    + Tambah Gereja Baru Sekarang
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Modal Create / Edit Gereja (Sesuai Skema PostgreSQL churches Lengkap) -->
      <Transition name="modal">
        <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-[#0B2027]/85 p-4 backdrop-blur-sm">
          <div class="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-amber-500/30 bg-[#123138] p-5 sm:p-6 shadow-2xl space-y-4">
            
            <!-- Modal Header -->
            <div class="flex items-center justify-between border-b border-white/10 pb-3">
              <div>
                <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-amber-300/80">
                  {{ modalMode === 'create' ? 'Tambah Data Baru' : 'Perbarui Data Gereja' }}
                </p>
                <h3 class="font-serif text-lg font-bold text-[#F5EFE0]">
                  {{ modalMode === 'create' ? 'Input Gereja ke PostgreSQL' : `Edit: ${selectedChurch?.church_name}` }}
                </h3>
              </div>
              <button @click="closeModal" class="rounded-lg p-2 text-[#8AA0A4] transition hover:bg-white/10 hover:text-[#EDE6D6]" title="Tutup">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18 18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Tab Nav inside Modal -->
            <div class="flex items-center gap-2 border-b border-white/10 pb-2 text-xs">
              <button
                type="button"
                @click="modalTab = 'info'"
                class="px-3 py-1.5 rounded-lg font-bold transition cursor-pointer"
                :class="modalTab === 'info' ? 'bg-amber-400 text-[#0B2027]' : 'text-slate-300 hover:bg-white/5'"
              >
                Informasi Utama & Alamat
              </button>
              <button
                type="button"
                @click="modalTab = 'medsos'"
                class="px-3 py-1.5 rounded-lg font-bold transition cursor-pointer"
                :class="modalTab === 'medsos' ? 'bg-amber-400 text-[#0B2027]' : 'text-slate-300 hover:bg-white/5'"
              >
                Media Sosial & Web
              </button>
            </div>

            <!-- Modal Form -->
            <form @submit.prevent="saveChurch" class="space-y-4 text-xs">
              
              <!-- TAB 1: INFORMASI UTAMA & ALAMAT -->
              <div v-show="modalTab === 'info'" class="grid grid-cols-1 gap-3.5 sm:grid-cols-2">
                <!-- Kode Gereja -->
                <label class="space-y-1">
                  <span class="font-semibold text-[#C6D2D0]">Kode Gereja *</span>
                  <input v-model.trim="form.church_code" required class="field font-mono uppercase" type="text" placeholder="Contoh: GP-005" />
                </label>

                <!-- Nama Gereja -->
                <label class="space-y-1">
                  <span class="font-semibold text-[#C6D2D0]">Nama Resmi Gereja *</span>
                  <input v-model.trim="form.church_name" required class="field" type="text" placeholder="Contoh: GKI Harapan Indah" />
                </label>

                <!-- Tanggal Berdiri / Lahir -->
                <label class="space-y-1">
                  <span class="font-semibold text-[#C6D2D0]">Tanggal Berdiri / Lahir Gereja</span>
                  <input v-model="form.established_date" class="field" type="date" />
                </label>

                <!-- Ketua Umum BPP -->
                <label class="space-y-1">
                  <span class="font-semibold text-[#C6D2D0]">Ketua Umum BPP Tiap Gereja</span>
                  <input v-model.trim="form.bpp_general_chairman" class="field" type="text" placeholder="Contoh: Pdt. Dr. Rubin Adi Abraham" />
                </label>

                <!-- Status Gereja -->
                <label class="space-y-1 sm:col-span-2">
                  <span class="font-semibold text-[#C6D2D0]">Status Operasional Gereja</span>
                  <select v-model="form.status" class="field">
                    <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
                  </select>
                </label>

                <!-- Alamat Lengkap -->
                <label class="space-y-1 sm:col-span-2">
                  <span class="font-semibold text-[#C6D2D0]">Alamat Lengkap Gedung Gereja *</span>
                  <textarea v-model.trim="form.address" required rows="2" class="field resize-none" placeholder="Jl. Raya Boulevard No. 1, Kota..."></textarea>
                </label>

                <!-- Kota / Wilayah -->
                <label class="space-y-1 sm:col-span-2">
                  <span class="font-semibold text-[#C6D2D0]">Kota / Wilayah Gereja</span>
                  <input v-model.trim="form.city" class="field" type="text" placeholder="Contoh: Jakarta Pusat, DKI Jakarta" />
                </label>

                <!-- Geolocation: Latitude & Longitude -->
                <div class="sm:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 rounded-xl bg-black/30 border border-amber-500/30">
                  <label class="space-y-1">
                    <span class="font-semibold text-amber-300 flex items-center gap-1">
                      <i class="bi bi-geo-alt"></i> Latitude (Garis Lintang)
                    </span>
                    <input v-model.number="form.latitude" step="any" class="field font-mono text-xs" type="number" placeholder="-6.1754" />
                  </label>

                  <label class="space-y-1">
                    <span class="font-semibold text-amber-300 flex items-center gap-1">
                      <i class="bi bi-geo-alt"></i> Longitude (Garis Bujur)
                    </span>
                    <input v-model.number="form.longitude" step="any" class="field font-mono text-xs" type="number" placeholder="106.8415" />
                  </label>

                  <div class="sm:col-span-2 space-y-1">
                    <div class="flex items-center justify-between">
                      <span class="font-semibold text-[#C6D2D0]">Google Maps URL</span>
                      <a 
                        v-if="form.latitude && form.longitude"
                        :href="form.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${form.latitude},${form.longitude}`" 
                        target="_blank" 
                        class="text-[10px] text-cyan-300 hover:underline inline-flex items-center gap-1"
                      >
                        <span>Uji Buka Maps ↗</span>
                      </a>
                    </div>
                    <input 
                      v-model.trim="form.google_maps_url" 
                      class="field font-mono text-xs" 
                      type="text" 
                      :placeholder="form.latitude && form.longitude ? `https://www.google.com/maps/search/?api=1&query=${form.latitude},${form.longitude}` : 'Tautan Google Maps...'" 
                    />
                  </div>
                </div>

                <!-- Deskripsi Sejarah -->
                <label class="space-y-1 sm:col-span-2">
                  <span class="font-semibold text-[#C6D2D0]">Deskripsi / Sejarah Singkat Gereja</span>
                  <textarea v-model.trim="form.church_description" rows="3" class="field resize-none" placeholder="Latar belakang berdirinya gereja atau visi misi pelayanan..."></textarea>
                </label>
              </div>

              <!-- TAB 2: MEDIA SOSIAL & LINKS -->
              <div v-show="modalTab === 'medsos'" class="space-y-3">
                <p class="text-[11px] text-slate-400">Tersimpan di kolom medsos tabel <code class="text-amber-300">churches</code> PostgreSQL.</p>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <!-- Facebook -->
                  <div class="space-y-1">
                    <span class="font-semibold text-[#C6D2D0] flex items-center gap-1">
                      <i class="bi bi-facebook text-blue-400"></i> Nama Akun Facebook
                    </span>
                    <input v-model.trim="form.facebook_name" class="field" type="text" placeholder="Nama Akun FB" />
                  </div>
                  <div class="space-y-1">
                    <span class="font-semibold text-[#C6D2D0]">Link Profil / Page FB</span>
                    <input v-model.trim="form.facebook_link" class="field" type="url" placeholder="https://facebook.com/..." />
                  </div>

                  <!-- Instagram -->
                  <div class="space-y-1">
                    <span class="font-semibold text-[#C6D2D0] flex items-center gap-1">
                      <i class="bi bi-instagram text-pink-400"></i> Username Instagram
                    </span>
                    <input v-model.trim="form.instagram_name" class="field" type="text" placeholder="@namagereja" />
                  </div>
                  <div class="space-y-1">
                    <span class="font-semibold text-[#C6D2D0]">Link Profil Instagram</span>
                    <input v-model.trim="form.instagram_link" class="field" type="url" placeholder="https://instagram.com/..." />
                  </div>

                  <!-- YouTube -->
                  <div class="space-y-1">
                    <span class="font-semibold text-[#C6D2D0] flex items-center gap-1">
                      <i class="bi bi-youtube text-red-400"></i> Channel YouTube
                    </span>
                    <input v-model.trim="form.youtube_name" class="field" type="text" placeholder="Nama Channel YouTube" />
                  </div>
                  <div class="space-y-1">
                    <span class="font-semibold text-[#C6D2D0]">Link Channel YouTube</span>
                    <input v-model.trim="form.youtube_link" class="field" type="url" placeholder="https://youtube.com/@..." />
                  </div>

                  <!-- TikTok -->
                  <div class="space-y-1">
                    <span class="font-semibold text-[#C6D2D0] flex items-center gap-1">
                      <i class="bi bi-tiktok text-teal-400"></i> Username TikTok
                    </span>
                    <input v-model.trim="form.tiktok_name" class="field" type="text" placeholder="@tiktok_gereja" />
                  </div>
                  <div class="space-y-1">
                    <span class="font-semibold text-[#C6D2D0]">Link Profil TikTok</span>
                    <input v-model.trim="form.tiktok_link" class="field" type="url" placeholder="https://tiktok.com/@..." />
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex flex-col-reverse gap-2 pt-3 sm:flex-row sm:justify-end border-t border-white/10">
                <button type="button" @click="closeModal" class="rounded-xl bg-white/5 px-4 py-2 font-semibold text-[#C6D2D0] transition hover:bg-white/10 cursor-pointer">
                  Batal
                </button>
                <button 
                  type="submit" 
                  :disabled="isSubmitting"
                  class="rounded-xl bg-amber-400 px-5 py-2 font-bold text-[#0B2027] transition hover:bg-amber-300 disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <i v-if="isSubmitting" class="bi bi-arrow-repeat animate-spin"></i>
                  <span>{{ isSubmitting ? 'Menyimpan...' : (modalMode === 'create' ? 'Simpan Gereja Baru' : 'Simpan Perubahan') }}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </div>
  </MainAdminLayout>
</template>

<style scoped>
.field {
  width: 100%;
  border-radius: 0.75rem;
  border: 1px solid var(--theme-border-soft, rgba(255, 255, 255, 0.1));
  background: var(--theme-bg-surface, #0B2027);
  padding: 0.5rem 0.75rem;
  color: var(--theme-text-primary, #EDE6D6);
  outline: none;
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.field:focus {
  border-color: var(--theme-gold, #fbbf24);
}

.field::placeholder {
  color: var(--theme-text-muted, #6f8589);
}

.field option {
  background: var(--theme-bg-card, #123138);
  color: var(--theme-text-primary, #EDE6D6);
}

:global(html[data-theme="light"]) .field,
:global(html.theme-light) .field,
:global(html.light) .field {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .field option,
:global(html.theme-light) .field option,
:global(html.light) .field option {
  background: #ffffff !important;
  color: #0f172a !important;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.98);
}
</style>
