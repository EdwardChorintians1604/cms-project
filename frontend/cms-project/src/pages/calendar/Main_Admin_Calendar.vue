<script setup>
import { computed, ref, reactive, onMounted } from 'vue'
import {
  format,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  addDays,
  subDays,
  isSameMonth,
  isToday,
  getDate,
  getDay
} from 'date-fns'
import { id as localeId } from 'date-fns/locale/id'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'

// --- State Data Utama ---
const agendas = ref([])
const churches = ref([])
const jemaatMembers = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

// Filter & Mode Tampilan
const activeView = ref('calendar') // 'calendar' | 'list'
const searchQuery = ref('')
const categoryFilter = ref('Semua')
const churchFilter = ref('Semua')
const statusFilter = ref('Semua')
const showHolyDays = ref(true)
const showBirthdays = ref(true)

// Kalender Navigation State
const currentDate = ref(new Date())
const selectedYear = ref(currentDate.value.getFullYear())
const selectedMonth = ref(currentDate.value.getMonth()) // 0 - 11
const selectedDateKey = ref(format(currentDate.value, 'yyyy-MM-dd'))

// Modal Form Tambah / Edit
const isFormModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const isSubmitting = ref(false)

// Modal Detail
const isDetailModalOpen = ref(false)
const selectedAgenda = ref(null)

// Modal Konfirmasi Hapus
const isDeleteModalOpen = ref(false)
const agendaToDelete = ref(null)

// Toast Feedback
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

const triggerToast = (msg, type = 'success') => {
  toastMessage.value = msg
  toastType.value = type
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 4000)
}

// Form Reactive
const form = reactive({
  title: '',
  description: '',
  category: 'Ibadah Raya',
  start_date: format(new Date(), 'yyyy-MM-dd'),
  end_date: '',
  start_time: '09:00 WIB',
  end_time: '11:30 WIB',
  location: '',
  church_id: null,
  church_name: 'Semua Cabang',
  organizer: '',
  target_audience: 'Semua Jemaat',
  status: 'Akan Datang',
  color: 'amber'
})

// Daftar Kategori Acara
const categoriesList = [
  { name: 'Ibadah Raya', color: 'amber', icon: 'bi-bell-fill' },
  { name: 'Doa & Puasa', color: 'purple', icon: 'bi-moon-stars-fill' },
  { name: 'Persekutuan Doa', color: 'indigo', icon: 'bi-heart-pulse-fill' },
  { name: 'Kebaktian Pemuda / Remaja', color: 'sky', icon: 'bi-lightning-charge-fill' },
  { name: 'Sekolah Minggu', color: 'emerald', icon: 'bi-palette-fill' },
  { name: 'Retret & KKR', color: 'rose', icon: 'bi-fire' },
  { name: 'Rapat Majelis / Pengurus', color: 'slate', icon: 'bi-people-fill' },
  { name: 'Bakti Sosial & Pelayanan', color: 'teal', icon: 'bi-hand-thumbs-up-fill' },
  { name: 'Seminar & Pelatihan', color: 'cyan', icon: 'bi-mortarboard-fill' },
  { name: 'Kegiatan Umum', color: 'amber', icon: 'bi-calendar-event' }
]

// Pilihan Warna Aksen
const colorOptions = [
  { label: 'Emas / Amber', value: 'amber', bgClass: 'bg-amber-500' },
  { label: 'Ungu Liturgi', value: 'purple', bgClass: 'bg-purple-600' },
  { label: 'Biru Langit', value: 'sky', bgClass: 'bg-sky-500' },
  { label: 'Hijau Emerald', value: 'emerald', bgClass: 'bg-emerald-500' },
  { label: 'Merah Rose', value: 'rose', bgClass: 'bg-rose-500' },
  { label: 'Indigo Royal', value: 'indigo', bgClass: 'bg-indigo-600' }
]

// --- Load Data dari Backend PostgreSQL / SQLite ---
const loadAgendas = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/agenda/?limit=300`)
    if (!res.ok) throw new Error('Gagal memuat daftar agenda kegiatan.')
    agendas.value = await res.json()
  } catch (err) {
    console.error('Error load agendas:', err)
    errorMessage.value = err.message || 'Gagal terhubung ke database agenda.'
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
    console.warn('Gagal memuat data cabang gereja:', err)
  }
}

const loadJemaat = async () => {
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/users/?limit=300`)
    if (res.ok) {
      jemaatMembers.value = await res.json()
    }
  } catch (err) {
    console.warn('Gagal memuat biodata jemaat:', err)
  }
}

onMounted(() => {
  loadAgendas()
  loadChurches()
  loadJemaat()
})

// --- Algoritma Astronomis Computus Hari Raya Liturgi Kristen ---
function getEasterDate(year) {
  const a = year % 19
  const b = Math.floor(year / 100)
  const c = year % 100
  const d = Math.floor(b / 4)
  const e = b % 4
  const f = Math.floor((b + 8) / 25)
  const g = Math.floor((b - f + 1) / 3)
  const h = (19 * a + b - d - g + 15) % 30
  const i = Math.floor(c / 4)
  const k = c % 4
  const l = (32 + 2 * e + 2 * i - h - k) % 7
  const m = Math.floor((a + 11 * h + 22 * l) / 451)
  const month = Math.floor((h + l - 7 * m + 114) / 31)
  const day = ((h + l - 7 * m + 114) % 31) + 1
  return new Date(year, month - 1, day)
}

const holyDaysList = computed(() => {
  const year = selectedYear.value
  const easter = getEasterDate(year)
  const rabuAbu = subDays(easter, 46)
  const jumatAgung = subDays(easter, 2)
  const paskah = easter
  const kenaikan = addDays(easter, 39)
  const pentakosta = addDays(easter, 49)

  const list = [
    { date: `${year}-01-01`, title: 'Tahun Baru Masehi', category: 'Liturgi', type: 'liturgi', icon: 'bi-stars' },
    { date: `${year}-01-06`, title: 'Hari Raya Epifani', category: 'Liturgi', type: 'liturgi', icon: 'bi-brightness-high-fill' },
    { date: format(rabuAbu, 'yyyy-MM-dd'), title: 'Rabu Abu (Pra-Paskah)', category: 'Liturgi', type: 'liturgi', icon: 'bi-moon-stars' },
    { date: format(jumatAgung, 'yyyy-MM-dd'), title: 'Jumat Agung (Wafat Kristus)', category: 'Liturgi', type: 'liturgi', icon: 'bi-plus-lg' },
    { date: format(paskah, 'yyyy-MM-dd'), title: 'Hari Raya Paskah (Kebangkitan)', category: 'Liturgi', type: 'liturgi', icon: 'bi-sun-fill' },
    { date: format(kenaikan, 'yyyy-MM-dd'), title: 'Kenaikan Yesus Kristus', category: 'Liturgi', type: 'liturgi', icon: 'bi-cloud-upload' },
    { date: format(pentakosta, 'yyyy-MM-dd'), title: 'Hari Pentakosta (Roh Kudus)', category: 'Liturgi', type: 'liturgi', icon: 'bi-fire' },
    { date: `${year}-12-24`, title: 'Malam Kudus Natal', category: 'Liturgi', type: 'liturgi', icon: 'bi-moon-stars-fill' },
    { date: `${year}-12-25`, title: 'Hari Raya Natal', category: 'Liturgi', type: 'liturgi', icon: 'bi-gift-fill' },
    { date: `${year}-12-31`, title: 'Malam Tutup Tahun', category: 'Liturgi', type: 'liturgi', icon: 'bi-hourglass-bottom' }
  ]
  return list
})

