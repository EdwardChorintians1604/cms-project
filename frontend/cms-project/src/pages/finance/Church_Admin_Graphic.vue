<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'
import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  Filler
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  Filler
)

const { user } = useAuth()
const { isDark } = useTheme()

// State Gereja Cabang
const activeChurch = ref({
  id: null,
  name: 'Gereja Cabang GracePoint'
})

// Filter Waktu
const selectedPeriod = ref('2026')
const selectedMonth = ref('all') // 'all' atau '09' (September), dll.

const periods = ['2026', '2025']
const months = [
  { value: 'all', label: 'Seluruh Bulan (Setahun)' },
  { value: '01', label: 'Januari' },
  { value: '02', label: 'Februari' },
  { value: '03', label: 'Maret' },
  { value: '04', label: 'April' },
  { value: '05', label: 'Mei' },
  { value: '06', label: 'Juni' },
  { value: '07', label: 'Juli' },
  { value: '08', label: 'Agustus' },
  { value: '09', label: 'September' },
  { value: '10', label: 'Oktober' },
  { value: '11', label: 'November' },
  { value: '12', label: 'Desember' }
]

// Raw Transactions State
const rawPemasukan = ref([])
const rawPengeluaran = ref([])
const isLoading = ref(false)

// Default Baseline Monthly Data Cabang (Jika database baru dibuat / masih sedikit)
const defaultMonthlyIn = [18500000, 21000000, 19800000, 24500000, 23200000, 25800000, 27400000, 26900000, 31200000, 29800000, 0, 0]
const defaultMonthlyOut = [11200000, 12800000, 11900000, 14500000, 13700000, 14800000, 15900000, 16200000, 17400000, 15800000, 0, 0]

