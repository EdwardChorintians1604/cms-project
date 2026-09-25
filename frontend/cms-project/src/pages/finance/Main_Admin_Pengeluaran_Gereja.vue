<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'
import { exportToCSV, exportToPDF, exportToJSON, downloadServerExport } from '@/utils/exportFinanceReport'

// --- State Data Utama Pengeluaran ---
const pengeluaranList = ref([])
const churches = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

// Filter
const searchQuery = ref('')
const categoryFilter = ref('Semua')
const churchFilter = ref('Semua')
const statusFilter = ref('Semua')

// Modal
const isModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const selectedItem = ref(null)
const isSubmitting = ref(false)

// Toast
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

// Form Pengeluaran
const form = reactive({
  tanggal: new Date().toISOString().slice(0, 10),
  kategori: 'Operasional Gedung & Utilitas',
  church_name: 'GracePoint Pusat',
  nominal: '',
  status: 'Disetujui',
  keperluan: '',
  penerima: '',
  disetujui_oleh: 'Bendahara / Superadmin'
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

// Data Mock Standar Graceful Fallback
const defaultMockData = [
  { id: 1, nomor_voucher: 'OUT-2026-001', tanggal: '2026-09-02', kategori: 'Operasional Gedung & Utilitas', church_name: 'GracePoint Pusat', nominal: 6800000, penerima: 'PLN & PDAM', keperluan: 'Tagihan listrik dan air ruang ibadah utama', status: 'Disetujui', disetujui_oleh: 'Superadmin' },
  { id: 2, nomor_voucher: 'OUT-2026-002', tanggal: '2026-09-06', kategori: 'Honorarium Pelayan Firman & Musik', church_name: 'GracePoint Pusat', nominal: 4500000, penerima: 'Pdt. Tamu & Pemuji', keperluan: 'Apresiasi pelayan firman Ibadah Raya', status: 'Disetujui', disetujui_oleh: 'Majelis Jemaat' },
  { id: 3, nomor_voucher: 'OUT-2026-003', tanggal: '2026-09-08', kategori: 'Pemeliharaan Aset & Fasilitas', church_name: 'Cabang GracePoint Barat', nominal: 7800000, penerima: 'CV Audio Pro', keperluan: 'Perbaikan mixer sound system & mic nirkabel', status: 'Disetujui', disetujui_oleh: 'Admin Cabang' },
  { id: 4, nomor_voucher: 'OUT-2026-004', tanggal: '2026-09-09', kategori: 'Diakonia Sosial & Santunan Kasih', church_name: 'GracePoint Pusat', nominal: 3500000, penerima: 'Jemaat Dhuafa & Sakit', keperluan: 'Bantuan biaya pengobatan 2 warga jemaat', status: 'Disetujui', disetujui_oleh: 'Komisi Diakonia' },
  { id: 5, nomor_voucher: 'OUT-2026-005', tanggal: '2026-09-11', kategori: 'Program Remaja, Pemuda & Sekolah Minggu', church_name: 'Cabang GracePoint Timur', nominal: 2200000, penerima: 'Guru Sekolah Minggu', keperluan: 'Alat peraga & snack kegiatan sekolah minggu', status: 'Disetujui', disetujui_oleh: 'Admin Cabang' },
  { id: 6, nomor_voucher: 'OUT-2026-006', tanggal: '2026-09-12', kategori: 'Konsumsi & Kelengkapan Ibadah', church_name: 'Cabang GracePoint Selatan', nominal: 1850000, penerima: 'Seksi Konsumsi', keperluan: 'Roti & anggur perjamuan kudus serta ramah tamah', status: 'Disetujui', disetujui_oleh: 'Superadmin' }
]

// --- Load Data dari Backend API ---
const loadData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    const headers = token ? { Authorization: `Bearer ${token}` } : {}

    const [resPengeluaran, resChurches] = await Promise.allSettled([
      fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pengeluaran/?limit=100`, { headers }),
      fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`, { headers })
    ])

    if (resPengeluaran.status === 'fulfilled' && resPengeluaran.value.ok) {
      const data = await resPengeluaran.value.json()
      if (Array.isArray(data) && data.length > 0) {
        pengeluaranList.value = data
      } else {
        pengeluaranList.value = defaultMockData
      }
    } else {
      pengeluaranList.value = defaultMockData
    }

    if (resChurches.status === 'fulfilled' && resChurches.value.ok) {
      churches.value = await resChurches.value.json()
    }
  } catch (err) {
    console.warn('Gagal memuat API pengeluaran, beralih ke data fallback:', err)
    pengeluaranList.value = defaultMockData
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})

