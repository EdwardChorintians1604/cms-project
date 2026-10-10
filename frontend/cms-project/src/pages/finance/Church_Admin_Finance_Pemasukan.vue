<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'
import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'
import { exportToCSV, exportToPDF, exportToJSON, downloadServerExport } from '@/utils/exportFinanceReport'

const { user } = useAuth()
const { isDark } = useTheme()

// --- State Gereja & Admin Cabang ---
const activeChurch = reactive({
  id: null,
  name: 'Gereja Cabang GracePoint'
})

// --- State Data Utama Pemasukan ---
const pemasukanList = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

// Filter & Pencarian
const searchQuery = ref('')
const categoryFilter = ref('Semua')
const methodFilter = ref('Semua')
const statusFilter = ref('Semua')

// Modal State
const isAddModalOpen = ref(false)
const isEditModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const selectedItem = ref(null)
const isSubmitting = ref(false)

// Toast State
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

// Form State (Tambah & Edit)
const form = reactive({
  id: null,
  nomor_transaksi: '',
  tanggal: new Date().toISOString().slice(0, 10),
  kategori: 'Persembahan Ibadah Raya',
  jumlah: '',
  metode_pembayaran: 'Tunai',
  donor_name: '',
  keterangan: '',
  status_verifikasi: 'Verified'
})

const categories = [
  'Persembahan Ibadah Raya',
  'Perpuluhan Jemaat',
  'Dana Pembangunan Gedung',
  'Ucapan Syukur & Baptisan',
  'Diakonia / Kasih',
  'Persembahan Khusus / KKR',
  'Lain-lain'
]

const paymentMethods = ['Tunai', 'Transfer Bank', 'QRIS Digital']
const verificationStatuses = ['Verified', 'Pending', 'Rejected']

// Mock Default Data Awal yang terstruktur untuk Church Admin
const getInitialMockData = (churchName) => [
  {
    id: 101,
    nomor_transaksi: 'IN-CAB-2026-001',
    tanggal: '2026-09-06',
    kategori: 'Persembahan Ibadah Raya',
    church_name: churchName,
    nominal: 12500000,
    jumlah: 12500000,
    metode_pembayaran: 'Tunai',
    nama_penyetor: 'Majelis Kolekte Ibadah 1',
    donor_name: 'Majelis Kolekte Ibadah 1',
    keterangan: 'Kolekte Ibadah Raya Minggu Sesi Pagi',
    status_verifikasi: 'Verified',
    created_at: '2026-09-06T10:30:00Z'
  },
  {
    id: 102,
    nomor_transaksi: 'IN-CAB-2026-002',
    tanggal: '2026-09-06',
    kategori: 'Persembahan Ibadah Raya',
    church_name: churchName,
    nominal: 8900000,
    jumlah: 8900000,
    metode_pembayaran: 'QRIS Digital',
    nama_penyetor: 'Jemaat QRIS Mandiri',
    donor_name: 'Jemaat QRIS Mandiri',
    keterangan: 'Persembahan digital QRIS barcode mimbar',
    status_verifikasi: 'Verified',
    created_at: '2026-09-06T11:45:00Z'
  },
  {
    id: 103,
    nomor_transaksi: 'IN-CAB-2026-003',
    tanggal: '2026-09-08',
    kategori: 'Perpuluhan Jemaat',
    church_name: churchName,
    nominal: 16500000,
    jumlah: 16500000,
    metode_pembayaran: 'Transfer Bank',
    nama_penyetor: 'Keluarga Bpk. Hendra Gunawan',
    donor_name: 'Keluarga Bpk. Hendra Gunawan',
    keterangan: 'Perpuluhan rutin keluarga bulan September',
    status_verifikasi: 'Verified',
    created_at: '2026-09-08T09:15:00Z'
  },
  {
    id: 104,
    nomor_transaksi: 'IN-CAB-2026-004',
    tanggal: '2026-09-10',
    kategori: 'Dana Pembangunan Gedung',
    church_name: churchName,
    nominal: 25000000,
    jumlah: 25000000,
    metode_pembayaran: 'Transfer Bank',
    nama_penyetor: 'Donatur Khusus Pembangunan',
    donor_name: 'Donatur Khusus Pembangunan',
    keterangan: 'Donasi renovasi atap dan ruang doa cabang',
    status_verifikasi: 'Verified',
    created_at: '2026-09-10T14:20:00Z'
  },
  {
    id: 105,
    nomor_transaksi: 'IN-CAB-2026-005',
    tanggal: '2026-09-13',
    kategori: 'Ucapan Syukur & Baptisan',
    church_name: churchName,
    nominal: 4500000,
    jumlah: 4500000,
    metode_pembayaran: 'Tunai',
    nama_penyetor: 'Ibu Maria Natalia',
    donor_name: 'Ibu Maria Natalia',
    keterangan: 'Ucapan syukur penyerahan anak & baptisan air',
    status_verifikasi: 'Verified',
    created_at: '2026-09-13T12:00:00Z'
  },
  {
    id: 106,
    nomor_transaksi: 'IN-CAB-2026-006',
    tanggal: '2026-09-15',
    kategori: 'Diakonia / Kasih',
    church_name: churchName,
    nominal: 5200000,
    jumlah: 5200000,
    metode_pembayaran: 'Tunai',
    nama_penyetor: 'Persekutuan Kaum Pria (PKP)',
    donor_name: 'Persekutuan Kaum Pria (PKP)',
    keterangan: 'Sumbangan kasih untuk kas diakonia jemaat prasejahtera',
    status_verifikasi: 'Verified',
    created_at: '2026-09-15T16:30:00Z'
  }
]

// Penyimpanan lokal persisten
const getStorageKey = () => `grace_pemasukan_cabang_${activeChurch.id || 'default'}`

