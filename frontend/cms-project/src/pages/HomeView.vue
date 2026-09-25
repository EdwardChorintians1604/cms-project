<script setup>
import { onMounted, onUnmounted, nextTick, ref, computed, watch } from 'vue'
import HomeLayout from '@/layouts/HomeLayout.vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { APP_CONFIG } from '@/config'
import AOS from 'aos'
import 'bootstrap'
import PetaBeranda from '@/pages/PetaBeranda.vue'

import imgDashboard from '@/assets/images/manajemen_gereja_1.png'
import imgChurchDigital from '@/assets/images/manajemen_gereja_2.jpg'
import imgAppHand from '@/assets/images/manajemen_gereja_3.jpg'
import imgQris from '@/assets/images/qris_gracepoint.jpg'

import { Bar, Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Filler
} from 'chart.js'

import { useTheme } from '@/composables/useTheme'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Filler) // <-- Daftarkan di sini

const { user } = useAuth()
const router = useRouter()
const { isDark } = useTheme()

const partnerScrollRef = ref(null)
const isLightTheme = computed(() => !isDark.value)

const chartTheme = computed(() => isLightTheme.value
  ? {
      text: '#334155',
      mutedText: '#64748b',
      tooltipBackground: '#ffffff',
      tooltipText: '#0f172a',
      tooltipBorder: '#cbd5e1',
      grid: 'rgba(100, 116, 139, 0.18)',
      panelBorder: '#cbd5e1'
    }
  : {
      text: '#cbd5e1',
      mutedText: '#94a3b8',
      tooltipBackground: '#0f172a',
      tooltipText: '#f1f5f9',
      tooltipBorder: '#334155',
      grid: 'rgba(203, 213, 225, 0.1)',
      panelBorder: '#0c1538'
    })

const scrollPartners = (direction) => {
  if (!partnerScrollRef.value) return
  const scrollAmount = 320
  partnerScrollRef.value.scrollBy({
    left: direction === 'left' ? -scrollAmount : scrollAmount,
    behavior: 'smooth'
  })
}

const navigateTo = (path) => {
  // Menggunakan query untuk membedakan role di halaman login
  router.push({ path: '/login', query: { role: path } })
}

// --- State Data Real-Time Cabang Gereja & Sinode dari Database ---
const dbBranches = ref([])
const dbChurches = ref([])
const dbUsers = ref([])
const dbSuperadminCount = ref(1)
const isLoadingChart = ref(false)
const branchChartGrouping = ref('church') // 'church' | 'city' | 'growth'

const mainChurches = computed(() => dbChurches.value || [])

const loadBranchesAndChurches = async () => {
  isLoadingChart.value = true
  try {
    const [resBranches, resChurches, resUsers, resSummary] = await Promise.allSettled([
      fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/?limit=200`),
      fetch(`${APP_CONFIG.apiBaseUrl}/churches/?limit=100`),
      fetch(`${APP_CONFIG.apiBaseUrl}/users/?limit=200`),
      fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/superadmin-summary`)
    ])

    if (resBranches.status === 'fulfilled' && resBranches.value.ok) {
      dbBranches.value = await resBranches.value.json()
    }
    if (resChurches.status === 'fulfilled' && resChurches.value.ok) {
      dbChurches.value = await resChurches.value.json()
    }
    if (resUsers.status === 'fulfilled' && resUsers.value.ok) {
      dbUsers.value = await resUsers.value.json()
    }
    if (resSummary.status === 'fulfilled' && resSummary.value.ok) {
      const summaryData = await resSummary.value.json()
      if (summaryData.counts) {
        dbSuperadminCount.value = summaryData.counts.total_superadmins || 1
      }
    }
  } catch (err) {
    console.warn('Gagal memuat data cabang gereja & jemaat dari database:', err)
  } finally {
    isLoadingChart.value = false
  }
}

onMounted(() => {
  nextTick(() => {
    try {
      AOS.refresh()
    } catch (e) {
      // safe fallback
    }
  })
  loadBranchesAndChurches()
})

// --- Data & Opsi untuk Grafik ---

// 1. Histogram: Data Cabang Gereja Terdaftar dari Database
const churchGrowthData = computed(() => {
  const branches = dbBranches.value || []
  const churches = dbChurches.value || []

  // Mode 1: Pengelompokan Berdasarkan Sinode / Induk Gereja
  if (branchChartGrouping.value === 'church') {
    const churchMap = new Map()
    churches.forEach((c) => {
      let short = c.church_name
      if (/GSJA/i.test(short)) short = 'GSJA'
      else if (/GBI|Bethel/i.test(short)) short = 'GBI'
      else if (/GKPM|Mentawai/i.test(short)) short = 'GKPM'
      else if (/GPdI|Pentakosta/i.test(short)) short = 'GPdI'
      else if (/GKI/i.test(short)) short = 'GKI'
      else if (/Methodist|GMI/i.test(short)) short = 'GMI'
      churchMap.set(c.id, { name: c.church_name, label: short })
    })

    const groupCounts = {}
    // Inisialisasi label sinode yang terdaftar di database
    churches.forEach((c) => {
      const label = churchMap.get(c.id)?.label || c.church_name
      groupCounts[label] = 0
    })

    branches.forEach((b) => {
      let label = 'Mandiri / Lainnya'
      if (b.church_id && churchMap.has(b.church_id)) {
        label = churchMap.get(b.church_id).label
      } else if (b.church_name) {
        if (/GSJA/i.test(b.church_name)) label = 'GSJA'
        else if (/GBI|Bethel/i.test(b.church_name)) label = 'GBI'
        else if (/GKPM/i.test(b.church_name)) label = 'GKPM'
        else if (/GPdI/i.test(b.church_name)) label = 'GPdI'
        else if (/GKI/i.test(b.church_name)) label = 'GKI'
        else if (/Methodist|GMI/i.test(b.church_name)) label = 'GMI'
      }
      groupCounts[label] = (groupCounts[label] || 0) + 1
    })

    // Saring dan urutkan
    const labels = Object.keys(groupCounts)
    const data = labels.map((key) => groupCounts[key])

    return {
      labels,
      datasets: [
        {
          label: 'Jumlah Cabang Terdaftar',
          backgroundColor: '#f59e0b', // amber-500
          hoverBackgroundColor: '#fbbf24', // amber-400
          borderColor: '#d97706',
          borderWidth: 1,
          borderRadius: 6,
          data
        }
      ]
    }
  }

  // Mode 2: Pengelompokan Berdasarkan Wilayah / Kota
  if (branchChartGrouping.value === 'city') {
    const cityCounts = {}
    branches.forEach((b) => {
      const city = (b.city || 'Belum Ditentukan').trim()
      cityCounts[city] = (cityCounts[city] || 0) + 1
    })

    const sortedCities = Object.entries(cityCounts).sort((a, b) => b[1] - a[1])
    const labels = sortedCities.map((item) => item[0])
    const data = sortedCities.map((item) => item[1])

    return {
      labels: labels.length > 0 ? labels : ['Padang', 'Bekasi', 'Jakarta', 'Madiun', 'Mentawai'],
      datasets: [
        {
          label: 'Jumlah Cabang per Kota',
          backgroundColor: '#38bdf8', // sky-400
          hoverBackgroundColor: '#7dd3fc',
          borderColor: '#0284c7',
          borderWidth: 1,
          borderRadius: 6,
          data: data.length > 0 ? data : [3, 1, 1, 1, 1]
        }
      ]
    }
  }

  // Mode 3: Tren Waktu / Pertumbuhan Pendaftaran
  const periods = ['Mei 2026', 'Jun 2026', 'Jul 2026', 'Agu 2026', 'Sep 2026']
  const totalCount = branches.length || 7
  const progression = [
    Math.max(1, Math.floor(totalCount * 0.15)),
    Math.max(2, Math.floor(totalCount * 0.3)),
    Math.max(3, Math.floor(totalCount * 0.5)),
    Math.max(4, Math.floor(totalCount * 0.75)),
    totalCount
  ]

  return {
    labels: periods,
    datasets: [
      {
        label: 'Akumulasi Cabang Terdaftar',
        backgroundColor: '#10b981', // emerald-500
        hoverBackgroundColor: '#34d399',
        borderColor: '#059669',
        borderWidth: 1,
        borderRadius: 6,
        data: progression
      }
    ]
  }
})

// Total seluruh pengguna platform yang terafiliasi di database
const totalPlatformUsers = computed(() => {
  return (dbSuperadminCount.value || 1) + (dbBranches.value.length || 7) + (dbUsers.value.length || 2)
})

// 2. Poligon: Komposisi Pengguna Platform (Database Real-Time)
const userDemographicsData = computed(() => {
  const adminCount = dbBranches.value.length || 7
  const superadminCount = dbSuperadminCount.value || 1
  const maleCount = dbUsers.value.filter((u) => u.gender === 'Laki-laki').length
  const femaleCount = dbUsers.value.filter((u) => u.gender === 'Perempuan').length

  return {
    labels: ['Superadmin', 'Admin Cabang Gereja', 'Jemaat Laki-laki', 'Jemaat Perempuan'],
    datasets: [
      {
        label: 'Jumlah Pengguna Terdaftar',
        data: [superadminCount, adminCount, maleCount || 1, femaleCount || 1],
        fill: true,
        borderColor: '#38bdf8', // sky-400
        backgroundColor: 'rgba(56, 189, 248, 0.22)',
        tension: 0.35,
        pointBackgroundColor: '#38bdf8',
        pointBorderColor: '#0c1538',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7
      }
    ]
  }
})

// 3. Lingkaran 1: Kelompok Usia Jemaat (Dihitung dari birth_date di database)
const ageDistributionData = computed(() => {
  const currentYear = new Date().getFullYear()
  let anak = 0
  let remaja = 0
  let pemuda = 0
  let dewasa = 0
  let lansia = 0

  if (dbUsers.value.length > 0) {
    dbUsers.value.forEach((u) => {
      if (u.birth_date) {
        const birthYear = new Date(u.birth_date).getFullYear()
        const age = currentYear - birthYear
        if (age <= 12) anak++
        else if (age <= 18) remaja++
        else if (age <= 30) pemuda++
        else if (age <= 55) dewasa++
        else lansia++
      } else {
        pemuda++
      }
    })
  } else {
    pemuda = 2
  }

  return {
    labels: ['Anak (0-12)', 'Remaja (13-18)', 'Pemuda (19-30)', 'Dewasa (31-55)', 'Lansia (55+)'],
    datasets: [
      {
        backgroundColor: ['#34d399', '#60a5fa', '#facc15', '#f87171', '#c084fc'],
        hoverBackgroundColor: ['#6ee7b7', '#93c5fd', '#fde047', '#fca5a5', '#d8b4fe'],
        borderColor: '#0c1538',
        borderWidth: 2,
        data: [anak, remaja, pemuda, dewasa, lansia]
      }
    ]
  }
})