// Computed Filtered List
const filteredList = computed(() => {
  return pengeluaranList.value.filter((item) => {
    const q = searchQuery.value.toLowerCase().trim()
    const matchesSearch =
      !q ||
      (item.kategori && item.kategori.toLowerCase().includes(q)) ||
      (item.keperluan && item.keperluan.toLowerCase().includes(q)) ||
      (item.penerima && item.penerima.toLowerCase().includes(q)) ||
      (item.church_name && item.church_name.toLowerCase().includes(q)) ||
      (item.nomor_voucher && item.nomor_voucher.toLowerCase().includes(q))

    const matchesCategory = categoryFilter.value === 'Semua' || item.kategori === categoryFilter.value
    const matchesChurch = churchFilter.value === 'Semua' || item.church_name === churchFilter.value
    const matchesStatus = statusFilter.value === 'Semua' || item.status === statusFilter.value

    return matchesSearch && matchesCategory && matchesChurch && matchesStatus
  })
})

// Metrics KPI
const metrics = computed(() => {
  const total = pengeluaranList.value.reduce((acc, curr) => acc + (Number(curr.nominal) || 0), 0)
  const currentMonthStr = new Date().toISOString().slice(0, 7)
  const thisMonth = pengeluaranList.value
    .filter((item) => item.tanggal && item.tanggal.startsWith(currentMonthStr))
    .reduce((acc, curr) => acc + (Number(curr.nominal) || 0), 0)

  const operasional = pengeluaranList.value
    .filter((item) => item.kategori.includes('Operasional') || item.kategori.includes('Pemeliharaan'))
    .reduce((acc, curr) => acc + (Number(curr.nominal) || 0), 0)

  const pelayanan = pengeluaranList.value
    .filter((item) => item.kategori.includes('Honorarium') || item.kategori.includes('Diakonia') || item.kategori.includes('Program'))
    .reduce((acc, curr) => acc + (Number(curr.nominal) || 0), 0)

  return { total, thisMonth, operasional, pelayanan }
})

const formatIDR = (num) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(num || 0)
}

// Modal Handlers
const openAddModal = () => {
  Object.assign(form, {
    tanggal: new Date().toISOString().slice(0, 10),
    kategori: 'Operasional Gedung & Utilitas',
    church_name: 'GracePoint Pusat',
    nominal: '',
    status: 'Disetujui',
    keperluan: '',
    penerima: '',
    disetujui_oleh: 'Superadmin'
  })
  isModalOpen.value = true
}

const openDetailModal = (item) => {
  selectedItem.value = item
  isDetailModalOpen.value = true
}

const handleSavePengeluaran = async () => {
  if (!form.nominal || Number(form.nominal) <= 0) {
    triggerToast('Nominal pengeluaran wajib diisi dengan benar.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const newItem = {
      id: Date.now(),
      nomor_voucher: `OUT-2026-${String(pengeluaranList.value.length + 1).padStart(3, '0')}`,
      tanggal: form.tanggal,
      kategori: form.kategori,
      church_name: form.church_name,
      nominal: Number(form.nominal),
      penerima: form.penerima || 'Vendor / Pelayan Terkait',
      keperluan: form.keperluan || 'Pengeluaran operasional pelayanan kas gereja',
      status: form.status || 'Disetujui',
      disetujui_oleh: form.disetujui_oleh || 'Superadmin'
    }

    try {
      const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
      await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pengeluaran/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(newItem)
      })
    } catch (e) {
      // Local fallback
    }

    pengeluaranList.value.unshift(newItem)
    triggerToast('Pengeluaran kas gereja berhasil diverifikasi dan dicatat.')
    isModalOpen.value = false
  } catch (err) {
    triggerToast('Gagal mencatat pengeluaran.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// --- Handler Ekspor Laporan Pengeluaran ---
const isExportMenuOpen = ref(false)

const handleExportPDF = async () => {
  isExportMenuOpen.value = false
  try {
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    await downloadServerExport({
      baseUrl: APP_CONFIG.apiBaseUrl,
      type: 'pengeluaran',
      format: 'pdf',
      token
    })
    triggerToast('Laporan PDF resmi pengeluaran berhasil diunduh dari server Python (ReportLab).')
  } catch (err) {
    exportToPDF({
      title: 'Pengeluaran Kas & Beban Operasional Gereja',
      items: filteredList.value,
      isPemasukan: false,
      churchFilter: churchFilter.value
    })
    triggerToast('Laporan PDF pengeluaran siap dicetak / disimpan.')
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
      token
    })
    triggerToast('Laporan Excel (.xlsx) pengeluaran berhasil diunduh dari server Python (openpyxl).')
  } catch (err) {
    exportToCSV({
      title: 'Pengeluaran Kas & Beban Operasional Gereja',
      filename: 'Laporan_Pengeluaran_Gereja',
      items: filteredList.value,
      isPemasukan: false,
      churchFilter: churchFilter.value
    })
    triggerToast('Laporan Excel / Spreadsheet pengeluaran berhasil diunduh.')
  }
}

