<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import AOS from 'aos'
import 'aos/dist/aos.css'

const route = useRoute()

// State Data
const systemLogs = ref([])
const isLoading = ref(false)
const isAutoRefresh = ref(true)
const lastRefreshed = ref(null)
const logLimit = ref(100)
const searchQuery = ref('')
const selectedLevel = ref('ALL')
const selectedEntity = ref('ALL')
const viewMode = ref('timeline') // 'timeline' | 'table'
const selectedLogDetail = ref(null)
const isDetailModalOpen = ref(false)
const copyNotification = ref('')

let refreshTimer = null

// Tingkat Level Konfigurasi Warna
const logLevelMeta = {
  SUCCESS: { 
    label: 'SUCCESS',
    dot: 'bg-teal-400 ring-teal-500/30', 
    badge: 'bg-teal-500/15 text-teal-300 border-teal-500/30',
    border: 'border-teal-500/30',
    bgLight: 'bg-teal-500/5',
    text: 'text-teal-300'
  },
  NOTICE:  { 
    label: 'NOTICE',
    dot: 'bg-amber-400 ring-amber-500/30', 
    badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    border: 'border-amber-500/30',
    bgLight: 'bg-amber-500/5',
    text: 'text-amber-300'
  },
  WARNING: { 
    label: 'WARNING',
    dot: 'bg-orange-400 ring-orange-500/30', 
    badge: 'bg-orange-500/15 text-orange-300 border-orange-500/30',
    border: 'border-orange-500/30',
    bgLight: 'bg-orange-500/5',
    text: 'text-orange-300'
  },
  ERROR:   { 
    label: 'ERROR',
    dot: 'bg-rose-500 ring-rose-500/40 animate-pulse', 
    badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
    border: 'border-rose-500/30',
    bgLight: 'bg-rose-500/10',
    text: 'text-rose-300'
  },
  INFO:    { 
    label: 'INFO',
    dot: 'bg-cyan-400 ring-cyan-500/30', 
    badge: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
    border: 'border-cyan-500/30',
    bgLight: 'bg-cyan-500/5',
    text: 'text-cyan-300'
  }
}

const logMeta = (level) => logLevelMeta[level] || logLevelMeta.INFO

// Format Waktu
const formatAuditTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return '-'
  return new Intl.DateTimeFormat('id-ID', {
    dateStyle: 'medium',
    timeStyle: 'medium'
  }).format(date)
}

const formatRelativeTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return '-'
  const diffSec = Math.floor((Date.now() - date.getTime()) / 1000)
  if (diffSec < 5) return 'Baru saja'
  if (diffSec < 60) return `${diffSec} detik lalu`
  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `${diffMin} menit lalu`
  const diffHours = Math.floor(diffMin / 60)
  if (diffHours < 24) return `${diffHours} jam lalu`
  return `${Math.floor(diffHours / 24)} hari lalu`
}