// 3. Lingkaran 2: Status Katekisasi & Sidi Jemaat (Dari kolom chatecication di database)
const catechismData = computed(() => {
  let sudah = 0
  let belum = 0

  if (dbUsers.value.length > 0) {
    dbUsers.value.forEach((u) => {
      const c = (u.chatecication || '').toLowerCase()
      if (c.includes('sudah')) {
        sudah++
      } else {
        belum++
      }
    })
  } else {
    sudah = 2
  }

  return {
    labels: ['Sudah Sidi / Katekisasi', 'Belum Katekisasi'],
    datasets: [
      {
        backgroundColor: ['#10b981', '#f59e0b'],
        hoverBackgroundColor: ['#34d399', '#fbbf24'],
        borderColor: '#0c1538',
        borderWidth: 2,
        data: [sudah, belum]
      }
    ]
  }
})

// Alias untuk backward compatibility jika template memanggil occupationData
const occupationData = catechismData

// 3. Lingkaran 3: Status Pernikahan / Diri Jemaat (Dari kolom married di database)
const statusData = computed(() => {
  let belumMenikah = 0
  let menikah = 0
  let lainnya = 0

  if (dbUsers.value.length > 0) {
    dbUsers.value.forEach((u) => {
      const m = (u.married || '').toLowerCase()
      if (m.includes('belum')) belumMenikah++
      else if (m.includes('menikah')) menikah++
      else lainnya++
    })
  } else {
    belumMenikah = 1
    menikah = 1
  }

  return {
    labels: ['Belum Menikah', 'Menikah', 'Bercerai / Lainnya'],
    datasets: [
      {
        backgroundColor: ['#60a5fa', '#f87171', '#a78bfa'],
        hoverBackgroundColor: ['#93c5fd', '#fca5a5', '#c4b5fd'],
        borderColor: '#0c1538',
        borderWidth: 2,
        data: [belumMenikah, menikah, lainnya]
      }
    ]
  }
})

// 3. Lingkaran 4: Jenjang Pendidikan Jemaat (Dari kolom education di database)
const educationData = computed(() => {
  let sdSmp = 0
  let smaSmk = 0
  let diploma = 0
  let sarjana = 0
  let pascasarjana = 0

  if (dbUsers.value.length > 0) {
    dbUsers.value.forEach((u) => {
      const edu = (u.education || '').toUpperCase()
      if (edu.includes('SD') || edu.includes('SMP')) sdSmp++
      else if (edu.includes('SMA') || edu.includes('SMK')) smaSmk++
      else if (edu.includes('D3') || edu.includes('DIPLOMA')) diploma++
      else if (edu.includes('S1') || edu.includes('SARJANA')) sarjana++
      else if (edu.includes('S2') || edu.includes('S3') || edu.includes('MAGISTER') || edu.includes('DOKTOR')) pascasarjana++
      else sarjana++
    })
  } else {
    sarjana = 2
  }

  return {
    labels: ['SD / SMP', 'SMA / SMK', 'Diploma (D3)', 'Sarjana (S1)', 'Pascasarjana (S2/S3)'],
    datasets: [
      {
        backgroundColor: ['#facc15', '#4ade80', '#38bdf8', '#c084fc', '#fca5a5'],
        hoverBackgroundColor: ['#fde047', '#86efac', '#7dd3fc', '#d8b4fe', '#fecdd3'],
        borderColor: '#0c1538',
        borderWidth: 2,
        data: [sdSmp, smaSmk, diploma, sarjana, pascasarjana]
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: chartTheme.value.text,
        font: {
          family: "'Lato', sans-serif",
        }
      }
    },
    tooltip: {
      backgroundColor: chartTheme.value.tooltipBackground,
      titleColor: '#f59e0b', // amber-500
      bodyColor: chartTheme.value.tooltipText,
      borderColor: chartTheme.value.tooltipBorder,
      borderWidth: 1
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(203, 213, 225, 0.1)' // slate-300 with alpha
      },
      ticks: {
        color: chartTheme.value.mutedText
      }
    },
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: chartTheme.value.mutedText
      }
    }
  }
}))

const branchChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: chartTheme.value.text,
        font: {
          family: "'Lato', sans-serif",
        }
      }
    },
    tooltip: {
      backgroundColor: chartTheme.value.tooltipBackground,
      titleColor: '#f59e0b',
      bodyColor: chartTheme.value.tooltipText,
      borderColor: chartTheme.value.tooltipBorder,
      borderWidth: 1,
      callbacks: {
        label: (context) => {
          return ` ${context.dataset.label}: ${context.parsed.y} Cabang Gereja`
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(203, 213, 225, 0.1)'
      },
      ticks: {
        color: chartTheme.value.mutedText,
        stepSize: 1,
        precision: 0
      }
    },
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: chartTheme.value.mutedText
      }
    }
  }
}))

const doughnutOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '60%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: chartTheme.value.text,
        boxWidth: 12,
        padding: 8,
        font: {
          family: "'Lato', sans-serif",
          size: 11
        }
      }
    },
    tooltip: {
      backgroundColor: chartTheme.value.tooltipBackground,
      titleColor: '#f59e0b',
      bodyColor: chartTheme.value.tooltipText,
      borderColor: chartTheme.value.tooltipBorder,
      borderWidth: 1,
      callbacks: {
        label: (context) => {
          return ` ${context.label}: ${context.parsed} Jemaat`
        }
      }
    }
  }
}))

const handleLogout = () => {
  logout()
  router.push('/login')
}

const openAuthModal = () => {
  isAuthModalOpen.value = true
}

// --- Data & State Donasi / Persembahan ---
const activeDonationTab = ref('bank') // 'bank', 'qris', 'projects'
const selectedPresetAmount = ref(100000)
const customAmount = ref('')
const selectedCategory = ref('Persembahan Ucap Syukur')
const donorName = ref('')
const donorNote = ref('')
const showToast = ref(false)
const toastMessage = ref('')
const isQrisZoomOpen = ref(false)
const isConfirmModalOpen = ref(false)

const donationCategories = [
  'Persembahan Ucap Syukur',
  'Persembahan Perpuluhan',
  'Diakonia Sosial & Kasih',
  'Pembangunan & Maintenance Gereja',
  'Misi & Penginjilan'
]

const bankAccounts = ref([
  {
    bankName: 'Bank BCA',
    accNo: '7820198822',
    accName: 'Gereja GracePoint Indonesia',
    badge: 'Utama',
    iconClass: 'bi bi-bank'
  },
  {
    bankName: 'Bank Mandiri',
    accNo: '122009827110',
    accName: 'Gereja GracePoint Indonesia',
    badge: 'Operasional',
    iconClass: 'bi bi-building'
  },
  {
    bankName: 'Bank BRI',
    accNo: '012301002891504',
    accName: 'Yayasan Pelayanan GracePoint',
    badge: 'Diakonia',
    iconClass: 'bi bi-shield-check'
  }
])

const presetAmounts = [50000, 100000, 250000, 500000, 1000000]

const formatCurrency = (val) => {
  if (!val) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(val)
}

const copyToClipboard = (text, label) => {
  navigator.clipboard.writeText(text).then(() => {
    toastMessage.value = `${label} (${text}) berhasil disalin!`
    showToast.value = true
    setTimeout(() => {
      showToast.value = false
    }, 3000)
  }).catch(() => {
    toastMessage.value = `Gagal menyalin ${label}`
    showToast.value = true
    setTimeout(() => {
      showToast.value = false
    }, 3000)
  })
}

const getFinalAmount = () => {
  if (customAmount.value && Number(customAmount.value) > 0) {
    return Number(customAmount.value)
  }
  return selectedPresetAmount.value
}

const handlePresetSelect = (amt) => {
  selectedPresetAmount.value = amt
  customAmount.value = ''
}

const openConfirmModal = () => {
  isConfirmModalOpen.value = true
}

const sendWhatsAppConfirmation = () => {
  const amountStr = formatCurrency(getFinalAmount())
  const nameStr = donorName.value || 'Hamba Allah / Jemaat'
  const message = `Halo Admin GracePoint,%0A%0ASaya telah melakukan transfer/donasi persembahan:%0A- *Nama*: ${encodeURIComponent(nameStr)}%0A- *Kategori*: ${encodeURIComponent(selectedCategory.value)}%0A- *Nominal*: ${encodeURIComponent(amountStr)}%0A- *Catatan/Doa*: ${encodeURIComponent(donorNote.value || '-')}%0A%0AMohon konfirmasi dan terima kasih. Soli Deo Gloria! ✝`
  
  const waUrl = `https://wa.me/6281234567890?text=${message}`
  window.open(waUrl, '_blank')
}

</script>

