<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// Base URL API
const apiBaseUrl = ref(import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1')

// Status Koneksi DBMS PostgreSQL
const dbmsStatus = reactive({
  connected: false,
  engine: 'PostgreSQL',
  table: 'church_members',
  lastStatus: 'Menghubungkan ke DBMS...',
})

// Konteks Cabang Gereja Aktif
const activeChurch = reactive({
  id: null,
  code: 'GBI-PAD-11',
  name: 'Gereja Bethel Indonesia Cabang',
  adminName: 'Admin Gereja',
})

// Helper Auth Token & Headers
const getAuthToken = () => {
  return (
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

// Inisialisasi Konteks Cabang dari Login / Session
const initChurchContext = async () => {
  try {
    const rawUser = localStorage.getItem('user_data') || localStorage.getItem('user')
    if (rawUser) {
      const u = JSON.parse(rawUser)
      if (u.church_code) activeChurch.code = u.church_code
      if (u.church_name) activeChurch.name = u.church_name
      if (u.admin_name || u.full_name) activeChurch.adminName = u.admin_name || u.full_name
      if (u.church_id) activeChurch.id = u.church_id
    }

    const token = getAuthToken()
    if (token) {
      const meRes = await fetch(`${apiBaseUrl.value}/users/me`, { headers: getAuthHeaders() })
      if (meRes.ok) {
        const me = await meRes.json()
        if (me.church_code) activeChurch.code = me.church_code
        if (me.church_name) activeChurch.name = me.church_name
        if (me.admin_name || me.full_name) activeChurch.adminName = me.admin_name || me.full_name
        if (me.church_id) activeChurch.id = me.church_id
      }
    }
  } catch (err) {
    console.warn('Gagal memuat profil cabang otomatis:', err)
  }
}

// State List Data & Loading
const members = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)

// State Pencarian & Filter
const searchQuery = ref('')
const selectedStatus = ref('all')

// Toast Notification
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

// Modal States
const isAddModalOpen = ref(false)
const isEditModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const selectedMember = ref(null)

// Form State (Tanpa Sektor)
const defaultMemberForm = () => ({
  id: null,
  church_code: activeChurch.code,
  member_no: '',
  name: '',
  gender: 'L',
  phone: '',
  email: '',
  family_role: 'Kepala Keluarga',
  birthdate: '',
  status_baptis: 'Sudah Baptis & Sidi',
  attendance_status: 'Aktif',
  last_attended: new Date().toISOString().split('T')[0],
  address: '',
  notes: ''
})

const formData = reactive(defaultMemberForm())

// Fetch Members from PostgreSQL Backend
const fetchMembers = async () => {
  isLoading.value = true
  dbmsStatus.lastStatus = 'Mengambil data dari PostgreSQL...'
  try {
    let url = `${apiBaseUrl.value}/church-members/`
    const params = new URLSearchParams()
    if (activeChurch.code && activeChurch.code !== 'DEFAULT') {
      params.append('church_code', activeChurch.code)
    }
    if (params.toString()) {
      url += `?${params.toString()}`
    }

    const res = await fetch(url, { headers: getAuthHeaders() })
    if (res.ok) {
      const data = await res.json()
      members.value = data
      dbmsStatus.connected = true
      dbmsStatus.lastStatus = `Sinkron (${data.length} jemaat terhubung)`
    } else {
      throw new Error(`HTTP ${res.status}`)
    }
  } catch (err) {
    console.error('Fetch members error:', err)
    dbmsStatus.connected = false
    dbmsStatus.lastStatus = 'Koneksi API / DB terputus'
    showToast('Gagal memuat data jemaat dari database', 'error')
  } finally {
    isLoading.value = false
  }
}

// Add New Member
const openAddModal = () => {
  Object.assign(formData, defaultMemberForm())
  formData.church_code = activeChurch.code
  isAddModalOpen.value = true
}

const handleAddMember = async () => {
  if (!formData.name) {
    showToast('Nama jemaat wajib diisi', 'error')
    return
  }
  isSubmitting.value = true
  try {
    const payload = {
      ...formData,
      church_code: activeChurch.code,
      church_id: activeChurch.id,
      birthdate: formData.birthdate || null,
      last_attended: formData.last_attended || null,
    }
    const res = await fetch(`${apiBaseUrl.value}/church-members/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      const created = await res.json()
      members.value.unshift(created)
      isAddModalOpen.value = false
      showToast(`Data jemaat ${created.name} berhasil disimpan ke database!`, 'success')
      await fetchMembers()
    } else {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Gagal menyimpan ke database')
    }
  } catch (err) {
    console.error('Save member error:', err)
    showToast(err.message || 'Terjadi kesalahan saat menyimpan jemaat', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Edit Member
const openEditModal = (m) => {
  selectedMember.value = m
  Object.assign(formData, {
    id: m.id,
    church_code: m.church_code || activeChurch.code,
    member_no: m.member_no || '',
    name: m.name,
    gender: m.gender || 'L',
    phone: m.phone || '',
    email: m.email || '',
    family_role: m.family_role || 'Kepala Keluarga',
    birthdate: m.birthdate ? m.birthdate.toString().substring(0, 10) : '',
    status_baptis: m.status_baptis || 'Sudah Baptis & Sidi',
    attendance_status: m.attendance_status || 'Aktif',
    last_attended: m.last_attended ? m.last_attended.toString().substring(0, 10) : '',
    address: m.address || '',
    notes: m.notes || ''
  })
  isEditModalOpen.value = true
}

const handleUpdateMember = async () => {
  if (!formData.name) {
    showToast('Nama jemaat wajib diisi', 'error')
    return
  }
  isSubmitting.value = true
  try {
    const payload = {
      ...formData,
      birthdate: formData.birthdate || null,
      last_attended: formData.last_attended || null,
    }
    const res = await fetch(`${apiBaseUrl.value}/church-members/${formData.id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      const updated = await res.json()
      const idx = members.value.findIndex(m => m.id === updated.id)
      if (idx !== -1) members.value[idx] = updated
      isEditModalOpen.value = false
      showToast(`Data jemaat ${updated.name} berhasil diperbarui!`, 'success')
    } else {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Gagal memperbarui data jemaat')
    }
  } catch (err) {
    console.error('Update member error:', err)
    showToast(err.message || 'Terjadi kesalahan saat memperbarui jemaat', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Delete Member
const openDeleteModal = (m) => {
  selectedMember.value = m
  isDeleteModalOpen.value = true
}

const handleDeleteMember = async () => {
  if (!selectedMember.value) return
  isSubmitting.value = true
  try {
    const res = await fetch(`${apiBaseUrl.value}/church-members/${selectedMember.value.id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    if (res.ok) {
      members.value = members.value.filter(m => m.id !== selectedMember.value.id)
      isDeleteModalOpen.value = false
      showToast(`Data jemaat ${selectedMember.value.name} telah dihapus dari database.`, 'success')
      selectedMember.value = null
    } else {
      throw new Error('Gagal menghapus data jemaat')
    }
  } catch (err) {
    console.error('Delete member error:', err)
    showToast(err.message || 'Terjadi kesalahan saat menghapus', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Detail Member
const openDetailModal = (m) => {
  selectedMember.value = m
  isDetailModalOpen.value = true
}

// Filter Data (Pencarian & Status Keaktifan)
const filteredMembers = computed(() => {
  return members.value.filter(m => {
    const nameStr = (m.name || '').toLowerCase()
    const phoneStr = (m.phone || '')
    const idStr = (m.member_no || `JM-${m.id}` || '').toLowerCase()
    const roleStr = (m.family_role || '').toLowerCase()
    const q = searchQuery.value.toLowerCase()

    const matchQuery = !q || nameStr.includes(q) || phoneStr.includes(q) || idStr.includes(q) || roleStr.includes(q)
    const matchStatus = selectedStatus.value === 'all' || m.attendance_status === selectedStatus.value
    return matchQuery && matchStatus
  })
})

// Jemaat yang berulang tahun pekan ini (dihitung dinamis dari tanggal lahir di DBMS)
const birthdayThisWeek = computed(() => {
  const now = new Date()
  const currentMonth = now.getMonth() // 0 - 11
  const currentDate = now.getDate()

  return members.value.filter(m => {
    if (!m.birthdate) return false
    const bDate = new Date(m.birthdate)
    // Cek jika bulan sama dan tanggal dalam rentang +- 4 hari
    if (bDate.getMonth() === currentMonth) {
      const diff = bDate.getDate() - currentDate
      return diff >= -3 && diff <= 5
    }
    return false
  })
})

// Jemaat pasif / Perhatian Khusus (> 3 minggu tidak absen atau status perhatian khusus)
const inactiveAlerts = computed(() => {
  const now = new Date()
  return members.value.filter(m => {
    if (m.attendance_status === 'Perhatian Khusus' || m.attendance_status === 'Pasif') return true
    if (m.last_attended) {
      const last = new Date(m.last_attended)
      const diffDays = Math.floor((now - last) / (1000 * 60 * 60 * 24))
      return diffDays >= 21
    }
    return false
  })
})

// Send WhatsApp Message
const sendWhatsApp = (phone, name, type = 'greeting') => {
  if (!phone) {
    showToast('Nomor WhatsApp belum tersedia untuk jemaat ini', 'error')
    return
  }
  let msg = ''
  if (type === 'birthday') {
    msg = `Shalom Saudara/i ${name}, segenap Gembala & Majelis Jemaat ${activeChurch.name} mengucapkan Selamat Ulang Tahun! Kiranya kasih karunia dan damai sejahtera Kristus senantiasa menyertai langkah hidup Saudara. Tuhan Yesus Memberkati! 🎂🎉`
  } else if (type === 'pastoral') {
    msg = `Shalom Saudara/i ${name}, kami dari tim penggembalaan ${activeChurch.name} rindu menanyakan kabar Saudara. Apakah ada pokok doa yang bisa kami dukung dalam doa minggu ini? Tuhan Yesus menyertai selalu. 🙏`
  } else {
    msg = `Shalom Saudara/i ${name}, salam kasih dari sekretariat Admin ${activeChurch.name}.`
  }
  const cleanPhone = phone.replace(/^0/, '62').replace(/[^0-9]/g, '')
  window.open(`https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`, '_blank')
}

onMounted(async () => {
  await initChurchContext()
  await fetchMembers()
})
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">

      <!-- Toast Notification -->
      <transition
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="toast.show"
          class="fixed bottom-5 right-5 z-[100] max-w-sm w-full rounded-2xl shadow-2xl p-4 border flex items-start gap-3 backdrop-blur-md"
          :class="[
            toast.type === 'error'
              ? 'bg-rose-950/90 border-rose-500/50 text-rose-200'
              : 'bg-slate-900/95 border-amber-500/40 text-amber-200'
          ]"
        >
          <span class="text-xl">{{ toast.type === 'error' ? '⚠️' : '✅' }}</span>
          <div class="flex-1 text-xs leading-relaxed font-medium">
            {{ toast.message }}
          </div>
          <button @click="toast.show = false" class="text-slate-400 hover:text-white">&times;</button>
        </div>
      </transition>
      
      <!-- Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-amber-400 font-bold">CRM & DATABASE JEMAAT</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Manajemen Data Induk Warga Jemaat
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Kelola data induk warga jemaat cabang, pantau keaktifan kehadiran, dan jangkau jemaat secara pastoral dengan database PostgreSQL live.
          </p>
        </div>

        <div class="flex items-center gap-3">
          <button
            @click="openAddModal"
            class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            <span>Tambah Jemaat Baru</span>
          </button>
        </div>
      </div>

      <!-- PostgreSQL Database Live Connection Status Banner -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-2xl bg-slate-950/70 border border-slate-800 backdrop-blur-md">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700/80">
            <span
              class="w-2.5 h-2.5 rounded-full"
              :class="dbmsStatus.connected ? 'bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400/50' : 'bg-rose-400'"
            ></span>
            <span class="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
              DBMS: <span class="text-cyan-300">{{ dbmsStatus.engine }}</span>
            </span>
          </div>
          <div class="text-xs text-slate-400 flex items-center gap-2">
            <span>Tabel: <code class="text-amber-300 font-mono font-semibold">{{ dbmsStatus.table }}</code></span>
            <span class="text-slate-600">•</span>
            <span>Cabang: <strong class="text-white">{{ activeChurch.name }}</strong> ({{ activeChurch.code }})</span>
          </div>
        </div>

        <div class="flex items-center gap-3 self-end sm:self-auto">
          <span class="text-[11px] text-slate-400">
            Status: <span :class="dbmsStatus.connected ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'">{{ dbmsStatus.lastStatus }}</span>
          </span>
          <button
            @click="fetchMembers"
            :disabled="isLoading"
            class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 hover:text-white flex items-center gap-1.5 transition cursor-pointer"
            title="Refresh Data dari DBMS"
          >
            <svg class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <span>Sync</span>
          </button>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Total Anggota" subtitle="Jiwa terdaftar di DBMS">
          <div class="text-3xl font-bold text-amber-400 mt-1">
            {{ members.length }} <span class="text-xs font-normal text-slate-400">Jiwa</span>
          </div>
        </Card>
        <Card title="Jemaat Aktif" subtitle="Hadir bulan ini">
          <div class="text-3xl font-bold text-emerald-400 mt-1">
            {{ members.filter(m => m.attendance_status === 'Aktif').length }} <span class="text-xs font-normal text-slate-400">Jiwa</span>
          </div>
        </Card>
        <Card title="Ulang Tahun Pekan Ini" subtitle="Perhatian Gembala">
          <div class="text-3xl font-bold text-sky-400 mt-1">
            {{ birthdayThisWeek.length }} <span class="text-xs font-normal text-slate-400">Jemaat</span>
          </div>
        </Card>
        <Card title="Perlu Perkunjungan" subtitle="Pasif / > 3 pekan">
          <div class="text-3xl font-bold text-rose-400 mt-1">
            {{ inactiveAlerts.length }} <span class="text-xs font-normal text-slate-400">Jiwa</span>
          </div>
        </Card>
      </div>

      <!-- Dual Attention Panel: Ulang Tahun & Deteksi Pasif -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5" id="ulang-tahun">
        <!-- Birthday Reminder Card -->
        <div class="bg-gradient-to-br from-slate-900/90 to-slate-950/90 border border-sky-500/30 rounded-2xl p-5 shadow-xl">
          <div class="flex items-center justify-between mb-3 border-b border-sky-500/20 pb-2.5">
            <div class="flex items-center gap-2">
              <span class="text-xl">🎂</span>
              <h3 class="font-bold text-white text-sm">Ulang Tahun Jemaat Pekan Ini</h3>
            </div>
            <span class="px-2 py-0.5 text-[10px] font-bold bg-sky-500/20 text-sky-300 rounded-md border border-sky-500/40">
              {{ birthdayThisWeek.length }} Jemaat
            </span>
          </div>
          <div class="space-y-2.5 max-h-56 overflow-y-auto pr-1">
            <div
              v-if="birthdayThisWeek.length === 0"
              class="py-6 text-center text-xs text-slate-400"
            >
              Belum ada jemaat yang berulang tahun pada pekan ini.
            </div>
            <div
              v-for="b in birthdayThisWeek"
              :key="b.id"
              class="flex items-center justify-between p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-sky-500/40 transition-colors"
            >
              <div>
                <p class="font-semibold text-white text-xs">{{ b.name }}</p>
                <p class="text-[11px] text-slate-400">Tgl Lahir: {{ b.birthdate }} • {{ b.family_role }}</p>
              </div>
              <button
                @click="sendWhatsApp(b.phone, b.name, 'birthday')"
                class="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-[11px] font-medium flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <span>💬 Kirim WA Ultah</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Pastoral Alert Card -->
        <div class="bg-gradient-to-br from-slate-900/90 to-slate-950/90 border border-rose-500/30 rounded-2xl p-5 shadow-xl">
          <div class="flex items-center justify-between mb-3 border-b border-rose-500/20 pb-2.5">
            <div class="flex items-center gap-2">
              <span class="text-xl">⚠️</span>
              <h3 class="font-bold text-white text-sm">Early Warning: Jemaat Perlu Perkunjungan</h3>
            </div>
            <span class="px-2 py-0.5 text-[10px] font-bold bg-rose-500/20 text-rose-300 rounded-md border border-rose-500/40">
              {{ inactiveAlerts.length }} Jiwa
            </span>
          </div>
          <div class="space-y-2.5 max-h-56 overflow-y-auto pr-1">
            <div
              v-if="inactiveAlerts.length === 0"
              class="py-6 text-center text-xs text-slate-400"
            >
              Semua jemaat terpantau aktif beribadah. Puji Tuhan!
            </div>
            <div
              v-for="m in inactiveAlerts"
              :key="m.id"
              class="flex items-center justify-between p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-rose-500/40 transition-colors"
            >
              <div>
                <p class="font-semibold text-white text-xs">{{ m.name }}</p>
                <p class="text-[11px] text-rose-300/80">
                  Peran: {{ m.family_role }} • Terakhir Hadir: {{ m.last_attended || 'Belum Ada' }}
                </p>
              </div>
              <button
                @click="sendWhatsApp(m.phone, m.name, 'pastoral')"
                class="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 text-[11px] font-medium flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <span>🤝 Sapa Pastoral</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Member Table Filter & List -->
      <Card title="Daftar Induk Warga Jemaat" subtitle="Filter dan cari data jemaat cabang yang tersimpan di PostgreSQL">
        <!-- Filter Controls -->
        <div class="flex flex-col sm:flex-row gap-3 items-center justify-between pt-2 pb-4">
          <div class="relative w-full sm:w-80">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Cari nama, No. WA, peran keluarga, atau No Anggota..."
              class="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
            />
          </div>

          <div class="flex items-center gap-2.5 w-full sm:w-auto">
            <select
              v-model="selectedStatus"
              class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-amber-400 cursor-pointer"
            >
              <option value="all">Semua Status Keaktifan</option>
              <option value="Aktif">Aktif</option>
              <option value="Perhatian Khusus">Perhatian Khusus</option>
              <option value="Pasif">Pasif</option>
              <option value="Pindah">Pindah</option>
            </select>
          </div>
        </div>

        <!-- Table Responsive -->
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-3">No. Jemaat</th>
                <th class="p-3">Nama Lengkap</th>
                <th class="p-3">Peran Keluarga</th>
                <th class="p-3">Status Sakramen</th>
                <th class="p-3">No. WhatsApp / Kontak</th>
                <th class="p-3">Kehadiran</th>
                <th class="p-3 text-right">Aksi Manajemen</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
              <tr v-if="isLoading" class="text-center">
                <td colspan="7" class="p-8 text-slate-400">
                  <div class="flex items-center justify-center gap-2">
                    <svg class="w-5 h-5 animate-spin text-amber-400" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                    <span>Memuat data jemaat dari PostgreSQL...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="filteredMembers.length === 0" class="text-center">
                <td colspan="7" class="p-8 text-slate-400">
                  Tidak ada data jemaat yang sesuai kriteria pencarian / filter.
                </td>
              </tr>
              <tr
                v-else
                v-for="m in filteredMembers"
                :key="m.id"
                class="hover:bg-slate-800/40 transition-colors"
              >
                <td class="p-3 font-mono text-slate-400">
                  {{ m.member_no || `JM-${String(m.id).padStart(3, '0')}` }}
                </td>
                <td class="p-3">
                  <div class="flex items-center gap-2.5">
                    <div
                      class="w-8 h-8 rounded-full font-bold flex items-center justify-center text-xs border"
                      :class="m.gender === 'P' ? 'bg-pink-500/20 text-pink-300 border-pink-500/30' : 'bg-amber-500/20 text-amber-300 border-amber-500/30'"
                    >
                      {{ m.name.charAt(0) }}
                    </div>
                    <div>
                      <p class="font-semibold text-white">{{ m.name }}</p>
                      <p class="text-[10px] text-slate-400">{{ m.gender === 'P' ? 'Perempuan' : 'Laki-laki' }}</p>
                    </div>
                  </div>
                </td>
                <td class="p-3">
                  <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                    {{ m.family_role }}
                  </span>
                </td>
                <td class="p-3">
                  <span class="text-[11px] text-sky-300">{{ m.status_baptis }}</span>
                </td>
                <td class="p-3">
                  <span class="font-mono text-slate-300">{{ m.phone || '-' }}</span>
                </td>
                <td class="p-3">
                  <span
                    :class="[
                      'px-2 py-0.5 rounded-full text-[10px] font-bold border',
                      m.attendance_status === 'Aktif'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                    ]"
                  >
                    {{ m.attendance_status }}
                  </span>
                </td>
                <td class="p-3 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <!-- WhatsApp -->
                    <button
                      v-if="m.phone"
                      @click="sendWhatsApp(m.phone, m.name)"
                      title="Hubungi WhatsApp"
                      class="p-1.5 rounded-lg bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 border border-emerald-500/30 transition-all cursor-pointer"
                    >
                      <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/></svg>
                    </button>

                    <!-- View Detail -->
                    <button
                      @click="openDetailModal(m)"
                      title="Lihat Detail Jemaat"
                      class="p-1.5 rounded-lg bg-sky-500/15 text-sky-300 hover:bg-sky-500/25 border border-sky-500/30 transition-all cursor-pointer"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    </button>

                    <!-- Edit -->
                    <button
                      @click="openEditModal(m)"
                      title="Edit Data Jemaat"
                      class="p-1.5 rounded-lg bg-amber-500/15 text-amber-300 hover:bg-amber-500/25 border border-amber-500/30 transition-all cursor-pointer"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>

                    <!-- Delete -->
                    <button
                      @click="openDeleteModal(m)"
                      title="Hapus Data Jemaat"
                      class="p-1.5 rounded-lg bg-rose-500/15 text-rose-400 hover:bg-rose-500/25 border border-rose-500/30 transition-all cursor-pointer"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <!-- Modal Tambah Jemaat Baru -->
      <div
        v-if="isAddModalOpen"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto"
      >
        <div class="bg-slate-900 border border-amber-500/30 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4 my-8">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span class="text-amber-400">👤</span> Tambah Data Jemaat Baru (DBMS PostgreSQL)
            </h3>
            <button @click="isAddModalOpen = false" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <form @submit.prevent="handleAddMember" class="space-y-3.5">
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Nama Lengkap Sesuai KTP *</label>
              <input
                v-model="formData.name"
                required
                type="text"
                placeholder="Contoh: Samuel Alexander"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Jenis Kelamin</label>
                <select
                  v-model="formData.gender"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="L">Laki-laki (L)</option>
                  <option value="P">Perempuan (P)</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">No. WhatsApp</label>
                <input
                  v-model="formData.phone"
                  type="text"
                  placeholder="0812xxxx"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Email</label>
                <input
                  v-model="formData.email"
                  type="email"
                  placeholder="jemaat@email.com"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Peran dalam Keluarga</label>
                <select
                  v-model="formData.family_role"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Kepala Keluarga">Kepala Keluarga</option>
                  <option value="Istri">Istri</option>
                  <option value="Pemuda">Pemuda</option>
                  <option value="Pemudi">Pemudi</option>
                  <option value="Anak">Anak</option>
                  <option value="Lansia">Lansia</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Status Rohani / Sakramen</label>
                <select
                  v-model="formData.status_baptis"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Sudah Baptis & Sidi">Sudah Baptis & Sidi</option>
                  <option value="Sudah Baptis">Sudah Baptis</option>
                  <option value="Belum Baptis">Belum Baptis (Simpatisan)</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Tanggal Lahir (Untuk Reminder Ultah)</label>
                <input
                  v-model="formData.birthdate"
                  type="date"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Status Keaktifan</label>
                <select
                  v-model="formData.attendance_status"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Aktif">Aktif</option>
                  <option value="Perhatian Khusus">Perhatian Khusus</option>
                  <option value="Pasif">Pasif</option>
                  <option value="Pindah">Pindah</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Tanggal Terakhir Hadir Ibadah</label>
              <input
                v-model="formData.last_attended"
                type="date"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Alamat Tempat Tinggal</label>
              <textarea
                v-model="formData.address"
                rows="2"
                placeholder="Jl. / Kompleks / Kelurahan..."
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              ></textarea>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Catatan Pastoral (Opsional)</label>
              <input
                v-model="formData.notes"
                type="text"
                placeholder="Catatan konseling, riwayat pelayanan..."
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
              <button
                type="button"
                @click="isAddModalOpen = false"
                class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
              >
                Batal
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs cursor-pointer shadow-lg shadow-amber-500/20 flex items-center justify-center gap-1.5"
              >
                <svg v-if="isSubmitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                <span>{{ isSubmitting ? 'Menyimpan...' : 'Simpan ke Database' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Modal Edit Jemaat -->
      <div
        v-if="isEditModalOpen"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto"
      >
        <div class="bg-slate-900 border border-amber-500/30 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4 my-8">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span class="text-amber-400">✏️</span> Edit Data Jemaat ({{ formData.member_no || formData.name }})
            </h3>
            <button @click="isEditModalOpen = false" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <form @submit.prevent="handleUpdateMember" class="space-y-3.5">
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Nama Lengkap Sesuai KTP *</label>
              <input
                v-model="formData.name"
                required
                type="text"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Jenis Kelamin</label>
                <select
                  v-model="formData.gender"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="L">Laki-laki (L)</option>
                  <option value="P">Perempuan (P)</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">No. WhatsApp</label>
                <input
                  v-model="formData.phone"
                  type="text"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Email</label>
                <input
                  v-model="formData.email"
                  type="email"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Peran dalam Keluarga</label>
                <select
                  v-model="formData.family_role"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Kepala Keluarga">Kepala Keluarga</option>
                  <option value="Istri">Istri</option>
                  <option value="Pemuda">Pemuda</option>
                  <option value="Pemudi">Pemudi</option>
                  <option value="Anak">Anak</option>
                  <option value="Lansia">Lansia</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Status Rohani / Sakramen</label>
                <select
                  v-model="formData.status_baptis"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Sudah Baptis & Sidi">Sudah Baptis & Sidi</option>
                  <option value="Sudah Baptis">Sudah Baptis</option>
                  <option value="Belum Baptis">Belum Baptis (Simpatisan)</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Tanggal Lahir</label>
                <input
                  v-model="formData.birthdate"
                  type="date"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Status Keaktifan</label>
                <select
                  v-model="formData.attendance_status"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Aktif">Aktif</option>
                  <option value="Perhatian Khusus">Perhatian Khusus</option>
                  <option value="Pasif">Pasif</option>
                  <option value="Pindah">Pindah</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Tanggal Terakhir Hadir</label>
              <input
                v-model="formData.last_attended"
                type="date"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Alamat Tempat Tinggal</label>
              <textarea
                v-model="formData.address"
                rows="2"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              ></textarea>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Catatan Pastoral</label>
              <input
                v-model="formData.notes"
                type="text"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
              <button
                type="button"
                @click="isEditModalOpen = false"
                class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
              >
                Batal
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs cursor-pointer shadow-lg shadow-amber-500/20 flex items-center justify-center gap-1.5"
              >
                <svg v-if="isSubmitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                <span>{{ isSubmitting ? 'Memperbarui...' : 'Simpan Perubahan' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Modal Detail Jemaat -->
      <div
        v-if="isDetailModalOpen && selectedMember"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      >
        <div class="bg-slate-900 border border-sky-500/30 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <div class="flex items-center gap-2.5">
              <div
                class="w-9 h-9 rounded-full font-bold flex items-center justify-center text-sm border"
                :class="selectedMember.gender === 'P' ? 'bg-pink-500/20 text-pink-300 border-pink-500/30' : 'bg-amber-500/20 text-amber-300 border-amber-500/30'"
              >
                {{ selectedMember.name.charAt(0) }}
              </div>
              <div>
                <h3 class="text-base font-bold text-white">{{ selectedMember.name }}</h3>
                <span class="text-[11px] font-mono text-slate-400">
                  {{ selectedMember.member_no || `JM-${String(selectedMember.id).padStart(3, '0')}` }}
                </span>
              </div>
            </div>
            <button @click="isDetailModalOpen = false" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <div class="space-y-3 text-xs">
            <div class="grid grid-cols-2 gap-3 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              <div>
                <span class="text-slate-500 block text-[10px] uppercase font-semibold">Peran Keluarga</span>
                <p class="font-medium text-white">{{ selectedMember.family_role }}</p>
              </div>
              <div>
                <span class="text-slate-500 block text-[10px] uppercase font-semibold">Status Sakramen</span>
                <p class="font-medium text-sky-300">{{ selectedMember.status_baptis }}</p>
              </div>
              <div>
                <span class="text-slate-500 block text-[10px] uppercase font-semibold">Keaktifan</span>
                <p class="font-semibold" :class="selectedMember.attendance_status === 'Aktif' ? 'text-emerald-400' : 'text-rose-400'">
                  {{ selectedMember.attendance_status }}
                </p>
              </div>
              <div>
                <span class="text-slate-500 block text-[10px] uppercase font-semibold">Jenis Kelamin</span>
                <p class="font-medium text-white">{{ selectedMember.gender === 'P' ? 'Perempuan' : 'Laki-laki' }}</p>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              <div>
                <span class="text-slate-500 block text-[10px] uppercase font-semibold">Tanggal Lahir</span>
                <p class="font-medium text-white">{{ selectedMember.birthdate || '-' }}</p>
              </div>
              <div>
                <span class="text-slate-500 block text-[10px] uppercase font-semibold">Terakhir Hadir</span>
                <p class="font-medium text-white">{{ selectedMember.last_attended || '-' }}</p>
              </div>
              <div>
                <span class="text-slate-500 block text-[10px] uppercase font-semibold">No. WhatsApp</span>
                <p class="font-medium text-emerald-400 font-mono">{{ selectedMember.phone || '-' }}</p>
              </div>
              <div>
                <span class="text-slate-500 block text-[10px] uppercase font-semibold">Email</span>
                <p class="font-medium text-slate-300 truncate">{{ selectedMember.email || '-' }}</p>
              </div>
            </div>

            <div v-if="selectedMember.address" class="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              <span class="text-slate-500 block text-[10px] uppercase font-semibold mb-1">Alamat</span>
              <p class="text-slate-300 leading-relaxed">{{ selectedMember.address }}</p>
            </div>

            <div v-if="selectedMember.notes" class="bg-amber-950/20 p-3 rounded-xl border border-amber-500/20">
              <span class="text-amber-400 block text-[10px] uppercase font-semibold mb-1">Catatan Pastoral</span>
              <p class="text-amber-200/90 leading-relaxed">{{ selectedMember.notes }}</p>
            </div>
          </div>

          <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
            <button
              v-if="selectedMember.phone"
              @click="sendWhatsApp(selectedMember.phone, selectedMember.name)"
              class="px-4 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <span>💬 Kirim WhatsApp</span>
            </button>
            <button
              @click="isDetailModalOpen = false"
              class="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-white font-medium cursor-pointer"
            >
              Tutup
            </button>
          </div>
        </div>
      </div>

      <!-- Modal Konfirmasi Hapus Jemaat -->
      <div
        v-if="isDeleteModalOpen && selectedMember"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      >
        <div class="bg-slate-900 border border-rose-500/30 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
          <div class="flex items-center gap-3 text-rose-400">
            <div class="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-xl">
              🗑️
            </div>
            <div>
              <h3 class="text-base font-bold text-white">Hapus Data Jemaat?</h3>
              <p class="text-xs text-slate-400">Tindakan ini akan menghapus data jemaat dari database PostgreSQL.</p>
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <p class="text-xs font-semibold text-white">{{ selectedMember.name }}</p>
            <p class="text-[11px] text-slate-400">
              No: {{ selectedMember.member_no || `JM-${selectedMember.id}` }} • Peran: {{ selectedMember.family_role }}
            </p>
          </div>

          <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
            <button
              type="button"
              @click="isDeleteModalOpen = false"
              class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
            >
              Batal
            </button>
            <button
              @click="handleDeleteMember"
              :disabled="isSubmitting"
              class="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs cursor-pointer shadow-lg shadow-rose-600/30 flex items-center justify-center gap-1.5"
            >
              <svg v-if="isSubmitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
              <span>{{ isSubmitting ? 'Menghapus...' : 'Ya, Hapus Data' }}</span>
            </button>
          </div>
        </div>
      </div>

    </div>
  </ChurchAdminLayout>
</template>
