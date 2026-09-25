<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import AOS from 'aos'
import 'aos/dist/aos.css'

const isLoading = ref(true)
const errorMessage = ref('')
const isSubmittingUser = ref(false)

// Database Connection Status dari PostgreSQL Backend
const dbStatus = ref({
  connected: true,
  engine: 'PostgreSQL 16 (Relational DB)',
  database: 'cms_database',
  host: 'localhost:5432',
  user: 'postgres',
  ssl: 'Mode Require / TLS Verified'
})

// ==========================================
// PALET REGISTRY — token warna statis
// ==========================================
const colorTokens = {
  brass: { border: 'border-amber-500/30', top: 'border-t-amber-400', text: 'text-amber-300', chip: 'bg-amber-500/10 text-amber-300 border-amber-500/30', hex: '#d8a94a' },
  verdigris: { border: 'border-teal-500/30', top: 'border-t-teal-400', text: 'text-teal-300', chip: 'bg-teal-500/10 text-teal-300 border-teal-500/30', hex: '#3fada8' },
  wine: { border: 'border-rose-500/30', top: 'border-t-rose-400', text: 'text-rose-300', chip: 'bg-rose-500/10 text-rose-300 border-rose-500/30', hex: '#b6555f' },
  slate: { border: 'border-cyan-500/30', top: 'border-t-cyan-400', text: 'text-cyan-300', chip: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30', hex: '#4c93a8' }
}

const getChartColor = (color) => colorTokens[color]?.hex || colorTokens.brass.hex

const sparklineOptions = {
  chart: { type: 'area', height: 56, sparkline: { enabled: true } },
  stroke: { curve: 'smooth', width: 2.5 },
  fill: {
    opacity: 0.3,
    type: 'gradient',
    gradient: { shade: 'dark', type: 'vertical', shadeIntensity: 0.5, inverseColors: false, opacityFrom: 0.6, opacityTo: 0.1, stops: [0, 90, 100] }
  },
  tooltip: { enabled: false },
  xaxis: { crosshairs: { width: 1 } },
  yaxis: { min: 0 }
}

// 4 Kartu Statistik Utama
const stats = ref([
  { title: 'Gereja Terdaftar', value: '0', subtitle: 'Memuat data...', color: 'brass', series: [{ data: [1, 2, 3, 4, 5] }] },
  { title: 'Admin Cabang Gereja', value: '0', subtitle: 'Memuat data...', color: 'verdigris', series: [{ data: [1, 2, 3, 4, 5] }] },
  { title: 'Total Jemaat Terdata', value: '0', subtitle: 'Memuat data...', color: 'slate', series: [{ data: [0, 1, 1, 1] }] },
  { title: 'Beban Server & DB', value: '14%', subtitle: 'PostgreSQL Server Active', color: 'wine', series: [{ data: [20, 15, 18, 12, 14] }] }
])

// Recent Churches List
const recentChurches = ref([])

let inboxRefreshTimer

const formatAuditTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return '-'
  return new Intl.DateTimeFormat('id-ID', {
    dateStyle: 'short',
    timeStyle: 'medium'
  }).format(date)
}

// ==========================================
// USER MANAGEMENT STATE (HAK AKSES & AKUN)
// ==========================================
const activeRoleTab = ref('all')
const searchUserQuery = ref('')

const roleTabs = [
  { key: 'all', label: 'Semua' },
  { key: 'superadmin', label: 'Superadmin' },
  { key: 'church_admin', label: 'Admin Cabang' },
  { key: 'user', label: 'Jemaat' }
]

const roleMeta = {
  superadmin:   { label: 'Superadmin',   badge: 'bg-amber-500/10 text-amber-300 border-amber-500/30' },
  church_admin: { label: 'Admin Cabang', badge: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30' },
  user:         { label: 'Jemaat',       badge: 'bg-slate-500/10 text-slate-300 border-slate-500/30' }
}

const userList = ref([])

const filteredUsers = computed(() => {
  return userList.value.filter(u => {
    const matchesTab = activeRoleTab.value === 'all' || u.role === activeRoleTab.value
    const matchesQuery = !searchUserQuery.value ||
      (u.full_name && u.full_name.toLowerCase().includes(searchUserQuery.value.toLowerCase())) ||
      (u.email && u.email.toLowerCase().includes(searchUserQuery.value.toLowerCase())) ||
      (u.church && u.church.toLowerCase().includes(searchUserQuery.value.toLowerCase()))
    return matchesTab && matchesQuery
  })
})

const isAddUserModalOpen = ref(false)
const newUserForm = ref({ full_name: '', email: '', role: 'user', church: '', password: '' })

// ==========================================
// BACKUP & RESTORE SERVER STATE
// ==========================================
const backups = ref([])

// Data statistik tahunan pendaftaran gereja
// Data statistik pertumbuhan bulanan pendaftaran platform (MoM 2026)
const churchStats = ref([
  { month: 'Apr', year: 2026, period: 'Apr 2026', count: 0, cumulative: 0, is_current: false },
  { month: 'Mei', year: 2026, period: 'Mei 2026', count: 0, cumulative: 0, is_current: false },
  { month: 'Jun', year: 2026, period: 'Jun 2026', count: 0, cumulative: 0, is_current: false },
  { month: 'Jul', year: 2026, period: 'Jul 2026', count: 0, cumulative: 0, is_current: false },
  { month: 'Agu', year: 2026, period: 'Agu 2026', count: 0, cumulative: 0, is_current: false },
  { month: 'Sep', year: 2026, period: 'Sep 2026', count: 5, cumulative: 5, is_current: true }
])

const chartViewMode = ref('monthly') // 'monthly' | 'cumulative'

const mathStats = ref({
  activity_rate: 80.0,
  active_churches: 4,
  inactive_churches: 1,
  admin_per_church: 1.0,
  member_per_church: 0.2,
  total_entities: 12,
  this_month_growth: 5
})

const getItemValue = (item) => {
  return chartViewMode.value === 'cumulative' ? (item.cumulative ?? item.count ?? 0) : (item.count ?? 0)
}

const maxCount = computed(() => {
  const vals = churchStats.value.map(d => getItemValue(d))
  return Math.max(6, ...vals)
})

const totalChurches = computed(() => {
  if (mathStats.value.active_churches !== undefined && mathStats.value.inactive_churches !== undefined) {
    return mathStats.value.active_churches + mathStats.value.inactive_churches
  }
  return 5
})

// ==========================================
// FETCH DATA DARI DATABASE POSTGRESQL (API)
// ==========================================
const loadDashboardData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/superadmin-summary`)
    if (!res.ok) throw new Error('Gagal memuat ringkasan data dari database.')
    const data = await res.json()

    // 1. Status Koneksi DB
    if (data.db_status) {
      dbStatus.value = data.db_status
    }

    // 2. Ringkasan Statistik
    if (data.counts) {
      const c = data.counts
      stats.value = [
        {
          title: 'Gereja Terdaftar',
          value: String(c.total_churches),
          subtitle: `${c.active_churches} gereja aktif di portal`,
          color: 'brass',
          series: [{ data: [1, 2, Math.max(2, c.total_churches - 1), c.total_churches] }]
        },
        {
          title: 'Admin Cabang Gereja',
          value: String(c.total_church_admins),
          subtitle: `${c.active_church_admins} akun admin aktif`,
          color: 'verdigris',
          series: [{ data: [1, 2, Math.max(2, c.total_church_admins - 1), c.total_church_admins] }]
        },
        {
          title: 'Total Jemaat Terdata',
          value: String(c.total_jemaat),
          subtitle: `${c.active_jemaat} jemaat terdata`,
          color: 'slate',
          series: [{ data: [0, 1, Math.max(1, c.total_jemaat)] }]
        },
        {
          title: 'Beban Server & DB',
          value: c.server_load || '14%',
          subtitle: `${c.total_superadmins} Superadmin aktif`,
          color: 'wine',
          series: [{ data: [18, 16, 20, 15, 14] }]
        }
      ]
    }

    // 3. Gereja Terbaru
    if (data.recent_churches) {
      recentChurches.value = data.recent_churches
    }

    // 4. Statistik Pertumbuhan & Indikator Matematis
    if (data.math_stats) {
      mathStats.value = data.math_stats
    }
    if (data.monthly_stats && data.monthly_stats.length > 0) {
      churchStats.value = data.monthly_stats
    } else if (data.church_stats_by_year && data.church_stats_by_year.length > 0) {
      churchStats.value = data.church_stats_by_year
    }

    // 5. Daftar Seluruh Pengguna
    if (data.all_users) {
      userList.value = data.all_users
    }

    // 6. Backup snapshots
    if (data.backups) {
      backups.value = data.backups
    }

    // 7. Permohonan Pendaftaran Gereja Baru (Inbox Superadmin)
    if (data.church_requests) {
      churchRequests.value = data.church_requests
      pendingRequestsCount.value = data.pending_church_requests_count || 0
    }
  } catch (err) {
    console.error('Error fetching dashboard summary:', err)
    errorMessage.value = err.message || 'Gagal memuat data dari basis data.'
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadDashboardData()
  inboxRefreshTimer = window.setInterval(loadChurchRequests, 15000)
  AOS.refresh()
})

onUnmounted(() => {
  window.clearInterval(inboxRefreshTimer)
})

const handleAddUser = async () => {
  if (!newUserForm.value.email || !newUserForm.value.full_name) return
  isSubmittingUser.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/create-user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name: newUserForm.value.full_name,
        email: newUserForm.value.email,
        role: newUserForm.value.role,
        church: newUserForm.value.church || 'Pusat (System)',
        password: newUserForm.value.password || 'GracePoint#2026'
      })
    })
    if (!res.ok) {
      const err = await res.json()
      alert(err.detail || 'Gagal menambahkan user baru.')
      return
    }
    const result = await res.json()
    if (result.user) {
      userList.value.unshift(result.user)
    }
    newUserForm.value = { full_name: '', email: '', role: 'user', church: '', password: '' }
    isAddUserModalOpen.value = false
    loadDashboardData()
  } catch (err) {
    console.error('Add user error:', err)
    alert('Terjadi kesalahan saat menambah pengguna.')
  } finally {
    isSubmittingUser.value = false
  }
}

const toggleUserActive = async (user) => {
  const newActive = !user.is_active
  try {
    const rawId = user.raw_id || user.id
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/toggle-user-status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: rawId,
        role: user.role,
        is_active: newActive
      })
    })
    if (res.ok) {
      user.is_active = newActive
    }
  } catch (err) {
    console.error('Toggle status error:', err)
  }
}

const changeUserRole = (user, event) => {
  user.role = event.target.value
}

const deleteUser = async (user) => {
  if (!confirm(`Hapus pengguna "${user.full_name}" (${user.email}) dari basis data?`)) return
  try {
    const rawId = user.raw_id || user.id
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/users/${user.role}/${rawId}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      userList.value = userList.value.filter(u => u.id !== user.id)
      loadDashboardData()
    } else {
      const err = await res.json()
      alert(err.detail || 'Gagal menghapus user.')
    }
  } catch (err) {
    console.error('Delete user error:', err)
  }
}

// ==========================================
// INBOX & PERMOHONAN GEREJA BARU
// ==========================================
const churchRequests = ref([])
const pendingRequestsCount = ref(0)
const isInboxModalOpen = ref(false)
const selectedRequestTab = ref('all') // 'all' | 'pending' | 'completed'
const inboxSearchQuery = ref('')
const isInboxLoading = ref(false)
const inboxLastUpdated = ref(null)

const inboxPendingCount = computed(() => churchRequests.value.filter(r => r.status === 'Menunggu').length)
const inboxCompletedCount = computed(() => churchRequests.value.filter(r => r.status === 'Selesai').length)
const inboxStats = computed(() => [
  { label: 'Total Inbox', value: churchRequests.value.length, tone: 'text-[#EDE6D6]' },
  { label: 'Menunggu', value: inboxPendingCount.value, tone: 'text-rose-300' },
  { label: 'Selesai', value: inboxCompletedCount.value, tone: 'text-teal-300' }
])

const filteredChurchRequests = computed(() => {
  const query = inboxSearchQuery.value.trim().toLowerCase()
  return churchRequests.value.filter(request => {
    const matchesStatus = selectedRequestTab.value === 'all' || request.status === (selectedRequestTab.value === 'pending' ? 'Menunggu' : 'Selesai')
    const searchableText = [
      request.id,
      request.applicant_name,
      request.proposed_main_church,
      request.proposed_branch_church,
      request.city,
      request.channel
    ].filter(Boolean).join(' ').toLowerCase()
    return matchesStatus && (!query || searchableText.includes(query))
  })
})

const completedRequestsCount = computed(() => {
  return churchRequests.value.filter(r => r.status === 'Selesai').length
})

const loadChurchRequests = async () => {
  isInboxLoading.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/church-requests`)
    if (res.ok) {
      const data = await res.json()
      churchRequests.value = data.requests || []
      pendingRequestsCount.value = data.pending || 0
      inboxLastUpdated.value = new Date().toISOString()
    }
  } catch (err) {
    console.error('Error loading church requests:', err)
  } finally {
    isInboxLoading.value = false
  }
}