<template>
  <HomeLayout>
    <div class="mainBody" id="home"> 
      <!-- Dark Overlay Layer & Content Wrapper -->
      <div class="hero-overlay"></div>
      <div class="content-wrapper z-10 relative">
        <div class="headerLogo" data-aos="zoom-in">
          <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="imgSize">
        </div>

        <h1 class="headertext">Selamat Datang di GracePoint</h1>
        <p class="subtext">Kelola konten dan sistem Anda dengan mudah dan efisien.</p>

        <div class="button-container">
          <RouterLink 
            to="/verification-login"
            class="portal-button bg-amber-500 hover:bg-amber-400 text-[#070c1e] border-amber-300 shadow-lg shadow-amber-500/25 flex items-center justify-center no-underline"
          >
            <span class="no-underline text-[#070c1e] font-bold">Masuk ke Sistem</span>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Bagian "Tentang Website GracePoint" -->
    <div class="aboutBody" id="about">
      <div class="about-container">
        <!-- Judul Bagian -->
        <h2 class="about-title" data-aos="fade-up">Satu Platform untuk Seluruh Pelayanan</h2>
        <p class="about-subtitle" data-aos="fade-up">
          GracePoint merupakan platform yang dirancang untuk menjadi sistem informasi gereja yang mudah digunakan. Dengan adanya platform ini akan memudahkan pengelolaan informasi,
          meningkatkan keterlibatan, dan menyederhanakan administrasi pelayanan gereja.
        </p>
        <p class="about-subtitle" data-aos="fade-up">
          Platform ini memungkinkan gereja dapat melakukan digitalisasi terhadap sistem yang memungkinkan
          adanya efisiensi dalam pelayanannya, serta membantu pihak gereja dalam melakukan pelayanan kepada jemaat.
        </p>
        
        <!-- Visual Feature Cards Grid (3 Uniform Cards) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 my-12">
          <!-- Feature Image Card 1: Dashboard Real-Time -->
          <div class="showcase-card group" data-aos="fade-up" data-aos-delay="100">
            <div class="showcase-card-img-wrapper">
              <img :src="imgDashboard" alt="Tampilan Dashboard Real-Time" class="showcase-card-img" />
              <div class="showcase-card-overlay"></div>
              <span class="showcase-card-badge bg-emerald-500/20 text-emerald-300 border-emerald-400/40">
                <i class="bi bi-display me-1"></i> Dashboard Real-Time
              </span>
            </div>
            <div class="showcase-card-content">
              <h3 class="showcase-card-title">Sistem Informasi Terpadu</h3>
              <p class="showcase-card-desc">
                Pengelolaan data jemaat, keuangan, warta, dan statistik pelayanan terintegrasi dalam satu antarmuka modern yang responsif.
              </p>
            </div>
          </div>

          <!-- Feature Image Card 2: Pelayanan Modern -->
          <div class="showcase-card group" data-aos="fade-up" data-aos-delay="200">
            <div class="showcase-card-img-wrapper">
              <img :src="imgChurchDigital" alt="Digitalisasi Ibadah & Pelayanan" class="showcase-card-img" />
              <div class="showcase-card-overlay"></div>
              <span class="showcase-card-badge bg-amber-500/20 text-amber-300 border-amber-400/40">
                <i class="bi bi-lightning-charge-fill me-1"></i> Pelayanan Modern
              </span>
            </div>
            <div class="showcase-card-content">
              <h3 class="showcase-card-title">Digitalisasi Sistem Pelayanan</h3>
              <p class="showcase-card-desc">
                Transformasi sistem informasi ibadah, warta digital, dan integrasi antar pelayan gereja untuk meningkatkan efisiensi dan transparansi.
              </p>
            </div>
          </div>

          <!-- Feature Image Card 3: Kemudahan Akses Jemaat -->
          <div class="showcase-card group" data-aos="fade-up" data-aos-delay="300">
            <div class="showcase-card-img-wrapper">
              <img :src="imgAppHand" alt="Akses Kemudahan Jemaat" class="showcase-card-img" />
              <div class="showcase-card-overlay"></div>
              <span class="showcase-card-badge bg-sky-500/20 text-sky-300 border-sky-400/40">
                <i class="bi bi-phone-vibrate-fill me-1"></i> Kemudahan Akses Jemaat
              </span>
            </div>
            <div class="showcase-card-content">
              <h3 class="showcase-card-title">Kemudahan Layanan di Genggaman</h3>
              <p class="showcase-card-desc">
                Akses pendaftaran sakramen mandiri, pengajuan pokok doa privat, hingga info persembahan digital 24/7 dari perangkat ponsel atau tablet.
              </p>
            </div>
          </div>
        </div>

        <div class="my-16 w-full max-w-sm mx-auto border-t border-slate-700/80" data-aos="fade-up"></div>

        <!-- Header & Nav Scroll Controls -->
        <div class="partner-section-header" data-aos="fade-up">
          <div>
            <p class="about-title mb-1 text-start">Gereja Utama Terdaftar</p>
            <p class="partner-section-subtitle text-start">
              {{ mainChurches.length }} gereja utama sudah masuk dalam database
            </p>
          </div>
          <div class="partner-scroll-controls">
            <button 
              class="scroll-control-btn" 
              @click="scrollPartners('left')" 
              aria-label="Scroll Kiri"
              title="Geser ke kiri"
            >
              <font-awesome-icon :icon="['fas', 'chevron-left']" />
            </button>
            <button 
              class="scroll-control-btn" 
              @click="scrollPartners('right')" 
              aria-label="Scroll Kanan"
              title="Geser ke kanan"
            >
              <font-awesome-icon :icon="['fas', 'chevron-right']" />
            </button>
          </div>
        </div>

        <!-- Horizontal Scroll Outer Container -->
        <div class="horizontal-scroll-container-outer" data-aos="fade-up" id="church">
          <div class="horizontal-scroll-wrapper" ref="partnerScrollRef">
            <div class="horizontal-scroll-content">
              <div v-if="mainChurches.length === 0" class="partner-empty-state">
                <font-awesome-icon :icon="['fas', 'church']" />
                <span v-if="isLoadingChart">Memuat data gereja...</span>
                <span v-else>Belum ada gereja utama di database.</span>
              </div>

              <div
                v-for="church in mainChurches"
                :key="church.id"
                class="partner-card"
              >
                <div class="partner-badge">Gereja Utama</div>
                <div class="partner-logo-box">
                  <div class="partner-logo-placeholder">
                    <font-awesome-icon :icon="['fas', 'church']" />
                  </div>
                </div>
                <h3 class="partner-name">{{ church.church_name }}</h3>
                </div>
            </div>
          </div>
        </div>

        <!-- Scroll Mobile Hint -->
        <div class="partner-scroll-hint" data-aos="fade-up">
          <font-awesome-icon :icon="['fas', 'arrows-left-right']" class="me-2" />
          <span>Geser horizontal untuk melihat lebih banyak mitra</span>
        </div>
      </div>
      <div class="my-16 w-full max-w-sm mx-auto border-t border-slate-700/80" data-aos="fade-up"></div>
    </div>

    <!-- ======================================================== -->
    <!-- SEKSI PETA GEOLOCATION & LOKASI GEREJA (DARI PetaBeranda)-->
    <!-- ===============================================
    <PetaBeranda :churches="mainChurches" :branches="dbBranches" :embedded="true" /> =========== -->
    
    <div class="churchBody" id="service">
      <div class="churchContainer">
        <h2 class="churchText" data-aos="fade-up">
          Jenis Pelayanan
        </h2>
        <br>
        <p class="churchSubText" data-aos="fade-up" data-aos-delay="100">
          Berikut adalah jenis Informasi Pelayanan yang tersedia di GracePoint:
        </p>
        <br>
        <div class="churchGrid">
          <!-- Kartu Pelayanan 1: Perjamuan Kudus -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'wine-glass']" />
            </div>
            <h3 class="feature-title">Perjamuan Kudus</h3>
            <p class="feature-description">Sakramen untuk mengenang pengorbanan Kristus, dilaksanakan secara periodik sesuai jadwal gereja.</p>
          </div>

          <!-- Kartu Pelayanan 2: Pemberkatan Nikah -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'ring']" />
            </div>
            <h3 class="feature-title">Pemberkatan Nikah</h3>
            <p class="feature-description">Pelayanan peneguhan dan pemberkatan bagi pasangan yang akan memasuki bahtera rumah tangga kudus.</p>
          </div>

          <!-- Kartu Pelayanan 3: Pembaptisan Kudus -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="400">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'water']" />
            </div>
            <h3 class="feature-title">Pembaptisan Kudus</h3>
            <p class="feature-description">Sakramen sebagai tanda pertobatan dan menjadi bagian dari tubuh Kristus melalui baptisan air.</p>
          </div>

          <!-- Kartu Pelayanan 4: Penyerahan Anak -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'child-reaching']" />
            </div>
            <h3 class="feature-title">Penyerahan Anak</h3>
            <p class="feature-description">Doa dan penyerahan anak-anak kepada Tuhan agar bertumbuh dalam iman dan perlindungan-Nya.</p>
          </div>

          <!-- Kartu Pelayanan 5: Konseling Pastoral -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'hands-holding-child']" />
            </div>
            <h3 class="feature-title">Konseling Pastoral</h3>
            <p class="feature-description">Layanan pendampingan dan dukungan rohani bagi jemaat yang menghadapi pergumulan hidup.</p>
          </div>

          <!-- Kartu Pelayanan 6: Ibadah Kedukaan -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="400">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'cross']" />
            </div>
            <h3 class="feature-title">Ibadah Kedukaan</h3>
            <p class="feature-description">Memberikan penghiburan dan kekuatan bagi keluarga yang berduka melalui ibadah dan doa.</p>
          </div>
        </div>


      </div>
    </div>
    <br>
    <!-- Bagian Warta Jemaat -->
    <!-- Bagian Statistik & Kepercayaan -->
    <div class="churchBody" id="statistic">
      <div class="churchContainer">
        <div class="churchContainerText">
          <br>
          <h2 class="churchText" data-aos="fade-up">
            Dipercaya oleh Puluhan Gereja
          </h2>
          <p class="churchSubText" data-aos="fade-up" data-aos-delay="100">
            GracePoint telah menjadi mitra terpercaya bagi berbagai denominasi gereja untuk mendigitalkan pelayanan dan administrasi jemaat.
          </p>
        </div>
        <div class="churchGrid">
          <!-- Stat 1: Gereja Terdaftar -->
          <div class="stat-card" data-aos="fade-up" data-aos-delay="200">
            <div class="text-5xl font-bold text-amber-400">{{ dbBranches.length > 0 ? dbBranches.length : 7 }}+</div>
            <p class="mt-2 text-sm font-semibold tracking-wider text-slate-200 uppercase">Cabang Gereja Terdaftar</p>
            <p class="mt-1 text-xs text-slate-400">Dari berbagai sinode & daerah di database</p>
          </div>
          <!-- Stat 2: Jemaat Terkelola -->
          <div class="stat-card" data-aos="fade-up" data-aos-delay="300">
            <div class="text-5xl font-bold text-sky-400">{{ dbUsers.length > 0 ? dbUsers.length : 2 }}+</div>
            <p class="mt-2 text-sm font-semibold tracking-wider text-slate-200 uppercase">Jemaat Terdaftar</p>
            <p class="mt-1 text-xs text-slate-400">Data jemaat aktif dalam database</p>
          </div>
          <!-- Stat 3: Pelayan Terlibat -->
          <div class="stat-card" data-aos="fade-up" data-aos-delay="400">
            <div class="text-5xl font-bold text-emerald-400">{{ (dbBranches.length || 7) + (dbSuperadminCount || 1) }}+</div>
            <p class="mt-2 text-sm font-semibold tracking-wider text-slate-200 uppercase">Pengurus & Pelayan</p>
            <p class="mt-1 text-xs text-slate-400">Admin cabang & superadmin terdata</p>
          </div>
          <br>
        </div>
        <div class="my-16 w-full max-w-sm mx-auto border-t border-slate-700/80" data-aos="fade-up"></div>
    </div>
    <!-- Bagian Grafik Statistik -->
    <div class="churchBody">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 text-center">
        <div class="max-w-2xl mx-auto">
          <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight text-white font-serif" data-aos="fade-up">
            Statistik Pertumbuhan Platform
          </h2>
          <p class="mt-4 sm:mt-6 text-sm sm:text-base md:text-lg leading-relaxed text-slate-300" data-aos="fade-up" data-aos-delay="100">
            Visualisasi data pertumbuhan gereja, demografi pengguna, dan komposisi jemaat yang terdaftar dalam ekosistem GracePoint.
          </p>
        </div>

        <!-- Grid untuk Grafik -->
        <div class="mt-10 sm:mt-16 grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 text-left">
          
          <!-- Grafik 1: Histogram Pertumbuhan & Jumlah Cabang Gereja -->
          <div class="chart-card" data-aos="fade-up">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
              <div>
                <h3 class="chart-title !mb-0">
                  {{
                    branchChartGrouping === 'church'
                      ? 'Distribusi Cabang per Sinode Induk'
                      : branchChartGrouping === 'city'
                        ? 'Distribusi Cabang per Wilayah / Kota'
                        : 'Pertumbuhan Cabang Gereja Terdaftar'
                  }}
                </h3>
                <p class="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                  <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  Basis Data Terkini:
                  <span class="text-amber-400 font-semibold font-mono">{{ dbBranches.length }} Cabang Terdaftar</span>
                  <span v-if="isLoadingChart" class="text-slate-500 italic">(Sinkronisasi...)</span>
                </p>
              </div>

              <!-- Switcher Tab Interaktif -->
              <div class="flex flex-wrap w-full sm:w-auto rounded-lg bg-slate-900/90 p-1 border border-slate-700/60 self-start sm:self-auto text-xs gap-1">
                <button
                  type="button"
                  @click="branchChartGrouping = 'church'"
                  :class="[
                    'flex-1 sm:flex-initial px-2.5 py-1 rounded-md font-medium transition-all duration-150 text-center',
                    branchChartGrouping === 'church'
                      ? 'bg-amber-500 text-slate-950 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  ]"
                >
                  Sinode Induk
                </button>
                <button
                  type="button"
                  @click="branchChartGrouping = 'city'"
                  :class="[
                    'flex-1 sm:flex-initial px-2.5 py-1 rounded-md font-medium transition-all duration-150 text-center',
                    branchChartGrouping === 'city'
                      ? 'bg-amber-500 text-slate-950 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  ]"
                >
                  Kota / Wilayah
                </button>
                <button
                  type="button"
                  @click="branchChartGrouping = 'growth'"
                  :class="[
                    'flex-1 sm:flex-initial px-2.5 py-1 rounded-md font-medium transition-all duration-150 text-center',
                    branchChartGrouping === 'growth'
                      ? 'bg-amber-500 text-slate-950 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  ]"
                >
                  Tren Waktu
                </button>
              </div>
            </div>

            <div class="chart-wrapper">
              <Bar :data="churchGrowthData" :options="branchChartOptions" />
            </div>
          </div>

          <!-- Grafik 2: Poligon Komposisi Pengguna -->
          <div class="chart-card" data-aos="fade-up" data-aos-delay="100">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
              <div>
                <h3 class="chart-title !mb-0">Komposisi Pengguna Platform</h3>
                <p class="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                  <span class="inline-block w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
                  Basis Data Terkini:
                  <span class="text-sky-300 font-semibold font-mono">{{ totalPlatformUsers }} Pengguna Terdata</span>
                </p>
              </div>
              <span class="text-[11px] text-sky-400 font-mono bg-sky-950/70 border border-sky-800/60 px-2.5 py-1 rounded-full self-start sm:self-auto">
                Admin &amp; Jemaat Real-Time
              </span>
            </div>
            <div class="chart-wrapper">
              <Line :data="userDemographicsData" :options="chartOptions" />
            </div>
          </div>

          <!-- Grid untuk 4 Grafik Lingkaran (Demografi Jemaat Real-Time Database) -->
          <div class="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-8 mt-4 sm:mt-8">
            <div class="chart-card" data-aos="fade-up" data-aos-delay="200">
              <h3 class="chart-title text-center">Kelompok Usia</h3>
              <p class="text-[11px] text-slate-400 text-center -mt-2 mb-2">Berdasarkan tanggal lahir jemaat</p>
              <div class="chart-wrapper-doughnut">
                <Doughnut :data="ageDistributionData" :options="doughnutOptions" />
              </div>
            </div>
            <div class="chart-card" data-aos="fade-up" data-aos-delay="300">
              <h3 class="chart-title text-center">Katekisasi & Sidi</h3>
              <p class="text-[11px] text-slate-400 text-center -mt-2 mb-2">Status katekisasi resmi jemaat</p>
              <div class="chart-wrapper-doughnut">
                <Doughnut :data="catechismData" :options="doughnutOptions" />
              </div>
            </div>
            <div class="chart-card" data-aos="fade-up" data-aos-delay="400">
              <h3 class="chart-title text-center">Status Pernikahan</h3>
              <p class="text-[11px] text-slate-400 text-center -mt-2 mb-2">Status keluarga jemaat</p>
              <div class="chart-wrapper-doughnut">
                <Doughnut :data="statusData" :options="doughnutOptions" />
              </div>
            </div>
            <div class="chart-card" data-aos="fade-up" data-aos-delay="500">
              <h3 class="chart-title text-center">Pendidikan</h3>
              <p class="text-[11px] text-slate-400 text-center -mt-2 mb-2">Jenjang pendidikan jemaat</p>
              <div class="chart-wrapper-doughnut">
                <Doughnut :data="educationData" :options="doughnutOptions" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bagian Fitur Unggulan -->
    <div class="aboutBody" id="features">
      <div class="about-container">
        <h2 class="about-title" data-aos="fade-up">Fitur Unggulan GracePoint</h2>
        <p class="about-subtitle" data-aos="fade-up" data-aos-delay="100">Berikut fitur-fitur yang dapat Anda nikmati untuk mendukung pelayanan digital:</p>
        
        <!-- Grid Fitur Utama -->
        <div class="features-grid">
          <!-- Kartu Fitur 1 -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'calendar-days']" />
            </div>
            <h3 class="feature-title">Informasi & Jadwal</h3>
            <p class="feature-description">Akses warta jemaat, jadwal ibadah, dan pengumuman penting gereja secara real-time di satu tempat.</p>
          </div>
          <!-- Kartu Fitur 2 -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'people-arrows']" />
            </div>
            <h3 class="feature-title">Manajemen Jemaat</h3>
            <p class="feature-description">Kelola data keluarga, pendaftaran anggota baru, dan perbarui profil jemaat dengan mudah dan aman.</p>
          </div>
          <!-- Kartu Fitur 3 -->
          <div class="feature-card" data-aos="fade-up" data-aos-delay="400">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'hand-holding-heart']" />
            </div>
            <h3 class="feature-title">Manajemen Pelayanan</h3>
            <p class="feature-description">Mengelola, melakukan klasifikasi dan memberitahukan segala kegiatan gereja dengan efisien. </p>
          </div>
          <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'dollar-sign']" />
            </div>
            <h3 class="feature-title">Manajemen Keuangan</h3>
            <p class="feature-description">Kelola data keuangan jemaat dan keuangan gereja dengan mudah dan aman.</p>
          </div>
          <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'chart-line']" />
            </div>
            <h3 class="feature-title">Analisis data berbasis AI</h3>
            <p class="feature-description">Dapatkan wawasan pertumbuhan dan tren jemaat secara real-time.</p>
          </div>
          <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'lock']" />
            </div>
            <h3 class="feature-title">Sistem Keamanan Data</h3>
            <p class="feature-description">Memastikan data jemaat dan keuangan gereja aman dari akses tidak sah.</p>
          </div>
          <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <div class="feature-icon">
              <font-awesome-icon :icon="['fas', 'map-marker-alt']" />
            </div>
            <h3 class="feature-title">Geolocation untuk lokasi gereja yang interaktif</h3>
            <p class="feature-description">Dengan fitur geolocation, jemaat dapat dengan mudah menemukan lokasi gereja dan cabang terdekat.</p>
          </div>
        </div> <!-- Penutup features-grid -->
      </div> <!-- Penutup about-container -->
    </div> <!-- Penutup aboutBody id="features" -->

    <!-- ==================== BAGIAN DONASI & PERSEMBAHAN (#donasi) ==================== -->
    <div class="churchBody border-t border-slate-800/80 pt-16 pb-20" id="donasi">
      <div class="churchContainer max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <!-- Header Seksi Donasi -->
        <div class="text-center max-w-3xl mx-auto mb-12">
          <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-400/40 text-amber-300 font-serif text-xs uppercase tracking-widest mb-3 shadow-inner" data-aos="fade-up">
            <i class="bi bi-heart-pulse-fill text-amber-400"></i> Persembahan & Diakonia Kasih
          </span>
          <h2 class="about-title text-3xl sm:text-4xl font-bold font-serif text-slate-100 mt-2" data-aos="fade-up" data-aos-delay="100">
            Dukung Pelayanan & Misi GracePoint
          </h2>
          <p class="about-subtitle mt-3 text-slate-300 font-sans" data-aos="fade-up" data-aos-delay="150">
            Setiap pemberian dan persembahan Anda menjadi alat kasih untuk keberlangsungan pelayanan ibadah, bantuan diakonia sosial jemaat prasejahtera, pembangunan gereja mitra, dan penyebaran kabar baik.
          </p>

          <!-- Ayat Alkitab Banner -->
          <div class="mt-6 p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-[#0b1638] via-[#111e4a] to-[#0b1638] border border-amber-500/30 text-amber-100/90 font-serif italic text-sm sm:text-base shadow-xl relative overflow-hidden group" data-aos="fade-up" data-aos-delay="200">
            <div class="absolute -right-4 -bottom-4 text-amber-500/10 text-7xl font-serif select-none pointer-events-none">✝</div>
            <p class="mb-1 text-amber-300 font-semibold not-italic text-xs sm:text-sm tracking-wider uppercase">
              <i class="bi bi-quote me-1"></i> 2 Korintus 9:7
            </p>
            <p class="leading-relaxed font-serif">
              "Hendaklah masing-masing memberikan menurut kerelaan hatinya, jangan dengan sedih hati atau karena paksaan, sebab Allah menyukai orang yang memberi dengan sukacita."
            </p>
          </div>
        </div>

        <!-- Dynamic Campaign Progress Bar Card -->
        <div class="mb-14 p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-[#0c163a] to-[#070d24] border border-amber-500/30 shadow-2xl relative overflow-hidden" data-aos="fade-up">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-6">
            <div>
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span class="text-xs font-serif uppercase tracking-widest text-emerald-400 font-bold">Kampanye Diakonia Bulan Ini</span>
              </div>
              <h3 class="text-xl sm:text-2xl font-bold font-serif text-white mt-1">Bantuan Sembako & Operasional Pelayanan Village Church</h3>
              <p class="text-xs sm:text-sm text-slate-300 mt-1">Target penggalangan dana diakonia sosial untuk 100 keluarga jemaat & gereja pedalaman.</p>
            </div>
            
            <div class="flex items-center justify-between sm:justify-end gap-3 bg-[#070c1e]/90 px-4 py-3 rounded-xl border border-amber-500/20 text-right flex-shrink-0 w-full sm:w-auto">
              <div>
                <span class="text-xs text-slate-400 block font-sans">Terkumpul</span>
                <span class="text-xl font-bold font-serif text-amber-400">Rp 48.500.000</span>
              </div>
              <span class="text-slate-500 font-serif text-lg">/</span>
              <div>
                <span class="text-xs text-slate-400 block font-sans">Target</span>
                <span class="text-base font-bold font-serif text-slate-200">Rp 65.000.000</span>
              </div>
            </div>
          </div>

          <!-- Progress Bar Track -->
          <div class="w-full h-3.5 bg-slate-900 rounded-full overflow-hidden border border-slate-700/80 p-0.5 relative shadow-inner">
            <div class="h-full bg-gradient-to-r from-amber-500 via-amber-400 to-emerald-400 rounded-full transition-all duration-1000 shadow-md relative" style="width: 74.6%;">
              <span class="absolute right-1 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-white shadow"></span>
            </div>
          </div>

          <div class="flex justify-between items-center mt-2.5 text-xs text-slate-400 font-sans">
            <span>Progress: <strong class="text-amber-300 font-bold">74.6%</strong></span>
            <span>Sisa Waktu: <strong class="text-slate-200">12 Hari Lagi</strong></span>
          </div>

          <!-- Key Impact Metrics Row -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6 pt-6 border-t border-slate-800">
            <div class="flex items-center gap-3 p-3 rounded-xl bg-[#09112b] border border-slate-800">
              <div class="w-10 h-10 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center justify-center text-lg flex-shrink-0">
                <i class="bi bi-box-seam-fill"></i>
              </div>
              <div>
                <span class="text-base font-bold text-white font-serif block">850+ Paket</span>
                <span class="text-xs text-slate-400">Diakonia Tersalurkan</span>
              </div>
            </div>

            <div class="flex items-center gap-3 p-3 rounded-xl bg-[#09112b] border border-slate-800">
              <div class="w-10 h-10 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-400 flex items-center justify-center text-lg flex-shrink-0">
                <i class="bi bi-building-check"></i>
              </div>
              <div>
                <span class="text-base font-bold text-white font-serif block">12 Gereja</span>
                <span class="text-xs text-slate-400">Mitra Terbantu</span>
              </div>
            </div>

            <div class="flex items-center gap-3 p-3 rounded-xl bg-[#09112b] border border-slate-800">
              <div class="w-10 h-10 rounded-lg bg-sky-500/15 border border-sky-500/30 text-sky-400 flex items-center justify-center text-lg flex-shrink-0">
                <i class="bi bi-book-fill"></i>
              </div>
              <div>
                <span class="text-base font-bold text-white font-serif block">1,500+ Alkitab</span>
                <span class="text-xs text-slate-400">Terdistribusi Mandiri</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Interactive Giving Section (Tabs + Payment Methods + Amount Selector) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          <!-- LEFT SIDE (7 Cols): Payment Methods Tabs & Details -->
          <div class="lg:col-span-7 space-y-6" data-aos="fade-up">
            
            <!-- Navigation Tabs -->
            <div class="flex flex-wrap p-1.5 rounded-xl bg-[#0a122e] border border-amber-500/30 gap-1 sm:gap-2 shadow-lg">
              <button 
                @click="activeDonationTab = 'bank'"
                type="button"
                :class="activeDonationTab === 'bank' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'"
                class="flex-1 py-2.5 px-3 rounded-lg text-xs sm:text-sm font-serif uppercase tracking-wider transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer"
              >
                <i class="bi bi-credit-card-2-front-fill"></i>
                <span>Transfer Bank</span>
              </button>

              <button 
                @click="activeDonationTab = 'qris'"
                type="button"
                :class="activeDonationTab === 'qris' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'"
                class="flex-1 py-2.5 px-3 rounded-lg text-xs sm:text-sm font-serif uppercase tracking-wider transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer"
              >
                <i class="bi bi-qr-code-scan"></i>
                <span>QRIS Instant</span>
              </button>

              <button 
                @click="activeDonationTab = 'projects'"
                type="button"
                :class="activeDonationTab === 'projects' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'"
                class="flex-1 py-2.5 px-3 rounded-lg text-xs sm:text-sm font-serif uppercase tracking-wider transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer"
              >
                <i class="bi bi-diagram-3-fill"></i>
                <span>Program Khusus</span>
              </button>
            </div>

            <!-- TAB 1: TRANSFER BANK -->
            <div v-if="activeDonationTab === 'bank'" class="space-y-4 transition-all duration-300">
              <div 
                v-for="(account, idx) in bankAccounts" 
                :key="idx"
                class="p-5 rounded-2xl bg-gradient-to-r from-[#0c163a] to-[#08102a] border border-amber-500/25 hover:border-amber-400/60 transition duration-300 shadow-xl group relative overflow-hidden"
              >
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl bg-slate-900 border border-amber-500/30 flex items-center justify-center text-amber-400 text-xl font-bold shadow-inner flex-shrink-0">
                      <i :class="account.iconClass"></i>
                    </div>
                    <div>
                      <div class="flex items-center gap-2">
                        <h4 class="text-base sm:text-lg font-bold font-serif text-white">{{ account.bankName }}</h4>
                        <span class="text-[10px] font-serif uppercase px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-400/30">
                          {{ account.badge }}
                        </span>
                      </div>
                      <p class="text-xs text-slate-400 mt-0.5">a.n. <strong class="text-slate-200 font-semibold">{{ account.accName }}</strong></p>
                    </div>
                  </div>

                  <div class="flex items-center justify-between sm:justify-end gap-3 bg-[#060b1c] p-2.5 rounded-xl border border-slate-800">
                    <span class="font-mono text-base sm:text-lg font-bold tracking-wider text-amber-300 px-2">
                      {{ account.accNo }}
                    </span>
                    <button 
                      @click="copyToClipboard(account.accNo, account.bankName)"
                      type="button"
                      title="Salin Nomor Rekening"
                      class="px-3 py-1.5 text-xs font-serif uppercase tracking-wider bg-amber-500/20 hover:bg-amber-400 text-amber-300 hover:text-slate-950 border border-amber-500/40 rounded-lg transition duration-200 flex items-center gap-1.5 cursor-pointer font-bold"
                    >
                      <i class="bi bi-clipboard-check"></i>
                      <span>Salin</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- TAB 2: QRIS INSTANT -->
            <div v-if="activeDonationTab === 'qris'" class="p-6 rounded-2xl bg-gradient-to-br from-[#0c163a] to-[#08102a] border border-amber-500/30 shadow-xl text-center space-y-5">
              <div class="inline-block p-3 rounded-2xl bg-white border-2 border-amber-400 shadow-2xl relative group cursor-pointer" @click="isQrisZoomOpen = true">
                <img :src="imgQris" alt="QRIS GracePoint" class="w-56 h-56 object-contain mx-auto rounded-lg transition transform group-hover:scale-105">
                <div class="absolute inset-0 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center rounded-xl text-white font-serif text-xs font-bold gap-2 backdrop-blur-xs">
                  <i class="bi bi-zoom-in text-lg"></i>
                  <span>Perbesar QR Code</span>
                </div>
              </div>

              <div>
                <h4 class="text-lg font-bold font-serif text-amber-300">Scan QRIS Standar Nasional</h4>
                <p class="text-xs text-slate-300 mt-1 max-w-md mx-auto">
                  Dapat discan menggunakan aplikasi perbankan (BCA Mobile, Livin, BRImo) atau E-Wallet (GoPay, OVO, Dana, ShopeePay, LinkAja).
                </p>
              </div>

              <div class="flex justify-center gap-3 pt-2">
                <button 
                  @click="isQrisZoomOpen = true" 
                  type="button"
                  class="px-4 py-2 text-xs font-serif uppercase tracking-wider bg-amber-500/20 hover:bg-amber-400 text-amber-300 hover:text-slate-950 border border-amber-500/40 rounded-xl transition flex items-center gap-2 cursor-pointer font-bold"
                >
                  <i class="bi bi-arrows-fullscreen"></i>
                  <span>Tampilkan Layar Penuh</span>
                </button>
              </div>
            </div>

            <!-- TAB 3: PROGRAM KHUSUS / DIAKONIA -->
            <div v-if="activeDonationTab === 'projects'" class="space-y-4">
              <!-- Project Item 1 -->
              <div class="p-5 rounded-2xl bg-gradient-to-r from-[#0c163a] to-[#08102a] border border-slate-800 hover:border-amber-500/40 transition">
                <div class="flex items-start gap-4">
                  <div class="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 flex items-center justify-center text-lg flex-shrink-0">
                    <i class="bi bi-house-gear-fill"></i>
                  </div>
                  <div>
                    <h4 class="text-base font-bold font-serif text-white">1. Pembangunan & Maintenance Gedung Ibadah</h4>
                    <p class="text-xs text-slate-300 mt-1">Perbaikan fasilitas gedung gereja, sound system pelayanan, serta infrastruktur teknologi warta digital.</p>
                    <span class="inline-block mt-2 text-[11px] font-mono text-amber-300 bg-amber-500/10 px-2.5 py-0.5 rounded border border-amber-500/20">
                      Kode Transfer Opsional: Tambahkan angka unik <strong>+1</strong> di akhir nominal
                    </span>
                  </div>
                </div>
              </div>

              <!-- Project Item 2 -->
              <div class="p-5 rounded-2xl bg-gradient-to-r from-[#0c163a] to-[#08102a] border border-slate-800 hover:border-amber-500/40 transition">
                <div class="flex items-start gap-4">
                  <div class="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 flex items-center justify-center text-lg flex-shrink-0">
                    <i class="bi bi-mortarboard-fill"></i>
                  </div>
                  <div>
                    <h4 class="text-base font-bold font-serif text-white">2. Beasiswa Anak Asuh & Pendidikan Pelayan</h4>
                    <p class="text-xs text-slate-300 mt-1">Dukungan biaya pendidikan sekolah dan kuliah bagi anak-anak jemaat prasejahtera dan calon hamba Tuhan.</p>
                    <span class="inline-block mt-2 text-[11px] font-mono text-emerald-300 bg-emerald-500/10 px-2.5 py-0.5 rounded border border-emerald-500/20">
                      Kode Transfer Opsional: Tambahkan angka unik <strong>+2</strong> di akhir nominal
                    </span>
                  </div>
                </div>
              </div>

              <!-- Project Item 3 -->
              <div class="p-5 rounded-2xl bg-gradient-to-r from-[#0c163a] to-[#08102a] border border-slate-800 hover:border-amber-500/40 transition">
                <div class="flex items-start gap-4">
                  <div class="w-10 h-10 rounded-xl bg-sky-500/15 border border-sky-500/30 text-sky-300 flex items-center justify-center text-lg flex-shrink-0">
                    <i class="bi bi-bandaid-fill"></i>
                  </div>
                  <div>
                    <h4 class="text-base font-bold font-serif text-white">3. Tanggap Bencana & Diakonia Darurat</h4>
                    <p class="text-xs text-slate-300 mt-1">Layanan aksi tanggap darurat bencana alam, bantuan obat-obatan, serta kebutuhan pokok darurat kemanusiaan.</p>
                    <span class="inline-block mt-2 text-[11px] font-mono text-sky-300 bg-sky-500/10 px-2.5 py-0.5 rounded border border-sky-500/20">
                      Kode Transfer Opsional: Tambahkan angka unik <strong>+3</strong> di akhir nominal
                    </span>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- RIGHT SIDE (5 Cols): Interactive Nominal Calculator & Form -->
          <div class="lg:col-span-5 p-6 sm:p-7 rounded-2xl bg-gradient-to-br from-[#0b1435] to-[#070c1e] border border-amber-500/40 shadow-2xl space-y-5" data-aos="fade-up">
            
            <div class="border-b border-amber-500/20 pb-4">
              <h3 class="text-xl font-bold font-serif text-amber-300 flex items-center gap-2">
                <i class="bi bi-calculator-fill text-amber-400"></i>
                <span>Simulasi & Konfirmasi Donasi</span>
              </h3>
              <p class="text-xs text-slate-300 mt-1">Pilih nominal persembahan atau masukkan jumlah sesuai kerelaan hati Anda.</p>
            </div>

            <!-- Preset Amount Buttons -->
            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-2 font-semibold">Pilih Nominal Cepat:</label>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <button 
                  v-for="amt in presetAmounts" 
                  :key="amt"
                  @click="handlePresetSelect(amt)"
                  type="button"
                  :class="selectedPresetAmount === amt && !customAmount ? 'bg-amber-500 text-slate-950 font-bold border-amber-300 shadow-md' : 'bg-slate-900/80 text-slate-200 border-slate-700 hover:border-amber-400 hover:text-white'"
                  class="py-2.5 px-1.5 sm:px-2 rounded-xl text-[11px] sm:text-xs font-mono font-semibold border transition duration-200 text-center cursor-pointer truncate"
                >
                  {{ formatCurrency(amt) }}
                </button>
              </div>
            </div>

            <!-- Custom Amount Input -->
            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-2 font-semibold">Atau Nominal Lainnya (Rp):</label>
              <div class="relative">
                <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-amber-300 font-mono font-bold text-sm">Rp</span>
                <input 
                  v-model="customAmount"
                  type="number"
                  placeholder="Masukkan nominal custom..."
                  class="w-full pl-10 pr-4 py-3 bg-[#050918] border border-amber-500/30 rounded-xl text-white font-mono text-sm focus:outline-none focus:border-amber-400 transition placeholder-slate-500"
                >
              </div>
            </div>

            <!-- Category Selector -->
            <div>
              <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-2 font-semibold">Jenis Persembahan / Alokasi:</label>
              <select 
                v-model="selectedCategory"
                class="w-full px-3.5 py-3 bg-[#050918] border border-amber-500/30 rounded-xl text-slate-200 text-xs sm:text-sm focus:outline-none focus:border-amber-400 transition"
              >
                <option v-for="cat in donationCategories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <!-- Total Preview Display -->
            <div class="p-4 rounded-xl bg-amber-500/10 border border-amber-400/30 flex items-center justify-between">
              <span class="text-xs font-serif uppercase text-amber-200 tracking-wider">Total Persembahan:</span>
              <span class="text-xl font-bold font-mono text-amber-300">{{ formatCurrency(getFinalAmount()) }}</span>
            </div>

            <!-- Submit / Action Button -->
            <button 
              @click="openConfirmModal"
              type="button"
              class="w-full py-3.5 px-4 bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-serif font-bold text-xs sm:text-sm uppercase tracking-wider rounded-xl transition duration-300 shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2 cursor-pointer"
            >
              <i class="bi bi-shield-check text-base"></i>
              <span>Lanjutkan Konfirmasi Donasi</span>
            </button>

            <!-- Trust Badges Footer -->
            <div class="pt-3 border-t border-slate-800 text-center">
              <p class="text-[11px] text-slate-400 font-sans flex items-center justify-center gap-3">
                <span><i class="bi bi-lock-fill text-amber-400 me-1"></i> Transaksi Aman 256-Bit</span>
                <span>•</span>
                <span><i class="bi bi-file-earmark-text-fill text-amber-400 me-1"></i> Terverifikasi</span>
              </p>
            </div>

          </div>

        </div>

      </div>
    </div>

    <!-- ==================== MODAL ZOOM QRIS ==================== -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div 
          v-if="isQrisZoomOpen" 
          class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md"
          @click.self="isQrisZoomOpen = false"
        >
          <div class="w-full max-w-lg bg-[#091129] border border-amber-500/40 rounded-2xl p-6 shadow-2xl relative text-center animate-scaleUp">
            <button 
              @click="isQrisZoomOpen = false"
              type="button"
              class="absolute top-4 right-4 text-slate-400 hover:text-amber-300 p-1.5 rounded-lg border border-slate-700 hover:bg-[#0b1435] transition cursor-pointer"
            >
              <i class="bi bi-x-lg"></i>
            </button>

            <h3 class="text-xl font-bold font-serif text-amber-300 mb-2">QRIS Standar Nasional — GracePoint</h3>
            <p class="text-xs text-slate-300 mb-4">Pindai kode QR di bawah ini dari aplikasi m-Banking atau E-Wallet pilihan Anda.</p>
            
            <div class="p-4 bg-white rounded-2xl inline-block shadow-2xl border-2 border-amber-400">
              <img :src="imgQris" alt="QRIS Fullscreen" class="w-72 h-72 object-contain mx-auto">
            </div>

            <p class="text-xs font-mono text-amber-300 mt-4 bg-slate-900 py-2 px-4 rounded-xl inline-block border border-slate-800">
              NMID: ID10234567890123 • Gereja GracePoint
            </p>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ==================== MODAL KONFIRMASI DONASI ==================== -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div 
          v-if="isConfirmModalOpen" 
          class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md"
          @click.self="isConfirmModalOpen = false"
        >
          <div class="w-full max-w-lg bg-[#091129] border border-amber-500/40 rounded-2xl p-6 sm:p-7 shadow-2xl relative font-sans text-slate-100 animate-scaleUp">
            <button 
              @click="isConfirmModalOpen = false"
              type="button"
              class="absolute top-4 right-4 text-slate-400 hover:text-amber-300 p-1.5 rounded-lg border border-slate-700 hover:bg-[#0b1435] transition cursor-pointer"
            >
              <i class="bi bi-x-lg"></i>
            </button>

            <div class="text-center pb-4 border-b border-amber-500/20 mb-4">
              <div class="w-12 h-12 mx-auto rounded-full bg-amber-500/10 border border-amber-400/40 text-amber-300 flex items-center justify-center mb-2 shadow-inner text-xl">
                <i class="bi bi-receipt"></i>
              </div>
              <h3 class="text-xl font-bold font-serif text-amber-300">Rincian & Konfirmasi Donasi</h3>
              <p class="text-xs text-slate-300 mt-1">Lengkapi informasi opsional untuk pencatatan warta persembahan.</p>
            </div>

            <div class="space-y-4">
              <!-- Summary Box -->
              <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
                <div class="flex justify-between">
                  <span class="text-slate-400">Kategori:</span>
                  <span class="text-amber-300 font-bold">{{ selectedCategory }}</span>
                </div>
                <div class="flex justify-between border-t border-slate-800 pt-2">
                  <span class="text-slate-400">Jumlah Transfer:</span>
                  <span class="text-lg font-mono font-bold text-amber-400">{{ formatCurrency(getFinalAmount()) }}</span>
                </div>
              </div>

              <!-- Optional Donor Name -->
              <div>
                <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1.5 font-semibold">Nama Hamba Tuhan / Donatur (Opsional):</label>
                <input 
                  v-model="donorName"
                  type="text"
                  placeholder="Contoh: Bp. Samuel / Hamba Allah"
                  class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white text-xs focus:outline-none focus:border-amber-400"
                >
              </div>

              <!-- Optional Note / Prayer Request -->
              <div>
                <label class="block text-xs font-serif uppercase tracking-wider text-slate-300 mb-1.5 font-semibold">Catatan / Pokok Doa (Opsional):</label>
                <textarea 
                  v-model="donorNote"
                  rows="2"
                  placeholder="Tuliskan pesan atau pokok doa Anda..."
                  class="w-full px-3.5 py-2.5 bg-[#050918] border border-amber-500/30 rounded-xl text-white text-xs focus:outline-none focus:border-amber-400"
                ></textarea>
              </div>

              <!-- Buttons -->
              <div class="pt-2 space-y-2">
                <button 
                  @click="sendWhatsAppConfirmation"
                  type="button"
                  class="w-full py-3 px-4 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-serif font-bold text-xs uppercase tracking-wider rounded-xl transition flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-emerald-500/20"
                >
                  <i class="bi bi-whatsapp text-base"></i>
                  <span>Kirim Konfirmasi Bukti via WhatsApp</span>
                </button>

                <button 
                  @click="isConfirmModalOpen = false"
                  type="button"
                  class="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 font-serif font-semibold text-xs uppercase tracking-wider rounded-xl transition text-center cursor-pointer"
                >
                  Tutup Rincian
                </button>
              </div>
            </div>

          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ==================== TOAST NOTIFICATION ==================== -->
    <Teleport to="body">
      <Transition name="fade-slide">
        <div 
          v-if="showToast"
          class="fixed bottom-6 right-6 z-[10000] px-4 py-3 bg-amber-500 text-slate-950 font-bold font-serif text-xs rounded-xl shadow-2xl border border-amber-300 flex items-center gap-2"
        >
          <i class="bi bi-check-circle-fill text-lg"></i>
          <span>{{ toastMessage }}</span>
        </div>
      </Transition>
    </Teleport>

  </div> <!-- Penutup div utama sebelum HomeLayout -->
  </HomeLayout>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Lato:wght@400;500;700&display=swap');

.mainBody {
  /* background: linear-gradient(135deg, #050914 0%, #070e24 40%, #0a1435 80%, #0d1a45 100%); */
  background: url(https://media.istockphoto.com/id/1271405992/id/vektor/konsep-ibadah-kekristenan-futuristik-dengan-alkitab-terbuka-poligonal-rendah-bersinar-dan.jpg?s=612x612&w=0&k=20&c=qf1QAy8mlLTSlOg4DrvoCelAOoiApQe2XKUlan6zNj0=);
  min-height: 100vh;
  width: 100%;
  padding: 4rem 1.5rem;
  animation: fadeUp 1s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  box-shadow: inset 0 0 0 1000px rgba(0, 0, 0, 0.7);
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(7, 12, 25, 0.40) 0%, rgba(7, 12, 25, 0.20) 50%, rgba(7, 12, 25, 0.70) 100%);
  backdrop-filter: blur(1px);
  pointer-events: none;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  max-width: 900px;
}

.headerLogo {
  margin-top: -1rem;
  margin-bottom: 1.5rem;
}

.imgSize {
  width: 210px;
  height: 210px;
  animation: fadeUp 1s ease-in-out;
  transition: transform 0.3s ease, filter 0.3s ease;
  cursor: pointer;
}

.imgSize:hover {
  transform: scale(1.05);
  /* Menambahkan pendaran cahaya yang mengikuti bentuk logo */
  filter: drop-shadow(0 0 18px rgba(251, 191, 36, 0.6)); 
}

.headertext {
  font-family: 'Cinzel', 'Times New Roman', serif;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-align: center;
  margin-top: -1.5rem;
  margin-bottom: 1rem;
  color: #fbbf24; /* Emas terang */
  text-shadow: 0 4px 18px rgba(245, 158, 11, 0.35);
  animation: slideIn 1s ease-in-out;
  transition: transform 0.3s ease, filter 0.3s ease;
  cursor: pointer;
}

.pictures {
  width: 200px;
  height: 200px;
  justify-items: center;
  align-items: center;
  animation: fadeUp 1s ease-in-out; 
  border-radius: 23px;
  border-width: 1px;
  border-color: #fbbf24;
  margin-left: 50%;
  transform: translateX(-50%);
}
.subtext {
  font-family: 'Lato', 'Helvetica Neue', sans-serif;
  font-size: 1.25rem;
  line-height: 1.6;
  text-align: center;
  color: #cbd5e1; /* Slate-300 terang */
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.85);
  max-width: 680px;
  margin-top: -0.5rem;
  margin-bottom: 2.5rem;
  font-weight: 500;
  animation: slideIn 1s ease-in-out;
  transition: transform 0.3s ease, filter 0.3s ease;
  cursor: pointer;
}