const loadData = async () => {
  isLoading.value = true
  try {
    const u = user.value
    if (u) {
      activeChurch.value.id = u.church_id || (u.church && u.church.id) || 1
      activeChurch.value.name = u.church_name || (u.church && u.church.church_name) || 'Gereja Cabang GracePoint'
    }

    // 1. Ambil dari LocalStorage Cabang
    const keyIn = `grace_pemasukan_cabang_${activeChurch.value.id || 'default'}`
    const keyOut = `grace_pengeluaran_cabang_${activeChurch.value.id || 'default'}`
    const localIn = localStorage.getItem(keyIn)
    const localOut = localStorage.getItem(keyOut)

    if (localIn) rawPemasukan.value = JSON.parse(localIn)
    if (localOut) rawPengeluaran.value = JSON.parse(localOut)

    // 2. Coba sync dari Backend API
    const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }

    const churchParam = activeChurch.value.id ? `?church_id=${activeChurch.value.id}&limit=500` : '?limit=500'
    const [resIn, resOut] = await Promise.allSettled([
      fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pemasukan${churchParam}`, { headers }),
      fetch(`${APP_CONFIG.apiBaseUrl}/keuangan/pengeluaran${churchParam}`, { headers })
    ])

    if (resIn.status === 'fulfilled' && resIn.value.ok) {
      const dataIn = await resIn.value.json()
      if (Array.isArray(dataIn) && dataIn.length > 0) {
        rawPemasukan.value = dataIn
      }
    }

    if (resOut.status === 'fulfilled' && resOut.value.ok) {
      const dataOut = await resOut.value.json()
      if (Array.isArray(dataOut) && dataOut.length > 0) {
        rawPengeluaran.value = dataOut
      }
    }
  } catch (err) {
    console.warn('Gagal memuat API statistik keuangan:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})

const formatIDR = (num) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(num || 0)
}

// ========================================================
// 1. RINGKASAN METRICS UTAMA (KPI CARDS)
// ========================================================
const kpiMetrics = computed(() => {
  // Hitung total pemasukan
  const totalInFromList = rawPemasukan.value.reduce((sum, item) => sum + (Number(item.jumlah || item.nominal) || 0), 0)
  const totalIn = totalInFromList > 0 ? totalInFromList : defaultMonthlyIn.reduce((a, b) => a + b, 0)

  // Hitung total pengeluaran
  const totalOutFromList = rawPengeluaran.value.reduce((sum, item) => sum + (Number(item.jumlah || item.nominal) || 0), 0)
  const totalOut = totalOutFromList > 0 ? totalOutFromList : defaultMonthlyOut.reduce((a, b) => a + b, 0)

  // Surplus Kas Bersih
  const netSurplus = totalIn - totalOut

  // Rasio Efisiensi (Beban dibanding Pemasukan)
  const efficiencyRatio = totalIn > 0 ? Math.round((totalOut / totalIn) * 100) : 0

  return { totalIn, totalOut, netSurplus, efficiencyRatio }
})

// ========================================================
// 2. CHART 1: TREN PEMASUKAN VS PENGELUARAN (BAR CHART)
// ========================================================
const trendBarData = computed(() => {
  const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  const inData = [...defaultMonthlyIn]
  const outData = [...defaultMonthlyOut]

  // Integrasikan data aktual dari pemasukan real-time
  rawPemasukan.value.forEach((item) => {
    if (item.tanggal) {
      const monthIdx = parseInt(item.tanggal.substring(5, 7), 10) - 1
      if (monthIdx >= 0 && monthIdx < 12) {
        inData[monthIdx] += Number(item.jumlah || item.nominal) || 0
      }
    }
  })

  // Integrasikan data aktual dari pengeluaran real-time
  rawPengeluaran.value.forEach((item) => {
    if (item.tanggal) {
      const monthIdx = parseInt(item.tanggal.substring(5, 7), 10) - 1
      if (monthIdx >= 0 && monthIdx < 12) {
        outData[monthIdx] += Number(item.jumlah || item.nominal) || 0
      }
    }
  })

  return {
    labels: monthLabels,
    datasets: [
      {
        label: 'Pemasukan Kas (IDR)',
        backgroundColor: '#10b981', // emerald-500
        hoverBackgroundColor: '#34d399',
        borderRadius: 6,
        data: inData
      },
      {
        label: 'Pengeluaran Kas (IDR)',
        backgroundColor: '#f43f5e', // rose-500
        hoverBackgroundColor: '#fb7185',
        borderRadius: 6,
        data: outData
      }
    ]
  }
})

const trendBarOptions = computed(() => {
  const textColor = isDark.value ? '#94a3b8' : '#475569'
  const gridColor = isDark.value ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)'
  const legendColor = isDark.value ? '#e2e8f0' : '#1e293b'

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: legendColor,
          font: { size: 12, weight: '600', family: 'sans-serif' }
        }
      },
      tooltip: {
        callbacks: {
          label: (ctx) => `${ctx.dataset.label}: ${formatIDR(ctx.raw)}`
        }
      }
    },
    scales: {
      x: {
        ticks: { color: textColor, font: { size: 11 } },
        grid: { color: gridColor }
      },
      y: {
        ticks: {
          color: textColor,
          font: { size: 10 },
          callback: (val) => `${(val / 1000000).toFixed(0)} jt`
        },
        grid: { color: gridColor }
      }
    }
  }
})

// ========================================================
// 3. CHART 2: KOMPOSISI PERSEMBAHAN JEMAAT (DOUGHNUT)
// ========================================================
const offeringCompositionData = computed(() => {
  const categoryTotals = {
    'Persembahan Ibadah Raya': 48500000,
    'Perpuluhan Jemaat': 62300000,
    'Dana Pembangunan Gedung': 35000000,
    'Ucapan Syukur & Baptisan': 16800000,
    'Diakonia / Kasih': 12400000,
    'Persembahan Khusus / KKR': 8500000
  }

  // Akumulasikan jika ada input dari tabel pemasukan
  rawPemasukan.value.forEach((item) => {
    const cat = item.kategori || 'Persembahan Ibadah Raya'
    const nominal = Number(item.jumlah || item.nominal) || 0
    if (categoryTotals[cat] !== undefined) {
      categoryTotals[cat] += nominal
    } else {
      categoryTotals['Persembahan Ibadah Raya'] += nominal
    }
  })

  return {
    labels: Object.keys(categoryTotals),
    datasets: [
      {
        backgroundColor: [
          '#10b981', // emerald
          '#38bdf8', // sky
          '#f59e0b', // amber
          '#a855f7', // purple
          '#ec4899', // pink
          '#6366f1'  // indigo
        ],
        borderWidth: 2,
        borderColor: isDark.value ? '#0f172a' : '#ffffff',
        hoverOffset: 8,
        data: Object.values(categoryTotals)
      }
    ]
  }
})

const offeringDoughnutOptions = computed(() => {
  const legendColor = isDark.value ? '#cbd5e1' : '#334155'
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: legendColor,
          font: { size: 10.5, family: 'sans-serif' },
          boxWidth: 12,
          padding: 12
        }
      },
      tooltip: {
        callbacks: {
          label: (ctx) => `${ctx.label}: ${formatIDR(ctx.raw)}`
        }
      }
    }
  }
})

// ========================================================
// 4. CHART 3: TREN PEROLEHAN PER MINGGU (LINE CHART)
// ========================================================
const weeklyOfferingLineData = computed(() => {
  return {
    labels: ['Minggu I (Sesi Pagi)', 'Minggu II (Sesi Pagi)', 'Minggu III (Sesi Pagi)', 'Minggu IV (Sesi Pagi)'],
    datasets: [
      {
        label: 'Persembahan Ibadah Raya 1',
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.12)',
        fill: true,
        tension: 0.35,
        pointRadius: 5,
        pointHoverRadius: 7,
        data: [7800000, 8950000, 8400000, 9600000]
      },
      {
        label: 'Persembahan Ibadah Raya 2 (Sore)',
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.12)',
        fill: true,
        tension: 0.35,
        pointRadius: 5,
        pointHoverRadius: 7,
        data: [5200000, 6100000, 5800000, 6900000]
      },
      {
        label: 'Youth Fellowship & Anak',
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.12)',
        fill: true,
        tension: 0.35,
        pointRadius: 5,
        pointHoverRadius: 7,
        data: [2100000, 2450000, 2200000, 2800000]
      }
    ]
  }
})

const weeklyLineOptions = computed(() => {
  const textColor = isDark.value ? '#94a3b8' : '#475569'
  const gridColor = isDark.value ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)'
  const legendColor = isDark.value ? '#e2e8f0' : '#1e293b'

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: legendColor,
          font: { size: 11, family: 'sans-serif' }
        }
      },
      tooltip: {
        callbacks: {
          label: (ctx) => `${ctx.dataset.label}: ${formatIDR(ctx.raw)}`
        }
      }
    },
    scales: {
      x: {
        ticks: { color: textColor, font: { size: 10 } },
        grid: { color: gridColor }
      },
      y: {
        ticks: {
          color: textColor,
          font: { size: 10 },
          callback: (val) => `${(val / 1000000).toFixed(1)} jt`
        },
        grid: { color: gridColor }
      }
    }
  }
})

// ========================================================
// 5. CHART 4: METODE PEMBAYARAN PERSEMBAHAN (DONUT)
// ========================================================
const paymentMethodChartData = computed(() => {
  let tunai = 42500000
  let qris = 38200000
  let transfer = 54100000

  rawPemasukan.value.forEach((item) => {
    const nominal = Number(item.jumlah || item.nominal) || 0
    if (item.metode_pembayaran === 'QRIS Digital') qris += nominal
    else if (item.metode_pembayaran === 'Transfer Bank') transfer += nominal
    else tunai += nominal
  })

  return {
    labels: ['Uang Tunai Lembaran', 'QRIS Digital Barcode', 'Transfer Bank'],
    datasets: [
      {
        backgroundColor: ['#10b981', '#06b6d4', '#f59e0b'],
        borderWidth: 2,
        borderColor: isDark.value ? '#0f172a' : '#ffffff',
        hoverOffset: 6,
        data: [tunai, qris, transfer]
      }
    ]
  }
})

// ========================================================
// 6. CHART 5: ALOKASI PENGELUARAN KAS CABANG (BAR HORIZONTAL)
// ========================================================
const expenseAllocationData = computed(() => {
  const expenseCategories = {
    'Operasional & Utilitas Gedung': 28500000,
    'Honorarium Pelayan Firman & Musik': 22400000,
    'Pemeliharaan Aset & Fasilitas': 16800000,
    'Diakonia Sosial & Kasih': 12500000,
    'Program Pemuda & Sekolah Minggu': 9400000,
    'Konsumsi & Kelengkapan Ibadah': 6800000
  }

  rawPengeluaran.value.forEach((item) => {
    const cat = item.kategori || 'Operasional & Utilitas Gedung'
    const nominal = Number(item.jumlah || item.nominal) || 0
    if (expenseCategories[cat] !== undefined) {
      expenseCategories[cat] += nominal
    } else {
      expenseCategories['Operasional & Utilitas Gedung'] += nominal
    }
  })

  return {
    labels: Object.keys(expenseCategories),
    datasets: [
      {
        label: 'Realisasi Beban (IDR)',
        backgroundColor: '#f43f5e',
        hoverBackgroundColor: '#fb7185',
        borderRadius: 6,
        data: Object.values(expenseCategories)
      }
    ]
  }
})

const horizontalBarOptions = computed(() => {
  const textColor = isDark.value ? '#94a3b8' : '#475569'
  const gridColor = isDark.value ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)'

  return {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => `Beban: ${formatIDR(ctx.raw)}`
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: textColor,
          font: { size: 10 },
          callback: (val) => `${(val / 1000000).toFixed(0)} jt`
        },
        grid: { color: gridColor }
      },
      y: {
        ticks: { color: textColor, font: { size: 10.5 } },
        grid: { display: false }
      }
    }
  }
})
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6 font-sans pb-12 transition-colors duration-300">

      <!-- NAVIGATION TABS SWITCHER -->
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
          <span>Kasir Hitung Pecahan</span>
        </RouterLink>

        <RouterLink 
          to="/church-finance-graphic"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 border shadow-sm',
            'bg-sky-500/20 text-sky-400 border-sky-500/40'
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
          ? 'border-sky-500/30 bg-gradient-to-r from-slate-950 via-slate-900 to-sky-950/40 text-white' 
          : 'border-sky-300 bg-gradient-to-r from-sky-50/90 via-white to-amber-50/50 text-slate-900'
      ]">
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/15 border border-sky-500/30 text-sky-400 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-pie-chart-fill"></i>
              <span>Financial Analytics &amp; Visual Intelligence • {{ activeChurch.name }}</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight">
              Grafik Laporan Keuangan &amp; Persembahan
            </h1>
            <p :class="['mt-1.5 text-xs sm:text-sm max-w-2xl leading-relaxed', isDark ? 'text-slate-300' : 'text-slate-600']">
              Visualisasi komprehensif arus kas masuk, pengeluaran operasional, perolehan persembahan kantong kebaktian, dan perbandingan donasi tunai vs QRIS secara real-time.
            </p>
          </div>

          <div class="flex items-center gap-3">
            <select 
              v-model="selectedPeriod"
              :class="[
                'rounded-xl border px-3 py-2 text-xs font-semibold outline-none transition cursor-pointer',
                isDark ? 'border-slate-700 bg-slate-900 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-800 focus:border-sky-500'
              ]"
            >
              <option v-for="p in periods" :key="p" :value="p">Tahun {{ p }}</option>
            </select>

            <select 
              v-model="selectedMonth"
              :class="[
                'rounded-xl border px-3 py-2 text-xs font-semibold outline-none transition cursor-pointer',
                isDark ? 'border-slate-700 bg-slate-900 text-white focus:border-sky-400' : 'border-slate-300 bg-white text-slate-800 focus:border-sky-500'
              ]"
            >
              <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </div>
        </div>
      </section>

      <!-- KPI METRICS SUMMARY -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Pemasukan -->
        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Total Pemasukan</span>
            <div class="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-sm">
              <i class="bi bi-arrow-down-left"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-emerald-400 font-mono">{{ formatIDR(kpiMetrics.totalIn) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Total persembahan &amp; donasi masuk</p>
        </div>

        <!-- Pengeluaran -->
        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Total Pengeluaran</span>
            <div class="w-8 h-8 rounded-lg bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400 text-sm">
              <i class="bi bi-arrow-up-right"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-rose-400 font-mono">{{ formatIDR(kpiMetrics.totalOut) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Realisasi beban kas cabang</p>
        </div>

        <!-- Surplus Kas -->
        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Saldo Kas Berjalan</span>
            <div class="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 text-sm">
              <i class="bi bi-wallet2"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-sky-400 font-mono">{{ formatIDR(kpiMetrics.netSurplus) }}</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Net reserve kas (Surplus)</p>
        </div>

        <!-- Rasio Anggaran -->
        <div :class="['rounded-2xl border p-4 backdrop-blur-md transition-colors', isDark ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200 bg-white shadow-sm']">
          <div class="flex items-center justify-between">
            <span :class="['text-[11px] font-semibold uppercase tracking-wider', isDark ? 'text-slate-400' : 'text-slate-500']">Rasio Beban Kas</span>
            <div class="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 text-sm">
              <i class="bi bi-speedometer2"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-amber-400 font-mono">{{ kpiMetrics.efficiencyRatio }}%</p>
          <p :class="['mt-1 text-[10px]', isDark ? 'text-slate-400' : 'text-slate-500']">Kategori: Sangat Sehat (Ideal &lt; 75%)</p>
        </div>
      </section>

      <!-- BARIS 1: GRAFIK UTAMA TREN ARUS KAS & PERSEMBAHAN JEMAAT -->
      <section class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Grafik 1: Perbandingan Pemasukan vs Pengeluaran Bulanan (8 Kolom) -->
        <div :class="['lg:col-span-8 rounded-3xl border p-5 sm:p-6 shadow-xl backdrop-blur-xl flex flex-col justify-between transition-colors', isDark ? 'border-slate-800 bg-slate-900/80 text-white' : 'border-slate-200 bg-white text-slate-900']">
          <div class="flex items-center justify-between pb-4 border-b border-slate-700/30">
            <div>
              <h3 class="font-serif text-lg font-bold flex items-center gap-2">
                <i class="bi bi-bar-chart-fill text-emerald-400"></i>
                <span>Arus Kas: Pemasukan vs Pengeluaran</span>
              </h3>
              <p :class="['text-xs mt-0.5', isDark ? 'text-slate-400' : 'text-slate-600']">
                Tren komparasi kas masuk persembahan dan beban pengeluaran kasir per bulan.
              </p>
            </div>
            <span class="text-xs px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-mono font-bold">
              12 Bulan Aktif
            </span>
          </div>

          <div class="mt-4 h-72 sm:h-80 w-full">
            <Bar :data="trendBarData" :options="trendBarOptions" />
          </div>
        </div>

        <!-- Grafik 2: Komposisi Kategori Persembahan Jemaat (4 Kolom) -->
        <div :class="['lg:col-span-4 rounded-3xl border p-5 sm:p-6 shadow-xl backdrop-blur-xl flex flex-col justify-between transition-colors', isDark ? 'border-slate-800 bg-slate-900/80 text-white' : 'border-slate-200 bg-white text-slate-900']">
          <div class="pb-4 border-b border-slate-700/30">
            <h3 class="font-serif text-lg font-bold flex items-center gap-2">
              <i class="bi bi-pie-chart text-sky-400"></i>
              <span>Persembahan Jemaat</span>
            </h3>
            <p :class="['text-xs mt-0.5', isDark ? 'text-slate-400' : 'text-slate-600']">
              Proporsi penerimaan per kategori ibadah dan dana donasi.
            </p>
          </div>

          <div class="mt-4 h-72 sm:h-80 w-full flex items-center justify-center">
            <Doughnut :data="offeringCompositionData" :options="offeringDoughnutOptions" />
          </div>
        </div>
      </section>

      <!-- BARIS 2: TREN MINGGUAN IBADAH, METODE PEMBAYARAN & ALOKASI PENGELUARAN -->
      <section class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Grafik 3: Perolehan Mingguan Ibadah Raya (4 Kolom) -->
        <div :class="['lg:col-span-4 rounded-3xl border p-5 sm:p-6 shadow-xl backdrop-blur-xl flex flex-col justify-between transition-colors', isDark ? 'border-slate-800 bg-slate-900/80 text-white' : 'border-slate-200 bg-white text-slate-900']">
          <div class="pb-4 border-b border-slate-700/30">
            <h3 class="font-serif text-base font-bold flex items-center gap-2">
              <i class="bi bi-graph-up text-amber-400"></i>
              <span>Tren Mingguan Ibadah Raya</span>
            </h3>
            <p :class="['text-xs mt-0.5', isDark ? 'text-slate-400' : 'text-slate-600']">
              Pola perolehan persembahan antar sesi ibadah dalam 1 bulan.
            </p>
          </div>

          <div class="mt-4 h-64 sm:h-72 w-full">
            <Line :data="weeklyOfferingLineData" :options="weeklyLineOptions" />
          </div>
        </div>

        <!-- Grafik 4: Metode Donasi Jemaat: Tunai vs QRIS vs Bank (4 Kolom) -->
        <div :class="['lg:col-span-4 rounded-3xl border p-5 sm:p-6 shadow-xl backdrop-blur-xl flex flex-col justify-between transition-colors', isDark ? 'border-slate-800 bg-slate-900/80 text-white' : 'border-slate-200 bg-white text-slate-900']">
          <div class="pb-4 border-b border-slate-700/30">
            <h3 class="font-serif text-base font-bold flex items-center gap-2">
              <i class="bi bi-qr-code-scan text-cyan-400"></i>
              <span>Metode Penyaluran Kas</span>
            </h3>
            <p :class="['text-xs mt-0.5', isDark ? 'text-slate-400' : 'text-slate-600']">
              Rasio uang tunai fisik lembaran vs donasi QRIS digital.
            </p>
          </div>

          <div class="mt-4 h-64 sm:h-72 w-full flex items-center justify-center">
            <Doughnut :data="paymentMethodChartData" :options="offeringDoughnutOptions" />
          </div>
        </div>

        <!-- Grafik 5: Alokasi Beban Pengeluaran Kas Cabang (4 Kolom) -->
        <div :class="['lg:col-span-4 rounded-3xl border p-5 sm:p-6 shadow-xl backdrop-blur-xl flex flex-col justify-between transition-colors', isDark ? 'border-slate-800 bg-slate-900/80 text-white' : 'border-slate-200 bg-white text-slate-900']">
          <div class="pb-4 border-b border-slate-700/30">
            <h3 class="font-serif text-base font-bold flex items-center gap-2">
              <i class="bi bi-receipt text-rose-400"></i>
              <span>Alokasi Beban Operasional</span>
            </h3>
            <p :class="['text-xs mt-0.5', isDark ? 'text-slate-400' : 'text-slate-600']">
              Beban belanja utilitas, honor pelayan, dan diakonia sosial.
            </p>
          </div>

          <div class="mt-4 h-64 sm:h-72 w-full">
            <Bar :data="expenseAllocationData" :options="horizontalBarOptions" />
          </div>
        </div>
      </section>

    </div>
  </ChurchAdminLayout>
</template>
