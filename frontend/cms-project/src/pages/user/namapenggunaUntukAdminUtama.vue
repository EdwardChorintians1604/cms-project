<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { useTheme } from '@/composables/useTheme'

const { isDark } = useTheme()

// --- State Data Jemaat dari PostgreSQL (tabel jemaat_users) ---
const members = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const searchQuery = ref('')
const statusFilter = ref('Semua')
const genderFilter = ref('Semua')
const isFormModalOpen = ref(false)
const isCardModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const selectedMember = ref(null)
const isSubmitting = ref(false)
const showToast = ref(false)
const toastMessage = ref('')

const form = reactive({
  full_name: '',
  username: '',
  nik: '',
  no_ktp: '',
  gender: 'Laki-laki',
  birth_place: '',
  birth_date: '',
  church_domisili: '',
  church_central: '',
  origin: '',
  email: '',
  phone: '',
  address: '',
  married: 'Belum Menikah',
  education: 'Sarjana (S1)',
  chatecication: 'Sudah',
  is_active: true,
  password: ''
})

// --- 1. Ambil Data Real dari Database PostgreSQL ---
const loadMembers = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/users/`)
    if (!res.ok) throw new Error('Gagal memuat data jemaat dari database.')
    members.value = await res.json()
  } catch (err) {
    console.error('Load members error:', err)
    errorMessage.value = err.message || 'Gagal memuat data jemaat.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadMembers()
})

// --- Hitung Usia dari birth_date ---
const getAge = (birthDateStr) => {
  if (!birthDateStr) return '-'
  const today = new Date()
  const birthDate = new Date(birthDateStr)
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age + ' Thn'
}

// --- Format Badge Tanggal Ulang Tahun Jemaat ---
const formatBirthdayBadge = (birthDateStr) => {
  if (!birthDateStr) return ''
  const d = new Date(birthDateStr)
  if (isNaN(d.getTime())) return ''
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  const today = new Date()
  const isThisMonth = d.getMonth() === today.getMonth()
  const isToday = isThisMonth && d.getDate() === today.getDate()
  if (isToday) return `${d.getDate()} ${months[d.getMonth()]} (Hari Ini!)`
  if (isThisMonth) return `${d.getDate()} ${months[d.getMonth()]} (Bulan Ini)`
  return `${d.getDate()} ${months[d.getMonth()]}`
}

// --- Computed Filters & Metrics ---
const filteredMembers = computed(() => {
  return members.value.filter(m => {
    const q = searchQuery.value.toLowerCase()
    const matchesSearch = 
      (m.full_name && m.full_name.toLowerCase().includes(q)) ||
      (m.nik && m.nik.includes(q)) ||
      (m.username && m.username.toLowerCase().includes(q)) ||
      (m.email && m.email.toLowerCase().includes(q)) ||
      (m.church_domisili && m.church_domisili.toLowerCase().includes(q)) ||
      (m.church_central && m.church_central.toLowerCase().includes(q))
    
    const memberStatus = m.is_active ? 'Aktif' : 'Nonaktif'
    const matchesStatus = statusFilter.value === 'Semua' || memberStatus === statusFilter.value
    const matchesGender = genderFilter.value === 'Semua' || m.gender === genderFilter.value

    return matchesSearch && matchesStatus && matchesGender
  })
})

const totalMembers = computed(() => members.value.length)
const activeMembers = computed(() => members.value.filter(m => m.is_active).length)
const inactiveMembers = computed(() => members.value.filter(m => !m.is_active).length)
const maleMembers = computed(() => members.value.filter(m => m.gender === 'Laki-laki').length)
const femaleMembers = computed(() => members.value.filter(m => m.gender === 'Perempuan').length)

// --- Actions CRUD ---
const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  Object.assign(form, {
    full_name: '',
    username: '',
    nik: '',
    no_ktp: '',
    gender: 'Laki-laki',
    birth_place: '',
    birth_date: '',
    church_domisili: '',
    church_central: '',
    origin: '',
    email: '',
    phone: '',
    address: '',
    married: 'Belum Menikah',
    education: 'Sarjana (S1)',
    chatecication: 'Sudah',
    is_active: true,
    password: ''
  })
  isFormModalOpen.value = true
}

const openEditModal = (member) => {
  isEditing.value = true
  editingId.value = member.id
  Object.assign(form, {
    full_name: member.full_name,
    username: member.username,
    nik: member.nik,
    no_ktp: member.no_ktp || '',
    gender: member.gender,
    birth_place: member.birth_place || '',
    birth_date: member.birth_date || '',
    church_domisili: member.church_domisili || '',
    church_central: member.church_central || '',
    origin: member.origin || '',
    email: member.email,
    phone: member.phone,
    address: member.address || '',
    married: member.married || 'Belum Menikah',
    education: member.education || 'Sarjana (S1)',
    chatecication: member.chatecication || 'Sudah',
    is_active: member.is_active ?? true,
    password: ''
  })
  isFormModalOpen.value = true
}

const openCardModal = (member) => {
  selectedMember.value = member
  isCardModalOpen.value = true
}

const saveMember = async () => {
  isSubmitting.value = true
  try {
    if (isEditing.value && editingId.value) {
      // Update
      const payload = {
        full_name: form.full_name.trim(),
        username: form.username.trim(),
        nik: form.nik.trim(),
        no_ktp: form.no_ktp.trim() || null,
        gender: form.gender,
        birth_place: form.birth_place.trim() || null,
        birth_date: form.birth_date || null,
        church_domisili: form.church_domisili.trim() || null,
        church_central: form.church_central.trim() || null,
        origin: form.origin.trim() || null,
        email: form.email.trim(),
        phone: form.phone.trim(),
        address: form.address.trim() || null,
        married: form.married,
        education: form.education,
        chatecication: form.chatecication,
        is_active: form.is_active
      }
      if (form.password) {
        payload.password = form.password
      }

      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/users/${editingId.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}))
        throw new Error(errJson.detail || 'Gagal memperbarui data jemaat.')
      }

      await loadMembers()
      triggerToast(`Data jemaat ${form.full_name} berhasil diperbarui di database!`)
    } else {
      // Create
      if (!form.password) {
        throw new Error('Kata sandi wajib diisi untuk anggota jemaat baru.')
      }
      const payload = {
        full_name: form.full_name.trim(),
        username: form.username.trim(),
        nik: form.nik.trim(),
        no_ktp: form.no_ktp.trim() || null,
        gender: form.gender,
        birth_place: form.birth_place.trim(),
        birth_date: form.birth_date,
        church_domisili: form.church_domisili.trim(),
        church_central: form.church_central.trim(),
        origin: form.origin.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
        address: form.address.trim(),
        married: form.married,
        education: form.education,
        chatecication: form.chatecication,
        is_active: form.is_active,
        password: form.password
      }

      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}))
        throw new Error(errJson.detail || 'Gagal menambahkan data jemaat.')
      }

      await loadMembers()
      triggerToast(`Data jemaat ${form.full_name} berhasil ditambahkan ke database!`)
    }
    isFormModalOpen.value = false
  } catch (err) {
    alert(err.message || 'Terjadi kesalahan.')
  } finally {
    isSubmitting.value = false
  }
}

const toggleMemberStatus = async (m) => {
  const newStatus = !m.is_active
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/users/${m.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: newStatus })
    })
    if (!res.ok) throw new Error('Gagal mengubah status jemaat.')
    m.is_active = newStatus
    triggerToast(`Status akun ${m.full_name} diubah menjadi ${newStatus ? 'Aktif' : 'Nonaktif'}!`)
  } catch (err) {
    alert(err.message || 'Gagal mengubah status akun.')
  }
}

const deleteMember = async (id) => {
  if (confirm('Apakah Anda yakin ingin menghapus data biodata jemaat ini dari database PostgreSQL?')) {
    try {
      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/users/${id}`, {
        method: 'DELETE'
      })
      if (!res.ok) throw new Error('Gagal menghapus data jemaat.')
      await loadMembers()
      triggerToast('Data jemaat berhasil dihapus dari database!')
    } catch (err) {
      alert(err.message || 'Gagal menghapus data jemaat.')
    }
  }
}