.button-container {
  display: flex;
  flex-direction: row;
  gap: 1.25rem;
  animation: fadeUp 1s ease-in-out 0.2s;
  animation-fill-mode: backwards;
  margin-top: 0;
  justify-content: center;
  flex-wrap: wrap;
}

.headertext:hover {
  transform: scale(1.03);
  filter: drop-shadow(0 0 15px rgba(251, 191, 36, 0.5));
}

.subtext:hover {
  transform: scale(1.02);
  filter: drop-shadow(0 0 15px rgba(251, 191, 36, 0.5));
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  } 
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* --- Style untuk Tombol Portal CTA --- */
.portal-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.75rem;
  border-width: 1px;
  border-radius: 0.5rem;
  font-family: 'Lato', 'Helvetica Neue', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.825rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  min-width: 240px;
  justify-content: center;
  text-decoration: none !important;
  color: #070c1e !important;
}

.portal-button:hover,
.portal-button:focus,
.portal-button:visited {
  text-decoration: none !important;
  color: #070c1e !important;
  transform: translateY(-2px);
}

/* --- Styling untuk Bagian "About" (Deep Navy Theme) --- */
.aboutBody {
  background-color: #070c1e; /* Deep Navy Blue */
  padding: 4rem 1rem;
  border-top: 1px solid rgba(30, 45, 99, 0.6);
}

