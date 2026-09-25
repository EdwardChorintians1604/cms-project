<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'

const API_BASE = APP_CONFIG?.apiBaseUrl || 'http://localhost:8000/api/v1'

// ─────────────────────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────────────────────
const isLoading    = ref(true)
const isScanning   = ref(false)
const hasError     = ref(false)
const errorMsg     = ref('')

// Dashboard data (dari API)
const securityScore      = ref(0)
const securityGrade      = ref('—')
const stats              = ref({})
const threatLogs         = ref([])
const securityComponents = ref([])
const systemInfo         = ref({})
const lastUpdated        = ref(null)

// Scan state
const scanProgress = ref(0)
const scanPhase    = ref('')
const scanLogs     = ref([])
const scanSummary  = ref(null)
const lastScanTime = ref(new Date().toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' }))

// Session info dari JWT di localStorage
const sessionInfo = computed(() => {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp     = payload.exp ? new Date(payload.exp * 1000) : null
    const sub     = payload.sub || ''
    const [prefix, id] = sub.split(':')
    const roleMap  = { admin: 'Superadmin', church_admin: 'Admin Gereja', jemaat: 'Jemaat', church: 'Admin Gereja' }
    const now      = new Date()
    const minsLeft = exp ? Math.max(0, Math.floor((exp - now) / 60000)) : null
    return {
      role: roleMap[prefix] || prefix || 'Unknown',
      id: id || sub,
      exp: exp ? exp.toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' }) : 'N/A',
      minsLeft,
      isExpiring: minsLeft !== null && minsLeft < 30,
    }
  } catch {
    return null
  }
})

// Toast
const showToast  = ref(false)
const toastMsg   = ref('')
const toastType  = ref('success')

const triggerToast = (msg, type = 'success') => {
  toastMsg.value  = msg
  toastType.value = type
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 4500)
}