// Fetch API Logs
const loadAuditLogs = async (silent = false) => {
  if (!silent) isLoading.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/audit-logs?limit=${logLimit.value}`)
    if (res.ok) {
      const data = await res.json()
      systemLogs.value = data.logs || []
      lastRefreshed.value = new Date()
    }
  } catch (err) {
    console.error('Error loading audit logs:', err)
  } finally {
    if (!silent) isLoading.value = false
  }
}

// Auto-Refresh Logic
const toggleAutoRefresh = () => {
  isAutoRefresh.value = !isAutoRefresh.value
  setupRefreshTimer()
}

const setupRefreshTimer = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (isAutoRefresh.value) {
    refreshTimer = setInterval(() => {
      loadAuditLogs(true)
    }, 5000)
  }
}

// Filtered List
const filteredLogs = computed(() => {
  let list = systemLogs.value

  if (selectedLevel.value !== 'ALL') {
    if (selectedLevel.value === 'ANOMALY') {
      list = list.filter(l => l.level === 'ERROR' || l.action === 'ANOMALY_DETECTED')
    } else {
      list = list.filter(l => l.level === selectedLevel.value)
    }
  }

  if (selectedEntity.value !== 'ALL') {
    list = list.filter(l => (l.entity || '').toLowerCase() === selectedEntity.value.toLowerCase())
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter(l => {
      return (
        (l.event || '').toLowerCase().includes(q) ||
        (l.user || '').toLowerCase().includes(q) ||
        (l.action || '').toLowerCase().includes(q) ||
        (l.entity || '').toLowerCase().includes(q) ||
        (l.entity_id ? String(l.entity_id) : '').toLowerCase().includes(q) ||
        (l.level || '').toLowerCase().includes(q)
      )
    })
  }

  return list
})

// KPI Perhitungan
const anomalyLogs = computed(() => systemLogs.value.filter(log => log.level === 'ERROR' || log.action === 'ANOMALY_DETECTED'))
const successCount = computed(() => systemLogs.value.filter(log => log.level === 'SUCCESS').length)
const warningCount = computed(() => systemLogs.value.filter(log => log.level === 'WARNING' || log.level === 'NOTICE').length)
const infoCount = computed(() => systemLogs.value.filter(log => log.level === 'INFO').length)

// Unique Entities List for Filter
const availableEntities = computed(() => {
  const set = new Set()
  systemLogs.value.forEach(l => {
    if (l.entity) set.add(l.entity)
  })
  return Array.from(set).sort()
})

// Inspector Modal
const openDetail = (log) => {
  selectedLogDetail.value = log
  isDetailModalOpen.value = true
}

const copyToClipboard = (text, label = 'Data') => {
  navigator.clipboard.writeText(text).then(() => {
    copyNotification.value = `${label} berhasil disalin ke clipboard!`
    setTimeout(() => {
      copyNotification.value = ''
    }, 2500)
  })
}

// Export logs to JSON
const exportLogsToJson = () => {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(filteredLogs.value, null, 2))
  const downloadAnchor = document.createElement('a')
  downloadAnchor.setAttribute("href", dataStr)
  downloadAnchor.setAttribute("download", `audit-log-gracepoint-${new Date().toISOString().slice(0, 10)}.json`)
  document.body.appendChild(downloadAnchor)
  downloadAnchor.click()
  downloadAnchor.remove()
}

// Export logs to CSV
const exportLogsToCsv = () => {
  const headers = ['ID', 'Waktu', 'Tingkat', 'Aktor', 'Aksi', 'Entitas', 'ID Entitas', 'Detail Aktivitas']
  const rows = filteredLogs.value.map(l => [
    l.id || '',
    l.created_at || l.time || '',
    l.level || '',
    `"${(l.user || '').replace(/"/g, '""')}"`,
    `"${(l.action || '').replace(/"/g, '""')}"`,
    `"${(l.entity || '').replace(/"/g, '""')}"`,
    `"${(l.entity_id || '').replace(/"/g, '""')}"`,
    `"${(l.event || '').replace(/"/g, '""')}"`
  ])
  
  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const downloadAnchor = document.createElement('a')
  downloadAnchor.setAttribute("href", encodeURI(csvContent))
  downloadAnchor.setAttribute("download", `audit-log-gracepoint-${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(downloadAnchor)
  downloadAnchor.click()
  downloadAnchor.remove()
}

watch(logLimit, () => {
  loadAuditLogs()
})

onMounted(async () => {
  await loadAuditLogs()
  setupRefreshTimer()
  AOS.init({ duration: 600, once: true })
  
  if (route.hash === '#anomali') {
    selectedLevel.value = 'ANOMALY'
  }
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<template>
  <MainAdminLayout>
    <div class="relative space-y-6 text-[#EDE6D6]">
      <div class="pointer-events-none fixed inset-0 -z-10 bg-[#0B2027]"></div>

      <!-- Toast Notification Copy -->
      <Transition name="fade">
        <div 
          v-if="copyNotification" 
          class="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-teal-500 text-slate-950 font-bold text-xs shadow-2xl flex items-center gap-2 border border-teal-300"
        >
          <span>✓</span>
          <span>{{ copyNotification }}</span>
        </div>
      </Transition>

      <!-- Header Section -->
      <section 
        data-aos="fade-down"
        class="relative overflow-hidden rounded-2xl border border-amber-500/20 bg-[#123138]/80 p-5 sm:p-6 shadow-2xl backdrop-blur-xl"
      >
        <div class="absolute inset-0 opacity-[0.05] pointer-events-none" style="background-image: radial-gradient(#EDE6D6 1px, transparent 1px); background-size: 20px 20px;"></div>
        
        <div class="relative z-10 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div class="flex items-center gap-2 mb-1.5 flex-wrap">
              <span class="text-[10px] font-bold uppercase tracking-[0.25em] text-cyan-300">Pusat Keamanan & Audit IT</span>
              <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/15 text-teal-300 border border-teal-500/30">
                <span class="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse"></span>
                PostgreSQL Live Stream
              </span>
              <span 
                v-if="anomalyLogs.length > 0"
                class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse"
              >
                ⚠️ {{ anomalyLogs.length }} Anomali Terdeteksi
              </span>
              <span v-else class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/10 text-teal-300 border border-teal-500/30">
                🛡️ Sistem Normal & Aman
              </span>
            </div>

            <h1 class="font-serif text-2xl sm:text-3xl font-bold tracking-tight text-[#F5EFE0]">
              Audit IT & Catatan Aktivitas Sistem
            </h1>
            <p class="mt-1 max-w-2xl text-xs sm:text-sm leading-relaxed text-[#B8C4C2]">
              Jejak kronologis audit server (audit trail) untuk seluruh perubahan data, autentikasi pengguna, pembuatan akun, mutasi basis data, dan integritas keamanan platform GracePoint.
            </p>
          </div>

          <!-- Quick Action Buttons -->
          <div class="flex flex-wrap items-center gap-2.5 shrink-0">
            <!-- Auto-Refresh Toggle Button -->
            <button
              @click="toggleAutoRefresh"
              :class="[
                'px-3 py-2 rounded-xl text-xs font-semibold border transition-all flex items-center gap-2 cursor-pointer shadow-sm',
                isAutoRefresh 
                  ? 'bg-teal-500/15 text-teal-300 border-teal-500/40 hover:bg-teal-500/25' 
                  : 'bg-white/5 text-[#8AA0A4] border-white/10 hover:text-[#EDE6D6]'
              ]"
              :title="isAutoRefresh ? 'Auto-refresh tiap 5 detik aktif' : 'Auto-refresh dinonaktifkan'"
            >
              <span class="w-2 h-2 rounded-full" :class="isAutoRefresh ? 'bg-teal-400 animate-ping' : 'bg-slate-500'"></span>
              <span>{{ isAutoRefresh ? 'Live Sync (5s)' : 'Sync Manual' }}</span>
            </button>

            <!-- Manual Reload Button -->
            <button
              @click="loadAuditLogs(false)"
              :disabled="isLoading"
              class="px-3.5 py-2 rounded-xl bg-[#0B2027]/80 hover:bg-[#0B2027] text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 font-semibold text-xs transition cursor-pointer flex items-center gap-2 disabled:opacity-50"
            >
              <svg :class="['w-4 h-4', { 'animate-spin': isLoading }]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>{{ isLoading ? 'Menyinkronkan...' : 'Muat Ulang' }}</span>
            </button>

            <!-- Export Dropdown / Buttons -->
            <button
              @click="exportLogsToJson"
              class="px-3 py-2 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 text-xs font-semibold transition cursor-pointer flex items-center gap-1.5"
              title="Unduh file log format JSON"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>JSON</span>
            </button>

            <button
              @click="exportLogsToCsv"
              class="px-3 py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition cursor-pointer flex items-center gap-1.5"
              title="Unduh file log format CSV / Excel"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
              <span>CSV</span>
            </button>
          </div>
        </div>
      </section>

      <!-- 4 Cards Stat Ringkasan Audit -->
      <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Card 1: Total Catatan -->
        <div data-aos="fade-up" data-aos-delay="50" class="bg-[#123138]/70 border border-cyan-500/20 rounded-2xl p-4 backdrop-blur-md shadow-xl">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] uppercase font-bold tracking-wider text-cyan-300/80">Total Audit Loaded</span>
            <span class="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-300">📋</span>
          </div>
          <p class="font-serif text-3xl font-bold text-cyan-200">{{ systemLogs.length }}</p>
          <p class="text-[11px] text-[#8AA0A4] mt-1">Dibatasi {{ logLimit }} riwayat terbaru</p>
        </div>

        <!-- Card 2: Status Anomali & Error -->
        <div 
          data-aos="fade-up" 
          data-aos-delay="100" 
          class="rounded-2xl p-4 backdrop-blur-md shadow-xl border transition"
          :class="anomalyLogs.length > 0 ? 'bg-rose-950/30 border-rose-500/40 shadow-rose-500/10' : 'bg-[#123138]/70 border-teal-500/20'"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] uppercase font-bold tracking-wider" :class="anomalyLogs.length > 0 ? 'text-rose-400' : 'text-teal-300/80'">
              Anomali & Error
            </span>
            <span class="p-1.5 rounded-lg" :class="anomalyLogs.length > 0 ? 'bg-rose-500/20 text-rose-300' : 'bg-teal-500/10 text-teal-300'">
              {{ anomalyLogs.length > 0 ? '🚨' : '🛡️' }}
            </span>
          </div>
          <p class="font-serif text-3xl font-bold" :class="anomalyLogs.length > 0 ? 'text-rose-400' : 'text-teal-300'">
            {{ anomalyLogs.length }}
          </p>
          <p class="text-[11px] mt-1" :class="anomalyLogs.length > 0 ? 'text-rose-300/80' : 'text-[#8AA0A4]'">
            {{ anomalyLogs.length > 0 ? 'Perlu tindakan investigasi segera' : 'Zero critical failure terdeteksi' }}
          </p>
        </div>

        <!-- Card 3: Operasi Sukses (CREATE & UPDATE) -->
        <div data-aos="fade-up" data-aos-delay="150" class="bg-[#123138]/70 border border-teal-500/20 rounded-2xl p-4 backdrop-blur-md shadow-xl">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] uppercase font-bold tracking-wider text-teal-300/80">Operasi Sukses (OK)</span>
            <span class="p-1.5 rounded-lg bg-teal-500/10 text-teal-300">✅</span>
          </div>
          <p class="font-serif text-3xl font-bold text-teal-200">{{ successCount }}</p>
          <p class="text-[11px] text-[#8AA0A4] mt-1">{{ Math.round((successCount / (systemLogs.length || 1)) * 100) }}% rasio aktivitas sukses</p>
        </div>

        <!-- Card 4: Waktu Sinkronisasi Terakhir -->
        <div data-aos="fade-up" data-aos-delay="200" class="bg-[#123138]/70 border border-amber-500/20 rounded-2xl p-4 backdrop-blur-md shadow-xl">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] uppercase font-bold tracking-wider text-amber-300/80">Aktivitas Terakhir</span>
            <span class="p-1.5 rounded-lg bg-amber-500/10 text-amber-300">⏱️</span>
          </div>
          <p class="font-serif text-xl font-bold text-amber-300 truncate">
            {{ systemLogs[0] ? formatRelativeTime(systemLogs[0].created_at || systemLogs[0].time) : '-' }}
          </p>
          <p class="text-[11px] text-[#8AA0A4] mt-1">
            {{ systemLogs[0] ? (systemLogs[0].user || 'System') : 'Belum ada event' }}
          </p>
        </div>
      </section>

      <!-- Filter & Search Toolbar -->
      <section 
        data-aos="fade-up" 
        class="bg-[#123138]/70 border border-white/5 rounded-2xl p-4 sm:p-5 shadow-xl backdrop-blur-md space-y-4"
      >
        <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          
          <!-- Search Bar -->
          <div class="relative flex-1 min-w-[240px]">
            <svg class="w-4 h-4 text-[#8AA0A4] absolute left-3.5 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-4.35-4.35M17 11a6 6 0 1 1-12 0 6 6 0 0 1 12 0z"/>
            </svg>
            <input 
              v-model="searchQuery" 
              type="search" 
              placeholder="Cari aktivitas, nama user, entitas (church, jemaat, backup), atau tipe aksi..." 
              class="w-full bg-[#0B2027]/80 border border-white/10 focus:border-cyan-400 text-[#EDE6D6] text-xs rounded-xl pl-10 pr-4 py-2.5 outline-none transition"
            />
          </div>

          <!-- Controls: Entity, Limit, View Mode -->
          <div class="flex flex-wrap items-center gap-2.5">
            <!-- Filter Entitas -->
            <select
              v-model="selectedEntity"
              class="bg-[#0B2027]/80 border border-white/10 text-[#EDE6D6] text-xs rounded-xl px-3 py-2.5 outline-none focus:border-cyan-400 cursor-pointer"
            >
              <option value="ALL">Semua Entitas ({{ availableEntities.length }})</option>
              <option v-for="ent in availableEntities" :key="ent" :value="ent">
                {{ ent }}
              </option>
            </select>

            <!-- Limit Selector -->
            <select
              v-model.number="logLimit"
              class="bg-[#0B2027]/80 border border-white/10 text-[#EDE6D6] text-xs rounded-xl px-3 py-2.5 outline-none focus:border-cyan-400 cursor-pointer font-mono"
            >
              <option :value="50">50 Baris</option>
              <option :value="100">100 Baris</option>
              <option :value="200">200 Baris</option>
            </select>

            <!-- View Switcher: Timeline vs Table -->
            <div class="flex items-center bg-[#0B2027]/80 border border-white/10 rounded-xl p-1">
              <button
                @click="viewMode = 'timeline'"
                :class="[
                  'px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5',
                  viewMode === 'timeline' ? 'bg-cyan-500 text-slate-950 shadow-md font-bold' : 'text-[#8AA0A4] hover:text-[#EDE6D6]'
                ]"
                title="Tampilan Garis Waktu Kronologis"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                <span>Timeline</span>
              </button>
              <button
                @click="viewMode = 'table'"
                :class="[
                  'px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5',
                  viewMode === 'table' ? 'bg-cyan-500 text-slate-950 shadow-md font-bold' : 'text-[#8AA0A4] hover:text-[#EDE6D6]'
                ]"
                title="Tampilan Tabel Rinci"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 4h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                <span>Tabel</span>
              </button>
            </div>

          </div>
        </div>

        <!-- Level Filter Tabs -->
        <div class="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar border-t border-white/5 pt-3">
          <span class="text-[10px] uppercase font-bold text-[#8AA0A4] mr-2 shrink-0">Filter Tingkat:</span>

          <button
            @click="selectedLevel = 'ALL'"
            :class="[
              'px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer shrink-0',
              selectedLevel === 'ALL' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold' : 'bg-white/5 text-[#8AA0A4] hover:text-[#EDE6D6]'
            ]"
          >
            Semua ({{ systemLogs.length }})
          </button>

          <button
            @click="selectedLevel = 'ANOMALY'"
            :class="[
              'px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer shrink-0 flex items-center gap-1.5',
              selectedLevel === 'ANOMALY' ? 'bg-rose-500/25 text-rose-300 border border-rose-500/50 font-bold shadow-lg shadow-rose-500/20' : 'bg-rose-500/10 text-rose-300/80 hover:bg-rose-500/15'
            ]"
          >
            <span>🚨 Anomali</span>
            <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-rose-950 font-mono">{{ anomalyLogs.length }}</span>
          </button>

          <button
            @click="selectedLevel = 'SUCCESS'"
            :class="[
              'px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer shrink-0 flex items-center gap-1.5',
              selectedLevel === 'SUCCESS' ? 'bg-teal-500/25 text-teal-300 border border-teal-500/50 font-bold' : 'bg-teal-500/10 text-teal-300/80 hover:bg-teal-500/15'
            ]"
          >
            <span>SUCCESS</span>
            <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-teal-950 font-mono">{{ successCount }}</span>
          </button>

          <button
            @click="selectedLevel = 'NOTICE'"
            :class="[
              'px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer shrink-0',
              selectedLevel === 'NOTICE' ? 'bg-amber-500/25 text-amber-300 border border-amber-500/50 font-bold' : 'bg-amber-500/10 text-amber-300/80 hover:bg-amber-500/15'
            ]"
          >
            NOTICE
          </button>

          <button
            @click="selectedLevel = 'WARNING'"
            :class="[
              'px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer shrink-0 flex items-center gap-1.5',
              selectedLevel === 'WARNING' ? 'bg-orange-500/25 text-orange-300 border border-orange-500/50 font-bold' : 'bg-orange-500/10 text-orange-300/80 hover:bg-orange-500/15'
            ]"
          >
            WARNING
          </button>

          <button
            @click="selectedLevel = 'ERROR'"
            :class="[
              'px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer shrink-0',
              selectedLevel === 'ERROR' ? 'bg-rose-500/25 text-rose-300 border border-rose-500/50 font-bold' : 'bg-rose-500/10 text-rose-300/80 hover:bg-rose-500/15'
            ]"
          >
            ERROR
          </button>

          <button
            @click="selectedLevel = 'INFO'"
            :class="[
              'px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer shrink-0',
              selectedLevel === 'INFO' ? 'bg-cyan-500/25 text-cyan-300 border border-cyan-500/50 font-bold' : 'bg-cyan-500/10 text-cyan-300/80 hover:bg-cyan-500/15'
            ]"
          >
            INFO ({{ infoCount }})
          </button>
        </div>
      </section>

      <!-- ======================================================= -->
      <!-- TAMPILAN 1: TIMELINE KRONOLOGIS (SESUAI DARI BERANDA)   -->
      <!-- ======================================================= -->
      <section 
        v-if="viewMode === 'timeline'"
        id="security"
        data-aos="fade-up"
        class="bg-[#123138]/70 border border-white/5 rounded-2xl p-6 sm:p-8 shadow-xl backdrop-blur-md"
      >
        <div class="flex flex-wrap items-center justify-between gap-3 mb-6 border-b border-white/5 pb-4">
          <div>
            <h2 class="font-serif text-lg sm:text-xl font-bold text-[#F5EFE0] flex items-center gap-2.5">
              <span>Catatan Aktivitas Sistem (Timeline View)</span>
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-black/40 font-mono text-cyan-300">
                {{ filteredLogs.length }} Baris
              </span>
            </h2>
            <p class="text-xs text-[#8AA0A4] mt-0.5">
              Urutan kronologis aksi dan peristiwa sistem dari yang paling baru ke terlama.
            </p>
          </div>

          <span
            class="px-3 py-1 rounded-full text-xs font-bold border transition shadow-sm"
            :class="anomalyLogs.length > 0 ? 'bg-rose-500/15 text-rose-300 border-rose-500/40 shadow-rose-500/10' : 'bg-teal-500/10 text-teal-300 border-teal-500/30'"
          >
            {{ anomalyLogs.length > 0 ? `${anomalyLogs.length} Anomali Terdeteksi` : 'Tidak Ada Anomali' }}
          </span>
        </div>

        <!-- Empty State -->
        <div v-if="filteredLogs.length === 0" class="py-14 text-center border border-dashed border-white/10 rounded-2xl bg-[#0B2027]/40">
          <p class="text-3xl mb-2">🔍</p>
          <p class="text-sm font-semibold text-[#EDE6D6]">Tidak ada catatan audit yang cocok</p>
          <p class="text-xs text-[#8AA0A4] mt-1 max-w-sm mx-auto">
            Coba sesuaikan kata kunci pencarian atau ganti filter tingkat level dan entitas di atas.
          </p>
        </div>

        <!-- Timeline Log Container -->
        <div v-else class="relative pl-6 sm:pl-8">
          <!-- Timeline Vertical Rule -->
          <div class="absolute left-[11px] sm:left-[15px] top-2 bottom-2 w-px bg-white/10"></div>

          <!-- Log Item -->
          <div 
            v-for="(log, lIdx) in filteredLogs" 
            :key="log.id || lIdx" 
            class="relative pb-6 last:pb-0 group"
          >
            <!-- Timeline Dot -->
            <span 
              class="absolute -left-6 sm:-left-8 top-1.5 w-3.5 h-3.5 rounded-full ring-4 ring-[#123138] transition-transform group-hover:scale-125" 
              :class="logMeta(log.level).dot"
            ></span>

            <!-- Content Card on Timeline -->
            <div 
              @click="openDetail(log)"
              class="p-3.5 sm:p-4 rounded-xl bg-[#0B2027]/60 border border-white/5 hover:border-cyan-500/30 hover:bg-[#0B2027]/90 transition-all duration-200 cursor-pointer shadow-sm hover:shadow-md"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="flex flex-wrap items-center gap-2.5">
                  <span 
                    class="font-mono text-[11px] text-cyan-300/80 bg-cyan-950/50 px-2 py-0.5 rounded border border-cyan-500/20" 
                    :title="log.created_at || log.time"
                  >
                    {{ formatAuditTime(log.created_at || log.time) }}
                  </span>
                  
                  <span class="text-sm font-semibold text-[#EDE6D6] group-hover:text-amber-300 transition">
                    {{ log.event }}
                  </span>
                </div>

                <div class="flex items-center gap-2 shrink-0">
                  <span class="text-[11px] font-mono text-[#8AA0A4] bg-white/5 px-2 py-0.5 rounded border border-white/5">
                    👤 {{ log.user || 'System' }}
                  </span>
                  <span class="px-2.5 py-0.5 rounded text-[10px] font-bold border uppercase font-mono" :class="logMeta(log.level).badge">
                    {{ log.level }}
                  </span>
                </div>
              </div>

              <!-- Action & Entity Subtitle -->
              <div v-if="log.action || log.entity" class="mt-2 flex flex-wrap items-center gap-2 text-[11px] font-mono text-[#6F8588]">
                <span class="px-2 py-0.5 rounded bg-black/30 text-amber-300/90 font-bold text-[10px]">
                  ACTION: {{ log.action }}
                </span>
                <span>•</span>
                <span class="text-slate-300">
                  Entitas: <strong class="text-slate-200">{{ log.entity }}</strong>
                  <span v-if="log.entity_id" class="text-amber-300/80"> #{{ log.entity_id }}</span>
                </span>
                <span class="ml-auto text-[10px] text-[#8AA0A4] italic group-hover:text-cyan-300 transition">
                  Klik untuk detail inspeksi &rarr;
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ======================================================= -->
      <!-- TAMPILAN 2: TABEL AUDIT DETAIL                          -->
      <!-- ======================================================= -->
      <section 
        v-else
        data-aos="fade-up"
        class="bg-[#123138]/70 border border-white/5 rounded-2xl p-6 shadow-xl backdrop-blur-md space-y-4"
      >
        <div class="flex items-center justify-between mb-2">
          <div>
            <h2 class="font-serif text-lg font-bold text-[#F5EFE0]">Tabel Catatan IT Audit</h2>
            <p class="text-xs text-[#8AA0A4]">Tinjau data relasional log dalam format baris dan kolom terstruktur.</p>
          </div>
          <span class="text-xs font-mono text-cyan-300 bg-[#0B2027] px-3 py-1 rounded-xl border border-cyan-500/30">
            {{ filteredLogs.length }} Baris Terfilter
          </span>
        </div>

        <div class="overflow-x-auto rounded-xl border border-white/10">
          <table class="w-full text-left text-xs">
            <thead class="bg-[#0B2027]/90 text-cyan-300 font-bold uppercase border-b border-cyan-500/20 font-mono text-[11px]">
              <tr>
                <th class="py-3.5 px-4">Waktu</th>
                <th class="py-3.5 px-4">Tingkat</th>
                <th class="py-3.5 px-4">Aktor / User</th>
                <th class="py-3.5 px-4">Aksi</th>
                <th class="py-3.5 px-4">Entitas Terkait</th>
                <th class="py-3.5 px-4">Deskripsi Aktivitas</th>
                <th class="py-3.5 px-4 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5 text-[#C6D2D0]">
              <tr 
                v-for="log in filteredLogs" 
                :key="log.id" 
                class="hover:bg-white/[0.04] transition cursor-pointer"
                @click="openDetail(log)"
              >
                <td class="py-3 px-4 font-mono text-[11px] text-[#8AA0A4] whitespace-nowrap">
                  {{ formatAuditTime(log.created_at || log.time) }}
                </td>
                <td class="py-3 px-4">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold border uppercase font-mono" :class="logMeta(log.level).badge">
                    {{ log.level }}
                  </span>
                </td>
                <td class="py-3 px-4 font-mono font-medium text-[#EDE6D6] whitespace-nowrap">
                  {{ log.user || 'System' }}
                </td>
                <td class="py-3 px-4 font-mono text-amber-300 font-semibold whitespace-nowrap">
                  {{ log.action }}
                </td>
                <td class="py-3 px-4 whitespace-nowrap">
                  <span class="px-2 py-0.5 rounded-full bg-white/5 border border-white/10 font-mono text-[10px] text-cyan-200">
                    {{ log.entity }}<span v-if="log.entity_id">: {{ log.entity_id }}</span>
                  </span>
                </td>
                <td class="py-3 px-4 font-medium text-[#EDE6D6] max-w-xs truncate" :title="log.event">
                  {{ log.event }}
                </td>
                <td class="py-3 px-4 text-right">
                  <button 
                    @click.stop="openDetail(log)" 
                    class="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-cyan-500/20 text-cyan-300 border border-white/10 hover:border-cyan-500/30 text-[11px] font-semibold transition"
                  >
                    Detail
                  </button>
                </td>
              </tr>
              <tr v-if="filteredLogs.length === 0">
                <td colspan="7" class="py-12 text-center text-[#8AA0A4]">
                  Tidak ada catatan audit yang cocok dengan filter atau pencarian.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ======================================================= -->
      <!-- MODAL DETAIL INSPECTOR AUDIT LOG                        -->
      <!-- ======================================================= -->
      <Transition name="modal">
        <div 
          v-if="isDetailModalOpen && selectedLogDetail" 
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B2027]/85 backdrop-blur-md overflow-y-auto"
        >
          <div class="bg-[#123138] border border-cyan-500/30 rounded-2xl p-6 w-full max-w-xl shadow-2xl space-y-4 my-auto text-slate-100 text-xs">
            
            <!-- Modal Header -->
            <div class="flex items-center justify-between border-b border-white/10 pb-3">
              <div class="flex items-center gap-2.5">
                <span class="w-3 h-3 rounded-full" :class="logMeta(selectedLogDetail.level).dot"></span>
                <h3 class="font-serif text-base font-bold text-[#F5EFE0]">
                  Inspeksi Detail Rekam Jejak IT
                </h3>
              </div>
              <button 
                @click="isDetailModalOpen = false" 
                class="text-[#8AA0A4] hover:text-[#EDE6D6] cursor-pointer text-sm p-1"
              >
                ✕
              </button>
            </div>

            <!-- Modal Body Details -->
            <div class="space-y-3">
              <div class="p-3.5 rounded-xl bg-[#0B2027]/80 border border-white/5 space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-[10px] uppercase font-bold text-[#8AA0A4]">Status & Tingkat:</span>
                  <span class="px-2.5 py-0.5 rounded text-[10px] font-bold border uppercase font-mono" :class="logMeta(selectedLogDetail.level).badge">
                    {{ selectedLogDetail.level }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-[10px] uppercase font-bold text-[#8AA0A4]">Waktu Kejadian:</span>
                  <span class="font-mono text-cyan-300">{{ formatAuditTime(selectedLogDetail.created_at || selectedLogDetail.time) }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-[10px] uppercase font-bold text-[#8AA0A4]">Aktor / Pengguna:</span>
                  <span class="font-mono text-[#EDE6D6] font-bold">{{ selectedLogDetail.user || 'System' }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-[10px] uppercase font-bold text-[#8AA0A4]">Aksi / Mutasi:</span>
                  <span class="font-mono text-amber-300 font-bold">{{ selectedLogDetail.action }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-[10px] uppercase font-bold text-[#8AA0A4]">Entitas Target:</span>
                  <span class="font-mono text-teal-300">{{ selectedLogDetail.entity }} (ID: {{ selectedLogDetail.entity_id || 'N/A' }})</span>
                </div>
              </div>

              <!-- Deskripsi Event Lengkap -->
              <div>
                <label class="block text-[10px] uppercase font-bold text-[#8AA0A4] mb-1">Catatan Deskripsi Lengkap:</label>
                <div class="p-3 rounded-xl bg-[#0B2027] border border-white/10 text-[#EDE6D6] font-medium leading-relaxed">
                  {{ selectedLogDetail.event }}
                </div>
              </div>

              <!-- Raw Payload Preview -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="text-[10px] uppercase font-bold text-[#8AA0A4]">Payload JSON Objek Log:</label>
                  <button 
                    type="button" 
                    @click="copyToClipboard(JSON.stringify(selectedLogDetail, null, 2), 'JSON Log')"
                    class="text-[10px] text-cyan-300 hover:underline flex items-center gap-1 cursor-pointer"
                  >
                    <span>📋 Salin JSON</span>
                  </button>
                </div>
                <pre class="p-3 rounded-xl bg-[#08171c] border border-white/5 text-[11px] font-mono text-cyan-200 overflow-x-auto max-h-36 custom-scrollbar">{{ JSON.stringify(selectedLogDetail, null, 2) }}</pre>
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="flex justify-end gap-2.5 pt-3 border-t border-white/10">
              <button 
                type="button" 
                @click="isDetailModalOpen = false" 
                class="px-4 py-2 rounded-xl bg-white/5 text-[#C6D2D0] hover:bg-white/10 font-semibold cursor-pointer"
              >
                Tutup
              </button>
            </div>

          </div>
        </div>
      </Transition>

    </div>
  </MainAdminLayout>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(11, 32, 39, 0.5);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(76, 147, 168, 0.4);
  border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(76, 147, 168, 0.7);
}

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>