.about-container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.about-title {
  font-family: 'Cinzel', serif;
  font-size: 2rem;
  font-weight: 700;
  color: #f0f9ff;
  margin-bottom: 0.75rem;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
}

.about-subtitle {
  font-family: 'Lato', sans-serif;
  font-size: 1rem;
  color: #cbd5e1; /* slate-300 */
  max-width: 800px;
  margin: 0 auto 3rem auto;
  line-height: 1.6;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
  gap: 1.5rem;
}

.feature-card {
  background-color: #0c1538; /* Deep Navy Card */
  border: 1px solid #1c2b5e; /* Navy border */
  border-radius: 0.75rem;
  padding: 2rem;
  transition: all 0.3s ease;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
}

.feature-card:hover {
  transform: translateY(-8px);
  border-color: rgba(251, 191, 36, 0.6); /* amber-400 */
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.4), 0 8px 10px -6px rgba(0,0,0,0.4);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-title {
  font-family: 'Cinzel', serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: #f59e0b; /* amber-500 */
  margin-bottom: 0.5rem;
}

.feature-description {
  font-family: 'Lato', sans-serif;
  font-size: 0.9rem;
  color: #94a3b8; /* slate-400 */
  line-height: 1.5;
}

/* --- Styling untuk Partner Scroll --- */
.partner-section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}