// ─────────────────────────────────────────────────────────────────────────────
// FETCH DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────
const fetchDashboard = async () => {
  try {
    hasError.value = false
    const token = localStorage.getItem('access_token')
    const res = await fetch(`${API_BASE}/security/dashboard`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()

    securityScore.value      = data.score?.score      ?? 0
    securityGrade.value      = data.score?.grade       ?? '—'
    stats.value              = data.stats              ?? {}
    threatLogs.value         = data.threat_logs        ?? []
    securityComponents.value = data.security_components ?? []
    systemInfo.value         = data.system_info        ?? {}
    lastUpdated.value        = new Date().toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })
  } catch (e) {
    hasError.value = true
    errorMsg.value = e.message || 'Gagal memuat data keamanan.'
    triggerToast('Gagal memuat data keamanan: ' + errorMsg.value, 'error')
  } finally {
    isLoading.value = false
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SECURITY SCAN (memanggil POST /security/scan)
// ─────────────────────────────────────────────────────────────────────────────
const runSecurityScan = async () => {
  if (isScanning.value) return
  isScanning.value = true
  scanProgress.value = 0
  scanLogs.value    = []
  scanSummary.value = null
  scanPhase.value   = 'Menginisialisasi pemindaian keamanan...'

  try {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`${API_BASE}/security/scan`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()

    // Animasikan step-by-step hasil dari API
    for (let i = 0; i < data.steps.length; i++) {
      await new Promise(r => setTimeout(r, 650))
      const step = data.steps[i]
      scanProgress.value = step.progress
      scanPhase.value    = step.phase
      const prefix = step.ok ? '[✓ OK]' : '[⚠ CATATAN]'
      scanLogs.value.push(`${prefix} ${step.log}`)
    }

    scanSummary.value = data.summary
    lastScanTime.value = new Date().toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })

    // Refresh security score setelah scan
    await fetchDashboard()

    const msg = data.summary.is_clean
      ? 'Pemindaian selesai! Tidak ditemukan celah kritis.'
      : `Pemindaian selesai! Ditemukan ${data.summary.total_findings} catatan keamanan.`
    triggerToast(msg, data.summary.is_clean ? 'success' : 'error')
  } catch (e) {
    scanLogs.value.push(`[ERROR] Gagal menghubungi server: ${e.message}`)
    triggerToast('Gagal menjalankan scan: ' + e.message, 'error')
  } finally {
    isScanning.value = false
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// EXPORT LAPORAN (data real dari API)
// ─────────────────────────────────────────────────────────────────────────────
const exportReport = () => {
  const report = {
    platform:     'GracePoint Church Management Platform',
    auditDate:    new Date().toISOString(),
    overallScore: `${securityScore.value}/100 (${securityGrade.value})`,
    stats:        stats.value,
    components:   securityComponents.value,
    threatLogs:   threatLogs.value,
    systemInfo:   systemInfo.value,
    generatedBy:  sessionInfo.value?.role || 'Superadmin',
  }
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href = url
  a.download = `GracePoint_Security_Report_${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  triggerToast('Laporan audit keamanan berhasil diunduh.')
}

// ─────────────────────────────────────────────────────────────────────────────
// AUTO-REFRESH setiap 30 detik
// ─────────────────────────────────────────────────────────────────────────────
let refreshTimer = null
onMounted(async () => {
  await fetchDashboard()
  refreshTimer = setInterval(fetchDashboard, 30_000)
})
onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})

// ─────────────────────────────────────────────────────────────────────────────
// COMPUTED / UTILS
// ─────────────────────────────────────────────────────────────────────────────
const scoreColor = computed(() => {
  if (securityScore.value >= 90) return 'text-emerald-400'
  if (securityScore.value >= 70) return 'text-amber-400'
  return 'text-rose-400'
})

const scoreGlow = computed(() => {
  if (securityScore.value >= 90) return 'shadow-emerald-500/30'
  if (securityScore.value >= 70) return 'shadow-amber-500/30'
  return 'shadow-rose-500/30'
})

const scoreRing = computed(() => {
  if (securityScore.value >= 90) return '#10b981'
  if (securityScore.value >= 70) return '#f59e0b'
  return '#ef4444'
})

// SVG ring untuk security score gauge
const ringCircumference = 2 * Math.PI * 52 // r=52
const ringOffset = computed(() =>
  ringCircumference - (securityScore.value / 100) * ringCircumference
)
</script>

<template>
  <MainAdminLayout>
    <div class="space-y-6 text-[#EDE6D6] font-sans pb-12">

      <!-- Toast -->
      <Transition name="toast">
        <div
          v-if="showToast"
          :class="[
            'fixed top-5 right-5 z-[100] max-w-md px-4 py-3 rounded-2xl shadow-2xl border flex items-center gap-3 backdrop-blur-xl transition-all duration-300',
            toastType === 'success'
              ? 'bg-emerald-950/90 text-emerald-200 border-emerald-500/50'
              : 'bg-rose-950/90 text-rose-200 border-rose-500/50'
          ]"
        >
          <i :class="['bi text-lg', toastType === 'success' ? 'bi-shield-fill-check text-emerald-400' : 'bi-exclamation-octagon-fill text-rose-400']"></i>
          <p class="text-xs font-semibold leading-relaxed">{{ toastMsg }}</p>
          <button @click="showToast = false" class="ml-auto text-slate-400 hover:text-white">
            <i class="bi bi-x-lg text-xs"></i>
          </button>
        </div>
      </Transition>

      <!-- HERO BANNER -->
      <section class="rounded-3xl border border-amber-500/25 bg-gradient-to-r from-[#0d1e27]/90 via-[#0b2027]/85 to-[#09151e]/90 p-6 shadow-2xl backdrop-blur-xl sm:p-8 relative overflow-hidden">
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -left-10 -top-10 w-48 h-48 bg-amber-500/5 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-shield-lock-fill"></i>
              <span>Cybersecurity &amp; Threat Defense Center</span>
              <!-- Indikator live refresh -->
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping ml-1"></span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-100">
              Deteksi Keamanan &amp; Pemindaian Kerentanan
            </h1>
            <p class="mt-1.5 text-xs sm:text-sm text-[#B8C4C2] max-w-2xl leading-relaxed">
              Pemantauan ancaman siber secara real-time dari database audit. Data diperbarui otomatis setiap 30 detik.
              <span v-if="lastUpdated" class="text-emerald-400 font-semibold"> · Diperbarui: {{ lastUpdated }}</span>
            </p>
          </div>

          <div class="flex items-center gap-3 shrink-0">
            <button
              type="button"
              @click="exportReport"
              class="px-4 py-2.5 rounded-xl border border-slate-700 text-xs text-slate-300 hover:text-amber-300 hover:bg-white/5 transition flex items-center gap-2 cursor-pointer"
            >
              <i class="bi bi-download"></i>
              <span>Unduh Laporan</span>
            </button>
            <button
              type="button"
              @click="fetchDashboard"
              :disabled="isLoading"
              class="px-4 py-2.5 rounded-xl border border-slate-700 text-xs text-slate-300 hover:text-sky-300 hover:bg-white/5 transition flex items-center gap-2 cursor-pointer disabled:opacity-50"
            >
              <i :class="['bi', isLoading ? 'bi-arrow-repeat animate-spin' : 'bi-arrow-clockwise']"></i>
              <span>Refresh</span>
            </button>
            <button
              type="button"
              @click="runSecurityScan"
              :disabled="isScanning || isLoading"
              class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 text-xs font-extrabold shadow-lg shadow-emerald-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50 transition"
            >
              <i :class="['bi', isScanning ? 'bi-arrow-repeat animate-spin' : 'bi-radar']"></i>
              <span>{{ isScanning ? 'Memindai...' : 'Pindai Sistem Sekarang' }}</span>
            </button>
          </div>
        </div>
      </section>

      <!-- LOADING STATE -->
      <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 gap-4">
        <div class="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
          <i class="bi bi-shield-shaded text-emerald-400 text-2xl animate-pulse"></i>
        </div>
        <p class="text-sm text-slate-400 animate-pulse">Memuat data keamanan dari server...</p>
      </div>

      <!-- ERROR STATE -->
      <div v-else-if="hasError" class="rounded-3xl border border-rose-500/30 bg-rose-950/20 p-8 text-center space-y-3">
        <i class="bi bi-exclamation-triangle-fill text-rose-400 text-3xl"></i>
        <p class="text-sm font-bold text-rose-300">Gagal memuat data keamanan</p>
        <p class="text-xs text-slate-400">{{ errorMsg }}</p>
        <button @click="fetchDashboard" class="mt-2 px-4 py-2 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs hover:bg-rose-500/30 transition">
          <i class="bi bi-arrow-clockwise mr-1"></i> Coba Lagi
        </button>
      </div>

      <template v-else>

        <!-- LIVE SCANNER OUTPUT -->
        <section v-if="isScanning || scanLogs.length > 0" class="rounded-3xl border border-emerald-500/30 bg-[#0c1a21]/90 p-6 shadow-2xl backdrop-blur-xl space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-300">
                <i class="bi bi-radar text-lg animate-spin" v-if="isScanning"></i>
                <i class="bi bi-check2-circle text-lg" v-else></i>
              </div>
              <div>
                <p class="text-xs font-bold text-white">{{ isScanning ? 'Pemindaian Kerentanan Sedang Berjalan...' : 'Hasil Audit Pemindaian Terakhir' }}</p>
                <p class="text-[11px] text-slate-400">{{ scanPhase || 'Selesai diverifikasi pada ' + lastScanTime }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <!-- Scan result badge -->
              <span v-if="scanSummary && !isScanning"
                :class="[
                  'text-[10px] font-bold px-2.5 py-1 rounded-full border',
                  scanSummary.is_clean
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                ]"
              >
                {{ scanSummary.is_clean ? `Skor: ${scanSummary.score} / Grade ${scanSummary.grade} — AMAN` : `${scanSummary.total_findings} Catatan Ditemukan` }}
              </span>
              <span class="text-sm font-black font-mono text-emerald-400">{{ scanProgress }}%</span>
            </div>
          </div>

          <div class="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-800">
            <div
              class="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-amber-400 transition-all duration-500"
              :style="{ width: `${scanProgress}%` }"
            ></div>
          </div>

          <!-- Console Stream -->
          <div class="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 font-mono text-[11px] text-slate-300 space-y-1 max-h-44 overflow-y-auto custom-scrollbar">
            <div v-for="(log, idx) in scanLogs" :key="idx" class="flex items-start gap-2">
              <span :class="log.startsWith('[⚠') ? 'text-amber-400' : 'text-emerald-400'">➜</span>
              <span :class="log.startsWith('[⚠') ? 'text-amber-200' : ''">{{ log }}</span>
            </div>
          </div>

          <!-- Scan Findings Detail -->
          <div v-if="scanSummary && scanSummary.findings?.length > 0 && !isScanning" class="space-y-2">
            <p class="text-[11px] font-bold text-amber-300 uppercase tracking-wider">Catatan yang Perlu Ditindaklanjuti:</p>
            <div v-for="(finding, i) in scanSummary.findings" :key="i"
              class="flex items-center gap-2 p-2.5 rounded-xl bg-amber-500/5 border border-amber-500/20 text-[11px] text-amber-200">
              <i class="bi bi-exclamation-triangle-fill text-amber-400 shrink-0"></i>
              {{ finding }}
            </div>
          </div>
        </section>

        <!-- TOP ROW: SCORE GAUGE + 4 METRICS -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">

          <!-- SECURITY SCORE GAUGE -->
          <div class="lg:col-span-3 p-5 rounded-3xl border border-white/10 bg-[#123138]/70 shadow-2xl backdrop-blur-xl flex flex-col items-center justify-center gap-3 relative overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-b from-transparent to-emerald-500/5 pointer-events-none"></div>
            <p class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Skor Keamanan Real-Time</p>

            <!-- SVG Ring Gauge -->
            <div class="relative w-36 h-36">
              <svg class="w-full h-full -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="10"/>
                <circle
                  cx="60" cy="60" r="52" fill="none"
                  :stroke="scoreRing"
                  stroke-width="10"
                  stroke-linecap="round"
                  :stroke-dasharray="ringCircumference"
                  :stroke-dashoffset="ringOffset"
                  style="transition: stroke-dashoffset 1s ease, stroke 0.5s ease;"
                />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span :class="['text-4xl font-black font-mono transition-all duration-700', scoreColor]">{{ securityScore }}</span>
                <span :class="['text-lg font-black', scoreColor]">{{ securityGrade }}</span>
              </div>
            </div>

            <div class="text-center space-y-0.5">
              <p :class="['text-xs font-bold', scoreColor]">
                {{ securityScore >= 90 ? 'Kondisi Prima' : securityScore >= 70 ? 'Perlu Perhatian' : 'Risiko Tinggi' }}
              </p>
              <p class="text-[10px] text-slate-500">Dihitung dari audit log real-time</p>
            </div>
          </div>

          <!-- 4 SECURITY COMPONENT CARDS -->
          <div class="lg:col-span-9 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              v-for="m in securityComponents"
              :key="m.id"
              class="p-5 rounded-3xl border border-white/10 bg-[#123138]/70 shadow-xl backdrop-blur-xl relative overflow-hidden group hover:border-white/20 transition"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <p class="text-[11px] font-medium text-slate-400">{{ m.title }}</p>
                  <h3 class="text-sm font-bold text-white mt-1 truncate">{{ m.value }}</h3>
                  <p class="text-[10px] text-slate-400 mt-0.5 leading-relaxed">{{ m.subtext }}</p>
                </div>
                <div :class="[
                    'w-10 h-10 rounded-2xl border flex items-center justify-center text-lg shrink-0 ml-3',
                    m.color === 'emerald' ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400' : '',
                    m.color === 'amber'   ? 'bg-amber-500/15   border-amber-500/30   text-amber-400'   : '',
                    m.color === 'sky'     ? 'bg-sky-500/15     border-sky-500/30     text-sky-400'     : '',
                    m.color === 'purple'  ? 'bg-purple-500/15  border-purple-500/30  text-purple-400'  : '',
                  ]"
                >
                  <i :class="['bi', m.icon]"></i>
                </div>
              </div>
              <!-- Status dot -->
              <div class="mt-3 flex items-center gap-1.5">
                <span :class="[
                    'w-1.5 h-1.5 rounded-full',
                    m.status === 'active'  ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                  ]"></span>
                <span class="text-[10px] text-slate-500">
                  {{ m.status === 'active' ? 'Aktif & Melindungi' : 'Perlu Perhatian' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- MAIN 2-COL LAYOUT -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <!-- KOLOM KIRI: INFO SISTEM + SESSION MONITOR -->
          <div class="lg:col-span-7 space-y-6">

            <!-- SYSTEM INFO NYATA -->
            <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-6 shadow-2xl backdrop-blur-xl space-y-5">
              <div class="flex items-center justify-between pb-3 border-b border-white/10">
                <div>
                  <h3 class="font-serif text-lg font-bold text-white flex items-center gap-2">
                    <i class="bi bi-shield-fill-exclamation text-amber-400"></i> Konfigurasi Keamanan Sistem Aktif
                  </h3>
                  <p class="text-xs text-slate-400 mt-0.5">Data konfigurasi nyata dari server — bukan statis.</p>
                </div>
                <span v-if="systemInfo.debug_mode"
                  class="text-[10px] font-bold px-2 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 uppercase tracking-wider">
                  DEV Mode
                </span>
                <span v-else
                  class="text-[10px] font-bold px-2 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 uppercase tracking-wider">
                  Production
                </span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <!-- JWT Config -->
                <div class="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-3">
                  <div class="flex items-center gap-2 text-amber-300">
                    <i class="bi bi-key-fill"></i>
                    <span class="text-xs font-bold">JWT & Token Auth</span>
                  </div>
                  <div class="space-y-2 text-[11px] font-mono">
                    <div class="flex justify-between">
                      <span class="text-slate-400">Algorithm</span>
                      <span class="text-emerald-300 font-bold">{{ systemInfo.jwt_algorithm || '—' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-slate-400">Token TTL</span>
                      <span class="text-white">{{ systemInfo.token_ttl_minutes ? Math.floor(systemInfo.token_ttl_minutes / 60) + ' jam' : '—' }}</span>
                    </div>
                  </div>
                </div>

                <!-- CORS Config -->
                <div class="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-3">
                  <div class="flex items-center gap-2 text-sky-300">
                    <i class="bi bi-globe2"></i>
                    <span class="text-xs font-bold">CORS & Origin Policy</span>
                  </div>
                  <div class="space-y-2 text-[11px] font-mono">
                    <div class="flex justify-between">
                      <span class="text-slate-400">Allowed Origins</span>
                      <span class="text-white">{{ systemInfo.cors_origins_count ?? '—' }} domain</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-slate-400">Rate Limit Store</span>
                      <span class="text-white truncate max-w-[120px]">{{ systemInfo.rate_limit_storage || '—' }}</span>
                    </div>
                  </div>
                </div>

                <!-- Audit Stats -->
                <div class="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-3">
                  <div class="flex items-center gap-2 text-purple-300">
                    <i class="bi bi-database-check"></i>
                    <span class="text-xs font-bold">Statistik Audit 24 Jam</span>
                  </div>
                  <div class="space-y-2 text-[11px] font-mono">
                    <div class="flex justify-between">
                      <span class="text-slate-400">Total Events</span>
                      <span class="text-white font-bold">{{ stats.total_events_24h ?? '—' }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-slate-400">Ancaman Diblokir</span>
                      <span class="text-rose-300 font-bold">{{ stats.blocked_attempts_24h ?? '—' }}</span>
                    </div>
                  </div>
                </div>

                <!-- Score Breakdown -->
                <div class="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-3">
                  <div class="flex items-center gap-2 text-emerald-300">
                    <i class="bi bi-graph-up-arrow"></i>
                    <span class="text-xs font-bold">Breakdown Skor Keamanan</span>
                  </div>
                  <div class="space-y-2 text-[11px] font-mono">
                    <div class="flex justify-between">
                      <span class="text-slate-400">Anomali 7 Hari</span>
                      <span :class="(stats.anomalies_7d ?? 0) > 0 ? 'text-rose-300' : 'text-emerald-300'" class="font-bold">
                        {{ stats.anomalies_7d ?? 0 }}
                      </span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-slate-400">Grade Keamanan</span>
                      <span :class="scoreColor" class="font-bold text-base">{{ securityGrade }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- SESSION MONITOR -->
            <section v-if="sessionInfo" class="rounded-3xl border border-sky-500/25 bg-gradient-to-b from-[#0b1c24] to-[#08151c] p-5 shadow-2xl space-y-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-2xl bg-sky-500/20 border border-sky-500/40 flex items-center justify-center text-sky-400 text-xl">
                  <i class="bi bi-person-badge-fill"></i>
                </div>
                <div>
                  <h4 class="text-xs font-bold text-white">Monitor Sesi Aktif (JWT Real-Time)</h4>
                  <p class="text-[10px] text-slate-400">Informasi token sesi Anda saat ini</p>
                </div>
                <!-- Expiring warning -->
                <span v-if="sessionInfo.isExpiring"
                  class="ml-auto text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-300 animate-pulse">
                  ⚠ Segera Kadaluarsa
                </span>
              </div>

              <div class="p-3 rounded-2xl bg-slate-950/80 border border-white/5 text-[11px] font-mono text-slate-300 grid grid-cols-2 gap-y-2">
                <div>
                  <span class="text-slate-400">Role:</span>
                  <span class="text-sky-300 font-bold ml-2">{{ sessionInfo.role }}</span>
                </div>
                <div>
                  <span class="text-slate-400">ID:</span>
                  <span class="text-slate-200 ml-2 truncate">{{ sessionInfo.id }}</span>
                </div>
                <div class="col-span-2">
                  <span class="text-slate-400">Token Kadaluarsa:</span>
                  <span class="text-amber-300 font-bold ml-2">{{ sessionInfo.exp }}</span>
                </div>
                <div class="col-span-2">
                  <span class="text-slate-400">Sisa Waktu:</span>
                  <span :class="sessionInfo.isExpiring ? 'text-rose-300' : 'text-emerald-300'" class="font-bold ml-2">
                    {{ sessionInfo.minsLeft !== null ? sessionInfo.minsLeft + ' menit' : 'N/A' }}
                  </span>
                </div>
              </div>
            </section>

            <!-- SESSION MONITOR — No Token -->
            <section v-else class="rounded-3xl border border-slate-700/50 bg-slate-950/40 p-5 text-center space-y-2">
              <i class="bi bi-person-slash text-slate-500 text-2xl"></i>
              <p class="text-xs text-slate-500">Tidak ada sesi aktif yang terdeteksi di penyimpanan lokal.</p>
            </section>

          </div>

          <!-- KOLOM KANAN: THREAT LOGS NYATA DARI DB -->
          <div class="lg:col-span-5 space-y-6">

            <!-- THREAT LOG FEED (Real dari audit_logs) -->
            <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-6 shadow-2xl backdrop-blur-xl space-y-4">
              <div class="flex items-center justify-between pb-2 border-b border-white/10">
                <div>
                  <h3 class="font-serif text-base font-bold text-white flex items-center gap-2">
                    <i class="bi bi-radioactive text-rose-400"></i> Ancaman & Anomali Terdeteksi
                  </h3>
                  <p class="text-[11px] text-slate-400">Log real dari database — diperbarui otomatis.</p>
                </div>
                <span class="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping"></span>
              </div>

              <!-- Empty state -->
              <div v-if="threatLogs.length === 0" class="py-8 text-center space-y-2">
                <i class="bi bi-shield-check text-emerald-400 text-3xl"></i>
                <p class="text-xs font-bold text-emerald-300">Tidak ada ancaman terdeteksi!</p>
                <p class="text-[11px] text-slate-500">Sistem berjalan normal. Tidak ada log anomali dalam database.</p>
              </div>

              <div v-else class="space-y-3 max-h-[420px] overflow-y-auto custom-scrollbar pr-1">
                <div
                  v-for="threat in threatLogs"
                  :key="threat.id"
                  class="p-3.5 rounded-2xl bg-slate-950/70 border border-slate-800/80 space-y-2 hover:border-slate-700 transition"
                >
                  <div class="flex items-center justify-between gap-2">
                    <span class="text-[10px] font-mono font-bold text-slate-400">{{ threat.timestamp }}</span>
                    <span :class="['px-2 py-0.5 rounded-full text-[9px] font-bold border shrink-0', threat.badge_class]">
                      {{ threat.action_taken }}
                    </span>
                  </div>

                  <div class="text-xs">
                    <p class="font-bold text-rose-300 leading-tight">{{ threat.attack_type }}</p>
                    <p class="font-mono text-[10px] text-slate-400 mt-0.5 truncate">{{ threat.target }}</p>
                  </div>

                  <div class="flex items-center justify-between pt-1 border-t border-white/5 text-[10px] font-mono text-slate-400">
                    <span>IP: <span class="text-slate-300">{{ threat.ip }}</span></span>
                    <span class="truncate max-w-[120px]">{{ threat.actor }}</span>
                  </div>
                </div>
              </div>
            </section>

            <!-- CRYPTOGRAPHIC INTEGRITY CARD -->
            <section class="rounded-3xl border border-amber-500/25 bg-gradient-to-b from-[#0b1c24] to-[#08151c] p-5 shadow-2xl space-y-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-2xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 text-xl">
                  <i class="bi bi-patch-check-fill"></i>
                </div>
                <div>
                  <h4 class="text-xs font-bold text-white">Sertifikasi Integritas Sistem</h4>
                  <p class="text-[10px] text-slate-400">GracePoint Security Assurance Standard</p>
                </div>
              </div>

              <div class="p-3 rounded-2xl bg-slate-950/80 border border-white/5 text-[11px] font-mono text-slate-300 space-y-1.5">
                <div class="flex justify-between">
                  <span class="text-slate-400">JWT Algorithm:</span>
                  <span class="text-emerald-300 font-bold">{{ systemInfo.jwt_algorithm || 'HS256' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-400">Password Hash:</span>
                  <span class="text-amber-300 font-bold">bcrypt (adaptive cost)</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-400">Audit Trail:</span>
                  <span class="text-sky-300 font-bold">Real-Time DB Logged</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-400">Terakhir Dipindai:</span>
                  <span class="text-slate-300">{{ lastScanTime }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-400">Data Diperbarui:</span>
                  <span class="text-slate-300">{{ lastUpdated || '—' }}</span>
                </div>
              </div>
            </section>

          </div>
        </div>

      </template>
    </div>
  </MainAdminLayout>
</template>

<style scoped>
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
  width: 5px;
  height: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.25);
  border-radius: 4px;
}
</style>