const holyDaysMap = computed(() => {
  const map = {}
  holyDaysList.value.forEach((h) => {
    map[h.date] = h
  })
  return map
})

// Peta Ulang Tahun Jemaat untuk Tahun Terpilih
const birthdaysMap = computed(() => {
  const map = {}
  const curYear = selectedYear.value
  jemaatMembers.value.forEach((u) => {
    if (!u.birth_date) return
    const parts = u.birth_date.split('-')
    if (parts.length < 3) return
    const bMonth = parts[1]
    const bDay = parts[2]
    const key = `${curYear}-${bMonth}-${bDay}`
    if (!map[key]) map[key] = []
    map[key].push({
      id: u.id,
      name: u.full_name,
      church: u.church_domisili || 'Cabang Mandiri',
      age: curYear - parseInt(parts[0], 10),
      type: 'birthday'
    })
  })
  return map
})

// Filtered Agendas
const filteredAgendas = computed(() => {
  return agendas.value.filter((item) => {
    const q = searchQuery.value.toLowerCase().trim()
    const matchesSearch =
      !q ||
      (item.title && item.title.toLowerCase().includes(q)) ||
      (item.description && item.description.toLowerCase().includes(q)) ||
      (item.location && item.location.toLowerCase().includes(q)) ||
      (item.organizer && item.organizer.toLowerCase().includes(q)) ||
      (item.church_name && item.church_name.toLowerCase().includes(q))

    const matchesCategory = categoryFilter.value === 'Semua' || item.category === categoryFilter.value
    const matchesChurch = churchFilter.value === 'Semua' || item.church_name === churchFilter.value
    const matchesStatus = statusFilter.value === 'Semua' || item.status === statusFilter.value

    return matchesSearch && matchesCategory && matchesChurch && matchesStatus
  })
})

// Peta Agenda per Tanggal (YYYY-MM-DD)
const agendasMap = computed(() => {
  const map = {}
  filteredAgendas.value.forEach((item) => {
    const key = item.start_date
    if (!map[key]) map[key] = []
    map[key].push(item)
  })
  return map
})

// --- Matriks Kalender 42 Cell (Presisi dengan date-fns) ---
const calendarDays = computed(() => {
  const monthDate = new Date(selectedYear.value, selectedMonth.value, 1)
  const monthStart = startOfMonth(monthDate)
  const monthEnd = endOfMonth(monthDate)
  const gridStart = startOfWeek(monthStart, { weekStartsOn: 0 })
  const gridEnd = endOfWeek(monthEnd, { weekStartsOn: 0 })

  const intervalDays = eachDayOfInterval({ start: gridStart, end: gridEnd })
  const days = [...intervalDays]
  while (days.length < 42) {
    days.push(addDays(days[days.length - 1], 1))
  }

  return days.map((d) => {
    const dateKey = format(d, 'yyyy-MM-dd')
    return {
      dateObj: d,
      dateKey,
      dayNumber: getDate(d),
      isCurrentMonth: isSameMonth(d, monthStart),
      isToday: isToday(d),
      isSunday: getDay(d) === 0,
      isSelected: selectedDateKey.value === dateKey,
      agendas: agendasMap.value[dateKey] || [],
      holyDay: showHolyDays.value ? (holyDaysMap.value[dateKey] || null) : null,
      birthdays: showBirthdays.value ? (birthdaysMap.value[dateKey] || []) : []
    }
  })
})

// Agenda & Item pada Tanggal Terpilih
const currentSelectedEvents = computed(() => {
  const key = selectedDateKey.value
  const listAgendas = agendasMap.value[key] || []
  const holy = showHolyDays.value ? (holyDaysMap.value[key] || null) : null
  const bdays = showBirthdays.value ? (birthdaysMap.value[key] || []) : []
  return {
    key,
    agendas: listAgendas,
    holyDay: holy,
    birthdays: bdays,
    total: listAgendas.length + (holy ? 1 : 0) + bdays.length
  }
})

// Ringkasan Statistik
const stats = computed(() => {
  const total = agendas.value.length
  const currentMonthStr = `${selectedYear.value}-${String(selectedMonth.value + 1).padStart(2, '0')}`
  const thisMonth = agendas.value.filter((a) => a.start_date && a.start_date.startsWith(currentMonthStr)).length
  const upcoming = agendas.value.filter((a) => a.status === 'Akan Datang' || a.status === 'Sedang Berlangsung').length
  const completed = agendas.value.filter((a) => a.status === 'Selesai').length

  return { total, thisMonth, upcoming, completed }
})

// Navigasi Bulan & Tahun
const monthNames = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]

const currentMonthLabel = computed(() => `${monthNames[selectedMonth.value]} ${selectedYear.value}`)

const prevMonth = () => {
  if (selectedMonth.value === 0) {
    selectedMonth.value = 11
    selectedYear.value--
  } else {
    selectedMonth.value--
  }
}

const nextMonth = () => {
  if (selectedMonth.value === 11) {
    selectedMonth.value = 0
    selectedYear.value++
  } else {
    selectedMonth.value++
  }
}

const resetToToday = () => {
  const now = new Date()
  selectedYear.value = now.getFullYear()
  selectedMonth.value = now.getMonth()
  selectedDateKey.value = format(now, 'yyyy-MM-dd')
}

const handleSelectDate = (cell) => {
  selectedDateKey.value = cell.dateKey
}

// Handler Dropdown Cabang di Form
const onChurchSelect = (event) => {
  const val = event.target.value
  if (val === 'Semua Cabang') {
    form.church_id = null
    form.church_name = 'Semua Cabang'
  } else {
    const found = churches.value.find((c) => c.church_name === val)
    if (found) {
      form.church_id = found.id
      form.church_name = found.church_name
    } else {
      form.church_name = val
    }
  }
}

// Modal Aksi
const openAddModal = (customDate = null) => {
  isEditing.value = false
  editingId.value = null
  Object.assign(form, {
    title: '',
    description: '',
    category: 'Ibadah Raya',
    start_date: customDate || selectedDateKey.value || format(new Date(), 'yyyy-MM-dd'),
    end_date: '',
    start_time: '09:00 WIB',
    end_time: '11:30 WIB',
    location: '',
    church_id: null,
    church_name: 'Semua Cabang',
    organizer: '',
    target_audience: 'Semua Jemaat',
    status: 'Akan Datang',
    color: 'amber'
  })
  isFormModalOpen.value = true
}

const openEditModal = (item) => {
  isEditing.value = true
  editingId.value = item.id
  Object.assign(form, {
    title: item.title,
    description: item.description || '',
    category: item.category || 'Ibadah Raya',
    start_date: item.start_date,
    end_date: item.end_date || '',
    start_time: item.start_time || '',
    end_time: item.end_time || '',
    location: item.location || '',
    church_id: item.church_id || null,
    church_name: item.church_name || 'Semua Cabang',
    organizer: item.organizer || '',
    target_audience: item.target_audience || 'Semua Jemaat',
    status: item.status || 'Akan Datang',
    color: item.color || 'amber'
  })
  isDetailModalOpen.value = false
  isFormModalOpen.value = true
}