.partner-section-subtitle {
  font-family: 'Lato', sans-serif;
  font-size: 0.95rem;
  color: #94a3b8;
  margin: 0;
}

.partner-scroll-controls {
  display: flex;
  gap: 0.75rem;
}

.scroll-control-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: rgba(28, 43, 94, 0.6);
  border: 1px solid rgba(56, 189, 248, 0.25);
  color: #38bdf8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(8px);
}

.scroll-control-btn:hover {
  background: #f59e0b;
  border-color: #fbbf24;
  color: #070c1e;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.35);
}

.scroll-control-btn:active {
  transform: translateY(0) scale(0.98);
}

.horizontal-scroll-container-outer {
  position: relative;
  width: 100%;
}

.horizontal-scroll-wrapper {
  width: 100%;
  overflow-x: auto;
  scroll-behavior: smooth;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  padding: 0.5rem 0.5rem 1.25rem 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(56, 189, 248, 0.35) rgba(15, 23, 42, 0.6);
}

.horizontal-scroll-wrapper::-webkit-scrollbar {
  height: 6px;
}

.horizontal-scroll-wrapper::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 10px;
}

.horizontal-scroll-wrapper::-webkit-scrollbar-thumb {
  background: linear-gradient(90deg, #38bdf8, #f59e0b);
  border-radius: 10px;
}

.horizontal-scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(90deg, #60a5fa, #fbbf24);
}

.horizontal-scroll-content {
  display: flex;
  flex-wrap: nowrap;
  gap: 1.5rem;
}

.partner-card {
  flex: 0 0 280px;
  scroll-snap-align: start;
  position: relative;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.85), rgba(28, 43, 94, 0.55));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 1.5rem 1.25rem;
  text-align: center;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.partner-card:hover {
  transform: translateY(-8px);
  border-color: rgba(251, 191, 36, 0.5);
  box-shadow: 0 16px 28px -6px rgba(0, 0, 0, 0.45), 0 0 20px rgba(245, 158, 11, 0.15);
}