const updateRequestStatus = async (reqId, newStatus) => {
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/church-requests/${reqId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    })
    if (res.ok) {
      const target = churchRequests.value.find(r => r.id === reqId)
      if (target) target.status = newStatus
      pendingRequestsCount.value = churchRequests.value.filter(r => r.status === 'Menunggu').length
    }
  } catch (err) {
    console.error('Failed to update request status:', err)
  }
}

const deleteChurchRequest = async (request) => {
  if (!window.confirm(`Hapus permohonan ${request.id} dari ${request.applicant_name}? Data ini tidak dapat dikembalikan.`)) return

  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/church-requests/${request.id}`, {
      method: 'DELETE'
    })
    if (!res.ok) {
      const error = await res.json().catch(() => ({}))
      throw new Error(error.detail || 'Gagal menghapus permohonan.')
    }
    churchRequests.value = churchRequests.value.filter(item => item.id !== request.id)
    pendingRequestsCount.value = inboxPendingCount.value
  } catch (err) {
    console.error('Error deleting church request:', err)
    window.alert(err.message || 'Gagal menghapus permohonan.')
  }
}

// Modal Input Cepat Gereja Baru ke Database
const isAddChurchFromRequestOpen = ref(false)
const selectedRequestForDb = ref(null)
const newChurchInput = ref({
  church_code: '',
  church_name: '',
  address: '',
  bpp_general_chairman: '',
  established_date: ''
})
const isSubmittingChurchDb = ref(false)
const dbInputSuccess = ref('')
const dbInputError = ref('')

const openAddChurchModal = (req) => {
  selectedRequestForDb.value = req
  dbInputError.value = ''
  dbInputSuccess.value = ''

  // Suggest church code based on uppercase letters / abbreviation
  const words = req.proposed_main_church.split(/\s+/)
  let suggestedCode = words.map(w => w[0]).join('').toUpperCase()
  if (suggestedCode.length < 3) suggestedCode = req.proposed_main_church.substring(0, 4).toUpperCase()

  newChurchInput.value = {
    church_code: suggestedCode,
    church_name: req.proposed_main_church,
    address: req.address !== '-' ? req.address : (req.city !== '-' ? req.city : 'Indonesia'),
    bpp_general_chairman: req.leader_name !== '-' ? req.leader_name : '',
    established_date: ''
  }
  isAddChurchFromRequestOpen.value = true
}

const submitChurchToDb = async () => {
  if (!newChurchInput.value.church_code || !newChurchInput.value.church_name || !newChurchInput.value.address) {
    dbInputError.value = 'Kode Gereja, Nama Gereja, dan Alamat wajib diisi!'
    return
  }

  isSubmittingChurchDb.value = true
  dbInputError.value = ''
  dbInputSuccess.value = ''

  try {
    const payload = {
      church_code: newChurchInput.value.church_code.trim().toUpperCase(),
      church_name: newChurchInput.value.church_name.trim(),
      address: newChurchInput.value.address.trim(),
      bpp_general_chairman: newChurchInput.value.bpp_general_chairman.trim() || null,
      established_date: newChurchInput.value.established_date || null,
      status: 'Aktif'
    }

    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/churches/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Gagal menyimpan gereja ke database.')
    }

    const created = await res.json()
    dbInputSuccess.value = `Gereja "${created.church_name}" (Kode: ${created.church_code}) berhasil disimpan ke PostgreSQL!`

    // Otomatis ubah status permohonan menjadi Selesai
    if (selectedRequestForDb.value) {
      await updateRequestStatus(selectedRequestForDb.value.id, 'Selesai')
    }

    await loadDashboardData()
    await loadChurchRequests()

    setTimeout(() => {
      isAddChurchFromRequestOpen.value = false
    }, 2200)
  } catch (err) {
    dbInputError.value = err.message || 'Terjadi kesalahan saat menyimpan ke database.'
  } finally {
    isSubmittingChurchDb.value = false
  }
}

const sendConfirmationWhatsApp = (req, customCode = null) => {
  const code = customCode || newChurchInput.value.church_code || 'resmi'
  const text = `Halo ${req.applicant_name},

Kabar baik dari GracePoint! Gereja Induk Anda:
"${req.proposed_main_church}" telah berhasil kami daftarkan ke database DBMS GracePoint dengan Kode Gereja: ${code}.

Silakan buka kembali halaman pendaftaran Admin Gereja di GracePoint, klik tombol "Refresh & Cek Daftar Gereja", dan lanjutkan registrasi Anda.

Terima kasih atas kerja samanya!
- Admin Utama GracePoint`

  const phone = req.applicant_phone.replace(/[^0-9]/g, '')
  const url = `https://wa.me/${phone}?text=${encodeURIComponent(text)}`
  window.open(url, '_blank')
}
</script>