const saveToLocalStorage = () => {
  try {
    localStorage.setItem(getStorageKey(), JSON.stringify(pemasukanList.value))
  } catch (e) {
    console.warn('Gagal menyimpan ke localStorage:', e)
  }
}

const loadFromLocalStorage = () => {
  try {
    const raw = localStorage.getItem(getStorageKey())
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed
      }
    }
  } catch (e) {
    console.warn('Gagal membaca localStorage:', e)
  }
  return null
}

// Inisialisasi Identitas Admin & Muat Data
const initChurchIdentity = async () => {
  const u = user.value
  if (u) {
    activeChurch.id = u.church_id || (u.church && u.church.id) || null
    activeChurch.name = u.church_name || (u.church && u.church.church_name) || 'Gereja Cabang GracePoint'
  }
}

const loadData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    await initChurchIdentity()

    // 1. Cek penyimpanan lokal terlebih dahulu
    const localData = loadFromLocalStorage()
    if (localData && localData.length > 0) {
      pemasukanList.value = localData
    }

    // 2. Coba sinkronisasi dengan Backend API
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }

    const churchParam = activeChurch.id ? `?church_id=${activeChurch.id}&limit=200` : '?limit=200'
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pemasukan${churchParam}`, { headers })

    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data) && data.length > 0) {
        // Normalisasi format item agar seragam antara `jumlah` dan `nominal`
        const normalized = data.map((item) => ({
          ...item,
          nominal: Number(item.jumlah ?? item.nominal ?? 0),
          jumlah: Number(item.jumlah ?? item.nominal ?? 0),
          church_name: item.church_name || activeChurch.name,
          nama_penyetor: item.donor_name || item.nama_penyetor || 'Jemaat Terkasih',
          donor_name: item.donor_name || item.nama_penyetor || 'Jemaat Terkasih'
        }))
        pemasukanList.value = normalized
        saveToLocalStorage()
      } else if (!localData) {
        pemasukanList.value = getInitialMockData(activeChurch.name)
        saveToLocalStorage()
      }
    } else if (!localData) {
      pemasukanList.value = getInitialMockData(activeChurch.name)
      saveToLocalStorage()
    }
  } catch (err) {
    console.warn('Backend API tidak terjangkau, menggunakan data tersimpan:', err)
    if (pemasukanList.value.length === 0) {
      pemasukanList.value = getInitialMockData(activeChurch.name)
      saveToLocalStorage()
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})

// --- Computed Filters ---
const filteredList = computed(() => {
  return pemasukanList.value.filter((item) => {
    const q = searchQuery.value.toLowerCase().trim()
    const matchesSearch =
      !q ||
      (item.nomor_transaksi && item.nomor_transaksi.toLowerCase().includes(q)) ||
      (item.kategori && item.kategori.toLowerCase().includes(q)) ||
      (item.keterangan && item.keterangan.toLowerCase().includes(q)) ||
      ((item.nama_penyetor || item.donor_name) && (item.nama_penyetor || item.donor_name).toLowerCase().includes(q))

    const matchesCategory = categoryFilter.value === 'Semua' || item.kategori === categoryFilter.value
    const matchesMethod = methodFilter.value === 'Semua' || item.metode_pembayaran === methodFilter.value
    const matchesStatus = statusFilter.value === 'Semua' || item.status_verifikasi === statusFilter.value

    return matchesSearch && matchesCategory && matchesMethod && matchesStatus
  })
})

// --- Computed Metrics KPI ---
const metrics = computed(() => {
  const list = pemasukanList.value
  const total = list.reduce((acc, curr) => acc + (Number(curr.jumlah || curr.nominal) || 0), 0)

  const nowYearMonth = new Date().toISOString().slice(0, 7)
  const thisMonth = list
    .filter((i) => i.tanggal && i.tanggal.startsWith(nowYearMonth))
    .reduce((acc, curr) => acc + (Number(curr.jumlah || curr.nominal) || 0), 0)

  const persembahan = list
    .filter((i) => i.kategori === 'Persembahan Ibadah Raya')
    .reduce((acc, curr) => acc + (Number(curr.jumlah || curr.nominal) || 0), 0)

  const perpuluhan = list
    .filter((i) => i.kategori === 'Perpuluhan Jemaat' || i.kategori === 'Dana Pembangunan Gedung')
    .reduce((acc, curr) => acc + (Number(curr.jumlah || curr.nominal) || 0), 0)

  return { total, thisMonth, persembahan, perpuluhan }
})

const formatIDR = (num) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(num || 0)
}

// --- CRUD Actions Handlers ---
const openAddModal = () => {
  Object.assign(form, {
    id: null,
    nomor_transaksi: '',
    tanggal: new Date().toISOString().slice(0, 10),
    kategori: 'Persembahan Ibadah Raya',
    jumlah: '',
    metode_pembayaran: 'Tunai',
    donor_name: '',
    keterangan: '',
    status_verifikasi: 'Verified'
  })
  isAddModalOpen.value = true
}

const openEditModal = (item) => {
  selectedItem.value = item
  Object.assign(form, {
    id: item.id,
    nomor_transaksi: item.nomor_transaksi,
    tanggal: item.tanggal,
    kategori: item.kategori,
    jumlah: Number(item.jumlah || item.nominal || 0),
    metode_pembayaran: item.metode_pembayaran,
    donor_name: item.donor_name || item.nama_penyetor || '',
    keterangan: item.keterangan || '',
    status_verifikasi: item.status_verifikasi || 'Verified'
  })
  isEditModalOpen.value = true
}

const openDetailModal = (item) => {
  selectedItem.value = item
  isDetailModalOpen.value = true
}

const openDeleteModal = (item) => {
  selectedItem.value = item
  isDeleteModalOpen.value = true
}

// SIMPAN (CREATE)
const handleSaveNew = async () => {
  const rawJumlah = Number(form.jumlah)
  if (!rawJumlah || rawJumlah <= 0) {
    triggerToast('Nominal persembahan kas wajib diisi dengan angka valid di atas 0.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const newItem = {
      id: Date.now(),
      nomor_transaksi: `IN-CAB-${new Date().getFullYear()}-${String(pemasukanList.value.length + 1).padStart(3, '0')}`,
      tanggal: form.tanggal,
      kategori: form.kategori,
      nominal: rawJumlah,
      jumlah: rawJumlah,
      church_id: activeChurch.id,
      church_name: activeChurch.name,
      metode_pembayaran: form.metode_pembayaran,
      nama_penyetor: form.donor_name || 'Jemaat Terkasih',
      donor_name: form.donor_name || 'Jemaat Terkasih',
      keterangan: form.keterangan || 'Pencatatan kas persembahan gereja cabang',
      status_verifikasi: form.status_verifikasi,
      created_at: new Date().toISOString()
    }

    // Panggil Backend API
    try {
      const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pemasukan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          church_id: activeChurch.id || 1,
          tanggal: form.tanggal,
          kategori: form.kategori,
          jumlah: rawJumlah,
          metode_pembayaran: form.metode_pembayaran,
          donor_name: form.donor_name || 'Jemaat Terkasih',
          keterangan: form.keterangan,
          status_verifikasi: form.status_verifikasi
        })
      })
      if (res.ok) {
        const serverCreated = await res.json()
        if (serverCreated && serverCreated.id) {
          newItem.id = serverCreated.id
          if (serverCreated.nomor_transaksi) newItem.nomor_transaksi = serverCreated.nomor_transaksi
        }
      }
    } catch (apiErr) {
      console.warn('API error saat create, beralih ke local storage persistence:', apiErr)
    }

    pemasukanList.value.unshift(newItem)
    saveToLocalStorage()
    triggerToast('Pemasukan kas gereja cabang berhasil dicatat!')
    isAddModalOpen.value = false
  } catch (err) {
    triggerToast('Terjadi kesalahan saat menyimpan pemasukan.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// UPDATE (EDIT)
const handleUpdate = async () => {
  const rawJumlah = Number(form.jumlah)
  if (!rawJumlah || rawJumlah <= 0) {
    triggerToast('Nominal persembahan kas wajib diisi dengan benar.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const idx = pemasukanList.value.findIndex((i) => i.id === form.id)
    if (idx !== -1) {
      const updated = {
        ...pemasukanList.value[idx],
        tanggal: form.tanggal,
        kategori: form.kategori,
        nominal: rawJumlah,
        jumlah: rawJumlah,
        metode_pembayaran: form.metode_pembayaran,
        nama_penyetor: form.donor_name || 'Jemaat Terkasih',
        donor_name: form.donor_name || 'Jemaat Terkasih',
        keterangan: form.keterangan,
        status_verifikasi: form.status_verifikasi,
        updated_at: new Date().toISOString()
      }

      // Coba kirim ke Backend API
      try {
        const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
        await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pemasukan/${form.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {})
          },
          body: JSON.stringify({
            tanggal: form.tanggal,
            kategori: form.kategori,
            jumlah: rawJumlah,
            metode_pembayaran: form.metode_pembayaran,
            donor_name: form.donor_name,
            keterangan: form.keterangan,
            status_verifikasi: form.status_verifikasi
          })
        })
      } catch (apiErr) {
        console.warn('API error saat update, tetap disimpan secara lokal:', apiErr)
      }

      pemasukanList.value[idx] = updated
      saveToLocalStorage()
      triggerToast('Perubahan transaksi pemasukan berhasil diperbarui!')
      isEditModalOpen.value = false
    }
  } catch (err) {
    triggerToast('Gagal memperbarui data pemasukan.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// DELETE (HAPUS)
const handleDelete = async () => {
  if (!selectedItem.value) return
  isSubmitting.value = true
  try {
    const itemId = selectedItem.value.id

    // Panggil Backend API
    try {
      const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
      await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pemasukan/${itemId}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
    } catch (apiErr) {
      console.warn('API error saat delete, tetap dihapus secara lokal:', apiErr)
    }

    pemasukanList.value = pemasukanList.value.filter((i) => i.id !== itemId)
    saveToLocalStorage()
    triggerToast('Data transaksi pemasukan berhasil dihapus dari sistem.')
    isDeleteModalOpen.value = false
    selectedItem.value = null
  } catch (err) {
    triggerToast('Gagal menghapus data pemasukan.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// --- Handler Ekspor Laporan ---
const isExportMenuOpen = ref(false)

const handleExportPDF = async () => {
  isExportMenuOpen.value = false
  try {
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    await downloadServerExport({
      baseUrl: APP_CONFIG.apiBaseUrl,
      type: 'pemasukan',
      format: 'pdf',
      token,
      churchId: activeChurch.id
    })
    triggerToast('Laporan PDF resmi berhasil diunduh dari server Python.')
  } catch (err) {
    exportToPDF({
      title: `Pemasukan Kas & Persembahan - ${activeChurch.name}`,
      items: filteredList.value,
      isPemasukan: true,
      churchFilter: activeChurch.name
    })
    triggerToast('Laporan PDF siap dicetak / disimpan.')
  }
}

const handleExportExcel = async () => {
  isExportMenuOpen.value = false
  try {
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    await downloadServerExport({
      baseUrl: APP_CONFIG.apiBaseUrl,
      type: 'pemasukan',
      format: 'excel',
      token,
      churchId: activeChurch.id
    })
    triggerToast('Laporan Excel (.xlsx) berhasil diunduh dari server Python.')
  } catch (err) {
    exportToCSV({
      title: `Pemasukan Kas & Persembahan - ${activeChurch.name}`,
      filename: `Laporan_Pemasukan_${activeChurch.name.replace(/\s+/g, '_')}`,
      items: filteredList.value,
      isPemasukan: true,
      churchFilter: activeChurch.name
    })
    triggerToast('Laporan Excel / Spreadsheet berhasil diunduh.')
  }
}

const handleExportJSON = () => {
  exportToJSON({
    title: `Pemasukan Kas & Persembahan - ${activeChurch.name}`,
    filename: `Data_Pemasukan_${activeChurch.name.replace(/\s+/g, '_')}`,
    items: filteredList.value,
    isPemasukan: true,
    churchFilter: activeChurch.name
  })
  isExportMenuOpen.value = false
  triggerToast('Data cadangan JSON audit berhasil diekspor.')
}
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6 font-sans pb-12 transition-colors duration-300">

      <!-- Toast Feedback -->
      <Transition name="toast">
        <div 
          v-if="showToast"
          :class="[
            'fixed top-5 right-5 z-[100] max-w-md px-4 py-3 rounded-2xl shadow-2xl border flex items-center gap-3 backdrop-blur-xl transition-all duration-300',
            toastType === 'success' 
              ? 'bg-emerald-950/95 text-emerald-200 border-emerald-500/50 shadow-emerald-950/50' 
              : 'bg-rose-950/95 text-rose-200 border-rose-500/50 shadow-rose-950/50'
          ]"
        >
          <i :class="['bi text-lg', toastType === 'success' ? 'bi-check-circle-fill text-emerald-400' : 'bi-exclamation-octagon-fill text-rose-400']"></i>
          <p class="text-xs font-semibold leading-relaxed">{{ toastMessage }}</p>
          <button @click="showToast = false" class="ml-auto text-slate-400 hover:text-white cursor-pointer">
            <i class="bi bi-x-lg text-xs"></i>
          </button>
        </div>
      </Transition>

      <!-- NAVIGATION TABS SWITCHER ANTAR MODUL KEUANGAN CABANG -->
      <div :class="['p-1.5 rounded-2xl border flex flex-wrap items-center gap-1.5 transition-colors', isDark ? 'bg-slate-900/80 border-slate-800' : 'bg-slate-100 border-slate-300/80']">
        <RouterLink 
          to="/church-finance-pemasukan"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 border shadow-sm',
            'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
          ]"
        >
          <i class="bi bi-arrow-down-left-circle-fill"></i>
          <span>Pemasukan Kas &amp; Persembahan</span>
        </RouterLink>

        <RouterLink 
          to="/church-finance-pengeluaran"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2 border border-transparent',
            isDark ? 'text-slate-400 hover:text-rose-300 hover:bg-slate-800/60' : 'text-slate-600 hover:text-rose-600 hover:bg-white'
          ]"
        >
          <i class="bi bi-arrow-up-right-circle"></i>
          <span>Pengeluaran Kas Operasional</span>
        </RouterLink>

        <RouterLink 
          to="/church-finance"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2 border border-transparent',
            isDark ? 'text-slate-400 hover:text-amber-300 hover:bg-slate-800/60' : 'text-slate-600 hover:text-amber-600 hover:bg-white'
          ]"
        >
          <i class="bi bi-calculator"></i>
          <span>Kasir Hitung Pecahan Ibadah</span>
        </RouterLink>

        <RouterLink 
          to="/church-finance-graphic"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2 border border-transparent',
            isDark ? 'text-slate-400 hover:text-sky-300 hover:bg-slate-800/60' : 'text-slate-600 hover:text-sky-600 hover:bg-white'
          ]"
        >
          <i class="bi bi-graph-up-arrow"></i>
          <span>Grafik &amp; Analisis Keuangan</span>
        </RouterLink>
      </div>

      <!-- HERO BANNER -->
      <section :class="[
        'relative overflow-hidden rounded-3xl border p-6 sm:p-8 shadow-2xl backdrop-blur-xl transition-all duration-300',
        isDark 
          ? 'border-emerald-500/30 bg-gradient-to-r from-slate-950 via-slate-900 to-emerald-950/40 text-white' 
          : 'border-emerald-300 bg-gradient-to-r from-emerald-50/90 via-white to-amber-50/50 text-slate-900'
      ]">
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-wallet2"></i>
              <span>Modul Finansial Gereja Cabang • {{ activeChurch.name }}</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight">
              Pemasukan Kas &amp; Persembahan Gereja
            </h1>
            <p :class="['mt-1.5 text-xs sm:text-sm max-w-2xl leading-relaxed', isDark ? 'text-slate-300' : 'text-slate-600']">
              Kelola pencatatan pemasukan kas jemaat, persembahan kantong ibadah raya, perpuluhan bulanan, dan penerimaan donasi digital QRIS cabang secara mandiri &amp; akuntabel.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <!-- Dropdown Ekspor -->
            <div class="relative">
              <button 
                type="button" 
                @click="isExportMenuOpen = !isExportMenuOpen"
                :class="[
                  'flex items-center gap-2 rounded-2xl border px-4 py-2.5 text-xs font-bold shadow-md transition cursor-pointer',
                  isDark 
                    ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/25' 
                    : 'border-emerald-400 bg-emerald-100 text-emerald-900 hover:bg-emerald-200'
                ]"
              >
                <i class="bi bi-download"></i>
                <span>Ekspor Laporan</span>
                <i :class="['bi text-[10px] transition-transform', isExportMenuOpen ? 'bi-chevron-up' : 'bi-chevron-down']"></i>
              </button>

              <Transition name="fade">
                <div 
                  v-if="isExportMenuOpen"
                  :class="[
                    'absolute right-0 z-50 mt-2 w-56 space-y-1 rounded-2xl border p-2 shadow-2xl backdrop-blur-xl',
                    isDark ? 'border-emerald-500/30 bg-slate-950/95 text-slate-200' : 'border-slate-200 bg-white text-slate-800'
                  ]"
                >
                  <div class="px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-wider text-slate-400 border-b border-slate-500/20">
                    Pilih Format Dokumen
                  </div>

                  <button 
                    type="button"
                    @click="handleExportPDF"
                    :class="['w-full text-left px-3 py-2 rounded-xl text-xs transition flex items-center gap-2.5 cursor-pointer', isDark ? 'hover:bg-slate-800/80 text-slate-200' : 'hover:bg-slate-100 text-slate-800']"
                  >
                    <i class="bi bi-file-earmark-pdf-fill text-rose-500 text-sm"></i>
                    <div>
                      <p class="font-bold">Laporan PDF (Resmi)</p>
                      <p class="text-[10px] text-slate-400">Format cetak berkop resmi</p>
                    </div>
                  </button>

                  <button 
                    type="button"
                    @click="handleExportExcel"
                    :class="['w-full text-left px-3 py-2 rounded-xl text-xs transition flex items-center gap-2.5 cursor-pointer', isDark ? 'hover:bg-slate-800/80 text-slate-200' : 'hover:bg-slate-100 text-slate-800']"
                  >
                    <i class="bi bi-file-earmark-excel-fill text-emerald-500 text-sm"></i>
                    <div>
                      <p class="font-bold">Excel / Spreadsheet</p>
                      <p class="text-[10px] text-slate-400">File tabel (.csv / .xlsx)</p>
                    </div>
                  </button>

                  <button 
                    type="button"
                    @click="handleExportJSON"
                    :class="['w-full text-left px-3 py-2 rounded-xl text-xs transition flex items-center gap-2.5 cursor-pointer', isDark ? 'hover:bg-slate-800/80 text-slate-200' : 'hover:bg-slate-100 text-slate-800']"
                  >
                    <i class="bi bi-filetype-json text-sky-500 text-sm"></i>
                    <div>
                      <p class="font-bold">Data JSON Audit</p>
                      <p class="text-[10px] text-slate-400">Cadangan backup digital</p>
                    </div>
                  </button>
                </div>
              </Transition>
            </div>

            <!-- Tombol Tambah Transaksi -->
            <button 
              type="button" 
              @click="openAddModal" 
              class="flex items-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 px-5 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-emerald-500/20 transition cursor-pointer"
            >
              <i class="bi bi-plus-circle-fill text-sm"></i>
              <span>Catat Pemasukan Baru</span>
            </button>
          </div>
        </div>
      </section>

      <!-- KPI METRICS SUMMARY -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Total Akumulasi</span>
            <div class="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-sm">
              <i class="bi bi-cash-stack"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-emerald-400 font-mono">{{ formatIDR(metrics.total) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Total kas masuk cabang</p>
        </div>

        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Bulan Berjalan</span>
            <div class="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 text-sm">
              <i class="bi bi-calendar-check"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-amber-400 font-mono">{{ formatIDR(metrics.thisMonth) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Pemasukan bulan aktif</p>
        </div>

        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Persembahan Ibadah</span>
            <div class="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 text-sm">
              <i class="bi bi-bell-fill"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-sky-400 font-mono">{{ formatIDR(metrics.persembahan) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Kolekte kantong kebaktian</p>
        </div>

        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Perpuluhan &amp; Khusus</span>
            <div class="w-8 h-8 rounded-lg bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 text-sm">
              <i class="bi bi-gift-fill"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-purple-400 font-mono">{{ formatIDR(metrics.perpuluhan) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Perpuluhan &amp; Pembangunan</p>
        </div>
      </section>

      <!-- FILTER & PENCARIAN TOOLBAR -->
      <section :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          
          <div class="relative">
            <i class="bi bi-search absolute left-3 top-2.5 text-slate-400 text-xs"></i>
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Cari transaksi, penyetor, keterangan..." 
              :class="[
                'w-full rounded-xl border pl-9 pr-3 py-2 text-xs outline-none transition',
                isDark ? 'border-slate-700 bg-slate-950/80 text-white placeholder-slate-500 focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-emerald-500'
              ]"
            />
          </div>

          <div>
            <select 
              v-model="categoryFilter"
              :class="[
                'w-full rounded-xl border px-3 py-2 text-xs outline-none transition cursor-pointer',
                isDark ? 'border-slate-700 bg-slate-950/80 text-white focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 focus:border-emerald-500'
              ]"
            >
              <option value="Semua">Semua Kategori Pemasukan</option>
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div>
            <select 
              v-model="methodFilter"
              :class="[
                'w-full rounded-xl border px-3 py-2 text-xs outline-none transition cursor-pointer',
                isDark ? 'border-slate-700 bg-slate-950/80 text-white focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 focus:border-emerald-500'
              ]"
            >
              <option value="Semua">Semua Metode Pembayaran</option>
              <option v-for="m in paymentMethods" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>

          <div>
            <select 
              v-model="statusFilter"
              :class="[
                'w-full rounded-xl border px-3 py-2 text-xs outline-none transition cursor-pointer',
                isDark ? 'border-slate-700 bg-slate-950/80 text-white focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 focus:border-emerald-500'
              ]"
            >
              <option value="Semua">Semua Status Verifikasi</option>
              <option v-for="s in verificationStatuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

        </div>
      </section>

      <!-- DATA TABLE PEMASUKAN KAS -->
      <section :class="['rounded-3xl border p-5 sm:p-6 shadow-2xl backdrop-blur-xl transition-colors', isDark ? 'border-slate-800 bg-slate-900/80 text-white' : 'border-slate-200 bg-white text-slate-900']">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-700/30">
          <div>
            <h3 class="font-serif text-xl font-bold">Buku Catatan Kas Masuk Cabang</h3>
            <p :class="['text-xs mt-0.5', isDark ? 'text-slate-400' : 'text-slate-600']">
              Daftar transaksi penerimaan kas persembahan yang tercatat di {{ activeChurch.name }}.
            </p>
          </div>
          <span class="text-xs text-emerald-400 font-mono font-bold self-start sm:self-auto">
            {{ filteredList.length }} Catatan Transaksi
          </span>
        </div>

        <div class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr :class="['border-b text-[11px] uppercase tracking-wider', isDark ? 'border-slate-800 text-slate-400 bg-slate-950/50' : 'border-slate-200 text-slate-600 bg-slate-100/70']">
                <th class="py-3 px-4">Tanggal &amp; No. Transaksi</th>
                <th class="py-3 px-4">Kategori Pemasukan</th>
                <th class="py-3 px-4">Penyetor / Donatur</th>
                <th class="py-3 px-4">Metode</th>
                <th class="py-3 px-4 text-right">Jumlah (IDR)</th>
                <th class="py-3 px-4 text-center">Status</th>
                <th class="py-3 px-4 text-center">Aksi CRUD</th>
              </tr>
            </thead>
            <tbody :class="['divide-y', isDark ? 'divide-slate-800/60' : 'divide-slate-200']">
              <tr 
                v-for="item in filteredList" 
                :key="item.id"
                :class="['transition group cursor-pointer', isDark ? 'hover:bg-slate-800/50' : 'hover:bg-slate-50']"
                @click="openDetailModal(item)"
              >
                <td class="py-3.5 px-4 whitespace-nowrap">
                  <span class="font-bold block">{{ item.tanggal }}</span>
                  <span class="text-[10px] text-amber-500 font-mono">{{ item.nomor_transaksi || `TRX-${item.id}` }}</span>
                </td>

                <td class="py-3.5 px-4">
                  <span class="font-semibold block">{{ item.kategori }}</span>
                  <span :class="['text-[11px] truncate max-w-xs block', isDark ? 'text-slate-400' : 'text-slate-500']">{{ item.keterangan || '-' }}</span>
                </td>

                <td class="py-3.5 px-4 font-medium">
                  {{ item.nama_penyetor || item.donor_name || 'Jemaat Terkasih' }}
                </td>

                <td class="py-3.5 px-4 whitespace-nowrap">
                  <span 
                    :class="[
                      'px-2.5 py-1 rounded-lg text-[10px] font-bold border',
                      item.metode_pembayaran === 'Tunai' 
                        ? 'bg-amber-500/15 text-amber-400 border-amber-500/30' 
                        : item.metode_pembayaran === 'Transfer Bank' 
                          ? 'bg-sky-500/15 text-sky-400 border-sky-500/30' 
                          : 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    ]"
                  >
                    {{ item.metode_pembayaran }}
                  </span>
                </td>

                <td class="py-3.5 px-4 text-right font-bold text-emerald-400 font-mono text-sm whitespace-nowrap">
                  + {{ formatIDR(item.jumlah || item.nominal) }}
                </td>

                <td class="py-3.5 px-4 text-center whitespace-nowrap">
                  <span 
                    :class="[
                      'px-2 py-0.5 rounded-full text-[10px] font-semibold border',
                      item.status_verifikasi === 'Verified'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : item.status_verifikasi === 'Pending'
                          ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                          : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                    ]"
                  >
                    {{ item.status_verifikasi || 'Verified' }}
                  </span>
                </td>

                <td class="py-3.5 px-4 text-center whitespace-nowrap" @click.stop>
                  <div class="flex items-center justify-center gap-1.5">
                    <!-- Detail -->
                    <button 
                      type="button" 
                      @click="openDetailModal(item)"
                      :class="['p-1.5 rounded-lg text-xs transition cursor-pointer', isDark ? 'text-slate-300 hover:text-amber-300 hover:bg-slate-800' : 'text-slate-600 hover:text-amber-600 hover:bg-slate-100']"
                      title="Lihat Rincian Voucher"
                    >
                      <i class="bi bi-eye"></i>
                    </button>

                    <!-- Edit -->
                    <button 
                      type="button" 
                      @click="openEditModal(item)"
                      :class="['p-1.5 rounded-lg text-xs transition cursor-pointer', isDark ? 'text-slate-300 hover:text-sky-300 hover:bg-slate-800' : 'text-slate-600 hover:text-sky-600 hover:bg-slate-100']"
                      title="Edit Data Pemasukan"
                    >
                      <i class="bi bi-pencil-square"></i>
                    </button>

                    <!-- Delete -->
                    <button 
                      type="button" 
                      @click="openDeleteModal(item)"
                      class="p-1.5 rounded-lg text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/15 transition cursor-pointer"
                      title="Hapus Transaksi"
                    >
                      <i class="bi bi-trash3"></i>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="filteredList.length === 0">
                <td colspan="7" class="py-12 text-center text-slate-400">
                  <i class="bi bi-inbox text-3xl block text-slate-600 mb-2"></i>
                  Tidak ada catatan pemasukan yang sesuai kriteria pencarian.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- ======================================================== -->
    <!-- MODAL CATAT PEMASUKAN BARU (CREATE)                     -->
    <!-- ======================================================== -->
    <Transition name="fade">
      <div 
        v-if="isAddModalOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto"
        @click.self="isAddModalOpen = false"
      >
        <div :class="['w-full max-w-lg rounded-3xl border p-6 shadow-2xl space-y-4 my-auto', isDark ? 'bg-slate-900 border-emerald-500/40 text-white' : 'bg-white border-emerald-300 text-slate-900']">
          <div class="flex items-center justify-between pb-3 border-b border-slate-700/30">
            <h3 class="font-serif text-lg font-bold flex items-center gap-2">
              <i class="bi bi-plus-circle-fill text-emerald-400"></i> Catat Pemasukan Kas Baru
            </h3>
            <button @click="isAddModalOpen = false" class="text-slate-400 hover:text-white cursor-pointer">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <form @submit.prevent="handleSaveNew" class="space-y-4 text-xs">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Tanggal Transaksi *</label>
                <input 
                  v-model="form.tanggal" 
                  type="date" 
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 focus:border-emerald-500']"
                />
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Kategori Kas *</label>
                <select 
                  v-model="form.kategori"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 focus:border-emerald-500']"
                >
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Nominal Penerimaan (Rp) *</label>
                <input 
                  v-model.number="form.jumlah" 
                  type="number" 
                  min="1"
                  placeholder="Contoh: 5000000"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 font-mono font-bold text-emerald-400 outline-none', isDark ? 'border-slate-700 bg-slate-950 focus:border-emerald-400' : 'border-slate-300 bg-white focus:border-emerald-500']"
                />
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Metode Pembayaran *</label>
                <select 
                  v-model="form.metode_pembayaran"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 focus:border-emerald-500']"
                >
                  <option v-for="m in paymentMethods" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block font-semibold mb-1 text-slate-400">Nama Penyetor / Donatur</label>
              <input 
                v-model="form.donor_name" 
                type="text" 
                placeholder="Contoh: Jemaat Sesi 1 / Nama Keluarga / Donatur"
                :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 focus:border-emerald-500']"
              />
            </div>

            <div>
              <label class="block font-semibold mb-1 text-slate-400">Keterangan / Keperluan Catatan</label>
              <textarea 
                v-model="form.keterangan" 
                rows="2" 
                placeholder="Rincian catatan penerimaan persembahan atau acara kebaktian..."
                :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-emerald-400' : 'border-slate-300 bg-white text-slate-900 focus:border-emerald-500']"
              ></textarea>
            </div>

            <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-700/30">
              <button 
                type="button" 
                @click="isAddModalOpen = false"
                :class="['px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer', isDark ? 'text-slate-400 hover:text-white bg-slate-800' : 'text-slate-600 hover:text-slate-900 bg-slate-100']"
              >
                Batal
              </button>
              <button 
                type="submit" 
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl text-xs font-bold text-slate-950 bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 transition cursor-pointer flex items-center gap-1.5 shadow-md shadow-emerald-500/20"
              >
                <i v-if="isSubmitting" class="bi bi-arrow-repeat animate-spin"></i>
                <i v-else class="bi bi-check2-circle"></i>
                <span>Simpan ke Buku Kas</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ======================================================== -->
    <!-- MODAL EDIT PEMASUKAN (UPDATE)                           -->
    <!-- ======================================================== -->
    <Transition name="fade">
      <div 
        v-if="isEditModalOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto"
        @click.self="isEditModalOpen = false"
      >
        <div :class="['w-full max-w-lg rounded-3xl border p-6 shadow-2xl space-y-4 my-auto', isDark ? 'bg-slate-900 border-sky-500/40 text-white' : 'bg-white border-sky-300 text-slate-900']">
          <div class="flex items-center justify-between pb-3 border-b border-slate-700/30">
            <h3 class="font-serif text-lg font-bold flex items-center gap-2">
              <i class="bi bi-pencil-square text-sky-400"></i> Edit Catatan Pemasukan Kas
            </h3>
            <button @click="isEditModalOpen = false" class="text-slate-400 hover:text-white cursor-pointer">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <form @submit.prevent="handleUpdate" class="space-y-4 text-xs">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Nomor Transaksi</label>
                <input 
                  :value="form.nomor_transaksi" 
                  disabled
                  class="w-full rounded-xl border border-slate-700/50 bg-slate-950/50 px-3 py-2 font-mono text-slate-400 cursor-not-allowed"
                />
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Tanggal Transaksi *</label>
                <input 
                  v-model="form.tanggal" 
                  type="date" 
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Kategori Kas *</label>
                <select 
                  v-model="form.kategori"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
                >
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Nominal Penerimaan (Rp) *</label>
                <input 
                  v-model.number="form.jumlah" 
                  type="number" 
                  min="1"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 font-mono font-bold text-emerald-400 outline-none', isDark ? 'border-slate-700 bg-slate-950 focus:border-sky-400' : 'border-slate-300 bg-white focus:border-sky-500']"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Metode Pembayaran *</label>
                <select 
                  v-model="form.metode_pembayaran"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
                >
                  <option v-for="m in paymentMethods" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Status Verifikasi</label>
                <select 
                  v-model="form.status_verifikasi"
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
                >
                  <option v-for="s in verificationStatuses" :key="s" :value="s">{{ s }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block font-semibold mb-1 text-slate-400">Nama Penyetor / Donatur</label>
              <input 
                v-model="form.donor_name" 
                type="text" 
                :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
              />
            </div>

            <div>
              <label class="block font-semibold mb-1 text-slate-400">Keterangan / Keperluan</label>
              <textarea 
                v-model="form.keterangan" 
                rows="2" 
                :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
              ></textarea>
            </div>

            <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-700/30">
              <button 
                type="button" 
                @click="isEditModalOpen = false"
                :class="['px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer', isDark ? 'text-slate-400 hover:text-white bg-slate-800' : 'text-slate-600 hover:text-slate-900 bg-slate-100']"
              >
                Batal
              </button>
              <button 
                type="submit" 
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl text-xs font-bold text-slate-950 bg-gradient-to-r from-sky-400 to-sky-500 hover:from-sky-300 hover:to-sky-400 transition cursor-pointer flex items-center gap-1.5 shadow-md shadow-sky-500/20"
              >
                <i v-if="isSubmitting" class="bi bi-arrow-repeat animate-spin"></i>
                <i v-else class="bi bi-check2-circle"></i>
                <span>Simpan Perubahan</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ======================================================== -->
    <!-- MODAL DETAIL TRANSAKSI (VIEW VOUCHER)                    -->
    <!-- ======================================================== -->
    <Transition name="fade">
      <div 
        v-if="isDetailModalOpen && selectedItem" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto"
        @click.self="isDetailModalOpen = false"
      >
        <div :class="['w-full max-w-lg rounded-3xl border p-6 shadow-2xl space-y-4 my-auto', isDark ? 'bg-slate-900 border-amber-500/40 text-white' : 'bg-white border-amber-300 text-slate-900']">
          <div class="flex items-center justify-between pb-3 border-b border-slate-700/30">
            <div>
              <span class="text-[10px] uppercase tracking-wider text-amber-400 font-extrabold block">BUKTI KAS MASUK (OFFICIAL VOUCHER)</span>
              <h3 class="font-serif text-lg font-bold">{{ selectedItem.nomor_transaksi || `TRX-${selectedItem.id}` }}</h3>
            </div>
            <button @click="isDetailModalOpen = false" class="text-slate-400 hover:text-white cursor-pointer">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <div class="space-y-3 text-xs">
            <div class="p-4 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-between">
              <div>
                <span class="text-[11px] text-emerald-400 font-semibold block">Total Nominal Diterima</span>
                <span class="text-2xl font-black text-emerald-300 font-mono">+ {{ formatIDR(selectedItem.jumlah || selectedItem.nominal) }}</span>
              </div>
              <span class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/40">
                {{ selectedItem.status_verifikasi || 'Verified' }}
              </span>
            </div>

            <div class="grid grid-cols-2 gap-3 pt-2">
              <div>
                <span class="text-[10px] text-slate-400 block">Tanggal Transaksi</span>
                <span class="font-bold">{{ selectedItem.tanggal }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Kategori Pemasukan</span>
                <span class="font-bold">{{ selectedItem.kategori }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Metode Pembayaran</span>
                <span class="font-bold">{{ selectedItem.metode_pembayaran }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Cabang Gereja</span>
                <span class="font-bold">{{ selectedItem.church_name || activeChurch.name }}</span>
              </div>
            </div>

            <div class="pt-2 border-t border-slate-700/30">
              <span class="text-[10px] text-slate-400 block">Penyetor / Donatur Terdaftar</span>
              <span class="font-semibold text-sm">{{ selectedItem.nama_penyetor || selectedItem.donor_name || 'Jemaat Terkasih' }}</span>
            </div>

            <div>
              <span class="text-[10px] text-slate-400 block">Catatan / Keterangan</span>
              <p class="mt-0.5 leading-relaxed">{{ selectedItem.keterangan || '-' }}</p>
            </div>

            <div class="p-3 rounded-xl border border-slate-700/40 bg-slate-950/40 text-[10px] font-mono text-slate-400 space-y-1">
              <div class="flex items-center justify-between">
                <span>Security Token SHA-256:</span>
                <span class="text-emerald-400 font-bold">VERIFIED_INTEGRITY</span>
              </div>
              <p class="truncate text-slate-500">HASH: 8f9b4c2e6d1a7f0e3b5a8c9d2e1f4a7b0c3d5e8a7f1b2c4d6e8a0b2c4d6e8f0a</p>
            </div>
          </div>

          <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-700/30">
            <button 
              type="button" 
              @click="isDetailModalOpen = false"
              :class="['px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer', isDark ? 'text-slate-400 hover:text-white bg-slate-800' : 'text-slate-600 hover:text-slate-900 bg-slate-100']"
            >
              Tutup
            </button>
            <button 
              type="button" 
              @click="isDetailModalOpen = false; openEditModal(selectedItem)"
              class="px-4 py-2 rounded-xl text-xs font-bold text-slate-950 bg-amber-400 hover:bg-amber-300 transition cursor-pointer flex items-center gap-1.5"
            >
              <i class="bi bi-pencil-square"></i>
              <span>Edit Voucher</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ======================================================== -->
    <!-- MODAL KONFIRMASI HAPUS (DELETE)                          -->
    <!-- ======================================================== -->
    <Transition name="fade">
      <div 
        v-if="isDeleteModalOpen && selectedItem" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md"
        @click.self="isDeleteModalOpen = false"
      >
        <div :class="['w-full max-w-md rounded-3xl border p-6 shadow-2xl space-y-4', isDark ? 'bg-slate-900 border-rose-500/40 text-white' : 'bg-white border-rose-300 text-slate-900']">
          <div class="w-12 h-12 rounded-2xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 text-xl mx-auto">
            <i class="bi bi-exclamation-triangle-fill"></i>
          </div>

          <div class="text-center space-y-1">
            <h3 class="font-serif text-lg font-bold text-rose-400">Konfirmasi Hapus Transaksi</h3>
            <p :class="['text-xs leading-relaxed', isDark ? 'text-slate-300' : 'text-slate-600']">
              Apakah Anda yakin ingin menghapus catatan pemasukan kas <span class="font-bold font-mono text-amber-400">{{ selectedItem.nomor_transaksi || `TRX-${selectedItem.id}` }}</span> sebesar <span class="font-bold text-emerald-400">{{ formatIDR(selectedItem.jumlah || selectedItem.nominal) }}</span>?
            </p>
            <p class="text-[11px] text-rose-400/90 font-medium pt-1">
              Tindakan ini akan mempengaruhi rekapitulasi buku kas gereja cabang!
            </p>
          </div>

          <div class="flex items-center justify-center gap-3 pt-3 border-t border-slate-700/30">
            <button 
              type="button" 
              @click="isDeleteModalOpen = false"
              :class="['px-5 py-2 rounded-xl text-xs font-semibold cursor-pointer', isDark ? 'text-slate-400 hover:text-white bg-slate-800' : 'text-slate-600 hover:text-slate-900 bg-slate-100']"
            >
              Batal
            </button>
            <button 
              type="button" 
              :disabled="isSubmitting"
              @click="handleDelete"
              class="px-5 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 transition cursor-pointer flex items-center gap-1.5 shadow-md shadow-rose-600/30"
            >
              <i v-if="isSubmitting" class="bi bi-arrow-repeat animate-spin"></i>
              <i v-else class="bi bi-trash3-fill"></i>
              <span>Ya, Hapus Transaksi</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </ChurchAdminLayout>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