const triggerToast = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}
</script>

<template>
  <MainAdminLayout>
    <div class="p-6 max-w-7xl mx-auto font-sans text-slate-100 space-y-6">
      
      <!-- Page Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-amber-500/30">
        <div>
          <h1 class="text-2xl font-bold font-serif text-amber-300 flex items-center gap-2">
            <i class="bi bi-person-lines-fill text-amber-400"></i>
            <span>Manajemen Biodata Jemaat</span>
          </h1>
          <p class="text-xs text-slate-300 mt-1">Data resmi jemaat & pengguna terdaftar di database PostgreSQL (tabel <code class="text-amber-400 bg-slate-900 px-1 py-0.5 rounded">jemaat_users</code>).</p>
        </div>

        <div class="flex flex-wrap items-center gap-2 self-start sm:self-auto">
          <!-- Tombol Navigasi ke Kalender Ultah Jemaat -->
          <router-link 
            to="/main_admin_calendar"
            style="text-decoration: none !important;"
            :class="[
              'px-3.5 py-2.5 font-serif font-bold text-xs uppercase tracking-wider rounded-xl transition-all duration-300 flex items-center gap-1.5 !no-underline hover:!no-underline cursor-pointer shadow-lg',
              isDark
                ? 'bg-gradient-to-r from-stone-800 to-yellow-600 hover:from-yellow-500 hover:to-amber-400 text-white shadow-yellow-900/60 border border-yellow-600/50'
                : 'bg-gradient-to-r from-amber-700 to-yellow-500 hover:from-yellow-400 hover:to-amber-300 text-white shadow-amber-600/40 border border-yellow-400/60'
            ]"
          >
            <span style="text-decoration: none !important;">Atur Agenda dan Jadwal Kegiatan di Kalender</span>
          </router-link>

        </div>
      </div>

      <!-- Error Notification -->
      <div v-if="errorMessage" class="p-3 bg-rose-950/80 border border-rose-800 text-rose-200 text-xs rounded-xl flex items-center gap-2">
        <i class="bi bi-exclamation-triangle-fill text-rose-400 text-base"></i>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Metrics Row -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="p-4 rounded-xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-amber-500/30 shadow-lg">
          <span class="text-xs text-slate-400 font-serif uppercase tracking-wider block">Total Jemaat Terdaftar</span>
          <span class="text-2xl font-bold font-serif text-amber-400 mt-1 block">{{ totalMembers }} Jiwa</span>
        </div>

        <div class="p-4 rounded-xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-emerald-500/30 shadow-lg">
          <span class="text-xs text-slate-400 font-serif uppercase tracking-wider block">Status Aktif</span>
          <span class="text-2xl font-bold font-serif text-emerald-400 mt-1 block">{{ activeMembers }} Jiwa</span>
        </div>

        <div class="p-4 rounded-xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-sky-500/30 shadow-lg">
          <span class="text-xs text-slate-400 font-serif uppercase tracking-wider block">Laki-laki</span>
          <span class="text-2xl font-bold font-serif text-sky-400 mt-1 block">{{ maleMembers }} Jiwa</span>
        </div>

        <div class="p-4 rounded-xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-purple-500/30 shadow-lg">
          <span class="text-xs text-slate-400 font-serif uppercase tracking-wider block">Perempuan</span>
          <span class="text-2xl font-bold font-serif text-purple-400 mt-1 block">{{ femaleMembers }} Jiwa</span>
        </div>
      </div>

      <!-- Controls & Filter Bar -->
      <div class="p-4 rounded-2xl bg-[#09112b] border border-slate-800 flex flex-col md:flex-row gap-4 items-center justify-between">
        <!-- Search Input -->
        <div class="relative w-full md:w-96">
          <i class="bi bi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Cari nama, NIK, username, gereja, atau email..."
            class="w-full pl-10 pr-4 py-2 bg-[#050918] border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
          >
        </div>

        <!-- Filter Dropdowns & Refresh -->
        <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-300 font-serif uppercase">Status:</span>
            <select 
              v-model="statusFilter"
              class="px-3 py-2 bg-[#050918] border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-400 cursor-pointer"
            >
              <option value="Semua">Semua Status</option>
              <option value="Aktif">Aktif</option>
              <option value="Nonaktif">Nonaktif</option>
            </select>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-300 font-serif uppercase">Gender:</span>
            <select 
              v-model="genderFilter"
              class="px-3 py-2 bg-[#050918] border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-400 cursor-pointer"
            >
              <option value="Semua">Semua Gender</option>
              <option value="Laki-laki">Laki-laki</option>
              <option value="Perempuan">Perempuan</option>
            </select>
          </div>

          <button 
            @click="loadMembers" 
            title="Refresh Data PostgreSQL"
            class="p-2 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-xl transition cursor-pointer border border-slate-700"
          >
            <i class="bi bi-arrow-clockwise" :class="{ 'animate-spin': isLoading }"></i>
          </button>
        </div>
      </div>

      <!-- Data Table -->
      <div class="rounded-2xl bg-gradient-to-br from-[#0c163a] to-[#070d24] border border-amber-500/30 shadow-2xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="bg-[#050918] text-amber-300 font-serif uppercase tracking-wider border-b border-amber-500/20">
                <th class="p-4">Identitas Jemaat</th>
                <th class="p-4">Gereja Domisili</th>
                <th class="p-4">Kontak & Alamat</th>
                <th class="p-4">Gender & Usia</th>
                <th class="p-4">Status</th>
                <th class="p-4 text-center">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800">
              <tr v-if="isLoading" class="text-center">
                <td colspan="6" class="p-8 text-slate-400 font-sans">
                  <i class="bi bi-arrow-clockwise animate-spin text-amber-400 text-xl block mb-2"></i>
                  Memuat biodata jemaat dari database PostgreSQL...
                </td>
              </tr>

              <tr v-else-if="filteredMembers.length === 0" class="text-center">
                <td colspan="6" class="p-8 text-slate-400 font-sans">
                  Tidak ada data biodata jemaat yang sesuai dengan pencarian.
                </td>
              </tr>

              <tr v-else v-for="m in filteredMembers" :key="m.id" class="hover:bg-slate-900/50 transition">
                
                <!-- Nama & NIK -->
                <td class="p-4">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 font-serif font-bold flex items-center justify-center flex-shrink-0 text-sm">
                      {{ m.full_name ? m.full_name.charAt(0) : 'J' }}
                    </div>
                    <div>
                      <div class="font-bold text-white text-sm font-serif">{{ m.full_name }}</div>
                      <div class="text-amber-300 font-mono text-[11px] mt-0.5">@{{ m.username }}</div>
                      <div class="text-slate-400 font-mono text-[10px]">NIK: {{ m.nik }}</div>
                    </div>
                  </div>
                </td>

                <!-- Gereja Domisili & Pusat -->
                <td class="p-4">
                  <div class="font-bold text-amber-200">{{ m.church_domisili }}</div>
                  <div v-if="m.church_central" class="text-slate-400 text-[11px] mt-0.5">
                    Pusat: {{ m.church_central }}
                  </div>
                  <div class="text-slate-400 text-[10px] mt-0.5">
                    Katekisasi: <span class="text-emerald-400 font-semibold">{{ m.chatecication || '-' }}</span>
                  </div>
                </td>

                <!-- Kontak -->
                <td class="p-4">
                  <div class="text-slate-200"><i class="bi bi-envelope me-1.5 text-amber-400"></i>{{ m.email }}</div>
                  <div class="text-slate-400 mt-0.5"><i class="bi bi-whatsapp me-1.5 text-emerald-400"></i>{{ m.phone }}</div>
                  <div v-if="m.address" class="text-slate-400 text-[11px] mt-0.5 truncate max-w-xs" :title="m.address">
                    <i class="bi bi-geo-alt me-1 text-sky-400"></i>{{ m.address }}
                  </div>
                </td>

                <!-- Gender & Usia + Badge Ultah Kalender -->
                <td class="p-4">
                  <div class="text-slate-200 font-semibold flex items-center gap-1.5">
                    <i :class="m.gender === 'Laki-laki' ? 'bi-gender-male text-sky-400' : 'bi-gender-female text-pink-400'"></i>
                    <span>{{ m.gender }}</span>
                  </div>
                  <div class="text-slate-400 text-[11px] mt-0.5">{{ getAge(m.birth_date) }} • {{ m.married || 'Belum Menikah' }}</div>
                  <div v-if="m.birth_place" class="text-slate-400 text-[10px] mt-0.5">Lahir: {{ m.birth_place }}</div>
                  
                  <!-- Badge Hari Ulang Tahun Jemaat di Kalender -->
                  <div v-if="m.birth_date" class="mt-1">
                    <router-link 
                      :to="`/hari-besar?filter=birthday&branch=${encodeURIComponent(m.church_domisili || '')}`"
                      class="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-md bg-pink-950/70 text-pink-300 border border-pink-500/30 hover:bg-pink-900 transition no-underline"
                      title="Lihat agenda ulang tahun jemaat ini di Kalender Gereja"
                    >
                      <span>🎂</span>
                      <span>{{ formatBirthdayBadge(m.birth_date) }}</span>
                      <i class="bi bi-arrow-up-right text-[8px]"></i>
                    </router-link>
                  </div>
                </td>

                <!-- Status -->
                <td class="p-4">
                  <span 
                    :class="m.is_active ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-rose-500/20 text-rose-300 border-rose-500/40'"
                    class="px-2.5 py-1 rounded-full text-[10px] font-serif uppercase tracking-wider font-bold border"
                  >
                    {{ m.is_active ? 'Aktif' : 'Nonaktif' }}
                  </span>
                </td>

                <!-- Actions -->
                <td class="p-4 text-center space-x-1.5">
                  <button 
                    @click="openCardModal(m)" 
                    title="Lihat Kartu Jemaat Digital"
                    class="p-1.5 bg-emerald-500/10 hover:bg-emerald-400 text-emerald-300 hover:text-slate-950 border border-emerald-500/30 rounded-lg transition cursor-pointer"
                  >
                    <i class="bi bi-person-badge"></i>
                  </button>

                  <button 
                    @click="openEditModal(m)" 
                    title="Edit Biodata"
                    class="p-1.5 bg-amber-500/10 hover:bg-amber-400 text-amber-300 hover:text-slate-950 border border-amber-500/30 rounded-lg transition cursor-pointer"
                  >
                    <i class="bi bi-pencil-square"></i>
                  </button>

                  <button 
                    @click="toggleMemberStatus(m)" 
                    :title="m.is_active ? 'Nonaktifkan Akun' : 'Aktifkan Akun'"
                    class="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition cursor-pointer border border-slate-700"
                  >
                    <i :class="m.is_active ? 'bi bi-slash-circle text-rose-400' : 'bi bi-check-circle text-emerald-400'"></i>
                  </button>

                  <button 
                    @click="deleteMember(m.id)" 
                    title="Hapus Data"
                    class="p-1.5 bg-rose-500/10 hover:bg-rose-500 text-rose-400 hover:text-white border border-rose-500/30 rounded-lg transition cursor-pointer"
                  >
                    <i class="bi bi-trash-fill"></i>
                  </button>
                </td>

              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Modal Form Tambah/Edit Biodata Jemaat -->
    <Teleport to="body">
      <div v-if="isFormModalOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
        <div class="w-full max-w-3xl max-h-[90vh] overflow-y-auto custom-scrollbar bg-[#091129] border border-amber-500/40 rounded-2xl p-6 sm:p-7 shadow-2xl relative font-sans text-slate-100">
          <button 
            @click="isFormModalOpen = false" 
            class="absolute top-4 right-4 text-slate-400 hover:text-amber-300 p-1.5 rounded-lg border border-slate-700 hover:bg-[#0b1435] transition cursor-pointer"
          >
            <i class="bi bi-x-lg"></i>
          </button>

          <h3 class="text-xl font-bold font-serif text-amber-300 mb-5 border-b border-amber-500/20 pb-3">
            {{ isEditing ? 'Edit Biodata Jemaat (PostgreSQL)' : 'Tambah Biodata Jemaat Baru (PostgreSQL)' }}
          </h3>

          <form @submit.prevent="saveMember" class="space-y-6 text-xs">
            
            <!-- Seksi 1: Data Pribadi -->
            <div class="space-y-3">
              <h4 class="text-amber-400 font-serif font-bold uppercase tracking-wider border-b border-slate-800 pb-1.5 flex items-center gap-2">
                <i class="bi bi-person-fill"></i> Data Identitas Pribadi
              </h4>

              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Nama Lengkap *</label>
                  <input v-model="form.full_name" type="text" required placeholder="Nama Lengkap Jemaat" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Username Akun *</label>
                  <input v-model="form.username" type="text" required placeholder="username.jemaat" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white font-mono">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">NIK (Nomor Induk Kependudukan) *</label>
                  <input v-model="form.nik" type="text" required placeholder="16 digit NIK" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white font-mono">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Nomor KTP (Opsional)</label>
                  <input v-model="form.no_ktp" type="text" placeholder="Nomor KTP jika berbeda" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white font-mono">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Jenis Kelamin *</label>
                  <select v-model="form.gender" required class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                    <option value="Laki-laki">Laki-laki</option>
                    <option value="Perempuan">Perempuan</option>
                  </select>
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Tempat Lahir *</label>
                  <input v-model="form.birth_place" type="text" required placeholder="Kota Lahir" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Tanggal Lahir *</label>
                  <input v-model="form.birth_date" type="date" required class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                  <p class="text-[11px] text-pink-300/90 mt-1 flex items-start gap-1 leading-tight">
                    <span class="text-xs">🎂</span>
                    <span>Tanggal lahir ini otomatis disinkronkan ke Kalender Hari Besar Gereja sebagai agenda Hari Ulang Tahun Jemaat cabang <strong>{{ form.church_domisili || 'bersangkutan' }}</strong>.</span>
                  </p>
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Status Pernikahan</label>
                  <select v-model="form.married" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                    <option value="Belum Menikah">Belum Menikah</option>
                    <option value="Menikah">Menikah</option>
                    <option value="Janda/Duda">Janda/Duda</option>
                  </select>
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Pendidikan Terakhir</label>
                  <input v-model="form.education" type="text" placeholder="Contoh: Sarjana (S1)" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                </div>
              </div>
            </div>

            <!-- Seksi 2: Keanggotaan & Gereja -->
            <div class="space-y-3">
              <h4 class="text-amber-400 font-serif font-bold uppercase tracking-wider border-b border-slate-800 pb-1.5 flex items-center gap-2">
                <i class="bi bi-church-fill"></i> Keanggotaan Gereja & Asal
              </h4>

              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Gereja Domisili / Ibadah *</label>
                  <input v-model="form.church_domisili" type="text" required placeholder="Contoh: GKPM Jemaat Pniel" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Gereja Pusat / Sinode *</label>
                  <input v-model="form.church_central" type="text" required placeholder="Contoh: Sinode GKPM" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Daerah / Suku Asal</label>
                  <input v-model="form.origin" type="text" placeholder="Contoh: Mentawai / Jawa" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Status Katekisasi</label>
                  <select v-model="form.chatecication" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                    <option value="Sudah">Sudah Katekisasi</option>
                    <option value="Belum">Belum Katekisasi</option>
                  </select>
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Status Akun</label>
                  <select v-model="form.is_active" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                    <option :value="true">Aktif</option>
                    <option :value="false">Nonaktif</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Seksi 3: Kontak & Alamat -->
            <div class="space-y-3">
              <h4 class="text-amber-400 font-serif font-bold uppercase tracking-wider border-b border-slate-800 pb-1.5 flex items-center gap-2">
                <i class="bi bi-geo-alt-fill"></i> Kontak & Alamat Domisili
              </h4>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="block font-semibold text-slate-300 mb-1">Email *</label>
                  <input v-model="form.email" type="email" required placeholder="email@jemaat.com" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                </div>

                <div>
                  <label class="block font-semibold text-slate-300 mb-1">No. HP / WhatsApp *</label>
                  <input v-model="form.phone" type="text" required placeholder="0812-xxxx-xxxx" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
                </div>
              </div>

              <div>
                <label class="block font-semibold text-slate-300 mb-1">Alamat Lengkap *</label>
                <textarea v-model="form.address" rows="2" required placeholder="Alamat rumah tinggal..." class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white"></textarea>
              </div>

              <div>
                <label class="block font-semibold text-slate-300 mb-1">
                  {{ isEditing ? 'Kata Sandi Baru (Kosongkan jika tidak diubah)' : 'Kata Sandi Akun Jemaat *' }}
                </label>
                <input v-model="form.password" :required="!isEditing" type="password" placeholder="••••••••••••" class="w-full px-3 py-2 bg-[#050918] border border-amber-500/30 rounded-xl text-white">
              </div>
            </div>

            <!-- Submit Button -->
            <div class="pt-3 border-t border-slate-800 flex justify-end gap-2">
              <button 
                type="button" 
                @click="isFormModalOpen = false" 
                class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-serif uppercase tracking-wider rounded-xl transition cursor-pointer"
              >
                Batal
              </button>
              <button 
                type="submit" 
                :disabled="isSubmitting"
                class="px-5 py-2 bg-amber-500 hover:bg-amber-400 disabled:bg-amber-500/50 text-slate-950 font-serif font-bold uppercase tracking-wider rounded-xl transition shadow-md cursor-pointer flex items-center gap-2"
              >
                <i v-if="isSubmitting" class="bi bi-arrow-clockwise animate-spin"></i>
                <span>{{ isEditing ? 'Perbarui Biodata' : 'Simpan ke Database' }}</span>
              </button>
            </div>

          </form>
        </div>
      </div>
    </Teleport>

    <!-- Modal Kartu Anggota Digital -->
    <Teleport to="body">
      <div v-if="isCardModalOpen && selectedMember" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
        <div class="w-full max-w-md bg-gradient-to-br from-[#0c163a] via-[#09112b] to-[#060b1e] border-2 border-amber-400/60 rounded-3xl p-6 shadow-2xl relative font-sans text-slate-100 space-y-5">
          <button 
            @click="isCardModalOpen = false" 
            class="absolute top-4 right-4 text-slate-400 hover:text-amber-300 p-1.5 rounded-lg border border-slate-700 hover:bg-[#0b1435] transition cursor-pointer"
          >
            <i class="bi bi-x-lg"></i>
          </button>

          <!-- Card Header -->
          <div class="text-center pb-3 border-b border-amber-500/30">
            <div class="inline-block px-3 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-400/40 text-[10px] font-serif uppercase tracking-widest font-bold mb-2">
              KARTU ANGGOTA JEMAAT DIGITAL
            </div>
            <h3 class="text-lg font-bold font-serif text-white tracking-wider">GRACEPOINT SYSTEM</h3>
            <p class="text-[11px] text-amber-200 font-serif">{{ selectedMember.church_domisili }}</p>
          </div>

          <!-- Card Content -->
          <div class="flex items-center gap-4">
            <div class="w-20 h-20 rounded-2xl bg-amber-500/20 border-2 border-amber-400 text-amber-300 font-serif text-3xl font-bold flex items-center justify-center flex-shrink-0 shadow-lg">
              {{ selectedMember.full_name ? selectedMember.full_name.charAt(0) : 'J' }}
            </div>

            <div class="space-y-1 text-xs">
              <div class="font-bold text-white text-base font-serif">{{ selectedMember.full_name }}</div>
              <div class="text-amber-300 font-mono font-bold">@{{ selectedMember.username }}</div>
              <div class="text-slate-300 text-[11px]">NIK: {{ selectedMember.nik }}</div>
              <div class="text-slate-400 text-[11px]">{{ selectedMember.gender }} • {{ getAge(selectedMember.birth_date) }}</div>
            </div>
          </div>

          <!-- Extra Member Details -->
          <div class="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5 text-[11px]">
            <div class="flex justify-between">
              <span class="text-slate-400">Kontak WhatsApp:</span>
              <span class="text-emerald-400 font-semibold">{{ selectedMember.phone }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Email:</span>
              <span class="text-slate-200 font-mono">{{ selectedMember.email }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Katekisasi:</span>
              <span class="text-amber-300 font-bold">{{ selectedMember.chatecication || '-' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Status Keanggotaan:</span>
              <span :class="selectedMember.is_active ? 'text-emerald-300' : 'text-rose-400'" class="font-bold">
                {{ selectedMember.is_active ? 'Aktif' : 'Nonaktif' }}
              </span>
            </div>
            <div v-if="selectedMember.address" class="flex justify-between">
              <span class="text-slate-400">Alamat:</span>
              <span class="text-slate-200 truncate max-w-xs">{{ selectedMember.address }}</span>
            </div>
          </div>

          <button 
            @click="isCardModalOpen = false" 
            class="w-full py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-serif font-bold text-xs uppercase tracking-wider rounded-xl transition cursor-pointer"
          >
            Tutup Kartu
          </button>
        </div>
      </div>
    </Teleport>

    <!-- Toast Notification -->
    <Teleport to="body">
      <Transition name="fade-slide">
        <div 
          v-if="showToast"
          class="fixed bottom-6 right-6 z-[10000] px-4 py-3 bg-amber-500 text-slate-950 font-bold font-serif text-xs rounded-xl shadow-2xl border border-amber-300 flex items-center gap-2"
        >
          <i class="bi bi-check-circle-fill text-lg"></i>
          <span>{{ toastMessage }}</span>
        </div>
      </Transition>
    </Teleport>

  </MainAdminLayout>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>