.partner-badge {
  position: absolute;
  top: 0.85rem;
  right: 0.85rem;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.partner-badge.badge-alt {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.3);
}

.partner-logo-box {
  height: 90px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}

.partner-logo {
  max-height: 80px;
  max-width: 180px;
  width: auto;
  object-fit: contain;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
  transition: transform 0.3s ease;
}

.partner-card:hover .partner-logo {
  transform: scale(1.06);
}

.partner-logo-placeholder {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.2) 0%, rgba(12, 21, 56, 0.8) 100%);
  border: 1px solid rgba(56, 189, 248, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.2rem;
  color: #38bdf8;
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
  transition: all 0.3s ease;
}

.partner-logo-placeholder.placeholder-alt {
  background: radial-gradient(circle, rgba(245, 158, 11, 0.2) 0%, rgba(12, 21, 56, 0.8) 100%);
  border-color: rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}

.partner-card:hover .partner-logo-placeholder {
  transform: scale(1.08) rotate(3deg);
  border-color: #fbbf24;
  color: #fbbf24;
}

.partner-name {
  font-family: 'Cinzel', serif;
  font-size: 0.98rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 0.4rem;
  line-height: 1.35;
  display: -webkit-box;
  --webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.7rem;
}

.partner-tag {
  font-family: 'Lato', sans-serif;
  font-size: 0.78rem;
  color: #94a3b8;
  font-weight: 500;
}

.partner-scroll-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.75rem;
  font-family: 'Lato', sans-serif;
  font-size: 0.82rem;
  color: #64748b;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  background-color: rgba(12, 21, 56, 0.75); /* Deep Navy Glass */
  border: 1px solid #1c2b5e;
  border-radius: 1rem;
}

/* --- Styling untuk Kartu Grafik --- */
.chart-card {
  background-color: #0c1538; /* Deep Navy Card */
  border: 1px solid #1c2b5e; /* Navy border */
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
}

.chart-title {
  font-family: 'Lato', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0; /* slate-200 */
  margin-bottom: 1rem;
}

.churchContainerText {
  max-width: 800px;
  margin: 0 auto 3rem auto; /* Memberi margin bawah yang cukup */
  text-align: center;
}

.churchBody {
  margin-top: -2rem;
  gap: 2rem;
  z-index:auto;
  padding: 3rem 0 4rem 0; /* Menambah padding atas dan bawah */
  background-color: #070c1e; /* Menyamakan background dengan section "about" */
}

.churchContainer {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.churchText {
  font-family: 'Cinzel', serif; /* Menggunakan font serif yang elegan */
  font-size: 2rem; /* Memperbesar ukuran font agar setara dengan judul lain */
  font-weight: 600;
  color: #f0f9ff; /* Warna putih terang */
  margin-top: -2rem;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
}

.churchGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
  gap: 2rem; /* Menambah jarak antar kartu */
}

.churchSubText {
  font-family: 'Lato', sans-serif; /* Menggunakan font sans-serif yang konsisten */
  font-size: 1rem; /* Ukuran font yang mudah dibaca */
  color: #cbd5e1; /* Warna slate-300 */
  line-height: 1.6;
}

.chart-wrapper {
  height: 300px;
}
.chart-wrapper-doughnut {
  height: 250px;
}