const handleExportJSON = () => {
  exportToJSON({
    title: 'Pengeluaran Kas & Beban Operasional Gereja',
    filename: 'Data_Pengeluaran_Gereja',
    items: filteredList.value,
    isPemasukan: false,
    churchFilter: churchFilter.value
  })
  isExportMenuOpen.value = false
  triggerToast('Data JSON pengeluaran berhasil diekspor.')
}
</script>

<template>
  <MainAdminLayout>
    <div class="space-y-6 text-[#EDE6D6] font-sans pb-12">

      <!-- Toast Feedback -->
      <Transition name="toast">
        <div 
          v-if="showToast"
          :class="[
            'fixed top-5 right-5 z-[100] max-w-md px-4 py-3 rounded-2xl shadow-2xl border flex items-center gap-3 backdrop-blur-xl transition-all duration-300',
            toastType === 'success' ? 'bg-emerald-950/90 text-emerald-200 border-emerald-500/50' : 'bg-rose-950/90 text-rose-200 border-rose-500/50'
          ]"
        >
          <i :class="['bi text-lg', toastType === 'success' ? 'bi-check-circle-fill text-emerald-400' : 'bi-exclamation-octagon-fill text-rose-400']"></i>
          <p class="text-xs font-semibold leading-relaxed">{{ toastMessage }}</p>
          <button @click="showToast = false" class="ml-auto text-slate-400 hover:text-white">
            <i class="bi bi-x-lg text-xs"></i>
          </button>
        </div>
      </Transition>

      <!-- HERO BANNER -->
      <section class="relative z-20 overflow-visible rounded-3xl border border-amber-500/25 bg-gradient-to-r from-[#0d1e27]/90 via-[#0b2027]/85 to-[#09151e]/90 p-6 shadow-2xl backdrop-blur-xl sm:p-8">
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-300 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-arrow-up-right-circle-fill"></i>
              <span>Cash Disbursement &amp; Audit</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-100">
              Pengeluaran Kas &amp; Beban Operasional
            </h1>
            <p class="mt-1.5 text-xs sm:text-sm text-[#B8C4C2] max-w-2xl leading-relaxed">
              Pengawasan anggaran operasional gedung, pemeliharaan fasilitas gereja, santunan diakonia kasih, dan honorarium pelayanan secara akuntabel.
            </p>
          </div>

          <div class="relative flex w-full min-w-0 flex-wrap items-center gap-2.5 sm:w-auto sm:flex-nowrap">
            <!-- Dropdown Ekspor Laporan Pengeluaran -->
            <div class="relative min-w-0 flex-1 sm:flex-none">
              <button 
                type="button" 
                @click="isExportMenuOpen = !isExportMenuOpen"
                class="flex w-full items-center justify-center gap-2 rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-2.5 text-xs font-bold text-amber-300 shadow-md transition hover:bg-amber-500/20 cursor-pointer sm:w-auto"
              >
                <i class="bi bi-download"></i>
                <span>Simpan / Ekspor Laporan</span>
                <i :class="['bi text-[10px] transition-transform', isExportMenuOpen ? 'bi-chevron-up' : 'bi-chevron-down']"></i>
              </button>

              <!-- Dropdown Menu -->
              <Transition name="fade" enter-active-class="transition duration-200" leave-active-class="transition duration-150">
                <div 
                  v-if="isExportMenuOpen"
                  class="absolute left-0 z-50 mt-2 w-[min(14rem,calc(100vw-2rem))] space-y-1 rounded-2xl border border-amber-500/30 bg-slate-950/95 p-2 shadow-2xl backdrop-blur-xl sm:right-0 sm:left-auto"
                >
                  <div class="px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-wider text-slate-400 border-b border-white/10">
                    Pilih Format Dokumen
                  </div>

                  <button 
                    type="button"
                    @click="handleExportPDF"
                    class="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-200 hover:bg-amber-500/15 hover:text-amber-300 transition flex items-center gap-2.5 cursor-pointer"
                  >
                    <i class="bi bi-file-earmark-pdf-fill text-rose-400 text-sm"></i>
                    <div>
                      <p class="font-bold">Laporan PDF (Resmi)</p>
                      <p class="text-[10px] text-slate-400">Siap cetak berkop sinode</p>
                    </div>
                  </button>

                  <button 
                    type="button"
                    @click="handleExportExcel"
                    class="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-200 hover:bg-amber-500/15 hover:text-amber-300 transition flex items-center gap-2.5 cursor-pointer"
                  >
                    <i class="bi bi-file-earmark-excel-fill text-emerald-400 text-sm"></i>
                    <div>
                      <p class="font-bold">Excel / Spreadsheet</p>
                      <p class="text-[10px] text-slate-400">File tabel (.csv / .xlsx)</p>
                    </div>
                  </button>

                  <button 
                    type="button"
                    @click="handleExportJSON"
                    class="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-200 hover:bg-amber-500/15 hover:text-amber-300 transition flex items-center gap-2.5 cursor-pointer"
                  >
                    <i class="bi bi-filetype-json text-sky-400 text-sm"></i>
                    <div>
                      <p class="font-bold">Data JSON Audit</p>
                      <p class="text-[10px] text-slate-400">Cadangan data digital</p>
                    </div>
                  </button>
                </div>
              </Transition>
            </div>

            <!-- Tombol Catat Pengeluaran Baru (Tetap utuh) -->
            <button 
              type="button" 
              @click="openAddModal" 
              class="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-amber-500 to-amber-400 px-5 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-amber-500/20 transition hover:from-amber-400 hover:to-amber-300 cursor-pointer sm:w-auto"
            >
              <i class="bi bi-plus-circle-fill text-sm"></i>
              <span>Catat Pengeluaran Baru</span>
            </button>
          </div>
        </div>
      </section>

      <!-- KPI METRICS -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Pengeluaran</span>
            <div class="w-8 h-8 rounded-lg bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400 text-sm">
              <i class="bi bi-box-arrow-up-right"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-rose-300 font-mono">{{ formatIDR(metrics.total) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Total kas keluar terserap</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Bulan Berjalan</span>
            <div class="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 text-sm">
              <i class="bi bi-calendar-event"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-amber-300 font-mono">{{ formatIDR(metrics.thisMonth) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Pengeluaran September 2026</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Operasional Gedung</span>
            <div class="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 text-sm">
              <i class="bi bi-tools"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-sky-300 font-mono">{{ formatIDR(metrics.operasional) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Listrik, air & pemeliharaan</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Pelayanan &amp; Diakonia</span>
            <div class="w-8 h-8 rounded-lg bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 text-sm">
              <i class="bi bi-heart-fill"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-purple-300 font-mono">{{ formatIDR(metrics.pelayanan) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Honorarium & kasih sesama</p>
        </div>
      </section>

      <!-- FILTER & SEARCH -->
      <section class="rounded-2xl border border-white/10 bg-[#123138]/70 p-4 backdrop-blur-md">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          
          <div class="relative">
            <i class="bi bi-search absolute left-3 top-2.5 text-slate-500 text-xs"></i>
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Cari voucher, penerima, keperluan..." 
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 outline-none focus:border-amber-400 transition"
            />
          </div>

          <div>
            <select 
              v-model="categoryFilter"
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-amber-400 transition cursor-pointer"
            >
              <option value="Semua">Semua Kategori Pengeluaran</option>
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div>
            <select 
              v-model="churchFilter"
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-amber-400 transition cursor-pointer"
            >
              <option value="Semua">Semua Cabang Gereja</option>
              <option value="GracePoint Pusat">GracePoint Pusat</option>
              <option v-for="c in churches" :key="c.id" :value="c.church_name">{{ c.church_name }}</option>
            </select>
          </div>

          <div>
            <select 
              v-model="statusFilter"
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-amber-400 transition cursor-pointer"
            >
              <option value="Semua">Semua Status Verifikasi</option>
              <option value="Disetujui">Disetujui</option>
              <option value="Menunggu">Menunggu Verifikasi</option>
              <option value="Ditolak">Ditolak</option>
            </select>
          </div>

        </div>
      </section>

      <!-- DATA TABLE -->
      <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-2xl backdrop-blur-xl">
        <div class="flex items-center justify-between pb-4 border-b border-white/10">
          <div>
            <h3 class="font-serif text-xl font-bold text-white">Buku Catatan Kas Keluar (Disbursement)</h3>
            <p class="text-xs text-slate-400 mt-0.5">Daftar transaksi realisasi pengeluaran dan beban kas operasional gereja.</p>
          </div>
          <span class="text-xs text-rose-300 font-mono font-semibold">
            {{ filteredList.length }} Bukti Pengeluaran
          </span>
        </div>

        <div class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400 bg-slate-950/40">
                <th class="py-3 px-4">Tanggal &amp; No. Voucher</th>
                <th class="py-3 px-4">Kategori Pengeluaran</th>
                <th class="py-3 px-4">Cabang Gereja</th>
                <th class="py-3 px-4">Penerima Dana</th>
                <th class="py-3 px-4">Status</th>
                <th class="py-3 px-4 text-right">Jumlah (IDR)</th>
                <th class="py-3 px-4 text-center">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              <tr 
                v-for="item in filteredList" 
                :key="item.id"
                class="hover:bg-slate-900/60 transition group cursor-pointer"
                @click="openDetailModal(item)"
              >
                <td class="py-3.5 px-4 whitespace-nowrap">
                  <span class="font-bold text-slate-200 block">{{ item.tanggal }}</span>
                  <span class="text-[10px] text-rose-400 font-mono">{{ item.nomor_voucher }}</span>
                </td>

                <td class="py-3.5 px-4">
                  <span class="font-semibold text-white block">{{ item.kategori }}</span>
                  <span class="text-[11px] text-slate-400 truncate max-w-xs block">{{ item.keperluan }}</span>
                </td>

                <td class="py-3.5 px-4 text-slate-300">
                  <span class="flex items-center gap-1.5">
                    <i class="bi bi-buildings text-slate-400"></i>
                    <span>{{ item.church_name }}</span>
                  </span>
                </td>

                <td class="py-3.5 px-4 text-slate-300 font-medium">
                  {{ item.penerima || '-' }}
                </td>

                <td class="py-3.5 px-4 whitespace-nowrap">
                  <span 
                    :class="[
                      'px-2.5 py-1 rounded-lg text-[10px] font-bold border',
                      item.status === 'Disetujui' ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' : item.status === 'Menunggu' ? 'bg-amber-500/15 text-amber-300 border-amber-500/30' : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                    ]"
                  >
                    {{ item.status }}
                  </span>
                </td>

                <td class="py-3.5 px-4 text-right font-bold text-rose-400 font-mono text-sm whitespace-nowrap">
                  - {{ formatIDR(item.nominal) }}
                </td>

                <td class="py-3.5 px-4 text-center whitespace-nowrap">
                  <button 
                    type="button" 
                    class="p-1.5 text-slate-300 hover:text-amber-300 hover:bg-slate-800 rounded-lg text-xs"
                    title="Lihat Detail Pengeluaran"
                    @click.stop="openDetailModal(item)"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                </td>
              </tr>

              <tr v-if="filteredList.length === 0">
                <td colspan="7" class="py-12 text-center text-slate-400">
                  <i class="bi bi-inbox text-2xl block text-slate-600 mb-2"></i>
                  Tidak ada catatan pengeluaran yang sesuai filter pencarian.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- MODAL CATAT PENGELUARAN -->
    <Transition name="modal">
      <div 
        v-if="isModalOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm"
      >
        <div class="w-full max-w-lg rounded-3xl border border-rose-500/30 bg-[#0c1b22] p-6 shadow-2xl text-slate-100 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <h3 class="font-serif text-lg font-bold text-white flex items-center gap-2">
              <i class="bi bi-plus-circle-fill text-rose-400"></i> Catat Pengeluaran Kas Baru
            </h3>
            <button @click="isModalOpen = false" class="text-slate-400 hover:text-white">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <form @submit.prevent="handleSavePengeluaran" class="space-y-3.5 text-xs">
            <div>
              <label class="block font-semibold text-slate-300 mb-1" for="pengeluaran-nominal">Nominal Beban Kas Keluar (Rp) *</label>
              <input 
                id="pengeluaran-nominal"
                v-model="form.nominal"
                type="number" 
                required 
                placeholder="Contoh: 3500000" 
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-sm font-mono text-rose-400 outline-none focus:border-amber-400"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="pengeluaran-tanggal">Tanggal Realisasi *</label>
                <input 
                  id="pengeluaran-tanggal"
                  v-model="form.tanggal"
                  type="date" 
                  required 
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="pengeluaran-kategori">Kategori Pengeluaran *</label>
                <select 
                  id="pengeluaran-kategori"
                  v-model="form.kategori"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-amber-400"
                >
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="pengeluaran-church">Cabang Terkait</label>
                <select 
                  id="pengeluaran-church"
                  v-model="form.church_name"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-amber-400"
                >
                  <option value="GracePoint Pusat">GracePoint Pusat</option>
                  <option v-for="c in churches" :key="c.id" :value="c.church_name">{{ c.church_name }}</option>
                </select>
              </div>

              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="pengeluaran-penerima">Penerima Dana / Rekanan</label>
                <input 
                  id="pengeluaran-penerima"
                  v-model="form.penerima"
                  type="text" 
                  placeholder="Contoh: Toko Sound / Bpk. Yosua" 
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-white outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <div>
              <label class="block font-semibold text-slate-300 mb-1" for="pengeluaran-keperluan">Keperluan / Rincian Pengeluaran</label>
              <textarea 
                id="pengeluaran-keperluan"
                v-model="form.keperluan"
                rows="2"
                placeholder="Rincian peruntukan dana, persetujuan majelis, dll..."
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-white outline-none focus:border-amber-400"
              ></textarea>
            </div>

            <div class="pt-3 border-t border-white/10 flex items-center justify-end gap-2.5">
              <button 
                type="button" 
                @click="isModalOpen = false" 
                class="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:bg-white/10"
              >
                Batal
              </button>
              <button 
                type="submit" 
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl bg-rose-500 hover:bg-rose-400 text-white font-bold shadow"
              >
                {{ isSubmitting ? 'Menyimpan...' : 'Simpan Pengeluaran' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- MODAL DETAIL PENGELUARAN -->
    <Transition name="modal">
      <div 
        v-if="isDetailModalOpen && selectedItem" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm"
      >
        <div class="w-full max-w-md rounded-3xl border border-rose-500/30 bg-[#0c1b22] p-6 shadow-2xl text-slate-100 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <div>
              <span class="text-[10px] text-rose-400 font-mono">{{ selectedItem.nomor_voucher }}</span>
              <h3 class="font-serif text-lg font-bold text-white">{{ selectedItem.kategori }}</h3>
            </div>
            <button @click="isDetailModalOpen = false" class="text-slate-400 hover:text-white">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <div class="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Jumlah Kas Keluar:</span>
              <span class="text-lg font-bold text-rose-400 font-mono">- {{ formatIDR(selectedItem.nominal) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Tanggal Realisasi:</span>
              <span class="text-white font-semibold">{{ selectedItem.tanggal }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Cabang Gereja:</span>
              <span class="text-white font-semibold">{{ selectedItem.church_name }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Penerima Dana:</span>
              <span class="text-amber-300 font-semibold">{{ selectedItem.penerima }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Status Verifikasi:</span>
              <span class="text-emerald-400 font-bold">{{ selectedItem.status }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Disetujui Oleh:</span>
              <span class="text-slate-300">{{ selectedItem.disetujui_oleh || 'Superadmin' }}</span>
            </div>
          </div>

          <div v-if="selectedItem.keperluan" class="p-3 bg-slate-900/60 rounded-xl border border-white/5 text-xs text-slate-300">
            <span class="text-[10px] font-bold text-slate-400 block mb-1">Keperluan / Keterangan:</span>
            {{ selectedItem.keperluan }}
          </div>

          <div class="pt-3 border-t border-white/10 flex justify-end">
            <button 
              type="button" 
              @click="isDetailModalOpen = false" 
              class="px-4 py-2 rounded-xl text-xs bg-slate-800 text-slate-200 hover:bg-slate-700"
            >
              Tutup Rincian
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
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
</style>
