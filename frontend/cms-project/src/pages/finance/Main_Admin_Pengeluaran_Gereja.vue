<script setup>
import { ref, computed, onMounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'
import { exportToCSV, exportToPDF, exportToJSON, downloadServerExport } from '@/utils/exportFinanceReport'
import { fetchAllFinanceRecords } from '@/utils/fetchAllFinanceRecords'

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
const isDetailModalOpen = ref(false)
const selectedItem = ref(null)

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
const categories = [
  'Operasional Gedung & Utilitas',
  'Honorarium Pelayan Firman & Musik',
  'Diakonia Sosial & Santunan Kasih',
  'Pemeliharaan Aset & Fasilitas',
  'Program Remaja, Pemuda & Sekolah Minggu',
  'Konsumsi & Kelengkapan Ibadah',
  'Lain-lain'
]

// --- Load Data dari Backend API ---
const loadData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    const headers = token ? { Authorization: `Bearer ${token}` } : {}

    const [resPengeluaran, resChurches] = await Promise.allSettled([
      fetchAllFinanceRecords(`${APP_CONFIG.apiBaseUrl}/keuangan/pengeluaran`, headers),
      fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`, { headers })
    ])

    if (resPengeluaran.status === 'fulfilled') {
      pengeluaranList.value = resPengeluaran.value.map((item) => ({
          ...item,
          nominal: Number(item.nominal ?? item.jumlah ?? 0),
          jumlah: Number(item.jumlah ?? item.nominal ?? 0),
          keperluan: item.keperluan || item.keterangan || 'Beban operasional gereja',
          nomor_voucher: item.nomor_voucher || item.nomor_transaksi || `OUT-${String(item.id).padStart(3, '0')}`,
          church_name: item.church_name || `Cabang ID #${item.church_id || 1}`
        }))
    } else {
      pengeluaranList.value = []
      errorMessage.value = 'Data pengeluaran tidak dapat dimuat dari server. Coba muat ulang.'
    }

    if (resChurches.status === 'fulfilled' && resChurches.value.ok) {
      const churchData = await resChurches.value.json()
      churches.value = Array.isArray(churchData) ? churchData : []
    }
  } catch (err) {
    console.error('Gagal memuat data pengeluaran:', err)
    pengeluaranList.value = []
    errorMessage.value = 'Terjadi kesalahan saat memuat data pengeluaran dari server.'
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
  const now = new Date()
  const currentMonthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
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

const currentMonthLabel = new Intl.DateTimeFormat('id-ID', { month: 'long', year: 'numeric' }).format(new Date())

const monthlyTrend = computed(() => {
  const months = Array.from({ length: 6 }, (_, index) => {
    const date = new Date()
    date.setDate(1)
    date.setMonth(date.getMonth() - 5 + index)
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    const total = pengeluaranList.value
      .filter(item => item.tanggal && item.tanggal.startsWith(key))
      .reduce((sum, item) => sum + (Number(item.nominal) || 0), 0)

    return { key, label: date.toLocaleDateString('id-ID', { month: 'short' }), total }
  })
  const maxTotal = Math.max(...months.map(month => month.total), 0)

  return months.map(month => ({
    ...month,
    height: maxTotal ? Math.max((month.total / maxTotal) * 100, 4) : 0
  }))
})

const formatIDR = (num) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(num || 0)
}

const openDetailModal = (item) => {
  selectedItem.value = item
  isDetailModalOpen.value = true
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
    items: pengeluaranList.value,
    isPemasukan: false,
    churchFilter: 'Semua'
  })
  isExportMenuOpen.value = false
  triggerToast('Cadangan JSON seluruh data pengeluaran berhasil diunduh.')
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
              Pemantauan dan pencadangan data pengeluaran gereja. Kebijakan serta pencatatan transaksi tetap menjadi kewenangan gereja.
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
                      <p class="text-[10px] text-slate-400">Cadangan seluruh data transaksi</p>
                    </div>
                  </button>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </section>

      <div v-if="errorMessage" role="alert" class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-xs text-rose-200">
        <span>{{ errorMessage }}</span>
        <button type="button" @click="loadData" class="shrink-0 rounded-lg border border-rose-400/30 px-3 py-1.5 font-semibold hover:bg-rose-500/15">
          Muat Ulang
        </button>
      </div>

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
          <p class="mt-1 text-[10px] text-slate-400">Pengeluaran {{ currentMonthLabel }}</p>
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

      <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-xl backdrop-blur-xl">
        <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-2 border-b border-white/10 pb-4">
          <div>
            <h3 class="font-serif text-lg font-bold text-white">Tren Pengeluaran Bulanan</h3>
            <p class="mt-1 text-xs text-slate-400">Enam bulan terakhir berdasarkan data transaksi yang dimuat.</p>
          </div>
          <span class="text-[10px] text-slate-500">Grafik pemantauan • bukan alat persetujuan</span>
        </div>
        <div v-if="isLoading" class="py-12 text-center text-xs text-slate-400">Memuat tren pengeluaran...</div>
        <div v-else class="mt-5 flex h-44 items-end gap-2 sm:gap-4">
          <div v-for="month in monthlyTrend" :key="month.key" class="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-2">
            <span class="max-w-full truncate text-[9px] text-slate-400 sm:text-[10px]">{{ month.total ? formatIDR(month.total) : '-' }}</span>
            <div class="flex h-28 w-full items-end justify-center rounded-t-lg bg-slate-950/50">
              <div
                class="w-2/3 rounded-t-md bg-gradient-to-t from-rose-600 to-amber-400 transition-all"
                :style="{ height: month.height + '%' }"
                :title="`${month.label}: ${formatIDR(month.total)}`"
              ></div>
            </div>
            <span class="text-[10px] font-semibold text-slate-300">{{ month.label }}</span>
          </div>
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

              <tr v-if="isLoading">
                <td colspan="7" class="py-12 text-center text-slate-400">Memuat catatan pengeluaran...</td>
              </tr>
              <tr v-else-if="filteredList.length === 0">
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
              <span class="text-slate-400">Status tercatat:</span>
              <span class="text-emerald-400 font-bold">{{ selectedItem.status }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Pihak gereja terkait:</span>
              <span class="text-slate-300">{{ selectedItem.disetujui_oleh || '-' }}</span>
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
