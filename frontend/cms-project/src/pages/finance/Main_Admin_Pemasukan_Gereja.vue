<script setup>
import { ref, computed, onMounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'
import { exportToCSV, exportToPDF, exportToJSON, downloadServerExport } from '@/utils/exportFinanceReport'
import { fetchAllFinanceRecords } from '@/utils/fetchAllFinanceRecords'

// --- State Data Utama Pemasukan ---
const pemasukanList = ref([])
const churches = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

// Filter & Pencarian
const searchQuery = ref('')
const categoryFilter = ref('Semua')
const churchFilter = ref('Semua')
const methodFilter = ref('Semua')

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

const categories = [
  'Persembahan Ibadah',
  'Perpuluhan Jemaat',
  'Dana Pembangunan',
  'Ucapan Syukur',
  'Diakonia / Kasih',
  'Persembahan Khusus / KKR',
  'Lain-lain'
]

const paymentMethods = ['Tunai', 'Transfer Bank', 'QRIS Digital']

// --- Load Data dari Database / API ---
const loadData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    const headers = token ? { Authorization: `Bearer ${token}` } : {}

    const [resPemasukan, resChurches] = await Promise.allSettled([
      fetchAllFinanceRecords(`${APP_CONFIG.apiBaseUrl}/keuangan/pemasukan`, headers),
      fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`, { headers })
    ])

    if (resPemasukan.status === 'fulfilled') {
      pemasukanList.value = resPemasukan.value.map((item) => ({
          ...item,
          nominal: Number(item.nominal ?? item.jumlah ?? 0),
          jumlah: Number(item.jumlah ?? item.nominal ?? 0),
          nama_penyetor: item.nama_penyetor || item.donor_name || 'Jemaat Terkasih',
          nomor_transaksi: item.nomor_transaksi || `IN-2026-${String(item.id).padStart(3, '0')}`,
          church_name: item.church_name || `Cabang ID #${item.church_id || 1}`
        }))
    } else {
      pemasukanList.value = []
      errorMessage.value = 'Data pemasukan tidak dapat dimuat dari server. Coba muat ulang.'
    }

    if (resChurches.status === 'fulfilled' && resChurches.value.ok) {
      const churchData = await resChurches.value.json()
      churches.value = Array.isArray(churchData) ? churchData : []
    }
  } catch (err) {
    console.error('Gagal memuat data pemasukan:', err)
    pemasukanList.value = []
    errorMessage.value = 'Terjadi kesalahan saat memuat data pemasukan dari server.'
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
      (item.kategori && item.kategori.toLowerCase().includes(q)) ||
      (item.keterangan && item.keterangan.toLowerCase().includes(q)) ||
      (item.church_name && item.church_name.toLowerCase().includes(q)) ||
      (item.nama_penyetor && item.nama_penyetor.toLowerCase().includes(q)) ||
      (item.nomor_transaksi && item.nomor_transaksi.toLowerCase().includes(q))

    const matchesCategory = categoryFilter.value === 'Semua' || item.kategori === categoryFilter.value
    const matchesChurch = churchFilter.value === 'Semua' || item.church_name === churchFilter.value
    const matchesMethod = methodFilter.value === 'Semua' || item.metode_pembayaran === methodFilter.value

    return matchesSearch && matchesCategory && matchesChurch && matchesMethod
  })
})

// Summary Metrics
const metrics = computed(() => {
  const total = pemasukanList.value.reduce((acc, curr) => acc + (Number(curr.nominal) || 0), 0)
  const now = new Date()
  const currentMonthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  const thisMonth = pemasukanList.value
    .filter((item) => item.tanggal && item.tanggal.startsWith(currentMonthStr))
    .reduce((acc, curr) => acc + (Number(curr.nominal) || 0), 0)

  const persembahan = pemasukanList.value
    .filter((item) => item.kategori === 'Persembahan Ibadah')
    .reduce((acc, curr) => acc + (Number(curr.nominal) || 0), 0)

  const perpuluhan = pemasukanList.value
    .filter((item) => item.kategori === 'Perpuluhan Jemaat' || item.kategori === 'Dana Pembangunan')
    .reduce((acc, curr) => acc + (Number(curr.nominal) || 0), 0)

  return { total, thisMonth, persembahan, perpuluhan }
})

const currentMonthLabel = new Intl.DateTimeFormat('id-ID', { month: 'long', year: 'numeric' }).format(new Date())

