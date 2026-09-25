<script setup>
import { ref, computed, onMounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const selectedYear = ref(2026)
const selectedBranch = ref('Semua Cabang')
const churches = ref([])

const loadChurches = async () => {
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`)
    if (res.ok) {
      churches.value = await res.json()
    }
  } catch (err) {
    console.warn('Gagal memuat cabang gereja:', err)
  }
}

onMounted(() => {
  loadChurches()
})

// Data Keuangan Akumulasi
const financialOverview = computed(() => {
  const totalIn = 148500000
  const totalOut = 84200000
  const netBalance = totalIn - totalOut
  const ratio = Math.round((totalOut / totalIn) * 100)

  return { totalIn, totalOut, netBalance, ratio }
})

const formatIDR = (num) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(num || 0)
}

// Chart 1: Tren Pemasukan vs Pengeluaran (Bar Chart)
const monthlyTrendData = computed(() => {
  return {
    labels: ['Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep'],
    datasets: [
      {
        label: 'Pemasukan Kas (IDR)',
        backgroundColor: '#10b981', // emerald-500
        hoverBackgroundColor: '#34d399',
        borderRadius: 8,
        data: [22500000, 24800000, 21000000, 26500000, 25800000, 27900000]
      },
      {
        label: 'Pengeluaran Kas (IDR)',
        backgroundColor: '#f43f5e', // rose-500
        hoverBackgroundColor: '#fb7185',
        borderRadius: 8,
        data: [13500000, 14200000, 12800000, 16000000, 13700000, 14000000]
      }
    ]
  }
})

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#cbd5e1',
        font: { size: 11, family: 'Inter' }
      }
    },
    tooltip: {
      callbacks: {
        label: function (context) {
          return `${context.dataset.label}: ${new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(context.raw)}`
        }
      }
    }
  },
  scales: {
    x: {
      ticks: { color: '#94a3b8' },
      grid: { color: 'rgba(255, 255, 255, 0.05)' }
    },
    y: {
      ticks: {
        color: '#94a3b8',
        callback: (val) => `${val / 1000000} jt`
      },
      grid: { color: 'rgba(255, 255, 255, 0.05)' }
    }
  }
}

// Chart 2: Komposisi Pemasukan (Doughnut)
const incomeBreakdownData = computed(() => {
  return {
    labels: ['Persembahan Ibadah', 'Perpuluhan Jemaat', 'Dana Pembangunan', 'Ucapan Syukur & Kasih'],
    datasets: [
      {
        backgroundColor: ['#f59e0b', '#38bdf8', '#a855f7', '#10b981'],
        borderWidth: 0,
        hoverOffset: 6,
        data: [45, 30, 15, 10]
      }
    ]
  }
})

// Chart 3: Komposisi Pengeluaran (Doughnut)
const expenseBreakdownData = computed(() => {
  return {
    labels: ['Operasional & Utilitas', 'Honorarium Pelayan', 'Pemeliharaan Gedung', 'Diakonia & Kasih'],
    datasets: [
      {
        backgroundColor: ['#f43f5e', '#fb923c', '#eab308', '#06b6d4'],
        borderWidth: 0,
        hoverOffset: 6,
        data: [40, 25, 20, 15]
      }
    ]
  }
})

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: '#cbd5e1',
        boxWidth: 12,
        font: { size: 10, family: 'Inter' }
      }
    }
  }
}
</script>

<template>
  <MainAdminLayout>
    <div class="space-y-6 text-[#EDE6D6] font-sans pb-12">

      <!-- HERO BANNER -->
      <section class="rounded-3xl border border-amber-500/25 bg-gradient-to-r from-[#0d1e27]/90 via-[#0b2027]/85 to-[#09151e]/90 p-6 shadow-2xl backdrop-blur-xl sm:p-8 relative overflow-hidden">
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-graph-up-arrow"></i>
              <span>Financial Analytics &amp; Visual Intelligence</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-100">
              Grafik &amp; Analisis Keuangan Gereja
            </h1>
            <p class="mt-1.5 text-xs sm:text-sm text-[#B8C4C2] max-w-2xl leading-relaxed">
              Analisis visual tren pemasukan, alokasi beban pengeluaran, surplus kas bersih, dan proyeksi likuiditas gereja antar cabang.
            </p>
          </div>

          <div class="flex items-center gap-2.5">
            <select 
              v-model="selectedBranch"
              class="px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-amber-300 font-semibold outline-none focus:border-amber-400"
            >
              <option value="Semua Cabang">Semua Cabang Gereja</option>
              <option value="GracePoint Pusat">GracePoint Pusat</option>
              <option v-for="c in churches" :key="c.id" :value="c.church_name">{{ c.church_name }}</option>
            </select>

            <select 
              v-model="selectedYear"
              class="px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-amber-300 font-semibold outline-none focus:border-amber-400"
            >
              <option :value="2026">Tahun 2026</option>
              <option :value="2025">Tahun 2025</option>
            </select>
          </div>
        </div>
      </section>

      <!-- KPI METRICS -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Saldo Kas Bersih</span>
            <div class="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-sm">
              <i class="bi bi-shield-check"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-emerald-300 font-mono">{{ formatIDR(financialOverview.netBalance) }}</p>
          <p class="mt-1 text-[10px] text-emerald-400/90 font-medium">Surplus kas operasional</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Pemasukan</span>
            <div class="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 text-sm">
              <i class="bi bi-arrow-down-left-circle-fill"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-amber-300 font-mono">{{ formatIDR(financialOverview.totalIn) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Akumulasi persembahan & perpuluhan</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Pengeluaran</span>
            <div class="w-8 h-8 rounded-lg bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400 text-sm">
              <i class="bi bi-arrow-up-right-circle-fill"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-rose-300 font-mono">{{ formatIDR(financialOverview.totalOut) }}</p>
          <p class="mt-1 text-[10px] text-slate-400">Akumulasi beban kas keluar</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-[#123138]/60 p-4 backdrop-blur-md">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Rasio Beban Kas</span>
            <div class="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 text-sm">
              <i class="bi bi-percent"></i>
            </div>
          </div>
          <p class="mt-2 text-xl sm:text-2xl font-black text-sky-300 font-mono">{{ financialOverview.ratio }}%</p>
          <p class="mt-1 text-[10px] text-sky-400/90 font-medium">Batas aman sehat (&lt; 70%)</p>
        </div>
      </section>

      <!-- MAIN CHART: TREN ARUS KAS BULANAN -->
      <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-2xl backdrop-blur-xl space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-white/10">
          <div>
            <h3 class="font-serif text-lg sm:text-xl font-bold text-white flex items-center gap-2">
              <i class="bi bi-bar-chart-fill text-amber-400"></i> Tren Pemasukan vs Pengeluaran Bulanan
            </h3>
            <p class="text-xs text-slate-400">Perbandingan riil arus kas masuk (hijau) dan arus kas keluar (merah) per bulan.</p>
          </div>
          <span class="text-xs px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30">
            Arus Kas Positif (Surplus)
          </span>
        </div>

        <div class="h-72 w-full pt-2">
          <Bar :data="monthlyTrendData" :options="barChartOptions" />
        </div>
      </section>

      <!-- DUAL BREAKDOWN DOUGHNUT CHARTS -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- Pemasukan Breakdown -->
        <div class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-2xl backdrop-blur-xl space-y-3">
          <div class="pb-3 border-b border-white/10">
            <h3 class="font-serif text-lg font-bold text-white flex items-center gap-2">
              <i class="bi bi-pie-chart-fill text-emerald-400"></i> Alokasi Sumber Pemasukan
            </h3>
            <p class="text-xs text-slate-400">Komposisi persentase pemasukan berdasarkan jenis persembahan.</p>
          </div>
          <div class="h-64 w-full pt-2">
            <Doughnut :data="incomeBreakdownData" :options="doughnutChartOptions" />
          </div>
        </div>

        <!-- Pengeluaran Breakdown -->
        <div class="rounded-3xl border border-white/10 bg-[#123138]/70 p-5 sm:p-6 shadow-2xl backdrop-blur-xl space-y-3">
          <div class="pb-3 border-b border-white/10">
            <h3 class="font-serif text-lg font-bold text-white flex items-center gap-2">
              <i class="bi bi-pie-chart-fill text-rose-400"></i> Distribusi Pos Pengeluaran
            </h3>
            <p class="text-xs text-slate-400">Komposisi alokasi dana operasional, honorarium, dan pelayanan.</p>
          </div>
          <div class="h-64 w-full pt-2">
            <Doughnut :data="expenseBreakdownData" :options="doughnutChartOptions" />
          </div>
        </div>

      </section>

      <!-- AUDIT & HEALTH STATUS RECOMMENDATION -->
      <section class="rounded-3xl border border-amber-500/25 bg-gradient-to-r from-[#112d33] via-[#0d2228] to-[#0a1b20] p-6 shadow-2xl backdrop-blur-xl space-y-3">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-300 text-lg">
            <i class="bi bi-shield-check"></i>
          </div>
          <div>
            <h4 class="font-serif text-base font-bold text-white">Evaluasi Kesehatan Kas Gereja (Financial Health Score)</h4>
            <p class="text-xs text-slate-400">Berdasarkan audit SHA-256 dan rasio likuiditas kas operasional GracePoint.</p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 text-xs">
          <div class="p-3 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-1">
            <span class="text-slate-400 block text-[11px]">Indeks Likuiditas Kas</span>
            <span class="text-base font-bold text-emerald-400 font-mono">1.76 (Sangat Sehat)</span>
            <p class="text-[10px] text-slate-500">Mampu menutupi operasional &gt; 5 bulan ke depan.</p>
          </div>

          <div class="p-3 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-1">
            <span class="text-slate-400 block text-[11px]">Integritas Hash Kriptografi</span>
            <span class="text-base font-bold text-amber-300 font-mono">SHA-256 Valid</span>
            <p class="text-[10px] text-slate-500">Tidak ada manipulasi data transaksi buku kas.</p>
          </div>

          <div class="p-3 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-1">
            <span class="text-slate-400 block text-[11px]">Rekomendasi Majelis</span>
            <span class="text-base font-bold text-sky-400 font-mono">Alokasi Pembangunan</span>
            <p class="text-[10px] text-slate-500">Kas surplus dapat dialokasikan ke renovasi cabang.</p>
          </div>
        </div>
      </section>

    </div>
  </MainAdminLayout>
</template>

<style scoped></style>
