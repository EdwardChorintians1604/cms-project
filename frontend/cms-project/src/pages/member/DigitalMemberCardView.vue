<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import QRCode from 'qrcode'
import { APP_CONFIG } from '@/config'
import { useTheme } from '@/composables/useTheme'

const route = useRoute()
const router = useRouter()
const { isDark } = useTheme()

const member = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const qrDataUrl = ref('')
const isCopied = ref(false)

const memberId = computed(() => route.params.id)

const cardUrl = computed(() => {
  if (typeof window === 'undefined') return ''
  return `${window.location.origin}/kartu-jemaat/${memberId.value}`
})

const fetchMemberData = async () => {
  if (!memberId.value) {
    errorMessage.value = 'ID jemaat tidak valid.'
    isLoading.value = false
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/church-members/${memberId.value}`)
    if (!res.ok) {
      if (res.status === 404) {
        throw new Error('Data kartu jemaat tidak ditemukan atau sudah tidak aktif.')
      }
      throw new Error(`Gagal memuat data jemaat (HTTP ${res.status}).`)
    }

    const data = await res.json()
    member.value = data

    // Generate QR Code containing this digital card URL
    qrDataUrl.value = await QRCode.toDataURL(cardUrl.value, {
      errorCorrectionLevel: 'H',
      margin: 2,
      width: 400,
      color: {
        dark: '#0f172a',
        light: '#ffffff'
      }
    })
  } catch (err) {
    console.error('Error fetching member card:', err)
    errorMessage.value = err.message || 'Terjadi kesalahan saat memuat kartu jemaat.'
  } finally {
    isLoading.value = false
  }
}

const copyCardLink = async () => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(cardUrl.value)
    } else {
      const ta = document.createElement('textarea')
      ta.value = cardUrl.value
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    isCopied.value = true
    setTimeout(() => {
      isCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('Gagal menyalin tautan:', err)
  }
}

const downloadCard = () => {
  if (!qrDataUrl.value || !member.value) return
  const link = document.createElement('a')
  link.href = qrDataUrl.value
  const cleanName = String(member.value.name || 'Jemaat').replace(/[^a-zA-Z0-9_-]/g, '_')
  link.download = `QR_Kartu_${cleanName}_${member.value.member_no || member.value.id}.png`
  link.click()
}

const printCard = () => {
  window.print()
}

onMounted(() => {
  fetchMemberData()
})
</script>

<template>
  <div 
    :class="[
      'min-h-screen py-8 px-4 sm:px-6 flex flex-col justify-between transition-colors duration-300 font-sans',
      isDark ? 'bg-[#050811] text-slate-100' : 'bg-slate-100 text-slate-800'
    ]"
  >
    <!-- Top Bar Navigation -->
    <header class="max-w-xl mx-auto w-full flex items-center justify-between mb-6">
      <router-link 
        to="/" 
        class="inline-flex items-center gap-2 text-xs font-semibold text-amber-500 hover:text-amber-400 transition"
      >
        <i class="bi bi-arrow-left text-sm"></i>
        <span>Beranda GracePoint</span>
      </router-link>
      <div class="flex items-center gap-2">
        <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          KTA Digital
        </span>
      </div>
    </header>

    <!-- Main Content Container -->
    <main class="max-w-md mx-auto w-full my-auto">
      <!-- Loading State -->
      <div 
        v-if="isLoading" 
        :class="[
          'rounded-3xl p-10 text-center shadow-xl border',
          isDark ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200'
        ]"
      >
        <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center text-3xl">
          <i class="bi bi-arrow-repeat animate-spin"></i>
        </div>
        <h2 class="text-lg font-bold mb-1">Memuat Kartu Jemaat...</h2>
        <p class="text-xs text-slate-400">Menghubungkan ke basis data identitas gereja...</p>
      </div>

      <!-- Error State -->
      <div 
        v-else-if="errorMessage" 
        :class="[
          'rounded-3xl p-8 text-center shadow-xl border',
          isDark ? 'bg-slate-900/80 border-rose-500/30' : 'bg-white border-rose-200'
        ]"
      >
        <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-rose-500/10 text-rose-500 flex items-center justify-center text-3xl">
          <i class="bi bi-exclamation-triangle"></i>
        </div>
        <h2 class="text-lg font-bold text-rose-500 mb-2">Kartu Tidak Ditemukan</h2>
        <p class="text-sm text-slate-400 mb-6">{{ errorMessage }}</p>
        <router-link 
          to="/" 
          class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs hover:bg-amber-400 transition"
        >
          <i class="bi bi-house"></i>
          Kembali ke Beranda
        </router-link>
      </div>

      <!-- Member Digital Card -->
      <div 
        v-else-if="member"
        class="space-y-4"
      >
        <!-- The ID Card (Printable & Saveable) -->
        <div 
          id="digital-card"
          :class="[
            'relative rounded-3xl overflow-hidden shadow-2xl border transition-all duration-300',
            isDark 
              ? 'bg-gradient-to-b from-slate-900 via-slate-900/95 to-slate-950 border-amber-500/30 text-white shadow-black/60' 
              : 'bg-gradient-to-b from-white via-white to-amber-50/30 border-amber-500/25 text-slate-800 shadow-slate-300/60'
          ]"
        >
          <!-- Top Banner Ribbon -->
          <div class="h-2 w-full bg-gradient-to-r from-amber-500 via-amber-300 to-amber-600"></div>

          <!-- Card Header: Church Brand -->
          <div 
            :class="[
              'p-5 sm:p-6 border-b flex items-center justify-between gap-3',
              isDark ? 'border-slate-800/80 bg-slate-950/40' : 'border-slate-100 bg-amber-50/30'
            ]"
          >
            <div class="flex items-center gap-3">
              <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-amber-500 to-amber-300 text-slate-950 flex items-center justify-center font-bold text-xl shadow-md shrink-0">
                <i class="bi bi-cross"></i>
              </div>
              <div class="min-w-0">
                <span class="text-[10px] uppercase font-bold tracking-widest text-amber-500 block">
                  GRACEPOINT CHURCH
                </span>
                <h1 :class="['text-base font-bold truncate leading-tight', isDark ? 'text-white' : 'text-slate-900']">
                  {{ member.church_name || 'Gereja Cabang GracePoint' }}
                </h1>
                <span class="text-[11px] font-mono text-slate-400">
                  Cabang: {{ member.church_code || '-' }}
                </span>
              </div>
            </div>

            <!-- Attendance Status Badge -->
            <span 
              :class="[
                'px-2.5 py-1 rounded-full text-[11px] font-bold border shrink-0',
                member.attendance_status === 'Aktif'
                  ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                  : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
              ]"
            >
              <i class="bi bi-patch-check-fill mr-1"></i>
              {{ member.attendance_status || 'Aktif' }}
            </span>
          </div>

          <!-- Member Profile Banner -->
          <div class="p-5 sm:p-6 space-y-6">
            <div class="flex items-center gap-4">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 text-white font-black text-2xl flex items-center justify-center shadow-lg shrink-0">
                {{ (member.name || 'J').charAt(0).toUpperCase() }}
              </div>
              <div class="min-w-0 flex-1">
                <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-amber-500/15 text-amber-500 font-bold">
                  {{ member.member_no || `ID-${member.id}` }}
                </span>
                <h2 :class="['text-xl font-bold truncate mt-1', isDark ? 'text-white' : 'text-slate-900']">
                  {{ member.name }}
                </h2>
                <p class="text-xs text-slate-400 font-medium">
                  {{ member.family_role || 'Jemaat' }} • {{ member.gender === 'P' ? 'Perempuan' : 'Laki-laki' }}
                </p>
              </div>
            </div>

            <!-- QR Code Box -->
            <div 
              :class="[
                'p-5 rounded-2xl border text-center flex flex-col items-center justify-center transition-all',
                isDark ? 'bg-slate-950/70 border-slate-800' : 'bg-slate-50 border-slate-200'
              ]"
            >
              <div class="relative p-3 bg-white rounded-2xl shadow-md border border-slate-200/80 max-w-full">
                <!-- Corner Scanner Markers -->
                <span class="absolute -top-1.5 -left-1.5 w-4 h-4 border-t-2 border-l-2 border-amber-500 rounded-tl-sm pointer-events-none"></span>
                <span class="absolute -top-1.5 -right-1.5 w-4 h-4 border-t-2 border-r-2 border-amber-500 rounded-tr-sm pointer-events-none"></span>
                <span class="absolute -bottom-1.5 -left-1.5 w-4 h-4 border-b-2 border-l-2 border-amber-500 rounded-bl-sm pointer-events-none"></span>
                <span class="absolute -bottom-1.5 -right-1.5 w-4 h-4 border-b-2 border-r-2 border-amber-500 rounded-br-sm pointer-events-none"></span>

                <div class="w-48 h-48 sm:w-56 sm:h-56 max-w-full flex items-center justify-center">
                  <img 
                    v-if="qrDataUrl" 
                    :src="qrDataUrl" 
                    :alt="`QR Code ${member.name}`" 
                    class="w-full h-full object-contain rounded-lg"
                  />
                  <div v-else class="text-xs text-slate-400">Menyiapkan QR...</div>
                </div>
              </div>

              <div class="mt-3.5 flex items-center gap-1.5 text-xs text-slate-400">
                <i class="bi bi-qr-code-scan text-amber-500"></i>
                <span class="font-medium">Scan untuk memvalidasi identitas jemaat</span>
              </div>
            </div>

            <!-- Member Details Grid -->
            <div 
              :class="[
                'rounded-2xl border p-4 grid grid-cols-2 gap-3 text-xs',
                isDark ? 'bg-slate-950/40 border-slate-800/80' : 'bg-white border-slate-200/80'
              ]"
            >
              <div>
                <span class="text-slate-400 block text-[10px] uppercase font-semibold">Status Baptis</span>
                <span class="font-semibold text-emerald-500 mt-0.5 block">
                  {{ member.status_baptis || 'Sudah Baptis & Sidi' }}
                </span>
              </div>

              <div>
                <span class="text-slate-400 block text-[10px] uppercase font-semibold">Tanggal Lahir</span>
                <span :class="['font-semibold mt-0.5 block', isDark ? 'text-slate-200' : 'text-slate-700']">
                  {{ member.birthdate ? new Date(member.birthdate).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' }) : '-' }}
                </span>
              </div>

              <div>
                <span class="text-slate-400 block text-[10px] uppercase font-semibold">No. WhatsApp / HP</span>
                <span :class="['font-mono font-semibold mt-0.5 block', isDark ? 'text-slate-200' : 'text-slate-700']">
                  {{ member.phone || '-' }}
                </span>
              </div>

              <div>
                <span class="text-slate-400 block text-[10px] uppercase font-semibold">Email</span>
                <span :class="['font-semibold mt-0.5 block truncate', isDark ? 'text-slate-200' : 'text-slate-700']" :title="member.email">
                  {{ member.email || '-' }}
                </span>
              </div>

              <div v-if="member.address" class="col-span-2 pt-2 border-t" :class="isDark ? 'border-slate-800' : 'border-slate-100'">
                <span class="text-slate-400 block text-[10px] uppercase font-semibold">Alamat Domisili</span>
                <span :class="['mt-0.5 block leading-relaxed', isDark ? 'text-slate-300' : 'text-slate-600']">
                  {{ member.address }}
                </span>
              </div>
            </div>

            <!-- Presensi Notice -->
            <div 
              :class="[
                'p-3 rounded-xl border flex items-center gap-2.5 text-xs',
                isDark ? 'bg-amber-500/10 border-amber-500/20 text-amber-200' : 'bg-amber-50 border-amber-200 text-amber-800'
              ]"
            >
              <i class="bi bi-info-circle-fill text-amber-500 text-sm shrink-0"></i>
              <div class="leading-tight">
                <span class="font-bold">Presensi Ibadah:</span> Kode QR ini terdaftar resmi pada sistem gereja dan dapat ditunjukkan kepada petugas saat hadir.
              </div>
            </div>
          </div>

          <!-- Card Footer -->
          <div 
            :class="[
              'p-4 border-t text-center text-[10px] tracking-wider uppercase',
              isDark ? 'border-slate-800 bg-slate-950/60 text-slate-500' : 'border-slate-100 bg-slate-50 text-slate-400'
            ]"
          >
            <span>✝ SOLI DEO GLORIA • KARTU IDENTITAS DIGITAL RESMI GRACEPOINT</span>
          </div>
        </div>

        <!-- Action Buttons (Mobile Friendly) -->
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-2">
          <button
            type="button"
            @click="downloadCard"
            class="flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-bold text-xs shadow-md hover:from-amber-400 hover:to-amber-300 transition active:scale-95"
          >
            <i class="bi bi-download"></i>
            <span>Simpan QR</span>
          </button>

          <button
            type="button"
            @click="copyCardLink"
            :class="[
              'flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl border font-semibold text-xs transition active:scale-95 shadow-sm',
              isCopied 
                ? 'bg-emerald-500 text-white border-emerald-500' 
                : (isDark ? 'bg-slate-900 border-slate-700 text-slate-200 hover:bg-slate-800' : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50')
            ]"
          >
            <i :class="isCopied ? 'bi bi-check-lg' : 'bi bi-link-45deg'"></i>
            <span>{{ isCopied ? 'Tersalin!' : 'Salin Tautan' }}</span>
          </button>

          <button
            type="button"
            @click="printCard"
            :class="[
              'col-span-2 sm:col-span-1 flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl border font-semibold text-xs transition active:scale-95 shadow-sm',
              isDark ? 'bg-slate-900 border-slate-700 text-slate-200 hover:bg-slate-800' : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
            ]"
          >
            <i class="bi bi-printer"></i>
            <span>Cetak Kartu</span>
          </button>
        </div>
      </div>
    </main>

    <!-- Footer Note -->
    <footer class="max-w-md mx-auto w-full text-center py-4 text-xs text-slate-500">
      &copy; {{ new Date().getFullYear() }} GracePoint Church. Platform Pelayanan Gereja.
    </footer>
  </div>
</template>

<style scoped>
@media print {
  body {
    background: white !important;
    color: black !important;
  }
  header, footer, button, .grid button {
    display: none !important;
  }
  #digital-card {
    border: 1px solid #cbd5e1 !important;
    box-shadow: none !important;
    max-width: 380px !important;
    margin: 0 auto !important;
  }
}
</style>