const monthlyTrend = computed(() => {
  const months = Array.from({ length: 6 }, (_, index) => {
    const date = new Date()
    date.setDate(1)
    date.setMonth(date.getMonth() - 5 + index)
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    const total = pemasukanList.value
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

// Modal Handlers
const openDetailModal = (item) => {
  selectedItem.value = item
  isDetailModalOpen.value = true
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
      token
    })
    triggerToast('Laporan PDF resmi berhasil diunduh dari server Python (ReportLab).')
  } catch (err) {
    exportToPDF({
      title: 'Pemasukan Kas & Persembahan Gereja',
      items: filteredList.value,
      isPemasukan: true,
      churchFilter: churchFilter.value
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
      token
    })
    triggerToast('Laporan Excel (.xlsx) berhasil diunduh dari server Python (openpyxl).')
  } catch (err) {
    exportToCSV({
      title: 'Pemasukan Kas & Persembahan Gereja',
      filename: 'Laporan_Pemasukan_Gereja',
      items: filteredList.value,
      isPemasukan: true,
      churchFilter: churchFilter.value
    })
    triggerToast('Laporan Excel / Spreadsheet berhasil diunduh.')
  }
}

const handleExportJSON = () => {
  exportToJSON({
    title: 'Pemasukan Kas & Persembahan Gereja',
    filename: 'Data_Pemasukan_Gereja',
    items: pemasukanList.value,
    isPemasukan: true,
    churchFilter: 'Semua'
  })
  isExportMenuOpen.value = false
  triggerToast('Cadangan JSON seluruh data pemasukan berhasil diunduh.')
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
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-wallet2"></i>
              <span>Financial Monitoring &amp; Backup</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-100">
              Pemasukan Kas &amp; Persembahan Gereja
            </h1>
            <p class="mt-1.5 text-xs sm:text-sm text-[#B8C4C2] max-w-2xl leading-relaxed">
              Pemantauan dan pencadangan data pemasukan gereja. Kebijakan serta pencatatan transaksi tetap menjadi kewenangan gereja.
            </p>
          </div>

          <div class="relative flex w-full min-w-0 flex-wrap items-center gap-2.5 sm:w-auto sm:flex-nowrap">
            <!-- Dropdown Ekspor Laporan -->
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
              <Transition name="fade">
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
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Akumulasi</span>
            <div class="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-sm">
              <i class="bi bi-cash-stack"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-emerald-300 font-mono">{{ formatIDR(metrics.total) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Total kas masuk terverifikasi</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Bulan Berjalan</span>
            <div class="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 text-sm">
              <i class="bi bi-calendar-check"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-amber-300 font-mono">{{ formatIDR(metrics.thisMonth) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Pemasukan {{ currentMonthLabel }}</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Persembahan Ibadah</span>
            <div class="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 text-sm">
              <i class="bi bi-bell-fill"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-sky-300 font-mono">{{ formatIDR(metrics.persembahan) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Kolekte kantong & umum</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Perpuluhan &amp; Khusus</span>
            <div class="w-8 h-8 rounded-lg bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 text-sm">
              <i class="bi bi-gift-fill"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-purple-300 font-mono">{{ formatIDR(metrics.perpuluhan) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Perpuluhan & pembangunan</p>
        </div>
      </section>

      <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-xl backdrop-blur-xl">
        <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-2 border-b border-white/10 pb-4">
          <div>
            <h3 class="font-serif text-lg font-bold text-white">Tren Pemasukan Bulanan</h3>
            <p class="mt-1 text-xs text-slate-400">Enam bulan terakhir berdasarkan data transaksi yang dimuat.</p>
          </div>
          <span class="text-[10px] text-slate-500">Grafik pemantauan • bukan alat persetujuan</span>
        </div>
        <div v-if="isLoading" class="py-12 text-center text-xs text-slate-400">Memuat tren pemasukan...</div>
        <div v-else class="mt-5 flex h-44 items-end gap-2 sm:gap-4">
          <div v-for="month in monthlyTrend" :key="month.key" class="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-2">
            <span class="max-w-full truncate text-[9px] text-slate-400 sm:text-[10px]">{{ month.total ? formatIDR(month.total) : '-' }}</span>
            <div class="flex h-28 w-full items-end justify-center rounded-t-lg bg-slate-950/50">
              <div
                class="w-2/3 rounded-t-md bg-gradient-to-t from-emerald-700 to-amber-400 transition-all"
                :style="{ height: month.height + '%' }"
                :title="`${month.label}: ${formatIDR(month.total)}`"
              ></div>
            </div>
            <span class="text-[10px] font-semibold text-slate-300">{{ month.label }}</span>
          </div>
        </div>
      </section>

      <!-- FILTER & SEARCH BAR -->
      <section class="rounded-2xl border border-white/10 bg-[#123138]/70 p-4 backdrop-blur-md">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          
          <div class="relative">
            <i class="bi bi-search absolute left-3 top-2.5 text-slate-500 text-xs"></i>
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Cari nomor, penyetor, keterangan..." 
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 outline-none focus:border-amber-400 transition"
            />
          </div>

          <div>
            <select 
              v-model="categoryFilter"
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-amber-400 transition cursor-pointer"
            >
              <option value="Semua">Semua Kategori Pemasukan</option>
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
              v-model="methodFilter"
              class="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs text-slate-200 outline-none focus:border-amber-400 transition cursor-pointer"
            >
              <option value="Semua">Semua Metode Pembayaran</option>
              <option v-for="m in paymentMethods" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>

        </div>
      </section>

      <!-- DATA TABLE -->
      <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-2xl backdrop-blur-xl">
        <div class="flex items-center justify-between pb-4 border-b border-white/10">
          <div>
            <h3 class="font-serif text-xl font-bold text-white">Buku Catatan Kas Masuk</h3>
            <p class="text-xs text-slate-400 mt-0.5">Daftar transaksi penerimaan kas jemaat yang tercatat di sistem.</p>
          </div>
          <span class="text-xs text-amber-300 font-mono font-semibold">
            {{ filteredList.length }} Catatan Transaksi
          </span>
        </div>

        <div class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400 bg-slate-950/40">
                <th class="py-3 px-4">Tanggal &amp; No. Transaksi</th>
                <th class="py-3 px-4">Kategori Pemasukan</th>
                <th class="py-3 px-4">Cabang Gereja</th>
                <th class="py-3 px-4">Penyetor / Sumber</th>
                <th class="py-3 px-4">Metode</th>
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
                  <span class="text-[10px] text-amber-400/90 font-mono">{{ item.nomor_transaksi }}</span>
                </td>

                <td class="py-3.5 px-4">
                  <span class="font-semibold text-white block">{{ item.kategori }}</span>
                  <span class="text-[11px] text-slate-400 truncate max-w-xs block">{{ item.keterangan }}</span>
                </td>

                <td class="py-3.5 px-4 text-slate-300">
                  <span class="flex items-center gap-1.5">
                    <i class="bi bi-buildings text-slate-400"></i>
                    <span>{{ item.church_name }}</span>
                  </span>
                </td>

                <td class="py-3.5 px-4 text-slate-300 font-medium">
                  {{ item.nama_penyetor || '-' }}
                </td>

                <td class="py-3.5 px-4 whitespace-nowrap">
                  <span 
                    :class="[
                      'px-2.5 py-1 rounded-lg text-[10px] font-bold border',
                      item.metode_pembayaran === 'Tunai' ? 'bg-amber-500/15 text-amber-300 border-amber-500/30' : item.metode_pembayaran === 'Transfer Bank' ? 'bg-sky-500/15 text-sky-300 border-sky-500/30' : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    ]"
                  >
                    {{ item.metode_pembayaran }}
                  </span>
                </td>

                <td class="py-3.5 px-4 text-right font-bold text-emerald-400 font-mono text-sm whitespace-nowrap">
                  + {{ formatIDR(item.nominal) }}
                </td>

                <td class="py-3.5 px-4 text-center whitespace-nowrap">
                  <button 
                    type="button" 
                    class="p-1.5 text-slate-300 hover:text-amber-300 hover:bg-slate-800 rounded-lg text-xs"
                    title="Lihat Detail Transaksi"
                    @click.stop="openDetailModal(item)"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                </td>
              </tr>

              <tr v-if="isLoading">
                <td colspan="7" class="py-12 text-center text-slate-400">Memuat catatan pemasukan...</td>
              </tr>
              <tr v-else-if="filteredList.length === 0">
                <td colspan="7" class="py-12 text-center text-slate-400">
                  <i class="bi bi-inbox text-2xl block text-slate-600 mb-2"></i>
                  Tidak ada catatan pemasukan yang sesuai kriteria pencarian.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- MODAL DETAIL PEMASUKAN -->
    <Transition name="modal">
      <div 
        v-if="isDetailModalOpen && selectedItem" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm"
      >
        <div class="w-full max-w-md rounded-3xl border border-amber-500/30 bg-[#0c1b22] p-6 shadow-2xl text-slate-100 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <div>
              <span class="text-[10px] text-amber-300 font-mono">{{ selectedItem.nomor_transaksi }}</span>
              <h3 class="font-serif text-lg font-bold text-white">{{ selectedItem.kategori }}</h3>
            </div>
            <button @click="isDetailModalOpen = false" class="text-slate-400 hover:text-white">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <div class="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Jumlah Kas Masuk:</span>
              <span class="text-lg font-bold text-emerald-400 font-mono">{{ formatIDR(selectedItem.nominal) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Tanggal Transaksi:</span>
              <span class="text-white font-semibold">{{ selectedItem.tanggal }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Cabang Gereja:</span>
              <span class="text-white font-semibold">{{ selectedItem.church_name }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Metode Penerimaan:</span>
              <span class="text-amber-300 font-semibold">{{ selectedItem.metode_pembayaran }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Penyetor / Sumber:</span>
              <span class="text-white">{{ selectedItem.nama_penyetor || '-' }}</span>
            </div>
          </div>

          <div v-if="selectedItem.keterangan" class="p-3 bg-slate-900/60 rounded-xl border border-white/5 text-xs text-slate-300">
            <span class="text-[10px] font-bold text-slate-400 block mb-1">Keterangan:</span>
            {{ selectedItem.keterangan }}
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