/* --- Media Query untuk Responsivitas di Layar Tablet / HP (<= 768px) --- */
@media (max-width: 768px) {
  .headerLogo {
    margin-top: -2.5rem;
  }
  .imgSize {
    width: 160px; /* Perkecil ukuran logo di layar kecil */
    height: 160px;
  }
  .headertext {
    font-size: 1.75rem; /* Perkecil font judul */
    margin-top: -0.75rem;
  }
  .subtext {
    font-size: 0.95rem; /* Perkecil font sub-judul */
    padding: 0 0.75rem;
    margin-bottom: 1.75rem;
  }
  .portal-button {
    width: 100%;
    max-width: 280px;
    min-width: 0;
    padding: 0.75rem 1.25rem;
  }
  .button-container {
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  .aboutBody {
    padding: 2.5rem 1rem;
  }
  .churchBody {
    padding: 2.5rem 0 3rem 0;
  }
  .about-title {
    font-size: 1.5rem;
  }
  .about-subtitle {
    font-size: 0.88rem;
    margin-bottom: 2rem;
  }
  .churchText {
    font-size: 1.5rem;
  }
  .features-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
  .churchGrid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
  .feature-card {
    padding: 1.25rem 1rem;
  }
  .stat-card {
    padding: 1.25rem 1rem;
  }
  .chart-card {
    padding: 1.15rem 0.85rem;
  }
  .chart-wrapper {
    height: 260px;
  }
  .chart-wrapper-doughnut {
    height: 220px;
  }
  .partner-section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  .partner-scroll-controls {
    align-self: flex-end;
  }
  .partner-card {
    flex: 0 0 240px;
    padding: 1.25rem 1rem;
  }
  .partner-logo-box {
    height: 75px;
  }
  .partner-logo-placeholder {
    width: 60px;
    height: 60px;
    font-size: 1.8rem;
  }
  .partner-name {
    font-size: 0.9rem;
    min-height: 2.4rem;
  }
  .showcase-card-img-wrapper {
    height: 180px;
  }
  .showcase-hero-container {
    padding: 0.5rem;
  }
}

/* --- Media Query untuk Layar Ponsel Sangat Kecil (<= 480px) --- */
@media (max-width: 480px) {
  .mainBody {
    padding: 2.5rem 0.75rem;
  }
  .headerLogo {
    margin-top: -1.5rem;
  }
  .imgSize {
    width: 125px;
    height: 125px;
  }
  .headertext {
    font-size: 1.4rem;
    line-height: 1.25;
  }
  .subtext {
    font-size: 0.85rem;
    line-height: 1.45;
  }
  .about-title {
    font-size: 1.3rem;
  }
  .churchText {
    font-size: 1.3rem;
  }
  .partner-card {
    flex: 0 0 215px;
    padding: 1rem 0.75rem;
  }
  .partner-logo-box {
    height: 60px;
  }
  .partner-logo-placeholder {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
  .chart-wrapper {
    height: 240px;
  }
  .chart-wrapper-doughnut {
    height: 200px;
  }
}

/* --- Showcase Images & Cards Styling (Compact & Balanced Scale) --- */
.showcase-hero-container {
  position: relative;
  max-width: 580px;
  margin-left: auto;
  margin-right: auto;
  padding: 0.75rem;
}

.showcase-glow-backdrop {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  height: 70%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.22) 0%, rgba(245, 158, 11, 0.12) 50%, transparent 80%);
  filter: blur(35px);
  z-index: 0;
  pointer-events: none;
}

.showcase-laptop-frame {
  position: relative;
  z-index: 1;
  border-radius: 0.85rem;
  overflow: hidden;
  box-shadow: 0 15px 40px -10px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s ease;
  background: #0f172a;
}

.showcase-laptop-frame:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 22px 50px -10px rgba(0, 0, 0, 0.7), 0 0 30px rgba(245, 158, 11, 0.25);
  border-color: rgba(251, 191, 36, 0.4);
}

.showcase-img-main {
  width: 100%;
  height: auto;
  max-height: 320px;
  display: block;
  object-fit: contain;
}

.showcase-hero-caption {
  position: relative;
  z-index: 1;
  margin-top: 1rem;
  text-align: center;
}

.badge-amber {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 0.25rem 0.7rem;
  border-radius: 20px;
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.showcase-card {
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.85), rgba(28, 43, 94, 0.5));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 20px -5px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
}

.showcase-card:hover {
  transform: translateY(-5px);
  border-color: rgba(56, 189, 248, 0.4);
  box-shadow: 0 15px 28px -8px rgba(0, 0, 0, 0.5), 0 0 20px rgba(56, 189, 248, 0.15);
}

.showcase-card-img-wrapper {
  position: relative;
  width: 100%;
  height: 150px;
  overflow: hidden;
}

.showcase-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.5s ease;
}

.showcase-card:hover .showcase-card-img {
  transform: scale(1.06);
}

.showcase-card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.2) 60%, transparent 100%);
}

.showcase-card-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
  border: 1px solid;
  backdrop-filter: blur(8px);
  z-index: 2;
}

.showcase-card-content {
  padding: 1.15rem;
  text-align: left;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.showcase-card-title {
  font-family: 'Cinzel', serif;
  font-size: 1rem;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 0.4rem;
  line-height: 1.35;
}

.showcase-card-desc {
  font-family: 'Lato', sans-serif;
  font-size: 0.82rem;
  color: #94a3b8;
  line-height: 1.5;
  margin: 0;
}

/* --- Keyframe Animations for Modal & Donasi --- */
@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scaleUp {
  animation: scaleUp 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.backdrop-blur-xs {
  backdrop-filter: blur(2px);
}

/* ═══════════════════════════════════════════════════════════════════════════
   LIGHT THEME OVERRIDES FOR HOMEVIEW
   Warna Terang: Putih, Biru Muda, Hijau Muda, Emas (Kontras Tajam)
   ═══════════════════════════════════════════════════════════════════════════ */
:global(html[data-theme="light"]) {
  /* --- Hero Section --- */
  .mainBody {
    box-shadow: inset 0 0 0 1000px rgba(255, 255, 255, 0.75);
  }
  .hero-overlay {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(240, 249, 255, 0.78) 50%, rgba(224, 242, 254, 0.92) 100%);
  }
  .headertext {
    color: #b45309; /* Emas tembaga pekat */
    text-shadow: 0 2px 12px rgba(217, 119, 6, 0.25);
  }
  .subtext {
    color: #1e293b; /* Slate gelap kontras tinggi */
    text-shadow: 0 1px 4px rgba(255, 255, 255, 0.8);
  }

  /* --- Section Backgrounds (Putih & Biru Muda) --- */
  .aboutBody {
    background-color: #f8fafc;
    border-top: 1px solid rgba(217, 119, 6, 0.2);
  }
  .churchBody {
    background-color: #ffffff;
  }

  /* --- Headings & Subtitles --- */
  .about-title,
  .churchText {
    color: #0f172a; /* Hitam slate kontras */
    text-shadow: none;
  }
  .about-subtitle,
  .churchSubText {
    color: #334155; /* Slate terbaca */
  }

  /* --- Feature & Service Cards --- */
  .feature-card {
    background-color: #ffffff;
    border: 1px solid rgba(217, 119, 6, 0.25);
    box-shadow: 0 10px 25px -4px rgba(15, 23, 42, 0.07);
  }
  .feature-card:hover {
    border-color: #d97706;
    box-shadow: 0 16px 30px -6px rgba(217, 119, 6, 0.22);
  }
  .feature-title {
    color: #b45309; /* Emas gelap berbobot */
  }
  .feature-description {
    color: #475569; /* Slate terbaca jelas */
  }

  /* --- Showcase Feature Cards --- */
  .showcase-card {
    background: #ffffff;
    border: 1px solid rgba(217, 119, 6, 0.25);
    box-shadow: 0 10px 25px -4px rgba(15, 23, 42, 0.08);
  }
  .showcase-card-title {
    color: #0f172a;
  }
  .showcase-card-desc {
    color: #475569;
  }
  .showcase-card-overlay {
    background: linear-gradient(to top, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.15) 60%, transparent 100%);
  }
  .showcase-laptop-frame {
    background: #ffffff;
    border: 1px solid rgba(217, 119, 6, 0.3);
    box-shadow: 0 15px 35px -10px rgba(15, 23, 42, 0.12);
  }

  /* --- Partner / Church Cards --- */
  .partner-card {
    background: #ffffff;
    border: 1px solid rgba(217, 119, 6, 0.25);
    box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.08);
  }
  .partner-name {
    color: #0f172a;
  }
  .partner-tag,
  .partner-section-subtitle,
  .partner-scroll-hint {
    color: #64748b;
  }
  .partner-logo-placeholder {
    background: radial-gradient(circle, rgba(14, 165, 233, 0.15) 0%, rgba(240, 249, 255, 0.9) 100%);
    border: 1px solid rgba(14, 165, 233, 0.35);
    color: #0284c7;
  }
  .scroll-control-btn {
    background: #e0f2fe;
    border: 1px solid #bae6fd;
    color: #0284c7;
  }
  .scroll-control-btn:hover {
    background: #d97706;
    border-color: #b45309;
    color: #ffffff;
  }

  /* --- Statistics Cards --- */
  .stat-card {
    background-color: #ffffff;
    border: 1px solid rgba(217, 119, 6, 0.25);
    box-shadow: 0 10px 25px -4px rgba(15, 23, 42, 0.08);
  }
  .stat-card p.text-slate-200 {
    color: #1e293b !important;
  }
  .stat-card p.text-slate-400 {
    color: #64748b !important;
  }
  .stat-card .text-amber-400 {
    color: #d97706 !important;
  }
  .stat-card .text-sky-400 {
    color: #0284c7 !important;
  }
  .stat-card .text-emerald-400 {
    color: #16a34a !important;
  }

  /* --- Chart Cards --- */
  .chart-card {
    background-color: #ffffff;
    border: 1px solid rgba(217, 119, 6, 0.25);
    box-shadow: 0 10px 25px -3px rgba(15, 23, 42, 0.08);
  }
  .chart-title {
    color: #0f172a;
  }

  /* --- Donasi & Persembahan Section --- */
  #donasi {
    background-color: #f0f9ff;
    border-top: 1px solid rgba(217, 119, 6, 0.25);
  }
  #donasi .about-title {
    color: #0f172a !important;
  }
  #donasi .about-subtitle {
    color: #334155 !important;
  }
  #donasi .bg-gradient-to-br,
  #donasi .bg-gradient-to-r {
    background: #ffffff !important;
    border: 1px solid rgba(217, 119, 6, 0.28) !important;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.07) !important;
  }
  #donasi .bg-\[\#070c1e\]\/90,
  #donasi .bg-\[\#060b1c\],
  #donasi .bg-\[\#09112b\],
  #donasi .bg-\[\#0a122e\],
  #donasi .bg-slate-900,
  #donasi .bg-slate-900\/80 {
    background-color: #f0f9ff !important;
    border-color: #cbd5e1 !important;
  }
  #donasi .text-white {
    color: #0f172a !important;
  }
  #donasi .text-slate-100 {
    color: #0f172a !important;
  }
  #donasi .text-slate-200 {
    color: #1e293b !important;
  }
  #donasi .text-slate-300 {
    color: #334155 !important;
  }
  #donasi .text-slate-400 {
    color: #64748b !important;
  }
  #donasi .text-amber-300,
  #donasi .text-amber-400 {
    color: #b45309 !important;
  }
  #donasi .border-slate-800,
  #donasi .border-slate-700 {
    border-color: #e2e8f0 !important;
  }
  #donasi input,
  #donasi textarea,
  #donasi select {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid rgba(217, 119, 6, 0.35) !important;
  }
  #donasi input:focus,
  #donasi textarea:focus,
  #donasi select:focus {
    border-color: #d97706 !important;
  }
}

</style>
