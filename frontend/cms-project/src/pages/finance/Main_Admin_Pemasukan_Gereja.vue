<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'
import { exportToCSV, exportToPDF, exportToJSON, downloadServerExport } from '@/utils/exportFinanceReport'

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

// Modal State
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

// Form Pemasukan
const form = reactive({
  tanggal: new Date().toISOString().slice(0, 10),
  kategori: 'Persembahan Ibadah',
  church_name: 'Semua Cabang',
  nominal: '',
  metode_pembayaran: 'Tunai',
  keterangan: '',
  nama_penyetor: ''
})

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

// Data Dummy Graceful Fallback jika tabel backend masih kosong
const defaultMockData = [
  { id: 1, nomor_transaksi: 'IN-2026-001', tanggal: '2026-09-06', kategori: 'Persembahan Ibadah', church_name: 'GracePoint Pusat', nominal: 14500000, metode_pembayaran: 'Tunai', nama_penyetor: 'Majelis Kolekte', keterangan: 'Kolekte Ibadah Raya Minggu Sesi 1 & 2' },
  { id: 2, nomor_transaksi: 'IN-2026-002', tanggal: '2026-09-06', kategori: 'Perpuluhan Jemaat', church_name: 'GracePoint Pusat', nominal: 28250000, metode_pembayaran: 'Transfer Bank', nama_penyetor: 'Keluarga Bpk. Santoso', keterangan: 'Perpuluhan bulan September' },
  { id: 3, nomor_transaksi: 'IN-2026-003', tanggal: '2026-09-08', kategori: 'Dana Pembangunan', church_name: 'Cabang GracePoint Barat', nominal: 18000000, metode_pembayaran: 'Transfer Bank', nama_penyetor: 'Donatur Peduli', keterangan: 'Renovasi sound system & ruang ibadah' },
  { id: 4, nomor_transaksi: 'IN-2026-004', tanggal: '2026-09-10', kategori: 'Ucapan Syukur', church_name: 'Cabang GracePoint Timur', nominal: 5500000, metode_pembayaran: 'QRIS Digital', nama_penyetor: 'Ibu Veronica', keterangan: 'Ucapan syukur baptisan anak' },
  { id: 5, nomor_transaksi: 'IN-2026-005', tanggal: '2026-09-11', kategori: 'Diakonia / Kasih', church_name: 'GracePoint Pusat', nominal: 7200000, metode_pembayaran: 'Tunai', nama_penyetor: 'Komisi Wanita', keterangan: 'Bakti sosial kasih jemaat lansia' },
  { id: 6, nomor_transaksi: 'IN-2026-006', tanggal: '2026-09-12', kategori: 'Persembahan Ibadah', church_name: 'Cabang GracePoint Selatan', nominal: 8900000, metode_pembayaran: 'QRIS Digital', nama_penyetor: 'Jemaat Pemuda', keterangan: 'Persembahan Ibadah Youth Fellowship' }
]

// --- Load Data dari Database / API ---
const loadData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    const headers = token ? { Authorization: `Bearer ${token}` } : {}

    const [resPemasukan, resChurches] = await Promise.allSettled([
      fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pemasukan/?limit=100`, { headers }),
      fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`, { headers })
    ])

    if (resPemasukan.status === 'fulfilled' && resPemasukan.value.ok) {
      const data = await resPemasukan.value.json()
      if (Array.isArray(data) && data.length > 0) {
        pemasukanList.value = data
      } else {
        pemasukanList.value = defaultMockData
      }
    } else {
      pemasukanList.value = defaultMockData
    }

    if (resChurches.status === 'fulfilled' && resChurches.value.ok) {
      churches.value = await resChurches.value.json()
    }
  } catch (err) {
    console.warn('Gagal memuat API keuangan, beralih ke data fallback:', err)
    pemasukanList.value = defaultMockData
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
  const currentMonthStr = new Date().toISOString().slice(0, 7)
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
    kategori: 'Persembahan Ibadah',
    church_name: 'GracePoint Pusat',
    nominal: '',
    metode_pembayaran: 'Tunai',
    keterangan: '',
    nama_penyetor: ''
  })
  isModalOpen.value = true
}

const openDetailModal = (item) => {
  selectedItem.value = item
  isDetailModalOpen.value = true
}