const openDetailModal = (item) => {
  selectedAgenda.value = item
  isDetailModalOpen.value = true
}

const openDeleteConfirm = (item) => {
  agendaToDelete.value = item
  isDeleteModalOpen.value = true
  isDetailModalOpen.value = false
}

// Submit Create or Update
const handleSubmitForm = async () => {
  if (!form.title.trim()) {
    triggerToast('Nama kegiatan wajib diisi.', 'error')
    return
  }
  if (!form.start_date) {
    triggerToast('Tanggal mulai wajib diisi.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      title: form.title.trim(),
      description: form.description ? form.description.trim() : null,
      category: form.category,
      start_date: form.start_date,
      end_date: form.end_date || null,
      start_time: form.start_time ? form.start_time.trim() : null,
      end_time: form.end_time ? form.end_time.trim() : null,
      location: form.location ? form.location.trim() : null,
      church_id: form.church_id || null,
      church_name: form.church_name || 'Semua Cabang',
      organizer: form.organizer ? form.organizer.trim() : null,
      target_audience: form.target_audience || 'Semua Jemaat',
      status: form.status,
      color: form.color
    }

    let res
    if (isEditing.value && editingId.value) {
      res = await fetch(`${APP_CONFIG.apiBaseUrl}/agenda/${editingId.value}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) throw new Error('Gagal memperbarui agenda kegiatan.')
      triggerToast('Agenda kegiatan berhasil diperbarui.')
    } else {
      res = await fetch(`${APP_CONFIG.apiBaseUrl}/agenda/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) throw new Error('Gagal menambahkan agenda kegiatan baru.')
      triggerToast('Agenda kegiatan baru berhasil disimpan.')
    }

    isFormModalOpen.value = false
    await loadAgendas()
  } catch (err) {
    console.error('Submit form error:', err)
    triggerToast(err.message || 'Terjadi kesalahan sistem saat menyimpan agenda.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Delete Action
const handleConfirmDelete = async () => {
  if (!agendaToDelete.value) return
  isSubmitting.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/agenda/${agendaToDelete.value.id}`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('Gagal menghapus agenda kegiatan.')
    triggerToast(`Agenda "${agendaToDelete.value.title}" berhasil dihapus.`)
    isDeleteModalOpen.value = false
    agendaToDelete.value = null
    await loadAgendas()
  } catch (err) {
    console.error('Delete error:', err)
    triggerToast(err.message || 'Gagal menghapus agenda.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Badge Helpers
const getCategoryBadgeClass = (category) => {
  switch (category) {
    case 'Ibadah Raya':
      return 'bg-amber-500/15 text-amber-300 border-amber-500/30'
    case 'Doa & Puasa':
      return 'bg-purple-500/15 text-purple-300 border-purple-500/30'
    case 'Persekutuan Doa':
      return 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30'
    case 'Kebaktian Pemuda / Remaja':
      return 'bg-sky-500/15 text-sky-300 border-sky-500/30'
    case 'Sekolah Minggu':
      return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
    case 'Retret & KKR':
      return 'bg-rose-500/15 text-rose-300 border-rose-500/30'
    case 'Rapat Majelis / Pengurus':
      return 'bg-slate-500/20 text-slate-300 border-slate-500/40'
    case 'Bakti Sosial & Pelayanan':
      return 'bg-teal-500/15 text-teal-300 border-teal-500/30'
    case 'Seminar & Pelatihan':
      return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
    default:
      return 'bg-amber-500/10 text-amber-200 border-amber-500/20'
  }
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'Akan Datang':
      return 'bg-sky-500/15 text-sky-300 border-sky-500/30'
    case 'Sedang Berlangsung':
      return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 animate-pulse'
    case 'Selesai':
      return 'bg-slate-800 text-slate-400 border-slate-700'
    case 'Dibatalkan':
      return 'bg-rose-500/15 text-rose-300 border-rose-500/30 line-through'
    default:
      return 'bg-slate-800 text-slate-300 border-slate-700'
  }
}

const formatDateId = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const parts = dateStr.split('-')
    if (parts.length === 3) {
      const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
      return format(d, 'EEEE, d MMMM yyyy', { locale: localeId })
    }
    return dateStr
  } catch (e) {
    return dateStr
  }
}
</script>

<template>
  <MainAdminLayout>
    <div class="space-y-6 text-[#EDE6D6] font-sans pb-12">

      <!-- TOP TOAST NOTIFICATION -->
      <Transition name="toast">
        <div 
          v-if="showToast"
          :class="[
            'fixed top-5 right-5 z-[100] max-w-md px-4 py-3 rounded-2xl shadow-2xl border flex items-center gap-3 backdrop-blur-xl transition-all duration-300',
            toastType === 'success' ? 'bg-emerald-950/90 text-emerald-200 border-emerald-500/50 shadow-emerald-950/40' : 'bg-rose-950/90 text-rose-200 border-rose-500/50 shadow-rose-950/40'
          ]"
        >
          <i :class="['bi text-lg', toastType === 'success' ? 'bi-check-circle-fill text-emerald-400' : 'bi-exclamation-octagon-fill text-rose-400']"></i>
          <p class="text-xs font-semibold leading-relaxed">{{ toastMessage }}</p>
          <button @click="showToast = false" class="ml-auto text-slate-400 hover:text-white">
            <i class="bi bi-x-lg text-xs"></i>
          </button>
        </div>
      </Transition>

      <!-- HERO BANNER HEADER -->
      <section class="rounded-3xl border border-amber-500/25 bg-gradient-to-r from-[#0d1e27]/90 via-[#0b2027]/85 to-[#09151e]/90 p-6 shadow-2xl backdrop-blur-xl sm:p-8 relative overflow-hidden">
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute top-0 right-1/4 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-2">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-extrabold uppercase tracking-widest">
              <i class="bi bi-calendar-range-fill"></i>
              <span>Sistem Manajemen Agenda & Kegiatan Terpadu</span>
            </div>
            
            <div class="flex items-center gap-2">
              <button 
                type="button" 
                @click="loadAgendas" 
                class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-900/80 hover:bg-slate-800 text-xs text-slate-300 hover:text-amber-300 transition cursor-pointer"
                title="Muat Ulang Data dari Database"
              >
                <i :class="['bi bi-arrow-clockwise', isLoading ? 'animate-spin text-amber-400' : '']"></i>
                <span class="hidden sm:inline">Refresh Data</span>
              </button>

              <button 
                type="button" 
                @click="openAddModal()" 
                class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 text-xs font-bold shadow-lg shadow-amber-500/20 transition duration-200 cursor-pointer"
              >
                <i class="bi bi-plus-circle-fill text-sm"></i>
                <span>Tambah Agenda Baru</span>
              </button>
            </div>
          </div>

          <div class="mt-3 flex flex-col lg:flex-row lg:items-end justify-between gap-4">
            <div>
              <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-100">
                Kalender & Penjadwalan Kegiatan Gereja
              </h1>
              <p class="mt-1.5 text-xs sm:text-sm text-[#B8C4C2] max-w-2xl leading-relaxed">
                Kelola seluruh agenda peribadahan, rapat majelis, program kategorial pemuda & anak, seminar, retret, hingga pelayanan sosial dari satu pusat kendali terpadu.
              </p>
            </div>

            <!-- View Switcher (Calendar vs List) -->
            <div class="flex items-center gap-1 bg-slate-950/80 border border-slate-800 p-1 rounded-2xl shrink-0">
              <button 
                type="button"
                @click="activeView = 'calendar'"
                :class="[
                  'px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer',
                  activeView === 'calendar' ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/25' : 'text-slate-400 hover:text-white'
                ]"
              >
                <i class="bi bi-calendar3"></i>
                <span>Kalender</span>
              </button>
              <button 
                type="button"
                @click="activeView = 'list'"
                :class="[
                  'px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer',
                  activeView === 'list' ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/25' : 'text-slate-400 hover:text-white'
                ]"
              >
                <i class="bi bi-list-task"></i>
                <span>Daftar Agenda ({{ filteredAgendas.length }})</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- SUMMARY KPI METRICS -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Agenda</span>
            <div class="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 text-sm">
              <i class="bi bi-journal-text"></i>
            </div>
          </div>
          <p class="mt-2 text-2xl font-black text-amber-300 font-mono">{{ stats.total }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Terdaftar di seluruh cabang</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Bulan Ini</span>
            <div class="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 text-sm">
              <i class="bi bi-calendar-check"></i>
            </div>
          </div>
          <p class="mt-2 text-2xl font-black text-sky-300 font-mono">{{ stats.thisMonth }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Jadwal pada {{ monthNames[selectedMonth] }}</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Akan Datang</span>
            <div class="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-sm">
              <i class="bi bi-hourglass-split"></i>
            </div>
          </div>
          <p class="mt-2 text-2xl font-black text-emerald-300 font-mono">{{ stats.upcoming }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Agenda aktif & persiapan</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md relative overflow-hidden">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Terlaksana</span>
            <div class="w-8 h-8 rounded-lg bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 text-sm">
              <i class="bi bi-check-all"></i>
            </div>
          </div>
          <p class="mt-2 text-2xl font-black text-purple-300 font-mono">{{ stats.completed }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Kegiatan sukses selesai</p>
        </div>
      </section>

      <!-- FILTER & CONTROL TOOLBAR -->
      <section class="rounded-2xl border border-white/10 bg-[#123138]/70 p-4 backdrop-blur-md space-y-3">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          
          <!-- Search Bar -->
          <div class="relative">
            <i class="bi bi-search absolute left-3 top-2.5 text-slate-500 text-xs"></i>
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Cari kegiatan, lokasi, PIC..." 
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 outline-none focus:border-amber-400 transition"
            />
          </div>

          <!-- Kategori Filter -->
          <div>
            <select 
              v-model="categoryFilter"
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-amber-400 transition cursor-pointer"
            >
              <option value="Semua">Semua Kategori</option>
              <option v-for="cat in categoriesList" :key="cat.name" :value="cat.name">{{ cat.name }}</option>
            </select>
          </div>

          <!-- Cabang Gereja Filter -->
          <div>
            <select 
              v-model="churchFilter"
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-amber-400 transition cursor-pointer"
            >
              <option value="Semua">Semua Cabang Gereja</option>
              <option value="Semua Cabang">Semua Cabang (Pusat)</option>
              <option v-for="c in churches" :key="c.id" :value="c.church_name">{{ c.church_name }}</option>
            </select>
          </div>

          <!-- Status Filter -->
          <div>
            <select 
              v-model="statusFilter"
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-amber-400 transition cursor-pointer"
            >
              <option value="Semua">Semua Status</option>
              <option value="Akan Datang">Akan Datang</option>
              <option value="Sedang Berlangsung">Sedang Berlangsung</option>
              <option value="Selesai">Selesai</option>
              <option value="Dibatalkan">Dibatalkan</option>
            </select>
          </div>

        </div>

        <!-- Secondary Filter Controls: Calendar Sync Toggles -->
        <div class="pt-2 border-t border-white/5 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-4">
            <span class="text-slate-400 text-[11px] font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <i class="bi bi-layers-fill text-amber-400"></i> Lapisan Kalender:
            </span>

            <label class="inline-flex items-center gap-2 cursor-pointer select-none">
              <input 
                v-model="showHolyDays" 
                type="checkbox" 
                class="rounded border-slate-700 text-amber-500 focus:ring-0 bg-slate-950" 
              />
              <span class="text-slate-300 hover:text-amber-300 transition">Hari Raya Liturgi (Paskah/Natal)</span>
            </label>

            <label class="inline-flex items-center gap-2 cursor-pointer select-none">
              <input 
                v-model="showBirthdays" 
                type="checkbox" 
                class="rounded border-slate-700 text-pink-500 focus:ring-0 bg-slate-950" 
              />
              <span class="text-slate-300 hover:text-pink-300 transition">Hari Ulang Tahun Jemaat</span>
            </label>
          </div>

          <div class="text-[11px] text-slate-400">
            Menampilkan <strong class="text-amber-300">{{ filteredAgendas.length }}</strong> agenda kegiatan
          </div>
        </div>
      </section>

      <!-- VIEW 1: MONTH CALENDAR GRID VIEW -->
      <div v-if="activeView === 'calendar'" class="grid gap-6 lg:grid-cols-[1fr_24rem] items-start">
        
        <!-- Main Calendar Section -->
        <div class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-2xl backdrop-blur-xl">
          
          <!-- Month & Year Navigation Header -->
          <div class="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-white/10">
            <div class="flex items-center gap-3">
              <h2 class="font-serif text-xl sm:text-2xl font-bold text-[#F5EFE0] tracking-wide flex items-center gap-2">
                <i class="bi bi-calendar4-week text-amber-400"></i>
                <span>{{ currentMonthLabel }}</span>
              </h2>
              <button 
                type="button" 
                @click="resetToToday" 
                class="px-2.5 py-1 text-[11px] font-bold rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 hover:bg-amber-500/30 transition cursor-pointer"
                title="Kembali ke Tanggal Hari Ini"
              >
                Hari Ini
              </button>
            </div>

            <div class="flex items-center gap-1.5 bg-slate-950/80 border border-slate-800 p-1 rounded-xl">
              <button 
                type="button" 
                @click="prevMonth"
                class="p-1.5 px-2.5 rounded-lg text-slate-300 hover:bg-white/10 hover:text-amber-300 transition cursor-pointer"
                title="Bulan Sebelumnya"
              >
                <i class="bi bi-chevron-left"></i>
              </button>
              
              <span class="min-w-28 text-center text-xs font-semibold text-slate-300">
                {{ monthNames[selectedMonth] }}
              </span>

              <button 
                type="button" 
                @click="nextMonth"
                class="p-1.5 px-2.5 rounded-lg text-slate-300 hover:bg-white/10 hover:text-amber-300 transition cursor-pointer"
                title="Bulan Berikutnya"
              >
                <i class="bi bi-chevron-right"></i>
              </button>
            </div>
          </div>

          <!-- Day of Week Headers -->
          <div class="grid grid-cols-7 gap-1 sm:gap-2 mt-4 text-center">
            <div class="py-2 text-[11px] font-extrabold text-rose-400 uppercase tracking-wider">Min</div>
            <div class="py-2 text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">Sen</div>
            <div class="py-2 text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">Sel</div>
            <div class="py-2 text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">Rab</div>
            <div class="py-2 text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">Kam</div>
            <div class="py-2 text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">Jum</div>
            <div class="py-2 text-[11px] font-extrabold text-amber-400 uppercase tracking-wider">Sab</div>
          </div>

          <!-- 42 Calendar Cells Grid -->
          <div class="grid grid-cols-7 gap-1 sm:gap-2 mt-2">
            <div 
              v-for="(cell, idx) in calendarDays" 
              :key="idx"
              @click="handleSelectDate(cell)"
              :class="[
                'min-h-[82px] sm:min-h-[102px] p-1.5 sm:p-2 rounded-xl border transition-all duration-200 flex flex-col justify-between cursor-pointer relative group',
                cell.isSelected 
                  ? 'border-amber-400 bg-gradient-to-b from-amber-500/20 to-slate-900 shadow-lg shadow-amber-500/10 ring-1 ring-amber-400/50' 
                  : cell.isToday 
                    ? 'border-amber-500/50 bg-slate-900/90 shadow-md' 
                    : cell.isCurrentMonth 
                      ? 'border-white/5 bg-slate-950/60 hover:border-amber-500/40 hover:bg-slate-900/80' 
                      : 'border-transparent bg-slate-950/25 opacity-40 hover:opacity-75'
              ]"
            >
              <!-- Cell Header (Day Number & Status) -->
              <div class="flex items-center justify-between">
                <span 
                  :class="[
                    'text-xs font-bold font-mono h-6 w-6 rounded-full flex items-center justify-center',
                    cell.isToday ? 'bg-amber-400 text-slate-950 font-black shadow' : cell.isSunday ? 'text-rose-400' : 'text-slate-300'
                  ]"
                >
                  {{ cell.dayNumber }}
                </span>

                <!-- Indicators Summary Counter if overcrowded -->
                <div class="flex items-center gap-1">
                  <span 
                    v-if="cell.agendas.length" 
                    class="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse"
                    title="Ada agenda kegiatan gereja"
                  ></span>
                  <span 
                    v-if="cell.holyDay" 
                    class="h-1.5 w-1.5 rounded-full bg-purple-400"
                    title="Ada Hari Raya Liturgi"
                  ></span>
                  <span 
                    v-if="cell.birthdays.length" 
                    class="h-1.5 w-1.5 rounded-full bg-pink-400"
                    title="Ada ulang tahun jemaat"
                  ></span>
                </div>
              </div>

              <!-- Cell Content Badges (max 2 preview items) -->
              <div class="space-y-1 mt-1 overflow-hidden">
                <!-- Church Agenda Badge -->
                <div 
                  v-for="ag in cell.agendas.slice(0, 2)" 
                  :key="ag.id"
                  @click.stop="openDetailModal(ag)"
                  :class="[
                    'px-1.5 py-0.5 rounded text-[9px] font-semibold truncate border transition leading-tight flex items-center gap-1 cursor-pointer hover:scale-102',
                    getCategoryBadgeClass(ag.category)
                  ]"
                  :title="`${ag.title} (${ag.start_time || ''}) - Klik untuk detail`"
                >
                  <span class="w-1 h-1 rounded-full bg-current shrink-0"></span>
                  <span class="truncate">{{ ag.title }}</span>
                </div>

                <!-- Liturgical Day Badge -->
                <div 
                  v-if="cell.holyDay && cell.agendas.length < 2"
                  class="px-1.5 py-0.5 rounded text-[9px] font-bold truncate bg-purple-950/80 text-purple-300 border border-purple-500/40 flex items-center gap-1"
                  :title="cell.holyDay.title"
                >
                  <i class="bi bi-stars text-[8px] text-amber-300"></i>
                  <span class="truncate">{{ cell.holyDay.title }}</span>
                </div>

                <!-- Birthday Badge Preview -->
                <div 
                  v-if="cell.birthdays.length && cell.agendas.length < 1 && !cell.holyDay"
                  class="px-1.5 py-0.5 rounded text-[9px] font-bold truncate bg-pink-950/80 text-pink-300 border border-pink-500/40 flex items-center gap-1"
                  :title="`${cell.birthdays.length} Jemaat Ultah`"
                >
                  <i class="bi bi-cake2-fill text-[8px]"></i>
                  <span class="truncate">Ultah: {{ cell.birthdays[0].name }}</span>
                </div>

                <!-- Overflow Indicator -->
                <div 
                  v-if="cell.agendas.length > 2" 
                  class="text-[8px] text-amber-400 font-semibold px-1"
                >
                  +{{ cell.agendas.length - 2 }} lainnya
                </div>
              </div>

              <!-- Quick Add Action on Hover -->
              <button 
                type="button"
                @click.stop="openAddModal(cell.dateKey)"
                title="Tambah agenda pada tanggal ini"
                class="hidden group-hover:flex absolute top-1 right-1 h-5 w-5 rounded-md bg-amber-400 text-slate-950 items-center justify-center text-[10px] font-black shadow cursor-pointer transition hover:bg-amber-300"
              >
                +
              </button>
            </div>
          </div>

          <!-- Color Legend Footer -->
          <div class="mt-6 pt-4 border-t border-white/10 flex flex-wrap items-center justify-between gap-3 text-[11px] text-slate-400">
            <div class="flex flex-wrap items-center gap-3">
              <span class="font-bold text-slate-300">Keterangan:</span>
              <span class="inline-flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Agenda Ibadah / Umum
              </span>
              <span class="inline-flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span> Liturgi Kristen
              </span>
              <span class="inline-flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-pink-500"></span> Ulang Tahun Jemaat
              </span>
            </div>
            <span class="text-slate-500 italic">Klik pada tanggal untuk melihat agenda lengkap & rincian.</span>
          </div>

        </div>

        <!-- Side Panel: Agenda on Selected Date -->
        <div class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-2xl backdrop-blur-xl space-y-4">
          
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <div>
              <p class="text-[10px] font-bold uppercase tracking-widest text-amber-300">Agenda Terpilih</p>
              <h3 class="font-serif text-lg font-bold text-white mt-0.5">
                {{ formatDateId(selectedDateKey) }}
              </h3>
            </div>
            <button 
              type="button" 
              @click="openAddModal(selectedDateKey)" 
              class="px-3 py-1.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 text-xs font-bold flex items-center gap-1 shadow cursor-pointer transition"
            >
              <i class="bi bi-plus-lg"></i>
              <span>Tambah</span>
            </button>
          </div>

          <!-- List of items on this date -->
          <div v-if="currentSelectedEvents.total > 0" class="space-y-3 max-h-[580px] overflow-y-auto pr-1 custom-scrollbar">
            
            <!-- Liturgical Day Card if any -->
            <div 
              v-if="currentSelectedEvents.holyDay" 
              class="p-3 rounded-2xl border border-purple-500/40 bg-purple-950/40 space-y-1"
            >
              <div class="flex items-center justify-between text-[11px]">
                <span class="font-bold text-purple-300 uppercase tracking-wide flex items-center gap-1.5">
                  <i class="bi bi-stars text-amber-300"></i> Hari Raya Liturgi Gereja
                </span>
                <span class="px-2 py-0.5 rounded-md bg-purple-900/60 text-purple-200 text-[10px] font-semibold border border-purple-700/50">
                  Kalender Gerejawi
                </span>
              </div>
              <h4 class="font-bold text-white text-sm mt-1">{{ currentSelectedEvents.holyDay.title }}</h4>
              <p class="text-[11px] text-purple-200/80 leading-relaxed">
                Hari peringatan keagamaan liturgi resmi gereja.
              </p>
            </div>

            <!-- Church Agendas on this date -->
            <div 
              v-for="item in currentSelectedEvents.agendas" 
              :key="item.id"
              class="p-3.5 rounded-2xl border border-white/10 bg-slate-950/70 hover:border-amber-500/40 hover:bg-slate-900/80 transition space-y-2 group"
            >
              <div class="flex items-start justify-between gap-2">
                <span :class="['px-2 py-0.5 rounded-md text-[10px] font-extrabold border', getCategoryBadgeClass(item.category)]">
                  {{ item.category }}
                </span>
                <span :class="['px-2 py-0.5 rounded-md text-[10px] font-bold border', getStatusBadgeClass(item.status)]">
                  {{ item.status }}
                </span>
              </div>

              <h4 class="font-bold text-white text-sm group-hover:text-amber-300 transition">
                {{ item.title }}
              </h4>

              <div class="space-y-1 text-xs text-slate-300">
                <div v-if="item.start_time" class="flex items-center gap-2">
                  <i class="bi bi-clock text-amber-400"></i>
                  <span>{{ item.start_time }} {{ item.end_time ? `- ${item.end_time}` : '' }}</span>
                </div>
                <div v-if="item.location" class="flex items-center gap-2">
                  <i class="bi bi-geo-alt text-amber-400"></i>
                  <span class="truncate">{{ item.location }}</span>
                </div>
                <div v-if="item.church_name" class="flex items-center gap-2 text-[11px] text-slate-400">
                  <i class="bi bi-buildings text-slate-500"></i>
                  <span>{{ item.church_name }}</span>
                </div>
              </div>

              <div class="pt-2 border-t border-white/10 flex items-center justify-between gap-2">
                <span class="text-[10px] text-slate-400 truncate">
                  PIC: {{ item.organizer || 'Majelis Gereja' }}
                </span>
                <div class="flex items-center gap-1">
                  <button 
                    type="button" 
                    @click="openDetailModal(item)" 
                    class="p-1.5 text-slate-300 hover:text-amber-300 hover:bg-white/10 rounded-lg text-xs"
                    title="Lihat Rincian"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button 
                    type="button" 
                    @click="openEditModal(item)" 
                    class="p-1.5 text-slate-300 hover:text-sky-300 hover:bg-white/10 rounded-lg text-xs"
                    title="Edit Agenda"
                  >
                    <i class="bi bi-pencil-square"></i>
                  </button>
                  <button 
                    type="button" 
                    @click="openDeleteConfirm(item)" 
                    class="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-white/10 rounded-lg text-xs"
                    title="Hapus Agenda"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- Jemaat Birthdays on this date -->
            <div 
              v-for="b in currentSelectedEvents.birthdays" 
              :key="b.id"
              class="p-3 rounded-2xl border border-pink-500/30 bg-pink-950/30 space-y-1"
            >
              <div class="flex items-center justify-between text-[11px]">
                <span class="font-bold text-pink-300 uppercase tracking-wide flex items-center gap-1.5">
                  <i class="bi bi-cake2-fill text-pink-400"></i> Ulang Tahun Jemaat
                </span>
                <span class="px-2 py-0.5 rounded-md bg-pink-900/60 text-pink-200 text-[10px] font-semibold border border-pink-700/50">
                  Usia {{ b.age }} Thn
                </span>
              </div>
              <h4 class="font-bold text-white text-sm">{{ b.name }}</h4>
              <p class="text-[11px] text-pink-200/80">Cabang: {{ b.church }}</p>
            </div>

          </div>

          <!-- Empty State on Selected Date -->
          <div v-else class="py-12 px-4 rounded-2xl border border-dashed border-white/10 text-center space-y-3">
            <div class="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 mx-auto flex items-center justify-center text-slate-500 text-xl">
              <i class="bi bi-calendar-x"></i>
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-300">Belum Ada Agenda</p>
              <p class="text-xs text-slate-500 mt-0.5">Tidak ada jadwal kegiatan gereja pada tanggal ini.</p>
            </div>
            <button 
              type="button" 
              @click="openAddModal(selectedDateKey)" 
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-bold border border-amber-500/30 cursor-pointer transition"
            >
              <i class="bi bi-plus-circle"></i>
              <span>Tambah Jadwal Baru</span>
            </button>
          </div>

        </div>

      </div>

      <!-- VIEW 2: FULL DATA TABLE & LIST VIEW -->
      <div v-else class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-2xl backdrop-blur-xl">
        <div class="flex items-center justify-between pb-4 border-b border-white/10">
          <div>
            <h3 class="font-serif text-xl font-bold text-white">Daftar Agenda Kegiatan Terdaftar</h3>
            <p class="text-xs text-slate-400 mt-0.5">Seluruh agenda kegiatan yang tercatat dalam database sistem.</p>
          </div>
          <button 
            type="button" 
            @click="openAddModal()" 
            class="px-4 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 text-xs font-bold flex items-center gap-1.5 shadow cursor-pointer transition"
          >
            <i class="bi bi-plus-lg"></i>
            <span>Tambah Agenda</span>
          </button>
        </div>

        <div class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400 bg-slate-950/40">
                <th class="py-3 px-4">Tanggal & Waktu</th>
                <th class="py-3 px-4">Nama Kegiatan & Kategori</th>
                <th class="py-3 px-4">Lokasi / Ruangan</th>
                <th class="py-3 px-4">Cabang Gereja</th>
                <th class="py-3 px-4">PIC / Penanggung Jawab</th>
                <th class="py-3 px-4">Status</th>
                <th class="py-3 px-4 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              <tr 
                v-for="item in filteredAgendas" 
                :key="item.id"
                class="hover:bg-slate-900/60 transition group"
              >
                <td class="py-3.5 px-4 whitespace-nowrap">
                  <span class="font-bold text-amber-300 font-mono block">{{ item.start_date }}</span>
                  <span class="text-[11px] text-slate-400">{{ item.start_time || 'Waktu Fleksibel' }}</span>
                </td>
                
                <td class="py-3.5 px-4">
                  <span class="font-bold text-white block group-hover:text-amber-300 transition">{{ item.title }}</span>
                  <span :class="['inline-block mt-1 px-2 py-0.5 rounded text-[9px] font-bold border', getCategoryBadgeClass(item.category)]">
                    {{ item.category }}
                  </span>
                </td>

                <td class="py-3.5 px-4 text-slate-300">
                  <span class="flex items-center gap-1.5">
                    <i class="bi bi-geo-alt text-amber-400"></i>
                    <span>{{ item.location || 'Tempat Ibadah Utama' }}</span>
                  </span>
                </td>

                <td class="py-3.5 px-4 text-slate-300">
                  <span>{{ item.church_name || 'Semua Cabang' }}</span>
                </td>

                <td class="py-3.5 px-4 text-slate-300">
                  <span class="block font-medium">{{ item.organizer || 'Majelis Gereja' }}</span>
                  <span class="text-[10px] text-slate-400">{{ item.target_audience || 'Semua Jemaat' }}</span>
                </td>

                <td class="py-3.5 px-4 whitespace-nowrap">
                  <span :class="['px-2.5 py-1 rounded-lg text-[10px] font-bold border', getStatusBadgeClass(item.status)]">
                    {{ item.status }}
                  </span>
                </td>

                <td class="py-3.5 px-4 text-right whitespace-nowrap">
                  <div class="inline-flex items-center gap-1">
                    <button 
                      type="button" 
                      @click="openDetailModal(item)" 
                      class="p-1.5 text-slate-300 hover:text-amber-300 hover:bg-slate-800 rounded-lg text-xs"
                      title="Lihat Rincian"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button 
                      type="button" 
                      @click="openEditModal(item)" 
                      class="p-1.5 text-slate-300 hover:text-sky-300 hover:bg-slate-800 rounded-lg text-xs"
                      title="Edit Agenda"
                    >
                      <i class="bi bi-pencil-square"></i>
                    </button>
                    <button 
                      type="button" 
                      @click="openDeleteConfirm(item)" 
                      class="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg text-xs"
                      title="Hapus Agenda"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="filteredAgendas.length === 0">
                <td colspan="7" class="py-12 text-center text-slate-400">
                  <i class="bi bi-inbox text-2xl block text-slate-600 mb-2"></i>
                  Tidak ada agenda yang cocok dengan filter atau pencarian Anda.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- MODAL FORM: TAMBAH / EDIT AGENDA KEGIATAN -->
    <Transition name="modal">
      <div 
        v-if="isFormModalOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/75 backdrop-blur-sm"
      >
        <div class="w-full max-w-2xl max-h-[90vh] overflow-y-auto custom-scrollbar rounded-3xl border border-amber-500/30 bg-[#0c1b22] p-6 shadow-2xl text-slate-100 space-y-5">
          
          <!-- Modal Header -->
          <div class="flex items-center justify-between pb-4 border-b border-white/10">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-300 text-lg">
                <i :class="isEditing ? 'bi-pencil-square' : 'bi-calendar-plus-fill'"></i>
              </div>
              <div>
                <h3 class="font-serif text-xl font-bold text-white">
                  {{ isEditing ? 'Edit Agenda Kegiatan' : 'Tambah Agenda Kegiatan Baru' }}
                </h3>
                <p class="text-xs text-slate-400">Lengkapi formulir penjadwalan kegiatan gereja di bawah ini.</p>
              </div>
            </div>
            <button 
              type="button" 
              @click="isFormModalOpen = false" 
              class="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/10"
            >
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <!-- Form Body -->
          <form @submit.prevent="handleSubmitForm" class="space-y-4">
            
            <!-- Nama Kegiatan -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-title">
                Nama / Judul Kegiatan <span class="text-rose-400">*</span>
              </label>
              <input 
                id="form-title"
                v-model="form.title"
                type="text" 
                required 
                placeholder="Contoh: Ibadah Syukur Awal Bulan & Doa Bersama" 
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 outline-none focus:border-amber-400"
              />
            </div>

            <!-- Kategori & Cabang Gereja Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-category">
                  Kategori Kegiatan <span class="text-rose-400">*</span>
                </label>
                <select 
                  id="form-category"
                  v-model="form.category"
                  required
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white outline-none focus:border-amber-400 cursor-pointer"
                >
                  <option v-for="cat in categoriesList" :key="cat.name" :value="cat.name">{{ cat.name }}</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-church">
                  Cabang Gereja Penyelenggara
                </label>
                <select 
                  id="form-church"
                  :value="form.church_name"
                  @change="onChurchSelect"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white outline-none focus:border-amber-400 cursor-pointer"
                >
                  <option value="Semua Cabang">Semua Cabang (Pusat)</option>
                  <option v-for="c in churches" :key="c.id" :value="c.church_name">{{ c.church_name }}</option>
                </select>
              </div>
            </div>

            <!-- Tanggal Mulai & Tanggal Selesai Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-start-date">
                  Tanggal Mulai <span class="text-rose-400">*</span>
                </label>
                <input 
                  id="form-start-date"
                  v-model="form.start_date"
                  type="date" 
                  required 
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-end-date">
                  Tanggal Selesai (Opsional)
                </label>
                <input 
                  id="form-end-date"
                  v-model="form.end_date"
                  type="date" 
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <!-- Jam Mulai & Jam Selesai Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-start-time">
                  Jam Mulai Pelaksanaan
                </label>
                <input 
                  id="form-start-time"
                  v-model="form.start_time"
                  type="text" 
                  placeholder="Contoh: 09:00 WIB" 
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-end-time">
                  Jam Selesai Pelaksanaan
                </label>
                <input 
                  id="form-end-time"
                  v-model="form.end_time"
                  type="text" 
                  placeholder="Contoh: 11:30 WIB" 
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <!-- Lokasi & Ruangan -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-location">
                Lokasi / Ruangan / Tautan Online
              </label>
              <input 
                id="form-location"
                v-model="form.location"
                type="text" 
                placeholder="Contoh: Gedung Gratia Lt. 2 / Ruang Serbaguna / Live Zoom" 
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 outline-none focus:border-amber-400"
              />
            </div>

            <!-- PIC & Sasaran Peserta Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-organizer">
                  Penanggung Jawab / PIC / Komisi
                </label>
                <input 
                  id="form-organizer"
                  v-model="form.organizer"
                  type="text" 
                  placeholder="Contoh: Pdt. Yohanes / Komisi Pemuda" 
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-target">
                  Sasaran Partisipan
                </label>
                <select 
                  id="form-target"
                  v-model="form.target_audience"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white outline-none focus:border-amber-400 cursor-pointer"
                >
                  <option value="Semua Jemaat">Semua Jemaat</option>
                  <option value="Pemuda & Remaja">Pemuda & Remaja</option>
                  <option value="Anak Sekolah Minggu">Anak Sekolah Minggu</option>
                  <option value="Kaum Pria / Bapak">Kaum Pria / Bapak</option>
                  <option value="Kaum Wanita / Ibu">Kaum Wanita / Ibu</option>
                  <option value="Lansia">Lansia</option>
                  <option value="Pengurus & Majelis">Pengurus & Majelis</option>
                </select>
              </div>
            </div>

            <!-- Status & Warna Aksen Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-status">
                  Status Agenda
                </label>
                <select 
                  id="form-status"
                  v-model="form.status"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white outline-none focus:border-amber-400 cursor-pointer"
                >
                  <option value="Akan Datang">Akan Datang</option>
                  <option value="Sedang Berlangsung">Sedang Berlangsung</option>
                  <option value="Selesai">Selesai</option>
                  <option value="Dibatalkan">Dibatalkan</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-color">
                  Warna Aksen Kalender
                </label>
                <select 
                  id="form-color"
                  v-model="form.color"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white outline-none focus:border-amber-400 cursor-pointer"
                >
                  <option v-for="c in colorOptions" :key="c.value" :value="c.value">{{ c.label }}</option>
                </select>
              </div>
            </div>

            <!-- Keterangan & Deskripsi -->
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1" for="form-desc">
                Deskripsi & Susunan Kegiatan
              </label>
              <textarea 
                id="form-desc"
                v-model="form.description"
                rows="3"
                placeholder="Rincian tema firman Tuhan, susunan acara, dresscode, dsb..." 
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 outline-none focus:border-amber-400"
              ></textarea>
            </div>

            <!-- Action Buttons -->
            <div class="pt-4 border-t border-white/10 flex items-center justify-end gap-3">
              <button 
                type="button" 
                @click="isFormModalOpen = false" 
                class="px-4 py-2.5 rounded-xl border border-slate-700 text-xs text-slate-300 hover:bg-white/10 cursor-pointer"
              >
                Batal
              </button>
              <button 
                type="submit" 
                :disabled="isSubmitting"
                class="px-5 py-2.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 text-xs font-bold shadow-lg shadow-amber-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50"
              >
                <i v-if="isSubmitting" class="bi bi-arrow-repeat animate-spin"></i>
                <span>{{ isSubmitting ? 'Menyimpan...' : (isEditing ? 'Perbarui Agenda' : 'Simpan Agenda') }}</span>
              </button>
            </div>

          </form>

        </div>
      </div>
    </Transition>

    <!-- MODAL DETAIL AGENDA -->
    <Transition name="modal">
      <div 
        v-if="isDetailModalOpen && selectedAgenda" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/75 backdrop-blur-sm"
      >
        <div class="w-full max-w-lg rounded-3xl border border-amber-500/30 bg-[#0c1b22] p-6 shadow-2xl text-slate-100 space-y-4">
          
          <div class="flex items-start justify-between gap-3">
            <span :class="['px-2.5 py-1 rounded-lg text-[10px] font-extrabold border', getCategoryBadgeClass(selectedAgenda.category)]">
              {{ selectedAgenda.category }}
            </span>
            <span :class="['px-2.5 py-1 rounded-lg text-[10px] font-bold border', getStatusBadgeClass(selectedAgenda.status)]">
              {{ selectedAgenda.status }}
            </span>
          </div>

          <div>
            <h3 class="font-serif text-2xl font-bold text-white">{{ selectedAgenda.title }}</h3>
            <p class="text-xs text-amber-300 font-mono mt-1 flex items-center gap-2">
              <i class="bi bi-calendar3"></i>
              <span>{{ formatDateId(selectedAgenda.start_date) }}</span>
            </p>
          </div>

          <div class="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5 text-xs">
            <div class="flex items-center gap-2.5 text-slate-300">
              <i class="bi bi-clock text-amber-400 shrink-0"></i>
              <span>Waktu: <strong>{{ selectedAgenda.start_time || 'Fleksibel' }} {{ selectedAgenda.end_time ? `- ${selectedAgenda.end_time}` : '' }}</strong></span>
            </div>
            <div class="flex items-center gap-2.5 text-slate-300">
              <i class="bi bi-geo-alt text-amber-400 shrink-0"></i>
              <span>Lokasi: <strong>{{ selectedAgenda.location || 'Gedung Ibadah Utama' }}</strong></span>
            </div>
            <div class="flex items-center gap-2.5 text-slate-300">
              <i class="bi bi-buildings text-amber-400 shrink-0"></i>
              <span>Cabang: <strong>{{ selectedAgenda.church_name || 'Semua Cabang' }}</strong></span>
            </div>
            <div class="flex items-center gap-2.5 text-slate-300">
              <i class="bi bi-person-badge text-amber-400 shrink-0"></i>
              <span>Penanggung Jawab (PIC): <strong>{{ selectedAgenda.organizer || 'Majelis Gereja' }}</strong></span>
            </div>
            <div class="flex items-center gap-2.5 text-slate-300">
              <i class="bi bi-people text-amber-400 shrink-0"></i>
              <span>Target Partisipan: <strong>{{ selectedAgenda.target_audience || 'Semua Jemaat' }}</strong></span>
            </div>
          </div>

          <div v-if="selectedAgenda.description" class="text-xs text-slate-300 leading-relaxed bg-slate-900/50 p-3.5 rounded-xl border border-white/5">
            <p class="font-bold text-slate-400 text-[10px] uppercase tracking-wider mb-1">Rincian Deskripsi:</p>
            <p class="whitespace-pre-line">{{ selectedAgenda.description }}</p>
          </div>

          <!-- Action Footer in Detail Modal -->
          <div class="pt-3 border-t border-white/10 flex items-center justify-between gap-2">
            <button 
              type="button" 
              @click="openDeleteConfirm(selectedAgenda)"
              class="px-3 py-2 rounded-xl text-xs font-bold text-rose-400 hover:bg-rose-500/10 border border-rose-500/20 cursor-pointer"
            >
              <i class="bi bi-trash mr-1"></i> Hapus
            </button>
            <div class="flex items-center gap-2">
              <button 
                type="button" 
                @click="openEditModal(selectedAgenda)"
                class="px-3.5 py-2 rounded-xl text-xs font-bold text-slate-950 bg-amber-400 hover:bg-amber-300 cursor-pointer shadow"
              >
                <i class="bi bi-pencil-square mr-1"></i> Edit Agenda
              </button>
              <button 
                type="button" 
                @click="isDetailModalOpen = false" 
                class="px-3.5 py-2 rounded-xl text-xs text-slate-300 hover:bg-white/10 border border-slate-700 cursor-pointer"
              >
                Tutup
              </button>
            </div>
          </div>

        </div>
      </div>
    </Transition>

    <!-- MODAL CONFIRM DELETE -->
    <Transition name="modal">
      <div 
        v-if="isDeleteModalOpen && agendaToDelete" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      >
        <div class="w-full max-w-md rounded-3xl border border-rose-500/40 bg-[#0c1b22] p-6 shadow-2xl text-slate-100 space-y-4 text-center">
          <div class="w-14 h-14 rounded-2xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 text-2xl mx-auto">
            <i class="bi bi-exclamation-triangle-fill"></i>
          </div>
          <div>
            <h3 class="font-serif text-xl font-bold text-white">Konfirmasi Hapus Agenda</h3>
            <p class="text-xs text-slate-400 mt-1">
              Apakah Anda yakin ingin menghapus agenda <strong class="text-white">"{{ agendaToDelete.title }}"</strong>? Tindakan ini tidak dapat dibatalkan.
            </p>
          </div>
          <div class="flex items-center justify-center gap-3 pt-3">
            <button 
              type="button" 
              @click="isDeleteModalOpen = false" 
              class="px-4 py-2.5 rounded-xl border border-slate-700 text-xs text-slate-300 hover:bg-white/10 cursor-pointer"
            >
              Batal
            </button>
            <button 
              type="button" 
              @click="handleConfirmDelete" 
              :disabled="isSubmitting"
              class="px-4 py-2.5 rounded-xl bg-rose-500 hover:bg-rose-400 text-white text-xs font-bold cursor-pointer disabled:opacity-50"
            >
              {{ isSubmitting ? 'Menghapus...' : 'Ya, Hapus Agenda' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </MainAdminLayout>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.96);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(11, 32, 39, 0.6);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.35);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(245, 158, 11, 0.65);
}
</style>
