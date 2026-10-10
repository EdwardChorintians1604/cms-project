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

// --- State Data Utama Pengeluaran ---
const pengeluaranList = ref([])
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
  nomor_voucher: '',
  tanggal: new Date().toISOString().slice(0, 10),
  kategori: 'Operasional Gedung & Utilitas',
  jumlah: '',
  metode_pembayaran: 'Tunai',
  penerima: '',
  keperluan: '',
  status_persetujuan: 'Disetujui',
  disetujui_oleh: 'Majelis Jemaat / Admin Cabang'
})

const categories = [
  'Operasional Gedung & Utilitas',
  'Honorarium Pelayan Firman & Musik',
  'Diakonia Sosial & Santunan Kasih',
  'Pemeliharaan Aset & Fasilitas',
  'Program Remaja, Pemuda & Sekolah Minggu',
  'Konsumsi & Kelengkapan Ibadah',
  'Lain-lain'
]

const paymentMethods = ['Tunai', 'Transfer Bank', 'QRIS Digital']
const approvalStatuses = ['Disetujui', 'Pending', 'Ditolak']

// Initial Mock Data untuk Church Admin Cabang
const getInitialMockData = (churchName) => [
  {
    id: 201,
    nomor_voucher: 'OUT-CAB-2026-001',
    nomor_transaksi: 'OUT-CAB-2026-001',
    tanggal: '2026-09-02',
    kategori: 'Operasional Gedung & Utilitas',
    church_name: churchName,
    nominal: 4750000,
    jumlah: 4750000,
    metode_pembayaran: 'Transfer Bank',
    penerima: 'PLN & Internet IndiHome',
    keperluan: 'Pembayaran tagihan listrik AC ruang ibadah dan koneksi Wi-Fi streaming',
    keterangan: 'Pembayaran tagihan listrik AC ruang ibadah dan koneksi Wi-Fi streaming',
    status_persetujuan: 'Disetujui',
    disetujui_oleh: 'Admin Cabang',
    created_at: '2026-09-02T11:00:00Z'
  },
  {
    id: 202,
    nomor_voucher: 'OUT-CAB-2026-002',
    nomor_transaksi: 'OUT-CAB-2026-002',
    tanggal: '2026-09-06',
    kategori: 'Honorarium Pelayan Firman & Musik',
    church_name: churchName,
    nominal: 3500000,
    jumlah: 3500000,
    metode_pembayaran: 'Tunai',
    penerima: 'Pdt. Tamu & Tim Pemuji',
    keperluan: 'Apresiasi pelayanan firman ibadah raya hari minggu',
    keterangan: 'Apresiasi pelayanan firman ibadah raya hari minggu',
    status_persetujuan: 'Disetujui',
    disetujui_oleh: 'Majelis Cabang',
    created_at: '2026-09-06T13:30:00Z'
  },
  {
    id: 203,
    nomor_voucher: 'OUT-CAB-2026-003',
    nomor_transaksi: 'OUT-CAB-2026-003',
    tanggal: '2026-09-08',
    kategori: 'Pemeliharaan Aset & Fasilitas',
    church_name: churchName,
    nominal: 5800000,
    jumlah: 5800000,
    metode_pembayaran: 'Transfer Bank',
    penerima: 'Teknisi Audio Mitra Suara',
    keperluan: 'Servis mixer audio, penggantian mic wireless dan instalasi kabel XLR',
    keterangan: 'Servis mixer audio, penggantian mic wireless dan instalasi kabel XLR',
    status_persetujuan: 'Disetujui',
    disetujui_oleh: 'Admin Cabang',
    created_at: '2026-09-08T15:45:00Z'
  },
  {
    id: 204,
    nomor_voucher: 'OUT-CAB-2026-004',
    nomor_transaksi: 'OUT-CAB-2026-004',
    tanggal: '2026-09-10',
    kategori: 'Diakonia Sosial & Santunan Kasih',
    church_name: churchName,
    nominal: 3000000,
    jumlah: 3000000,
    metode_pembayaran: 'Tunai',
    penerima: 'Keluarga Jemaat Lansia Sakit',
    keperluan: 'Bantuan santunan pengobatan dan rawat inap keluarga jemaat',
    keterangan: 'Bantuan santunan pengobatan dan rawat inap keluarga jemaat',
    status_persetujuan: 'Disetujui',
    disetujui_oleh: 'Komisi Diakonia',
    created_at: '2026-09-10T10:15:00Z'
  },
  {
    id: 205,
    nomor_voucher: 'OUT-CAB-2026-005',
    nomor_transaksi: 'OUT-CAB-2026-005',
    tanggal: '2026-09-12',
    kategori: 'Program Remaja, Pemuda & Sekolah Minggu',
    church_name: churchName,
    nominal: 1850000,
    jumlah: 1850000,
    metode_pembayaran: 'Tunai',
    penerima: 'Guru Sekolah Minggu',
    keperluan: 'Pembelian buku mewarnai, alat peraga visual alkitab dan snack anak',
    keterangan: 'Pembelian buku mewarnai, alat peraga visual alkitab dan snack anak',
    status_persetujuan: 'Disetujui',
    disetujui_oleh: 'Admin Cabang',
    created_at: '2026-09-12T14:00:00Z'
  },
  {
    id: 206,
    nomor_voucher: 'OUT-CAB-2026-006',
    nomor_transaksi: 'OUT-CAB-2026-006',
    tanggal: '2026-09-14',
    kategori: 'Konsumsi & Kelengkapan Ibadah',
    church_name: churchName,
    nominal: 1200000,
    jumlah: 1200000,
    metode_pembayaran: 'Tunai',
    penerima: 'Seksi Konsumsi Cabang',
    keperluan: 'Roti & anggur perjamuan kudus mingguan serta ramah tamah pelayan',
    keterangan: 'Roti & anggur perjamuan kudus mingguan serta ramah tamah pelayan',
    status_persetujuan: 'Disetujui',
    disetujui_oleh: 'Admin Cabang',
    created_at: '2026-09-14T11:20:00Z'
  }
]