<template>
  <MainAdminLayout>
    <div class="relative space-y-10 text-[#EDE6D6]">

      <!-- ambient ink wash, sits behind everything -->
      <div class="pointer-events-none fixed inset-0 -z-10 bg-[#0B2027]"></div>
      <div class="pointer-events-none fixed -top-40 -right-40 w-[36rem] h-[36rem] rounded-full bg-amber-500/5 blur-3xl -z-10"></div>
      <div class="pointer-events-none fixed bottom-0 left-0 w-[28rem] h-[28rem] rounded-full bg-teal-500/5 blur-3xl -z-10"></div>

      <!-- ======================================================= -->
      <!-- HEADER — "sampul registry"                               -->
      <!-- ======================================================= -->
      <div id="data" data-aos="fade-down" data-aos-duration="600" class="animate__animated animate__fadeInDown relative overflow-hidden bg-[#123138]/80 border border-amber-500/20 rounded-3xl shadow-2xl backdrop-blur-xl">
        <div class="absolute inset-0 opacity-[0.07] pointer-events-none" style="background-image:radial-gradient(#EDE6D6 1px, transparent 1px); background-size:22px 22px;"></div>

        <div class="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-8 p-8">
          <div class="flex items-center gap-6">
            <!-- signature ornament: rosette / quatrefoil, echoes a rose window -->
            <div class="w-20 h-20 shrink-0 rounded-2xl bg-gradient-to-br from-amber-500/20 to-transparent border border-amber-400/30 flex items-center justify-center animate__animated animate__zoomIn">
              <svg viewBox="0 0 48 48" class="w-11 h-11 text-amber-300">
                <g fill="none" stroke="currentColor" stroke-width="1.4">
                  <circle cx="24" cy="24" r="4.2" />
                  <path d="M24 4c4 4 4 12 0 16-4-4-4-12 0-16z" />
                  <path d="M24 44c4-4 4-12 0-16-4 4-4 12 0 16z" />
                  <path d="M4 24c4-4 12-4 16 0-4 4-12 4-16 0z" />
                  <path d="M44 24c-4-4-12-4-16 0 4 4 12 4 16 0z" />
                  <circle cx="24" cy="24" r="17" opacity="0.4" />
                </g>
              </svg>
            </div>
            <div>
              <p class="text-[11px] uppercase tracking-[0.25em] text-amber-300/80 font-semibold mb-1">Buku Registry &middot; GracePoint Network</p>
              <h1 class="font-serif text-3xl sm:text-4xl font-bold text-[#F5EFE0] tracking-tight">Selamat Datang, Superadmin</h1>
              <p class="text-[#B8C4C2] text-sm mt-2 max-w-xl leading-relaxed">Kelola pendaftaran gereja, manajemen akun, pemantauan server, dan cadangan basis data dari satu konsol terpusat.</p>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-3 w-full sm:w-auto">
            <!-- Tombol Notifikasi & Inbox Permohonan Gereja Baru -->
            <button
              @click="isInboxModalOpen = true"
              class="relative px-4 py-3 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/40 font-bold text-xs transition-all flex items-center gap-2 cursor-pointer shrink-0 shadow-lg"
              title="Lihat Inbox & Permohonan Gereja Baru dari calon pendaftar"
            >
              <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span>Inbox Permohonan</span>
            </button>
            <button
              @click="loadDashboardData"
              :disabled="isLoading"
              class="px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-amber-300 border border-amber-500/30 font-semibold text-xs transition-all flex items-center gap-2 cursor-pointer shrink-0 disabled:opacity-50"
              title="Segarkan data dari database"
            >
              <svg :class="['w-4 h-4', { 'animate-spin': isLoading }]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              <span>{{ isLoading ? 'Sinkronisasi...' : 'Segarkan Data' }}</span>
            </button>
            <router-link
              to="/register-gereja"
              class="w-full sm:w-auto px-5 py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-[#0B2027] font-bold text-xs shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center gap-2 shrink-0 no-underline"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/></svg>
              <span>Daftar Gereja Baru</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- ======================================================= -->
      <!-- RINGKASAN — "lempeng registry"                           -->
      <!-- ======================================================= -->
      <div id="analytics" data-aos="fade-up" data-aos-duration="600" class="space-y-4">
        <div class="flex items-center gap-3">
          <svg viewBox="0 0 24 24" class="w-3.5 h-3.5 text-amber-400/70" fill="currentColor"><path d="M12 2l2.2 6.8H21l-5.6 4.1 2.1 6.9L12 15.8 6.5 19.8l2.1-6.9L3 8.8h6.8z"/></svg>
          <h2 class="text-[11px] font-bold uppercase tracking-[0.25em] text-amber-300/80">Ringkasan Statistik Real-Time Database</h2>
          <div class="h-px flex-1 bg-gradient-to-r from-amber-500/20 to-transparent"></div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
          <div
            v-for="(item, idx) in stats"
            :key="idx"
            data-aos="zoom-in-up"
            :data-aos-delay="idx * 100"
            class="relative bg-[#123138]/70 border border-white/5 border-t-4 rounded-2xl p-5 overflow-hidden backdrop-blur-md transition hover:-translate-y-1 duration-300"
            :class="colorTokens[item.color].top"
          >
            <p class="text-[10px] uppercase tracking-[0.18em] text-[#B8C4C2] font-semibold">{{ item.title }}</p>
            <div class="flex items-end justify-between gap-2 mt-3">
              <div class="font-serif text-3xl font-bold tracking-tight" :class="colorTokens[item.color].text">{{ item.value }}</div>
            </div>
            <p class="text-[11px] text-[#8AA0A4] mt-1">{{ item.subtitle }}</p>
            <div class="w-full -mb-4 mt-2">
              <apexchart type="area" height="52" :options="{ ...sparklineOptions, colors: [getChartColor(item.color)] }" :series="item.series" />
            </div>
          </div>
        </div>
      </div>

      <!-- ======================================================= -->
      <!-- KONTEN UTAMA                                             -->
      <!-- ======================================================= -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Kolom kiri -->
        <div class="lg:col-span-2 space-y-6">

          <!-- Statistik pendaftaran gereja & adopsi platform -->
          <div id="statistika-gereja" data-aos="fade-up" data-aos-delay="150" class="bg-[#123138]/70 border border-amber-500/15 rounded-2xl p-6 shadow-xl backdrop-blur-md">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
              <div>
                <div class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
                  <h2 class="font-serif text-lg font-bold text-[#F5EFE0]">Tren Pertumbuhan Pendaftaran Platform</h2>
                </div>
                <p class="text-xs text-[#8AA0A4] mt-0.5">Statistik riil pendaftaran gereja cabang per bulan (Tahun Berjalan 2026)</p>
              </div>

              <!-- Switch Mode: Bulanan (Baru) vs Akumulatif -->
              <div class="flex items-center gap-2">
                <div class="flex items-center bg-[#0B2027] p-1 rounded-xl border border-white/10 text-xs">
                  <button
                    @click="chartViewMode = 'monthly'"
                    class="px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer"
                    :class="chartViewMode === 'monthly' ? 'bg-amber-400 text-[#0B2027]' : 'text-[#8AA0A4] hover:text-amber-300'"
                  >
                    Bulanan (Baru)
                  </button>
                  <button
                    @click="chartViewMode = 'cumulative'"
                    class="px-3 py-1.5 rounded-lg font-semibold transition cursor-pointer"
                    :class="chartViewMode === 'cumulative' ? 'bg-amber-400 text-[#0B2027]' : 'text-[#8AA0A4] hover:text-amber-300'"
                  >
                    Akumulatif
                  </button>
                </div>
                <router-link
                  to="/data-gereja"
                  class="flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/25 rounded-xl text-xs font-semibold transition-all no-underline"
                >
                  Lihat Semua
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </router-link>
              </div>
            </div>

            <!-- SVG Bar Chart -->
            <div class="relative h-64 w-full mb-4">
              <svg class="w-full h-full" viewBox="0 0 600 240" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="barGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#f59e0b" />
                    <stop offset="100%" stop-color="#b45309" />
                  </linearGradient>
                  <linearGradient id="barGradientCurrent" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#fbbf24" />
                    <stop offset="100%" stop-color="#d97706" />
                  </linearGradient>
                </defs>

                <!-- Grid Horizontal Lines -->
                <line x1="50" y1="200" x2="580" y2="200" stroke="rgba(237,230,214,0.12)" stroke-width="1"/>
                <line x1="50" y1="150" x2="580" y2="150" stroke="rgba(237,230,214,0.06)" stroke-width="1" stroke-dasharray="4 4"/>
                <line x1="50" y1="100" x2="580" y2="100" stroke="rgba(237,230,214,0.06)" stroke-width="1" stroke-dasharray="4 4"/>
                <line x1="50" y1="50" x2="580" y2="50" stroke="rgba(237,230,214,0.06)" stroke-width="1" stroke-dasharray="4 4"/>

                <!-- Bars & Labels -->
                <g v-for="(item, i) in churchStats" :key="item.month">
                  <!-- Bar -->
                  <rect
                    :x="75 + i * 84"
                    :y="getItemValue(item) > 0 ? (200 - (getItemValue(item) / maxCount) * 150) : 197"
                    width="44"
                    :height="getItemValue(item) > 0 ? Math.max(10, (getItemValue(item) / maxCount) * 150) : 3"
                    :fill="item.is_current ? 'url(#barGradientCurrent)' : (getItemValue(item) > 0 ? 'url(#barGradient)' : 'rgba(255,255,255,0.08)')"
                    rx="6"
                    class="transition-all duration-500 ease-out hover:opacity-80 cursor-pointer"
                  />
                  <!-- Value Text -->
                  <text
                    :x="75 + i * 84 + 22"
                    :y="getItemValue(item) > 0 ? (200 - (getItemValue(item) / maxCount) * 150 - 8) : 190"
                    text-anchor="middle"
                    :fill="item.is_current ? '#fbbf24' : (getItemValue(item) > 0 ? '#e6bb63' : '#64748b')"
                    font-size="11"
                    font-weight="bold"
                  >{{ getItemValue(item) > 0 ? (chartViewMode === 'monthly' ? `+${getItemValue(item)}` : `${getItemValue(item)}`) : '0' }}</text>

                  <!-- Month Label -->
                  <text
                    :x="75 + i * 84 + 22"
                    y="222"
                    text-anchor="middle"
                    :fill="item.is_current ? '#f59e0b' : '#8AA0A4'"
                    :font-weight="item.is_current ? 'bold' : 'normal'"
                    font-size="11"
                  >{{ item.month }}</text>
                </g>

                <!-- Axis Lines -->
                <line x1="50" y1="200" x2="580" y2="200" stroke="rgba(237,230,214,0.25)" stroke-width="1"/>
                <line x1="50" y1="200" x2="50" y2="30" stroke="rgba(237,230,214,0.25)" stroke-width="1"/>

                <!-- Y-axis Values -->
                <text x="40" y="204" fill="#8AA0A4" font-size="10" text-anchor="end">0</text>
                <text x="40" y="154" fill="#8AA0A4" font-size="10" text-anchor="end">{{ Math.round(maxCount * 0.33) }}</text>
                <text x="40" y="104" fill="#8AA0A4" font-size="10" text-anchor="end">{{ Math.round(maxCount * 0.66) }}</text>
                <text x="40" y="54" fill="#8AA0A4" font-size="10" text-anchor="end">{{ maxCount }}</text>
              </svg>
            </div>

            <!-- Metrik Indikator Matematis & Statistik -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div class="bg-[#0B2027]/70 border border-teal-500/20 rounded-xl p-4 text-center">
                <div class="flex items-center justify-center gap-1.5 mb-1">
                  <span class="w-2 h-2 rounded-full bg-teal-400"></span>
                  <p class="text-[10px] uppercase tracking-wide text-[#8AA0A4]">Rasio Keaktifan Cabang</p>
                </div>
                <p class="font-serif text-2xl font-bold text-teal-300">{{ mathStats.activity_rate }}%</p>
                <p class="text-[10px] text-teal-200/70 mt-0.5">{{ mathStats.active_churches }} dari {{ totalChurches }} cabang berstatus Aktif</p>
              </div>

              <div class="bg-[#0B2027]/70 border border-amber-500/20 rounded-xl p-4 text-center">
                <div class="flex items-center justify-center gap-1.5 mb-1">
                  <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                  <p class="text-[10px] uppercase tracking-wide text-[#8AA0A4]">Pendaftaran Bulan Ini</p>
                </div>
                <p class="font-serif text-2xl font-bold text-amber-300">+{{ mathStats.this_month_growth }} Cabang</p>
                <p class="text-[10px] text-amber-200/70 mt-0.5">Periode September 2026 (Live)</p>
              </div>

              <div class="bg-[#0B2027]/70 border border-cyan-500/20 rounded-xl p-4 text-center">
                <div class="flex items-center justify-center gap-1.5 mb-1">
                  <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
                  <p class="text-[10px] uppercase tracking-wide text-[#8AA0A4]">Rata-Rata Admin / Cabang</p>
                </div>
                <p class="font-serif text-2xl font-bold text-cyan-300">{{ mathStats.admin_per_church }}</p>
                <p class="text-[10px] text-cyan-200/70 mt-0.5">{{ mathStats.total_entities }} total entitas akun terdata</p>
              </div>
            </div>
          </div>

          <!-- Shortcut ke Halaman Audit IT Terpisah -->
          <div id="security" data-aos="fade-up" data-aos-delay="200" class="bg-[#123138]/70 border border-teal-500/25 rounded-2xl p-5 shadow-xl backdrop-blur-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div class="flex items-center gap-3">
              <div class="p-2.5 rounded-xl bg-teal-500/10 text-teal-300 border border-teal-500/30 text-xl">
                🛡️
              </div>
              <div>
                <h3 class="font-serif text-sm font-bold text-[#F5EFE0]">Audit IT & Rekam Jejak Sistem</h3>
                <p class="text-[11px] text-[#8AA0A4] mt-0.5">Seluruh rekam jejak audit server & anomali kini dikelola terpusat di halaman khusus.</p>
              </div>
            </div>
            <RouterLink
              to="/audit-it"
              class="px-4 py-2 rounded-xl bg-teal-500/15 hover:bg-teal-500/25 text-teal-300 border border-teal-500/40 text-xs font-bold transition flex items-center gap-1.5 shrink-0"
            >
              <span>Buka Menu Audit IT</span>
              <span>&rarr;</span>
            </RouterLink>
          </div>

        </div>

        <!-- Kolom kanan -->
        <div class="space-y-4">

          <div data-aos="fade-left" data-aos-delay="200" class="bg-[#123138]/70 border border-white/5 rounded-2xl px-4 py-3.5 shadow-xl backdrop-blur-md">
            <div class="flex items-center justify-between gap-3 mb-3">
              <div class="flex items-center gap-2 min-w-0">
                <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-teal-500/10 text-teal-300 border border-teal-500/20">
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 7c0-1.105 3.582-2 8-2s8 .895 8 2-3.582 2-8 2-8-.895-8-2Zm0 0v5c0 1.105 3.582 2 8 2s8-.895 8-2V7m-16 5v5c0 1.105 3.582 2 8 2s8-.895 8-2v-5" /></svg>
                </span>
                <h2 class="truncate font-serif text-sm font-bold text-[#F5EFE0]">Koneksi Basis Data</h2>
              </div>
              <span
                class="flex shrink-0 items-center gap-1.5 rounded-full border px-2 py-1 text-[10px] font-bold"
                :class="dbStatus.connected ? 'bg-teal-500/10 text-teal-300 border-teal-500/30' : 'bg-rose-500/10 text-rose-300 border-rose-500/30'"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="dbStatus.connected ? 'bg-teal-400 animate-pulse' : 'bg-rose-400'"></span>
                {{ dbStatus.connected ? 'Terhubung' : 'Terputus' }}
              </span>
            </div>

            <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-[11px]">
              <div class="min-w-0 border-b border-white/5 pb-2">
                <dt class="text-[#8AA0A4]">Engine</dt>
                <dd class="truncate font-semibold text-[#EDE6D6]" :title="dbStatus.engine">{{ dbStatus.engine }}</dd>
              </div>
              <div class="min-w-0 border-b border-white/5 pb-2">
                <dt class="text-[#8AA0A4]">Database</dt>
                <dd class="truncate font-mono text-[#EDE6D6]" :title="dbStatus.database">{{ dbStatus.database }}</dd>
              </div>
              <div class="min-w-0">
                <dt class="text-[#8AA0A4]">Host</dt>
                <dd class="truncate font-mono text-[#EDE6D6]" :title="dbStatus.host">{{ dbStatus.host }}</dd>
              </div>
              <div class="min-w-0">
                <dt class="text-[#8AA0A4]">User</dt>
                <dd class="truncate font-mono text-[#EDE6D6]" :title="dbStatus.user">{{ dbStatus.user }}</dd>
              </div>
            </dl>
            <p class="mt-2 truncate border-t border-white/5 pt-2 text-[10px] text-teal-300" :title="dbStatus.ssl">SSL: {{ dbStatus.ssl }}</p>
          </div>

          <div data-aos="fade-left" data-aos-delay="300" class="bg-[#123138]/70 border border-white/5 rounded-2xl px-4 py-3.5 shadow-xl backdrop-blur-md">
            <div class="flex items-center justify-between gap-3 mb-3">
              <h2 class="font-serif text-sm font-bold text-[#F5EFE0]">Gereja Terbaru</h2>
              <RouterLink to="/data-gereja" class="text-[10px] font-semibold text-amber-300 hover:text-amber-200 no-underline">Lihat semua</RouterLink>
            </div>
            <div class="space-y-1.5">
              <div
                v-for="church in recentChurches" :key="church.id"
                class="flex items-center justify-between gap-2 rounded-lg bg-[#0B2027]/60 px-3 py-2 border-l-2"
                :class="church.status === 'Aktif' ? 'border-l-teal-400' : 'border-l-amber-400'"
              >
                <div class="min-w-0">
                  <p class="truncate text-[11px] font-semibold text-[#EDE6D6]">{{ church.name }}</p>
                  <p class="text-[10px] text-[#8AA0A4] font-mono">{{ church.code }} &middot; {{ church.date }}</p>
                </div>
                <span
                  class="ml-1 shrink-0 rounded-full border px-2 py-0.5 text-[9px] font-bold"
                  :class="church.status === 'Aktif' ? 'bg-teal-500/10 text-teal-300 border-teal-500/30' : 'bg-amber-500/10 text-amber-300 border-amber-500/30'"
                >{{ church.status }}</span>
              </div>
              <p v-if="recentChurches.length === 0" class="py-3 text-center text-[11px] text-[#8AA0A4]">Belum ada data gereja.</p>
            </div>
          </div>
        </div>

      </div>

      <!-- ======================================================= -->
      <!-- INBOX & PERMOHONAN PENDAFTARAN GEREJA BARU               -->
      <!-- ======================================================= -->
      <div id="inbox-permohonan" data-aos="fade-up" data-aos-delay="100" class="space-y-6 pt-6 border-t border-white/5">
        <div class="bg-[#123138]/70 border border-amber-500/20 rounded-2xl p-6 shadow-2xl backdrop-blur-md">
              <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-5 mb-6">
                <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
                <p class="text-[10px] uppercase tracking-[0.2em] text-amber-300/80 font-bold">Kotak Masuk & Tiket Bantuan</p>
              </div>
                  <h2 class="font-serif text-xl sm:text-2xl font-bold text-[#F5EFE0]">Inbox Permohonan Gereja Baru</h2>
                  <p class="text-xs text-[#8AA0A4] mt-1 leading-relaxed max-w-2xl">Semua permohonan dari calon pendaftar gereja, dengan status dan tindakan yang tersinkron dari inbox aktual.</p>
                  <p v-if="inboxLastUpdated" class="text-[10px] text-teal-300/70 mt-2 font-mono">Sinkron terakhir: {{ formatAuditTime(inboxLastUpdated) }}</p>
                </div>

                <div class="flex items-center gap-2.5 shrink-0">
                  <button
                    @click="loadChurchRequests"
                    :disabled="isInboxLoading"
                    class="px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-amber-300 border border-amber-500/30 font-semibold text-xs transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    <svg :class="['w-3.5 h-3.5', { 'animate-spin': isInboxLoading }]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 014.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    <span>{{ isInboxLoading ? 'Memuat...' : 'Segarkan Inbox' }}</span>
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
                <div v-for="stat in inboxStats" :key="stat.label" class="rounded-xl bg-[#0B2027]/70 border border-white/5 px-4 py-3">
                  <p class="text-[10px] uppercase tracking-[0.16em] text-[#8AA0A4]">{{ stat.label }}</p>
                  <p class="font-serif text-2xl font-bold mt-1" :class="stat.tone">{{ stat.value }}</p>
                </div>
              </div>

          <!-- Filter Tab Permohonan -->
              <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-5 border-b border-white/5 pb-3">
                <div class="flex items-center gap-2 overflow-x-auto">
            <button
              @click="selectedRequestTab = 'all'"
              :class="['px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer flex items-center gap-1.5', selectedRequestTab === 'all' ? 'bg-amber-400 text-[#0B2027]' : 'bg-[#0B2027]/60 text-[#8AA0A4] hover:text-[#EDE6D6]']"
            >
              <span>Semua Permohonan</span>
              <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-black/20 font-mono">{{ churchRequests.length }}</span>
            </button>

            <button
              @click="selectedRequestTab = 'pending'"
              :class="['px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer flex items-center gap-1.5', selectedRequestTab === 'pending' ? 'bg-rose-500 text-white' : 'bg-[#0B2027]/60 text-[#8AA0A4] hover:text-[#EDE6D6]']"
            >
              <span>Menunggu Tindakan</span>
              <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-black/30 font-mono">{{ inboxPendingCount }}</span>
            </button>

            <button
              @click="selectedRequestTab = 'completed'"
              :class="['px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer flex items-center gap-1.5', selectedRequestTab === 'completed' ? 'bg-teal-500 text-white' : 'bg-[#0B2027]/60 text-[#8AA0A4] hover:text-[#EDE6D6]']"
            >
              <span>Selesai Dimasukkan</span>
              <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-black/20 font-mono">{{ inboxCompletedCount }}</span>
            </button>
                </div>
                <div class="relative w-full md:w-64 shrink-0">
                  <svg class="w-4 h-4 text-[#8AA0A4] absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-4.35-4.35M17 11a6 6 0 1 1-12 0 6 6 0 0 1 12 0z"/></svg>
                  <input v-model="inboxSearchQuery" type="search" placeholder="Cari ID, gereja, pendaftar..." class="w-full bg-[#0B2027]/70 border border-white/10 focus:border-amber-400 text-[#EDE6D6] text-xs rounded-xl pl-9 pr-3 py-2.5 outline-none" />
                </div>
              </div>

          <!-- Empty State -->
          <div v-if="filteredChurchRequests.length === 0" class="py-12 text-center text-[#8AA0A4] border border-dashed border-white/10 rounded-xl">
            <p class="text-2xl mb-1">{{ inboxSearchQuery ? '⌕' : '📭' }}</p>
            <p class="text-xs">{{ inboxSearchQuery ? 'Tidak ada permohonan yang cocok dengan pencarian.' : 'Tidak ada permohonan dalam kategori ini.' }}</p>
          </div>

          <!-- Request Cards Grid -->
          <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div
              v-for="req in filteredChurchRequests"
              :key="req.id"
              class="p-4 rounded-2xl bg-[#0B2027]/70 border transition duration-200 flex flex-col justify-between"
              :class="req.status === 'Menunggu' ? 'border-amber-500/30 hover:border-amber-400/50 shadow-lg' : 'border-white/5 opacity-80'"
            >
              <div>
                <!-- Card Header -->
                <div class="flex items-center justify-between gap-2 border-b border-white/5 pb-2.5 mb-3">
                  <div class="flex items-center gap-2">
                    <span class="font-mono text-[11px] font-bold text-amber-300">{{ req.id }}</span>
                    <!-- Saluran Badge -->
                    <span v-if="req.channel === 'direct'" class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-500/15 border border-amber-500/30 text-amber-300">
                      🏛️ Direct Sistem
                    </span>
                    <span v-else-if="req.channel === 'wa'" class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
                      💬 WhatsApp
                    </span>
                    <span v-else class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-cyan-500/15 border border-cyan-500/30 text-cyan-300">
                      ✉️ Email
                    </span>
                  </div>

                  <!-- Status Badge -->
                  <span
                    :class="[
                      'px-2.5 py-0.5 rounded-full text-[10px] font-bold border',
                      req.status === 'Menunggu' 
                        ? 'bg-rose-500/15 border-rose-500/40 text-rose-300' 
                        : 'bg-teal-500/15 border-teal-500/40 text-teal-300'
                    ]"
                  >
                    {{ req.status }}
                  </span>
                </div>

                <!-- Info Pokok Gereja -->
                <div class="space-y-1.5 mb-3">
                  <h4 class="font-serif font-bold text-sm text-[#F5EFE0]">
                    {{ req.proposed_main_church }}
                  </h4>
                  <p v-if="req.proposed_branch_church && req.proposed_branch_church !== '-'" class="text-xs text-amber-300/90 font-medium">
                    📍 Cabang yang direncanakan: {{ req.proposed_branch_church }}
                  </p>
                  <p class="text-[11px] text-[#8AA0A4]">
                    Wilayah: <span class="text-[#EDE6D6]">{{ req.city }}</span> | Pimpinan: <span class="text-[#EDE6D6]">{{ req.leader_name }}</span>
                  </p>
                  <p class="text-[11px] text-[#8AA0A4]">
                    Alamat: <span class="text-[#EDE6D6]">{{ req.address }}</span>
                  </p>
                </div>

                <!-- Keluh Kesah Pendaftar -->
                <div class="p-2.5 rounded-xl bg-[#123138]/80 border border-white/5 text-[11px] text-amber-100/90 mb-3 italic">
                  "{{ req.complaint_notes }}"
                </div>

                <!-- Kontak Pendaftar -->
                <div class="flex items-center justify-between text-[11px] text-[#8AA0A4] mb-3">
                  <span>Pendaftar: <strong class="text-[#EDE6D6]">{{ req.applicant_name }}</strong></span>
                  <span class="font-mono text-emerald-400">WA: {{ req.applicant_phone }}</span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="pt-3 border-t border-white/5 flex flex-wrap items-center justify-between gap-2">
                <div class="text-[10px] text-[#8AA0A4] font-mono">
                  {{ req.created_at }}
                </div>

                <div class="flex items-center gap-2">
                  <!-- Button Chat WA -->
                  <button
                    type="button"
                    @click="sendConfirmationWhatsApp(req)"
                    class="px-2.5 py-1.5 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/40 text-emerald-300 text-xs font-semibold transition cursor-pointer flex items-center gap-1"
                    title="Hubungi pendaftar via WhatsApp"
                  >
                    <span>💬 Hubungi WA</span>
                  </button>

                  <!-- Button Input ke Database -->
                  <button
                    v-if="req.status === 'Menunggu'"
                    type="button"
                    @click="openAddChurchModal(req)"
                    class="px-3.5 py-1.5 rounded-lg bg-amber-400 hover:bg-amber-300 text-[#0B2027] text-xs font-bold transition cursor-pointer flex items-center gap-1.5 shadow-md shadow-amber-500/20"
                  >
                    <span>⚡ Input ke DBMS</span>
                  </button>

                  <!-- Toggle Selesai/Menunggu -->
                  <button
                    v-else
                    type="button"
                    @click="updateRequestStatus(req.id, 'Menunggu')"
                    class="px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-[#8AA0A4] transition cursor-pointer"
                  >
                    Tandai Belum
                  </button>
                  <button
                    type="button"
                    @click="deleteChurchRequest(req)"
                    class="px-2.5 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs font-semibold transition cursor-pointer"
                    title="Hapus permohonan dari inbox"
                  >
                    Hapus
                  </button>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>

      <!-- ======================================================= -->
      <!-- MANAJEMEN PENGGUNA TERPUSAT                              -->
      <!-- ======================================================= -->
      <div id="management" data-aos="fade-up" data-aos-delay="150" class="space-y-6 pt-6 border-t border-white/5">
        <div id="admin-cabang" class="bg-[#123138]/70 border border-amber-500/15 rounded-2xl p-6 shadow-2xl backdrop-blur-md">

          <!-- Header -->
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div>
              <p class="text-[10px] uppercase tracking-[0.2em] text-amber-300/80 font-semibold mb-1">Manajemen Pengguna Terpusat</p>
              <h2 class="font-serif text-xl font-bold text-[#F5EFE0]">Kelola Seluruh Akun</h2>
              <p class="text-xs text-[#8AA0A4] mt-0.5">Pilih kategori akun untuk membuka halaman pengelolaan terpusat.</p>
            </div>
            <!-- Badge total -->
            <div class="flex items-center gap-2 shrink-0">
              <span class="px-3 py-1.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/25">
                {{ userList.length }} Akun Terdaftar
              </span>
            </div>
          </div>

          <!-- 3 Access Buttons -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">

            <!-- Tombol: Jemaat (User) -->
            <router-link
              to="/data-pengguna"
              class="group relative flex flex-col gap-3 p-5 rounded-2xl border border-slate-500/20 bg-[#0B2027]/60 hover:bg-slate-500/10 hover:border-slate-400/40 transition-all duration-300 cursor-pointer no-underline hover:no-underline"
              style="text-decoration: none !important;"
            >
              <!-- Icon -->
              <div class="w-11 h-11 rounded-xl flex items-center justify-center bg-slate-500/10 border border-slate-500/20 group-hover:bg-slate-500/20 transition-all duration-300">
                <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2h5M12 12a4 4 0 100-8 4 4 0 000 8z"/>
                </svg>
              </div>
              <!-- Label -->
              <div>
                <p class="text-[10px] uppercase tracking-widest text-slate-400/70 font-semibold mb-0.5">Akun</p>
                <h3 class="font-serif font-bold text-base text-[#EDE6D6] group-hover:text-white transition-colors">Jemaat (User)</h3>
                <p class="text-[11px] text-[#8AA0A4] mt-1 leading-relaxed">Kelola akun jemaat terdaftar, status aktif, dan data profil.</p>
              </div>
              <!-- Arrow badge -->
              <div class="absolute top-4 right-4 w-7 h-7 rounded-full flex items-center justify-center bg-slate-500/10 border border-slate-500/20 group-hover:bg-slate-400/20 group-hover:border-slate-400/40 transition-all">
                <svg class="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-200 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>
                </svg>
              </div>
            </router-link>

            <!-- Tombol: Superadmin -->
            <router-link
              to="/main_admin_user"
              class="group relative flex flex-col gap-3 p-5 rounded-2xl border border-amber-500/20 bg-[#0B2027]/60 hover:bg-amber-500/10 hover:border-amber-400/40 transition-all duration-300 cursor-pointer no-underline hover:no-underline"
              style="text-decoration: none !important;"
            >
              <!-- Icon -->
              <div class="w-11 h-11 rounded-xl flex items-center justify-center bg-amber-500/10 border border-amber-500/20 group-hover:bg-amber-500/20 transition-all duration-300">
                <svg class="w-5 h-5 text-amber-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
                </svg>
              </div>
              <!-- Label -->
              <div>
                <p class="text-[10px] uppercase tracking-widest text-amber-400/70 font-semibold mb-0.5">Akun</p>
                <h3 class="font-serif font-bold text-base text-[#EDE6D6] group-hover:text-white transition-colors">Superadmin</h3>
                <p class="text-[11px] text-[#8AA0A4] mt-1 leading-relaxed">Kelola akun superadmin, hak akses penuh, dan status sistem.</p>
              </div>
              <!-- Arrow badge -->
              <div class="absolute top-4 right-4 w-7 h-7 rounded-full flex items-center justify-center bg-amber-500/10 border border-amber-500/20 group-hover:bg-amber-400/20 group-hover:border-amber-400/40 transition-all">
                <svg class="w-3.5 h-3.5 text-amber-400 group-hover:text-amber-200 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>
                </svg>
              </div>
            </router-link>

            <!-- Tombol: Admin Cabang (Church Admin) -->
            <router-link
              to="/manajemen-admin-cabang"
              class="group relative flex flex-col gap-3 p-5 rounded-2xl border border-cyan-500/20 bg-[#0B2027]/60 hover:bg-cyan-500/10 hover:border-cyan-400/40 transition-all duration-300 cursor-pointer no-underline hover:no-underline"
              style="text-decoration: none !important;"
            >
              <!-- Icon -->
              <div class="w-11 h-11 rounded-xl flex items-center justify-center bg-cyan-500/10 border border-cyan-500/20 group-hover:bg-cyan-500/20 transition-all duration-300">
                <svg class="w-5 h-5 text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
              </div>
              <!-- Label -->
              <div>
                <p class="text-[10px] uppercase tracking-widest text-cyan-400/70 font-semibold mb-0.5">Akun</p>
                <h3 class="font-serif font-bold text-base text-[#EDE6D6] group-hover:text-white transition-colors">Admin Cabang</h3>
                <p class="text-[11px] text-[#8AA0A4] mt-1 leading-relaxed">Kelola akun admin per gereja cabang, tugas, dan izin pengelolaan.</p>
              </div>
              <!-- Arrow badge -->
              <div class="absolute top-4 right-4 w-7 h-7 rounded-full flex items-center justify-center bg-cyan-500/10 border border-cyan-500/20 group-hover:bg-cyan-400/20 group-hover:border-cyan-400/40 transition-all">
                <svg class="w-3.5 h-3.5 text-cyan-400 group-hover:text-cyan-200 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>
                </svg>
              </div>
            </router-link>

          </div>

          <!-- Hint footer -->
          <p class="text-[10px] text-[#8AA0A4]/60 mt-5 flex items-center gap-1.5">
            <svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Klik salah satu kartu di atas untuk membuka halaman pengelolaan akun lengkap beserta tabel data.
          </p>

        </div>
      </div>


      <!-- ======================================================= -->
      <!-- BACKUP & RESTORE                                         -->
      <!-- ======================================================= -->
      <div id="databackup" data-aos="fade-up" data-aos-delay="200" class="space-y-6 pt-6 border-t border-white/5">
        <div class="bg-[#123138]/70 border border-white/5 rounded-2xl p-6 shadow-2xl backdrop-blur-md">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <p class="text-[10px] uppercase tracking-[0.2em] text-cyan-300/80 font-semibold mb-1">Infrastruktur Server</p>
              <h2 class="font-serif text-xl font-bold text-[#F5EFE0]">Backup & Pemulihan Database</h2>
              <p class="text-xs text-[#8AA0A4] mt-0.5">Salinan cadangan (SQL dump) dan snapshot point PostgreSQL Database.</p>
            </div>
            <router-link
              to="/backup-database"
              class="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-[#0B2027] font-bold text-xs shadow-lg shadow-cyan-500/20 transition flex items-center gap-2 cursor-pointer shrink-0 no-underline"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
              <span>Buka Registry Backup</span>
            </router-link>
          </div>

          <div class="overflow-x-auto rounded-xl border border-white/10">
            <table class="w-full text-left text-xs">
              <thead class="bg-[#0B2027]/80 text-cyan-300 font-bold uppercase border-b border-cyan-500/20">
                <tr>
                  <th class="py-3 px-4">Nama Berkas SQL</th>
                  <th class="py-3 px-4">Tipe Backup</th>
                  <th class="py-3 px-4">Ukuran</th>
                  <th class="py-3 px-4">Waktu Pembuatan</th>
                  <th class="py-3 px-4">Status</th>
                  <th class="py-3 px-4 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/5 text-[#C6D2D0]">
                <tr v-for="b in backups" :key="b.id" class="hover:bg-white/[0.03] transition">
                  <td class="py-3.5 px-4 font-mono font-bold text-[#EDE6D6]">{{ b.filename }}</td>
                  <td class="py-3.5 px-4 text-[#8AA0A4]">{{ b.type }}</td>
                  <td class="py-3.5 px-4 font-mono text-amber-300">{{ b.size }}</td>
                  <td class="py-3.5 px-4 text-[#8AA0A4] font-mono">{{ b.created_at }}</td>
                  <td class="py-3.5 px-4">
                    <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-teal-500/10 text-teal-300 border border-teal-500/30">{{ b.status }}</span>
                  </td>
                  <td class="py-3.5 px-4 text-right text-[#8AA0A4]">Registry</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    <!-- ======================================================= -->
    <!-- MODAL: TAMBAH USER / ADMIN BARU                          -->
    <!-- ======================================================= -->
    <!-- MODAL INPUT CEPAT GEREJA DARI PERMOHONAN KE POSTGRESQL  -->
    <!-- ======================================================= -->
    <Transition name="modal">
      <div v-if="isAddChurchFromRequestOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B2027]/85 backdrop-blur-md overflow-y-auto">
        <div class="bg-[#123138] border border-amber-500/35 rounded-2xl p-6 w-full max-w-lg shadow-2xl space-y-4 my-auto text-slate-100 text-xs">
          
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <div class="flex items-center gap-2">
              <span class="text-base">🏛️</span>
              <h3 class="font-serif text-base font-bold text-[#F5EFE0]">Input Gereja Baru ke Database</h3>
            </div>
            <button @click="isAddChurchFromRequestOpen = false" class="text-[#8AA0A4] hover:text-[#EDE6D6] cursor-pointer">✕</button>
          </div>

          <div v-if="dbInputError" class="p-3 bg-rose-950/80 border border-rose-800 text-rose-200 rounded-xl">
            ⚠️ {{ dbInputError }}
          </div>

          <div v-if="dbInputSuccess" class="p-4 bg-emerald-950/80 border border-emerald-700 text-emerald-200 rounded-xl space-y-2">
            <p class="font-bold">✅ {{ dbInputSuccess }}</p>
            <div class="pt-1 flex items-center gap-2">
              <button
                type="button"
                @click="sendConfirmationWhatsApp(selectedRequestForDb)"
                class="px-3.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold transition cursor-pointer flex items-center gap-1.5"
              >
                <span>💬 Kirim Konfirmasi ke WhatsApp Pendaftar</span>
              </button>
            </div>
          </div>

          <form v-else @submit.prevent="submitChurchToDb" class="space-y-3.5">
            
            <!-- Kode Gereja (Superadmin tentukan sendiri) -->
            <div class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30">
              <div class="flex items-center justify-between mb-1">
                <label class="font-bold text-amber-300">
                  Kode Gereja Induk (Tentukan Sendiri) <span class="text-rose-400">*</span>
                </label>
                <span class="text-[10px] text-amber-400/80">Wajib Unik</span>
              </div>
              <input 
                v-model="newChurchInput.church_code" 
                required 
                type="text" 
                placeholder="Contoh: GSJA, GKPM, GKI" 
                class="w-full bg-[#0B2027] border border-amber-500/40 focus:border-amber-300 text-amber-200 font-mono font-bold rounded-xl p-2.5 uppercase outline-none" 
              />
              <p class="text-[10px] text-slate-300 mt-1">
                Kode ini digunakan sebagai kode induk afiliasi gereja cabang di seluruh Indonesia.
              </p>
            </div>

            <!-- Nama Gereja Induk -->
            <div>
              <label class="block text-[#C6D2D0] font-semibold mb-1">Nama Gereja Induk / Sinode <span class="text-rose-400">*</span></label>
              <input v-model="newChurchInput.church_name" required type="text" class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-[#EDE6D6] rounded-xl p-2.5 outline-none" />
            </div>

            <!-- Alamat Gereja -->
            <div>
              <label class="block text-[#C6D2D0] font-semibold mb-1">Alamat Kantor Pusat / Sinode <span class="text-rose-400">*</span></label>
              <textarea v-model="newChurchInput.address" required rows="2" class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-[#EDE6D6] rounded-xl p-2.5 outline-none"></textarea>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <!-- Ketua BPP -->
              <div>
                <label class="block text-[#C6D2D0] font-semibold mb-1">Ketua Sinode / BPP</label>
                <input v-model="newChurchInput.bpp_general_chairman" type="text" placeholder="Pdt. ..." class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-[#EDE6D6] rounded-xl p-2.5 outline-none" />
              </div>

              <!-- Tanggal Berdiri -->
              <div>
                <label class="block text-[#C6D2D0] font-semibold mb-1">Tgl Berdiri (Opsional)</label>
                <input v-model="newChurchInput.established_date" type="date" class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-[#EDE6D6] rounded-xl p-2.5 outline-none" />
              </div>
            </div>

            <!-- Catatan Pendaftar Asal -->
            <div v-if="selectedRequestForDb" class="p-2.5 rounded-xl bg-[#0B2027]/60 border border-white/5 text-[11px] text-[#8AA0A4]">
              <span>Pemohon: <strong class="text-[#EDE6D6]">{{ selectedRequestForDb.applicant_name }}</strong> (WA: {{ selectedRequestForDb.applicant_phone }})</span>
            </div>

            <div class="flex justify-end gap-2.5 pt-2 border-t border-white/10">
              <button type="button" @click="isAddChurchFromRequestOpen = false" class="px-4 py-2 rounded-xl bg-white/5 text-[#C6D2D0] hover:bg-white/10 font-semibold cursor-pointer">Batal</button>
              <button 
                type="submit" 
                :disabled="isSubmittingChurchDb"
                class="px-5 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-[#0B2027] font-bold transition cursor-pointer disabled:opacity-50 flex items-center gap-1.5 shadow-lg shadow-amber-500/20"
              >
                <span>{{ isSubmittingChurchDb ? 'Menyimpan ke PostgreSQL...' : '💾 Simpan ke Database PostgreSQL' }}</span>
              </button>
            </div>
          </form>

        </div>
      </div>
    </Transition>

    <!-- ======================================================= -->
    <!-- MODAL: TAMBAH USER / ADMIN BARU                          -->
    <!-- ======================================================= -->
    <Transition name="modal">
      <div v-if="isAddUserModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B2027]/85 backdrop-blur-sm">
        <div class="bg-[#123138] border border-amber-500/25 rounded-2xl p-6 w-full max-w-md shadow-2xl space-y-4">
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 class="font-serif text-base font-bold text-[#F5EFE0]">Tambah Pengguna Baru</h3>
            <button @click="isAddUserModalOpen = false" class="text-[#8AA0A4] hover:text-[#EDE6D6] cursor-pointer">✕</button>
          </div>

          <form @submit.prevent="handleAddUser" class="space-y-4 text-xs">
            <div>
              <label class="block text-[#C6D2D0] font-semibold mb-1">Nama Lengkap</label>
              <input v-model="newUserForm.full_name" required type="text" placeholder="Masukkan nama..." class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-[#EDE6D6] rounded-xl p-2.5 outline-none" />
            </div>
            <div>
              <label class="block text-[#C6D2D0] font-semibold mb-1">Email</label>
              <input v-model="newUserForm.email" required type="email" placeholder="user@domain.com" class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-[#EDE6D6] rounded-xl p-2.5 outline-none" />
            </div>
            <div>
              <label class="block text-[#C6D2D0] font-semibold mb-1">Role / Hak Akses</label>
              <select v-model="newUserForm.role" class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-[#EDE6D6] rounded-xl p-2.5 outline-none">
                <option value="superadmin">Admin Utama (Superadmin)</option>
                <option value="church_admin">Admin Cabang Gereja</option>
                <option value="user">User / Jemaat</option>
              </select>
            </div>
            <div>
              <label class="block text-[#C6D2D0] font-semibold mb-1">Cabang Gereja</label>
              <input v-model="newUserForm.church" type="text" placeholder="Nama cabang gereja..." class="w-full bg-[#0B2027] border border-white/10 focus:border-amber-400 text-[#EDE6D6] rounded-xl p-2.5 outline-none" />
            </div>
            <div class="flex justify-end gap-2 pt-2">
              <button type="button" @click="isAddUserModalOpen = false" class="px-4 py-2 rounded-xl bg-white/5 text-[#C6D2D0] hover:bg-white/10 font-semibold cursor-pointer">Batal</button>
              <button type="submit" class="px-4 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-[#0B2027] font-bold cursor-pointer">Simpan User</button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ======================================================= -->
    <!-- MODAL POPUP: INBOX NOTIFIKASI PERMOHONAN GEREJA BARU    -->
    <!-- ======================================================= -->
    <Transition name="modal">
      <div v-if="isInboxModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B2027]/85 backdrop-blur-md overflow-y-auto">
        <div class="bg-[#123138] border border-amber-500/35 rounded-2xl p-6 w-full max-w-3xl shadow-2xl space-y-4 my-auto text-slate-100 text-xs">
          
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <div class="flex items-center gap-2">
              <span class="text-lg">📥</span>
              <div>
                <h3 class="font-serif text-base font-bold text-[#F5EFE0]">Kotak Masuk Permohonan Gereja</h3>
                <p class="text-[11px] text-[#8AA0A4]">Daftar tiket permohonan gereja baru dari calon admin jemaat.</p>
              </div>
            </div>
            <button @click="isInboxModalOpen = false" class="text-[#8AA0A4] hover:text-[#EDE6D6] cursor-pointer text-sm">✕</button>
          </div>

          <!-- Filter Tab in Modal -->
          <div class="flex items-center gap-2 border-b border-white/5 pb-2.5">
            <button
              @click="selectedRequestTab = 'all'"
              :class="['px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer', selectedRequestTab === 'all' ? 'bg-amber-400 text-[#0B2027]' : 'bg-[#0B2027]/60 text-[#8AA0A4]']"
            >
              Semua ({{ churchRequests.length }})
            </button>
            <button
              @click="selectedRequestTab = 'pending'"
              :class="['px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer', selectedRequestTab === 'pending' ? 'bg-rose-500 text-white' : 'bg-[#0B2027]/60 text-[#8AA0A4]']"
            >
              Menunggu ({{ pendingRequestsCount }})
            </button>
            <button
              @click="selectedRequestTab = 'completed'"
              :class="['px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer', selectedRequestTab === 'completed' ? 'bg-teal-500 text-white' : 'bg-[#0B2027]/60 text-[#8AA0A4]']"
            >
              Selesai ({{ completedRequestsCount }})
            </button>
          </div>

          <!-- Request Items List -->
          <div class="max-h-[60vh] overflow-y-auto space-y-3 pr-1">
            <div v-if="filteredChurchRequests.length === 0" class="py-12 text-center text-[#8AA0A4]">
              <p class="text-2xl mb-1">📭</p>
              <p>Tidak ada permohonan dalam kategori ini.</p>
            </div>

            <div
              v-for="req in filteredChurchRequests"
              :key="req.id"
              class="p-4 rounded-xl bg-[#0B2027]/80 border transition duration-200"
              :class="req.status === 'Menunggu' ? 'border-amber-500/30' : 'border-white/5'"
            >
              <div class="flex items-center justify-between gap-2 mb-2">
                <div class="flex items-center gap-2">
                  <span class="font-mono font-bold text-amber-300 text-xs">{{ req.id }}</span>
                  <span v-if="req.channel === 'direct'" class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-500/15 border border-amber-500/30 text-amber-300">
                    🏛️ Direct Sistem
                  </span>
                  <span v-else-if="req.channel === 'wa'" class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
                    💬 WhatsApp
                  </span>
                  <span v-else class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-cyan-500/15 border border-cyan-500/30 text-cyan-300">
                    ✉️ Email
                  </span>
                </div>
                <span
                  :class="[
                    'px-2.5 py-0.5 rounded-full text-[10px] font-bold border',
                    req.status === 'Menunggu' ? 'bg-rose-500/15 border-rose-500/40 text-rose-300' : 'bg-teal-500/15 border-teal-500/40 text-teal-300'
                  ]"
                >
                  {{ req.status }}
                </span>
              </div>

              <h4 class="font-bold text-sm text-[#F5EFE0]">{{ req.proposed_main_church }}</h4>
              <p v-if="req.proposed_branch_church && req.proposed_branch_church !== '-'" class="text-amber-300 text-[11px] font-medium mt-0.5">
                Cabang: {{ req.proposed_branch_church }}
              </p>
              <p class="text-[11px] text-[#8AA0A4] mt-1">
                Alamat: {{ req.address }} | Wilayah: {{ req.city }} | Pimpinan: {{ req.leader_name }}
              </p>
              <div class="p-2 rounded-lg bg-[#123138] border border-white/5 text-[11px] text-amber-100/80 my-2 italic">
                "{{ req.complaint_notes }}"
              </div>
              <div class="flex items-center justify-between text-[11px] text-[#8AA0A4] pt-1">
                <span>Pemohon: <strong class="text-[#EDE6D6]">{{ req.applicant_name }}</strong> (WA: {{ req.applicant_phone }})</span>
                <span class="font-mono text-[10px]">{{ req.created_at }}</span>
              </div>

              <div class="mt-3 pt-2.5 border-t border-white/5 flex items-center justify-end gap-2">
                <button
                  type="button"
                  @click="sendConfirmationWhatsApp(req)"
                  class="px-2.5 py-1.5 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/40 text-emerald-300 text-xs font-semibold transition cursor-pointer"
                >
                  💬 Hubungi WA
                </button>
                <button
                  v-if="req.status === 'Menunggu'"
                  type="button"
                  @click="isInboxModalOpen = false; openAddChurchModal(req)"
                  class="px-3 py-1.5 rounded-lg bg-amber-400 hover:bg-amber-300 text-[#0B2027] text-xs font-bold transition cursor-pointer"
                >
                  ⚡ Input ke DBMS
                </button>
                <button
                  type="button"
                  @click="deleteChurchRequest(req)"
                  class="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs font-semibold transition cursor-pointer"
                >
                  Hapus
                </button>
              </div>
            </div>
          </div>

          <div class="flex justify-end pt-3 border-t border-white/10">
            <button @click="isInboxModalOpen = false" class="px-4 py-2 rounded-xl bg-white/5 text-[#C6D2D0] hover:bg-white/10 font-semibold cursor-pointer">
              Tutup
            </button>
          </div>

        </div>
      </div>
    </Transition>

  </MainAdminLayout>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }
</style>