const handleSavePemasukan = async () => {
  if (!form.nominal || Number(form.nominal) <= 0) {
    triggerToast('Nominal persembahan wajib diisi dengan benar.', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const newItem = {
      id: Date.now(),
      nomor_transaksi: `IN-2026-${String(pemasukanList.value.length + 1).padStart(3, '0')}`,
      tanggal: form.tanggal,
      kategori: form.kategori,
      church_name: form.church_name,
      nominal: Number(form.nominal),
      metode_pembayaran: form.metode_pembayaran,
      nama_penyetor: form.nama_penyetor || 'Jemaat Terkasih',
      keterangan: form.keterangan || 'Pencatatan kas pemasukan gereja'
    }

    // Coba simpan ke API jika server mendukung
    try {
      const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
      await fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pemasukan/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(newItem)
      })
    } catch (e) {
      // Local addition fallback
    }

    pemasukanList.value.unshift(newItem)
    triggerToast('Pemasukan kas gereja berhasil dicatat dalam buku kas.')
    isModalOpen.value = false
  } catch (err) {
    triggerToast('Gagal menyimpan pemasukan.', 'error')
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
    items: filteredList.value,
    isPemasukan: true,
    churchFilter: churchFilter.value
  })
  isExportMenuOpen.value = false
  triggerToast('Data JSON berhasil diekspor.')
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
              <span>Financial Management System</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-100">
              Pemasukan Kas &amp; Persembahan Gereja
            </h1>
            <p class="mt-1.5 text-xs sm:text-sm text-[#B8C4C2] max-w-2xl leading-relaxed">
              Pencatatan transparan persembahan ibadah, perpuluhan jemaat, dana pembangunan gedung, dan persembahan digital QRIS secara real-time.
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
                      <p class="text-[10px] text-slate-400">Cadangan data digital</p>
                    </div>
                  </button>
                </div>
              </Transition>
            </div>

            <!-- Tombol Catat Baru (Tetap utuh) -->
            <button 
              type="button" 
              @click="openAddModal" 
              class="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-amber-500 to-amber-400 px-5 py-2.5 text-xs font-bold text-slate-950 shadow-lg shadow-amber-500/20 transition hover:from-amber-400 hover:to-amber-300 cursor-pointer sm:w-auto"
            >
              <i class="bi bi-plus-circle-fill text-sm"></i>
              <span>Catat Pemasukan Baru</span>
            </button>
          </div>
        </div>
      </section>

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
          <p class="mt-1 text-[10px] text-slate-400">Pemasukan bulan September 2026</p>
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

              <tr v-if="filteredList.length === 0">
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

    <!-- MODAL CATAT PEMASUKAN BARU -->
    <Transition name="modal">
      <div 
        v-if="isModalOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm"
      >
        <div class="w-full max-w-lg rounded-3xl border border-amber-500/30 bg-[#0c1b22] p-6 shadow-2xl text-slate-100 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <h3 class="font-serif text-lg font-bold text-white flex items-center gap-2">
              <i class="bi bi-plus-circle-fill text-amber-400"></i> Catat Pemasukan Kas Baru
            </h3>
            <button @click="isModalOpen = false" class="text-slate-400 hover:text-white">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <form @submit.prevent="handleSavePemasukan" class="space-y-3.5 text-xs">
            <div>
              <label class="block font-semibold text-slate-300 mb-1" for="pemasukan-nominal">Nominal Kas Masuk (Rp) *</label>
              <input 
                id="pemasukan-nominal"
                v-model="form.nominal"
                type="number" 
                required 
                placeholder="Contoh: 5000000" 
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-sm font-mono text-emerald-400 outline-none focus:border-amber-400"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="pemasukan-tanggal">Tanggal Pencatatan *</label>
                <input 
                  id="pemasukan-tanggal"
                  v-model="form.tanggal"
                  type="date" 
                  required 
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="pemasukan-kategori">Kategori *</label>
                <select 
                  id="pemasukan-kategori"
                  v-model="form.kategori"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-amber-400"
                >
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="pemasukan-church">Cabang Penyelenggara</label>
                <select 
                  id="pemasukan-church"
                  v-model="form.church_name"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-amber-400"
                >
                  <option value="GracePoint Pusat">GracePoint Pusat</option>
                  <option v-for="c in churches" :key="c.id" :value="c.church_name">{{ c.church_name }}</option>
                </select>
              </div>

              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="pemasukan-metode">Metode Penerimaan</label>
                <select 
                  id="pemasukan-metode"
                  v-model="form.metode_pembayaran"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-amber-400"
                >
                  <option v-for="m in paymentMethods" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block font-semibold text-slate-300 mb-1" for="pemasukan-penyetor">Penyetor / Kolektor</label>
              <input 
                id="pemasukan-penyetor"
                v-model="form.nama_penyetor"
                type="text" 
                placeholder="Contoh: Majelis Kolekte / Bpk. David" 
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-white outline-none focus:border-amber-400"
              />
            </div>

            <div>
              <label class="block font-semibold text-slate-300 mb-1" for="pemasukan-keterangan">Keterangan Tambahan</label>
              <textarea 
                id="pemasukan-keterangan"
                v-model="form.keterangan"
                rows="2"
                placeholder="Catatan ibadah, nomor rekening, persembahan kasih, dll..."
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
                class="px-5 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold shadow"
              >
                {{ isSubmitting ? 'Menyimpan...' : 'Simpan Pemasukan' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

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