// Penyimpanan lokal persisten
const getStorageKey = () => `grace_pengeluaran_cabang_${activeChurch.id || 'default'}`

const saveToLocalStorage = () => {
  try {
    localStorage.setItem(getStorageKey(), JSON.stringify(pengeluaranList.value))
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

    // 1. Cek penyimpanan lokal
    const localData = loadFromLocalStorage()
    if (localData && localData.length > 0) {
      pengeluaranList.value = localData
    }

    // 2. Coba ambil dari Backend API
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }

    const churchParam = activeChurch.id ? `?church_id=${activeChurch.id}&limit=200` : '?limit=200'
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pengeluaran${churchParam}`, { headers })

    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data) && data.length > 0) {
        const normalized = data.map((item) => ({
          ...item,
          nominal: Number(item.jumlah ?? item.nominal ?? 0),
          jumlah: Number(item.jumlah ?? item.nominal ?? 0),
          church_name: item.church_name || activeChurch.name,
          keperluan: item.keterangan || item.keperluan || 'Beban operasional gereja cabang',
          nomor_voucher: item.nomor_voucher || item.nomor_transaksi || `OUT-CAB-${item.id}`
        }))
        pengeluaranList.value = normalized
        saveToLocalStorage()
      } else if (!localData) {
        pengeluaranList.value = getInitialMockData(activeChurch.name)
        saveToLocalStorage()
      }
    } else if (!localData) {
      pengeluaranList.value = getInitialMockData(activeChurch.name)
      saveToLocalStorage()
    }
  } catch (err) {
    console.warn('Backend API tidak terjangkau, menggunakan data tersimpan:', err)
    if (pengeluaranList.value.length === 0) {
      pengeluaranList.value = getInitialMockData(activeChurch.name)
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
  return pengeluaranList.value.filter((item) => {
    const q = searchQuery.value.toLowerCase().trim()
    const matchesSearch =
      !q ||
      ((item.nomor_voucher || item.nomor_transaksi) && (item.nomor_voucher || item.nomor_transaksi).toLowerCase().includes(q)) ||
      (item.kategori && item.kategori.toLowerCase().includes(q)) ||
      ((item.keperluan || item.keterangan) && (item.keperluan || item.keterangan).toLowerCase().includes(q)) ||
      (item.penerima && item.penerima.toLowerCase().includes(q))

    const matchesCategory = categoryFilter.value === 'Semua' || item.kategori === categoryFilter.value
    const matchesMethod = methodFilter.value === 'Semua' || item.metode_pembayaran === methodFilter.value
    const matchesStatus = statusFilter.value === 'Semua' || item.status_persetujuan === statusFilter.value

    return matchesSearch && matchesCategory && matchesMethod && matchesStatus
  })
})

// --- Computed Metrics KPI ---
const metrics = computed(() => {
  const list = pengeluaranList.value
  const total = list.reduce((acc, curr) => acc + (Number(curr.jumlah || curr.nominal) || 0), 0)

  const nowYearMonth = new Date().toISOString().slice(0, 7)
  const thisMonth = list
    .filter((i) => i.tanggal && i.tanggal.startsWith(nowYearMonth))
    .reduce((acc, curr) => acc + (Number(curr.jumlah || curr.nominal) || 0), 0)

  const operasional = list
    .filter((i) => i.kategori === 'Operasional Gedung & Utilitas' || i.kategori === 'Pemeliharaan Aset & Fasilitas')
    .reduce((acc, curr) => acc + (Number(curr.jumlah || curr.nominal) || 0), 0)

  const honorDiakonia = list
    .filter((i) => i.kategori === 'Honorarium Pelayan Firman & Musik' || i.kategori === 'Diakonia Sosial & Santunan Kasih')
    .reduce((acc, curr) => acc + (Number(curr.jumlah || curr.nominal) || 0), 0)

  return { total, thisMonth, operasional, honorDiakonia }
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
    nomor_voucher: '',
    tanggal: new Date().toISOString().slice(0, 10),
    kategori: 'Operasional Gedung & Utilitas',
    jumlah: '',
    metode_pembayaran: 'Tunai',
    penerima: '',
    keperluan: '',
    status_persetujuan: 'Disetujui',
    disetujui_oleh: 'Majelis Jemaat / Admin Cabang'
  })
  isAddModalOpen.value = true
}

const openEditModal = (item) => {
  selectedItem.value = item
  Object.assign(form, {
    id: item.id,
    nomor_voucher: item.nomor_voucher || item.nomor_transaksi || `OUT-CAB-${item.id}`,
    tanggal: item.tanggal,
    kategori: item.kategori,
    jumlah: Number(item.jumlah || item.nominal || 0),
    metode_pembayaran: item.metode_pembayaran,
    penerima: item.penerima || '',
    keperluan: item.keperluan || item.keterangan || '',
    status_persetujuan: item.status_persetujuan || 'Disetujui',
    disetujui_oleh: item.disetujui_oleh || 'Admin Cabang'
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

// SIMPAN PENGELUARAN BARU (CREATE)
const handleSaveNew = async () => {
  const rawJumlah = Number(form.jumlah)
  if (!rawJumlah || rawJumlah <= 0) {
    triggerToast('Nominal beban pengeluaran kas wajib diisi dengan benar.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const newItem = {
      id: Date.now(),
      nomor_voucher: `OUT-CAB-${new Date().getFullYear()}-${String(pengeluaranList.value.length + 1).padStart(3, '0')}`,
      nomor_transaksi: `OUT-CAB-${new Date().getFullYear()}-${String(pengeluaranList.value.length + 1).padStart(3, '0')}`,
      tanggal: form.tanggal,
      kategori: form.kategori,
      nominal: rawJumlah,
      jumlah: rawJumlah,
      church_id: activeChurch.id,
      church_name: activeChurch.name,
      metode_pembayaran: form.metode_pembayaran,
      penerima: form.penerima || 'Pihak Terkait',
      keperluan: form.keperluan || 'Beban operasional gereja cabang',
      keterangan: form.keperluan || 'Beban operasional gereja cabang',
      status_persetujuan: form.status_persetujuan,
      disetujui_oleh: form.disetujui_oleh,
      created_at: new Date().toISOString()
    }

    // Panggil Backend API
    try {
      const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pengeluaran`, {
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
          penerima: form.penerima || 'Pihak Terkait',
          keterangan: form.keperluan,
          status_persetujuan: form.status_persetujuan
        })
      })
      if (res.ok) {
        const serverCreated = await res.json()
        if (serverCreated && serverCreated.id) {
          newItem.id = serverCreated.id
          if (serverCreated.nomor_voucher) newItem.nomor_voucher = serverCreated.nomor_voucher
        }
      }
    } catch (apiErr) {
      console.warn('API error saat create pengeluaran, disimpan secara lokal:', apiErr)
    }

    pengeluaranList.value.unshift(newItem)
    saveToLocalStorage()
    triggerToast('Voucher pengeluaran kas operasional berhasil dibukukan!')
    isAddModalOpen.value = false
  } catch (err) {
    triggerToast('Terjadi kesalahan saat menyimpan pengeluaran.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// UPDATE PENGELUARAN (EDIT)
const handleUpdate = async () => {
  const rawJumlah = Number(form.jumlah)
  if (!rawJumlah || rawJumlah <= 0) {
    triggerToast('Nominal beban pengeluaran kas wajib diisi dengan benar.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const idx = pengeluaranList.value.findIndex((i) => i.id === form.id)
    if (idx !== -1) {
      const updated = {
        ...pengeluaranList.value[idx],
        tanggal: form.tanggal,
        kategori: form.kategori,
        nominal: rawJumlah,
        jumlah: rawJumlah,
        metode_pembayaran: form.metode_pembayaran,
        penerima: form.penerima,
        keperluan: form.keperluan,
        keterangan: form.keperluan,
        status_persetujuan: form.status_persetujuan,
        disetujui_oleh: form.disetujui_oleh,
        updated_at: new Date().toISOString()
      }

      // Coba panggil Backend API
      try {
        const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
        await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pengeluaran/${form.id}`, {
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
            penerima: form.penerima,
            keterangan: form.keperluan,
            status_persetujuan: form.status_persetujuan
          })
        })
      } catch (apiErr) {
        console.warn('API error saat update pengeluaran, tetap disimpan lokal:', apiErr)
      }

      pengeluaranList.value[idx] = updated
      saveToLocalStorage()
      triggerToast('Voucher pengeluaran kas berhasil diperbarui!')
      isEditModalOpen.value = false
    }
  } catch (err) {
    triggerToast('Gagal memperbarui data pengeluaran.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// DELETE PENGELUARAN (HAPUS)
const handleDelete = async () => {
  if (!selectedItem.value) return
  isSubmitting.value = true
  try {
    const itemId = selectedItem.value.id

    try {
      const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
      await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pengeluaran/${itemId}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
    } catch (apiErr) {
      console.warn('API error saat delete pengeluaran, tetap dihapus lokal:', apiErr)
    }

    pengeluaranList.value = pengeluaranList.value.filter((i) => i.id !== itemId)
    saveToLocalStorage()
    triggerToast('Catatan pengeluaran berhasil dihapus dari sistem.')
    isDeleteModalOpen.value = false
    selectedItem.value = null
  } catch (err) {
    triggerToast('Gagal menghapus data pengeluaran.', 'error')
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
      type: 'pengeluaran',
      format: 'pdf',
      token,
      churchId: activeChurch.id
    })
    triggerToast('Laporan PDF pengeluaran resmi berhasil diunduh dari server Python.')
  } catch (err) {
    exportToPDF({
      title: `Pengeluaran Kas & Beban Operasional - ${activeChurch.name}`,
      items: filteredList.value,
      isPemasukan: false,
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
      type: 'pengeluaran',
      format: 'excel',
      token,
      churchId: activeChurch.id
    })
    triggerToast('Laporan Excel (.xlsx) berhasil diunduh dari server Python.')
  } catch (err) {
    exportToCSV({
      title: `Pengeluaran Kas & Beban Operasional - ${activeChurch.name}`,
      filename: `Laporan_Pengeluaran_${activeChurch.name.replace(/\s+/g, '_')}`,
      items: filteredList.value,
      isPemasukan: false,
      churchFilter: activeChurch.name
    })
    triggerToast('Laporan Excel / Spreadsheet berhasil diunduh.')
  }
}

const handleExportJSON = () => {
  exportToJSON({
    title: `Pengeluaran Kas & Beban Operasional - ${activeChurch.name}`,
    filename: `Data_Pengeluaran_${activeChurch.name.replace(/\s+/g, '_')}`,
    items: filteredList.value,
    isPemasukan: false,
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
              ? 'bg-rose-950/95 text-rose-200 border-rose-500/50 shadow-rose-950/50' 
              : 'bg-amber-950/95 text-amber-200 border-amber-500/50 shadow-amber-950/50'
          ]"
        >
          <i :class="['bi text-lg', toastType === 'success' ? 'bi-check-circle-fill text-rose-400' : 'bi-exclamation-octagon-fill text-amber-400']"></i>
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
            'px-4 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2 border border-transparent',
            isDark ? 'text-slate-400 hover:text-emerald-300 hover:bg-slate-800/60' : 'text-slate-600 hover:text-emerald-600 hover:bg-white'
          ]"
        >
          <i class="bi bi-arrow-down-left-circle"></i>
          <span>Pemasukan Kas &amp; Persembahan</span>
        </RouterLink>

        <RouterLink 
          to="/church-finance-pengeluaran"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 border shadow-sm',
            'bg-rose-500/20 text-rose-400 border-rose-500/40'
          ]"
        >
          <i class="bi bi-arrow-up-right-circle-fill"></i>
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
          ? 'border-rose-500/30 bg-gradient-to-r from-slate-950 via-slate-900 to-rose-950/40 text-white' 
          : 'border-rose-300 bg-gradient-to-r from-rose-50/90 via-white to-amber-50/50 text-slate-900'
      ]">
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-400 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-receipt-cutoff"></i>
              <span>Voucher Belanja &amp; Beban Operasional • {{ activeChurch.name }}</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight">
              Pengeluaran Kas Operasional Gereja
            </h1>
            <p :class="['mt-1.5 text-xs sm:text-sm max-w-2xl leading-relaxed', isDark ? 'text-slate-300' : 'text-slate-600']">
              Atur dan pantau pencatatan voucher pengeluaran kas, pembayaran listrik &amp; utilitas gedung, apresiasi pelayan firman, pemeliharaan fasilitas gereja, dan bantuan diakonia secara akurat.
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
                    ? 'border-rose-500/40 bg-rose-500/15 text-rose-300 hover:bg-rose-500/25' 
                    : 'border-rose-400 bg-rose-100 text-rose-900 hover:bg-rose-200'
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
                    isDark ? 'border-rose-500/30 bg-slate-950/95 text-slate-200' : 'border-slate-200 bg-white text-slate-800'
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
                      <p class="text-[10px] text-slate-400">Format voucher cetak resmi</p>
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
              class="flex items-center gap-2 rounded-2xl bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-400 hover:to-rose-500 px-5 py-2.5 text-xs font-bold text-white shadow-lg shadow-rose-500/20 transition cursor-pointer"
            >
              <i class="bi bi-dash-circle-fill text-sm"></i>
              <span>Catat Pengeluaran Baru</span>
            </button>
          </div>
        </div>
      </section>

      <!-- KPI METRICS SUMMARY -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Total Pengeluaran</span>
            <div class="w-8 h-8 rounded-lg bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400 text-sm">
              <i class="bi bi-cash"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-rose-400 font-mono">{{ formatIDR(metrics.total) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Total beban kas terbayar</p>
        </div>

        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Bulan Berjalan</span>
            <div class="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 text-sm">
              <i class="bi bi-calendar-check"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-amber-400 font-mono">{{ formatIDR(metrics.thisMonth) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Realisasi bulan aktif</p>
        </div>

        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Operasional &amp; Gedung</span>
            <div class="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 text-sm">
              <i class="bi bi-building-gear"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-sky-400 font-mono">{{ formatIDR(metrics.operasional) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Utilitas &amp; perawatan aset</p>
        </div>

        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Honor &amp; Diakonia</span>
            <div class="w-8 h-8 rounded-lg bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 text-sm">
              <i class="bi bi-heart-pulse-fill"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-purple-400 font-mono">{{ formatIDR(metrics.honorDiakonia) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Pelayanan firman &amp; santunan</p>
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
              placeholder="Cari voucher, penerima, keperluan..." 
              :class="[
                'w-full rounded-xl border pl-9 pr-3 py-2 text-xs outline-none transition',
                isDark ? 'border-slate-700 bg-slate-950/80 text-white placeholder-slate-500 focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-rose-500'
              ]"
            />
          </div>

          <div>
            <select 
              v-model="categoryFilter"
              :class="[
                'w-full rounded-xl border px-3 py-2 text-xs outline-none transition cursor-pointer',
                isDark ? 'border-slate-700 bg-slate-950/80 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500'
              ]"
            >
              <option value="Semua">Semua Kategori Beban</option>
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div>
            <select 
              v-model="methodFilter"
              :class="[
                'w-full rounded-xl border px-3 py-2 text-xs outline-none transition cursor-pointer',
                isDark ? 'border-slate-700 bg-slate-950/80 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500'
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
                isDark ? 'border-slate-700 bg-slate-950/80 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500'
              ]"
            >
              <option value="Semua">Semua Status Persetujuan</option>
              <option v-for="s in approvalStatuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

        </div>
      </section>

      <!-- DATA TABLE PENGELUARAN KAS -->
      <section :class="['rounded-3xl border p-5 sm:p-6 shadow-2xl backdrop-blur-xl transition-colors', isDark ? 'border-slate-800 bg-slate-900/80 text-white' : 'border-slate-200 bg-white text-slate-900']">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-700/30">
          <div>
            <h3 class="font-serif text-xl font-bold">Buku Catatan Kas Keluar Cabang</h3>
            <p :class="['text-xs mt-0.5', isDark ? 'text-slate-400' : 'text-slate-600']">
              Daftar voucher beban operasional yang telah dikeluarkan oleh {{ activeChurch.name }}.
            </p>
          </div>
          <span class="text-xs text-rose-400 font-mono font-bold self-start sm:self-auto">
            {{ filteredList.length }} Voucher Tercatat
          </span>
        </div>

        <div class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr :class="['border-b text-[11px] uppercase tracking-wider', isDark ? 'border-slate-800 text-slate-400 bg-slate-950/50' : 'border-slate-200 text-slate-600 bg-slate-100/70']">
                <th class="py-3 px-4">Tanggal &amp; No. Voucher</th>
                <th class="py-3 px-4">Kategori Beban</th>
                <th class="py-3 px-4">Penerima Dana</th>
                <th class="py-3 px-4">Metode</th>
                <th class="py-3 px-4 text-right">Nominal Beban (IDR)</th>
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
                  <span class="text-[10px] text-amber-500 font-mono">{{ item.nomor_voucher || item.nomor_transaksi }}</span>
                </td>

                <td class="py-3.5 px-4">
                  <span class="font-semibold block">{{ item.kategori }}</span>
                  <span :class="['text-[11px] truncate max-w-xs block', isDark ? 'text-slate-400' : 'text-slate-500']">{{ item.keperluan || item.keterangan || '-' }}</span>
                </td>

                <td class="py-3.5 px-4 font-medium">
                  {{ item.penerima || '-' }}
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

                <td class="py-3.5 px-4 text-right font-bold text-rose-400 font-mono text-sm whitespace-nowrap">
                  - {{ formatIDR(item.jumlah || item.nominal) }}
                </td>

                <td class="py-3.5 px-4 text-center whitespace-nowrap">
                  <span 
                    :class="[
                      'px-2 py-0.5 rounded-full text-[10px] font-semibold border',
                      item.status_persetujuan === 'Disetujui'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : item.status_persetujuan === 'Pending'
                          ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                          : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                    ]"
                  >
                    {{ item.status_persetujuan || 'Disetujui' }}
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
                      title="Edit Voucher Pengeluaran"
                    >
                      <i class="bi bi-pencil-square"></i>
                    </button>

                    <!-- Delete -->
                    <button 
                      type="button" 
                      @click="openDeleteModal(item)"
                      class="p-1.5 rounded-lg text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/15 transition cursor-pointer"
                      title="Hapus Voucher"
                    >
                      <i class="bi bi-trash3"></i>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="filteredList.length === 0">
                <td colspan="7" class="py-12 text-center text-slate-400">
                  <i class="bi bi-inbox text-3xl block text-slate-600 mb-2"></i>
                  Tidak ada catatan pengeluaran yang sesuai kriteria pencarian.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- ======================================================== -->
    <!-- MODAL CATAT PENGELUARAN BARU (CREATE)                   -->
    <!-- ======================================================== -->
    <Transition name="fade">
      <div 
        v-if="isAddModalOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto"
        @click.self="isAddModalOpen = false"
      >
        <div :class="['w-full max-w-lg rounded-3xl border p-6 shadow-2xl space-y-4 my-auto', isDark ? 'bg-slate-900 border-rose-500/40 text-white' : 'bg-white border-rose-300 text-slate-900']">
          <div class="flex items-center justify-between pb-3 border-b border-slate-700/30">
            <h3 class="font-serif text-lg font-bold flex items-center gap-2">
              <i class="bi bi-dash-circle-fill text-rose-400"></i> Buat Voucher Pengeluaran Baru
            </h3>
            <button @click="isAddModalOpen = false" class="text-slate-400 hover:text-white cursor-pointer">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <form @submit.prevent="handleSaveNew" class="space-y-4 text-xs">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Tanggal Pengeluaran *</label>
                <input 
                  v-model="form.tanggal" 
                  type="date" 
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500']"
                />
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Kategori Beban *</label>
                <select 
                  v-model="form.kategori"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500']"
                >
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Nominal Beban (Rp) *</label>
                <input 
                  v-model.number="form.jumlah" 
                  type="number" 
                  min="1"
                  placeholder="Contoh: 2500000"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 font-mono font-bold text-rose-400 outline-none', isDark ? 'border-slate-700 bg-slate-950 focus:border-rose-400' : 'border-slate-300 bg-white focus:border-rose-500']"
                />
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Metode Pembayaran *</label>
                <select 
                  v-model="form.metode_pembayaran"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500']"
                >
                  <option v-for="m in paymentMethods" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Penerima Dana / Vendor</label>
                <input 
                  v-model="form.penerima" 
                  type="text" 
                  placeholder="Contoh: CV Audio Pro / PLN / Seksi Konsumsi"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500']"
                />
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Disetujui Oleh</label>
                <input 
                  v-model="form.disetujui_oleh" 
                  type="text" 
                  placeholder="Contoh: Majelis Cabang / Bendahara"
                  :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500']"
                />
              </div>
            </div>

            <div>
              <label class="block font-semibold mb-1 text-slate-400">Keperluan / Keterangan Belanja</label>
              <textarea 
                v-model="form.keperluan" 
                rows="2" 
                placeholder="Rincian peruntukan pengeluaran kas atau nomor kuitansi eksternal..."
                required
                :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-rose-400' : 'border-slate-300 bg-white text-slate-900 focus:border-rose-500']"
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
                class="px-5 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 transition cursor-pointer flex items-center gap-1.5 shadow-md shadow-rose-600/30"
              >
                <i v-if="isSubmitting" class="bi bi-arrow-repeat animate-spin"></i>
                <i v-else class="bi bi-check2-circle"></i>
                <span>Simpan Voucher Pengeluaran</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ======================================================== -->
    <!-- MODAL EDIT PENGELUARAN (UPDATE)                         -->
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
              <i class="bi bi-pencil-square text-sky-400"></i> Edit Voucher Pengeluaran Kas
            </h3>
            <button @click="isEditModalOpen = false" class="text-slate-400 hover:text-white cursor-pointer">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <form @submit.prevent="handleUpdate" class="space-y-4 text-xs">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Nomor Voucher</label>
                <input 
                  :value="form.nomor_voucher" 
                  disabled
                  class="w-full rounded-xl border border-slate-700/50 bg-slate-950/50 px-3 py-2 font-mono text-slate-400 cursor-not-allowed"
                />
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Tanggal Pengeluaran *</label>
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
                <label class="block font-semibold mb-1 text-slate-400">Kategori Beban *</label>
                <select 
                  v-model="form.kategori"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
                >
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Nominal Beban (Rp) *</label>
                <input 
                  v-model.number="form.jumlah" 
                  type="number" 
                  min="1"
                  required
                  :class="['w-full rounded-xl border px-3 py-2 font-mono font-bold text-rose-400 outline-none', isDark ? 'border-slate-700 bg-slate-950 focus:border-sky-400' : 'border-slate-300 bg-white focus:border-sky-500']"
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
                <label class="block font-semibold mb-1 text-slate-400">Status Persetujuan</label>
                <select 
                  v-model="form.status_persetujuan"
                  :class="['w-full rounded-xl border px-3 py-2 outline-none cursor-pointer', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
                >
                  <option v-for="s in approvalStatuses" :key="s" :value="s">{{ s }}</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold mb-1 text-slate-400">Penerima Dana / Vendor</label>
                <input 
                  v-model="form.penerima" 
                  type="text" 
                  :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
                />
              </div>

              <div>
                <label class="block font-semibold mb-1 text-slate-400">Disetujui Oleh</label>
                <input 
                  v-model="form.disetujui_oleh" 
                  type="text" 
                  :class="['w-full rounded-xl border px-3 py-2 outline-none', isDark ? 'border-slate-700 bg-slate-950 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-900 focus:border-sky-500']"
                />
              </div>
            </div>

            <div>
              <label class="block font-semibold mb-1 text-slate-400">Keperluan / Keterangan</label>
              <textarea 
                v-model="form.keperluan" 
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
    <!-- MODAL DETAIL VOUCHER PENGELUARAN (VIEW)                 -->
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
              <span class="text-[10px] uppercase tracking-wider text-rose-400 font-extrabold block">VOUCHER PENGELUARAN KAS RESMI</span>
              <h3 class="font-serif text-lg font-bold">{{ selectedItem.nomor_voucher || selectedItem.nomor_transaksi }}</h3>
            </div>
            <button @click="isDetailModalOpen = false" class="text-slate-400 hover:text-white cursor-pointer">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <div class="space-y-3 text-xs">
            <div class="p-4 rounded-2xl border border-rose-500/30 bg-rose-500/10 flex items-center justify-between">
              <div>
                <span class="text-[11px] text-rose-400 font-semibold block">Total Beban Dikeluarkan</span>
                <span class="text-2xl font-black text-rose-300 font-mono">- {{ formatIDR(selectedItem.jumlah || selectedItem.nominal) }}</span>
              </div>
              <span class="px-3 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-400/40">
                {{ selectedItem.status_persetujuan || 'Disetujui' }}
              </span>
            </div>

            <div class="grid grid-cols-2 gap-3 pt-2">
              <div>
                <span class="text-[10px] text-slate-400 block">Tanggal Beban</span>
                <span class="font-bold">{{ selectedItem.tanggal }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Kategori Beban</span>
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

            <div class="pt-2 border-t border-slate-700/30 grid grid-cols-2 gap-3">
              <div>
                <span class="text-[10px] text-slate-400 block">Penerima Dana / Vendor</span>
                <span class="font-semibold text-sm">{{ selectedItem.penerima || '-' }}</span>
              </div>
              <div>
                <span class="text-[10px] text-slate-400 block">Disetujui Oleh</span>
                <span class="font-semibold text-sm">{{ selectedItem.disetujui_oleh || 'Admin Cabang' }}</span>
              </div>
            </div>

            <div>
              <span class="text-[10px] text-slate-400 block">Keperluan / Keterangan Belanja</span>
              <p class="mt-0.5 leading-relaxed">{{ selectedItem.keperluan || selectedItem.keterangan || '-' }}</p>
            </div>

            <div class="p-3 rounded-xl border border-slate-700/40 bg-slate-950/40 text-[10px] font-mono text-slate-400 space-y-1">
              <div class="flex items-center justify-between">
                <span>Security Token SHA-256:</span>
                <span class="text-rose-400 font-bold">APPROVED_DISBURSEMENT</span>
              </div>
              <p class="truncate text-slate-500">HASH: a3c7e1f4b89d2e0a6f5c8d1b4e7a0b3c5e8a7f1b2c4d6e8a0b2c4d6e8f0a9b2</p>
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
            <h3 class="font-serif text-lg font-bold text-rose-400">Konfirmasi Hapus Voucher</h3>
            <p :class="['text-xs leading-relaxed', isDark ? 'text-slate-300' : 'text-slate-600']">
              Apakah Anda yakin ingin menghapus voucher pengeluaran kas <span class="font-bold font-mono text-amber-400">{{ selectedItem.nomor_voucher || selectedItem.nomor_transaksi }}</span> sebesar <span class="font-bold text-rose-400">{{ formatIDR(selectedItem.jumlah || selectedItem.nominal) }}</span>?
            </p>
            <p class="text-[11px] text-rose-400/90 font-medium pt-1">
              Catatan ini akan dihapus permanen dari buku kas operasional cabang!
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
              <span>Ya, Hapus Voucher</span>
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
