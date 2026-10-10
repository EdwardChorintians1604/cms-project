<script setup>
import { computed, onMounted, ref } from 'vue'
import QRCode from 'qrcode'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'
import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'

const { user } = useAuth()
const { isDark } = useTheme()

const members = ref([])
const churchCode = ref('')
const churchName = ref('')
const searchQuery = ref('')
const statusFilter = ref('Aktif')
const isLoading = ref(false)
const errorMessage = ref('')
const selectedMember = ref(null)
const selectedQrCode = ref('')
const isGeneratingQr = ref(false)
const qrError = ref('')
const copiedCode = ref(false)
const copiedLink = ref(false)
const copiedWaMsg = ref(false)
const whatsappPhone = ref('')

const authHeaders = () => {
  const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const filteredMembers = computed(() => {
  const query = searchQuery.value.trim().toLocaleLowerCase('id')

  return members.value.filter(member => {
    const matchesQuery = !query ||
      String(member.name || '').toLocaleLowerCase('id').includes(query) ||
      String(member.member_no || '').toLocaleLowerCase('id').includes(query) ||
      String(member.phone || '').toLocaleLowerCase('id').includes(query)
    const matchesStatus = statusFilter.value === 'Semua' || statusFilter.value === 'all' || member.attendance_status === statusFilter.value
    return matchesQuery && matchesStatus
  })
})

const memberStatuses = computed(() => [...new Set(
  members.value.map(member => member.attendance_status).filter(Boolean)
)])

const loadMembers = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const profile = user.value || storage.get(STORAGE_KEYS.USER_DATA) || {}
    churchCode.value = String(profile.church_code || '').trim()
    churchName.value = profile.church_name || profile.church?.church_name || 'Gereja Cabang'

    if (!churchCode.value || churchCode.value === 'DEFAULT') {
      throw new Error('Kode cabang gereja tidak ditemukan pada akun admin. Pastikan akun terhubung ke gereja yang benar.')
    }

    const allMembers = []
    const pageSize = 200
    let skip = 0

    while (true) {
      const params = new URLSearchParams({
        church_code: churchCode.value,
        skip: String(skip),
        limit: String(pageSize)
      })
      const response = await fetch(`${APP_CONFIG.apiBaseUrl}/church-members/?${params}`, {
        headers: authHeaders()
      })
      if (!response.ok) {
        throw new Error(`Gagal memuat data jemaat (HTTP ${response.status}).`)
      }

      const page = await response.json()
      if (!Array.isArray(page)) {
        throw new Error('Format data jemaat dari server tidak valid.')
      }

      allMembers.push(...page)
      if (page.length < pageSize) break
      skip += pageSize
    }

    members.value = allMembers
  } catch (error) {
    console.error('Gagal memuat daftar jemaat untuk QR:', error)
    members.value = []
    errorMessage.value = error.message || 'Terjadi kesalahan saat memuat data jemaat.'
  } finally {
    isLoading.value = false
  }
}

const getMemberCardUrl = (member) => {
  if (!member) return ''
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  return `${origin}/kartu-jemaat/${member.id}`
}

const createQrCode = async (member) => {
  selectedMember.value = member
  selectedQrCode.value = ''
  qrError.value = ''
  isGeneratingQr.value = true
  copiedCode.value = false
  copiedLink.value = false
  copiedWaMsg.value = false
  whatsappPhone.value = member.phone || ''

  try {
    const cardUrl = getMemberCardUrl(member)
    selectedQrCode.value = await QRCode.toDataURL(cardUrl, {
      errorCorrectionLevel: 'H',
      margin: 2,
      width: 480,
      color: {
        dark: '#0f172a',
        light: '#ffffff'
      }
    })
  } catch (error) {
    console.error('Gagal membuat QR jemaat:', error)
    qrError.value = 'QR tidak dapat dibuat. Silakan coba lagi.'
  } finally {
    isGeneratingQr.value = false
  }
}

const copyCardUrl = async () => {
  if (!selectedMember.value) return
  const cardUrl = getMemberCardUrl(selectedMember.value)
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(cardUrl)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = cardUrl
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    copiedLink.value = true
    setTimeout(() => {
      copiedLink.value = false
    }, 2000)
  } catch (e) {
    console.error('Gagal menyalin tautan:', e)
  }
}

const cleanPhoneNumber = (phone) => {
  if (!phone) return ''
  let cleaned = String(phone).replace(/[^0-9]/g, '')
  if (cleaned.startsWith('0')) {
    cleaned = '62' + cleaned.slice(1)
  } else if (cleaned.startsWith('8')) {
    cleaned = '62' + cleaned
  }
  return cleaned
}

const getWaMessage = (member) => {
  if (!member) return ''
  const cardUrl = getMemberCardUrl(member)
  const memberNo = member.member_no || `ID-${member.id}`
  const chName = churchName.value || 'GracePoint Church'

  return `Shalom Saudara/i *${member.name}*,\n\nSalam sejahtera dalam kasih Tuhan Yesus Kristus.\n\nBerikut adalah tautan resmi *Kartu Digital Jemaat GracePoint* Anda untuk cabang *${chName}*:\n🔗 ${cardUrl}\n\n📋 *Detail Data Keanggotaan:*\n• No. Anggota: *${memberNo}*\n• Status: *${member.attendance_status || 'Aktif'}*\n• Peran: *${member.family_role || 'Jemaat'}*\n\nSilakan buka tautan di atas untuk melihat data identitas keanggotaan Anda dan simpan kode QR yang tertera untuk kebutuhan pelayanan gereja.\n\nTuhan Yesus Memberkati! 🙏✨\n_— Pengurus GracePoint Church_`
}

const openWhatsApp = (member) => {
  const targetMember = member || selectedMember.value
  if (!targetMember) return

  const targetPhone = cleanPhoneNumber(whatsappPhone.value || targetMember.phone)
  const message = getWaMessage(targetMember)
  const encodedMsg = encodeURIComponent(message)
  const waUrl = targetPhone 
    ? `https://api.whatsapp.com/send?phone=${targetPhone}&text=${encodedMsg}`
    : `https://api.whatsapp.com/send?text=${encodedMsg}`
  window.open(waUrl, '_blank')
}

const copyWaMessage = async () => {
  if (!selectedMember.value) return
  const message = getWaMessage(selectedMember.value)
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(message)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = message
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    copiedWaMsg.value = true
    setTimeout(() => {
      copiedWaMsg.value = false
    }, 2000)
  } catch (err) {
    console.error('Gagal menyalin pesan WhatsApp:', err)
  }
}

const copyPayload = async () => {
  if (!selectedMember.value) return
  const memberIdentifier = selectedMember.value.member_no || `ID-${selectedMember.value.id}`
  const payload = `GPJ:1:${churchCode.value}:${memberIdentifier}`
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(payload)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = payload
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    copiedCode.value = true
    setTimeout(() => {
      copiedCode.value = false
    }, 2000)
  } catch (e) {
    console.error('Gagal menyalin:', e)
  }
}

const printQrCard = () => {
  if (!selectedQrCode.value || !selectedMember.value) return
  const printWindow = window.open('', '_blank')
  if (!printWindow) return

  const memberIdentifier = selectedMember.value.member_no || `ID-${selectedMember.value.id}`
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Kartu QR Presensi - ${selectedMember.value.name}</title>
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f8fafc;
            padding: 20px;
          }
          .card {
            width: 340px;
            padding: 28px 24px;
            background: #ffffff;
            border-radius: 20px;
            border: 2px solid #e2e8f0;
            box-shadow: 0 10px 25px rgba(0,0,0,0.06);
            text-align: center;
          }
          .badge {
            display: inline-block;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #d97706;
            background: #fef3c7;
            padding: 4px 10px;
            border-radius: 999px;
            margin-bottom: 8px;
          }
          .church {
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 16px;
          }
          .qr-box {
            background: #ffffff;
            padding: 12px;
            border-radius: 16px;
            border: 1px solid #cbd5e1;
            display: inline-block;
            margin-bottom: 16px;
          }
          .qr-img {
            width: 210px;
            height: 210px;
            display: block;
          }
          .name {
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 4px;
          }
          .code {
            font-size: 12px;
            color: #64748b;
            font-family: monospace;
            background: #f1f5f9;
            display: inline-block;
            padding: 3px 8px;
            border-radius: 6px;
            margin-bottom: 14px;
          }
          .footer {
            font-size: 10px;
            color: #94a3b8;
            border-top: 1px dashed #e2e8f0;
            padding-top: 12px;
          }
        </style>
      </head>
      <body>
        <div class="card">
          <div class="badge">Kartu Presensi Jemaat</div>
          <div class="church">GracePoint • ${churchName.value || 'Gereja Cabang'}</div>
          <div class="qr-box">
            <img class="qr-img" src="${selectedQrCode.value}" alt="QR Code" />
          </div>
          <div class="name">${selectedMember.value.name}</div>
          <div class="code">${memberIdentifier}</div>
          <div class="footer">Soli Deo Gloria • GracePoint Verification Standard</div>
        </div>
        <script>
          window.onload = function() {
            window.print();
            window.onafterprint = function() { window.close(); };
          };
        <\/script>
      </body>
    </html>
  `)
  printWindow.document.close()
}

const downloadQrCode = () => {
  if (!selectedQrCode.value || !selectedMember.value) return

  const identifier = selectedMember.value.member_no || `ID-${selectedMember.value.id}`
  const rawName = String(selectedMember.value.name || 'Jemaat').trim().replace(/[^a-zA-Z0-9_-]/g, '_')
  const safeIdentifier = String(identifier).replace(/[^a-zA-Z0-9_-]/g, '-')
  const link = document.createElement('a')
  link.href = selectedQrCode.value
  link.download = `QR_${rawName}_${safeIdentifier}.png`
  link.click()
}

onMounted(loadMembers)
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">
      <!-- Page Header -->
      <div 
        :class="[
          'flex flex-col gap-4 border-b pb-5 sm:flex-row sm:items-center sm:justify-between transition-colors',
          isDark ? 'border-amber-500/20' : 'border-amber-500/30'
        ]"
      >
        <div>
          <div class="mb-1 flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-full bg-sky-400"></span>
            <span class="text-xs font-bold uppercase tracking-widest text-sky-400">KARTU QR JEMAAT</span>
          </div>
          <h1 :class="['font-serif text-2xl font-bold tracking-wide sm:text-3xl transition-colors', isDark ? 'text-white' : 'text-slate-900']">
            Kode QR Anggota Jemaat
          </h1>
          <p :class="['mt-1 text-sm transition-colors', isDark ? 'text-slate-400' : 'text-slate-600']">
            Buat dan unduh kode QR identitas presensi untuk jemaat {{ churchName }}. Cepat, akurat, dan tanpa antrean.
          </p>
        </div>
        <button
          type="button"
          @click="loadMembers"
          :disabled="isLoading"
          :class="[
            'inline-flex items-center justify-center gap-2 rounded-xl border px-4 py-2.5 text-xs font-semibold transition disabled:cursor-wait disabled:opacity-60 shadow-sm',
            isDark 
              ? 'border-slate-700 bg-slate-900 text-slate-200 hover:border-amber-400/50 hover:text-amber-300' 
              : 'border-slate-200 bg-white text-slate-700 hover:border-amber-500 hover:text-amber-600'
          ]"
        >
          <i :class="['bi', isLoading ? 'bi-arrow-repeat animate-spin' : 'bi-arrow-clockwise']"></i>
          Muat Ulang Jemaat
        </button>
      </div>

      <!-- Stat Cards -->
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-3">
        <Card title="Total Jemaat" subtitle="Terdaftar di cabang ini">
          <div :class="['mt-1 text-3xl font-bold', isDark ? 'text-white' : 'text-slate-900']">
            {{ members.length }} <span :class="['text-xs font-normal', isDark ? 'text-slate-400' : 'text-slate-500']">Jemaat</span>
          </div>
        </Card>
        <Card title="QR Siap Digenerate" subtitle="Satu kode unik per jemaat">
          <div class="mt-1 text-3xl font-bold text-sky-400">
            {{ members.length }} <span :class="['text-xs font-normal', isDark ? 'text-slate-400' : 'text-slate-500']">Kode</span>
          </div>
        </Card>
        <Card title="Cabang Terhubung" :subtitle="churchCode || 'Kode cabang belum tersedia'">
          <div class="mt-1 truncate text-lg font-bold text-amber-400">{{ churchName }}</div>
        </Card>
      </div>

      <!-- Error State -->
      <div
        v-if="errorMessage"
        role="alert"
        class="flex flex-col gap-3 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200 sm:flex-row sm:items-center sm:justify-between"
      >
        <span>{{ errorMessage }}</span>
        <button type="button" @click="loadMembers" class="shrink-0 rounded-lg border border-rose-400/30 px-3 py-1.5 text-xs font-semibold hover:bg-rose-500/15">
          Coba Lagi
        </button>
      </div>

      <!-- Members Table Card -->
      <Card title="Daftar Jemaat" subtitle="Buat atau unduh QR identitas presensi secara perorangan">
        <div class="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-[minmax(0,1fr)_12rem]">
          <label class="relative block">
            <span class="sr-only">Cari nama atau nomor anggota</span>
            <i class="bi bi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Cari nama atau nomor anggota..."
              :class="[
                'w-full rounded-xl border py-2.5 pl-9 pr-3 text-sm outline-none transition focus:border-amber-400',
                isDark ? 'border-slate-700 bg-slate-950 text-white placeholder-slate-500' : 'border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400'
              ]"
            />
          </label>
          <label>
            <span class="sr-only">Filter status anggota</span>
            <select
              v-model="statusFilter"
              :class="[
                'w-full rounded-xl border px-3 py-2.5 text-sm outline-none transition focus:border-amber-400',
                isDark ? 'border-slate-700 bg-slate-950 text-white' : 'border-slate-200 bg-slate-50 text-slate-800'
              ]"
            >
              <option value="Aktif">Jemaat Aktif</option>
              <option value="all">Semua Status</option>
              <option v-for="status in memberStatuses" :key="status" :value="status">{{ status }}</option>
            </select>
          </label>
        </div>

        <div v-if="isLoading" class="py-12 text-center text-sm text-slate-400">
          <i class="bi bi-arrow-repeat mr-2 animate-spin"></i>Memuat daftar jemaat...
        </div>
        <div v-else-if="!errorMessage && members.length === 0" :class="['rounded-xl border border-dashed py-12 text-center', isDark ? 'border-slate-700' : 'border-slate-200']">
          <i class="bi bi-people mb-2 block text-3xl text-slate-400"></i>
          <p :class="['text-sm font-semibold', isDark ? 'text-slate-300' : 'text-slate-700']">Belum ada data jemaat untuk cabang ini.</p>
          <p class="mt-1 text-xs text-slate-400">Tambahkan data jemaat terlebih dahulu melalui menu Kelola Jemaat.</p>
        </div>
        <div v-else-if="filteredMembers.length === 0" class="py-10 text-center text-sm text-slate-400">
          Tidak ada jemaat yang cocok dengan pencarian atau filter.
        </div>
        <div v-else :class="['overflow-x-auto rounded-xl border', isDark ? 'border-slate-800' : 'border-slate-200']">
          <table class="w-full min-w-[680px] text-left text-sm">
            <thead :class="['border-b text-[11px] uppercase tracking-wider', isDark ? 'border-slate-800 bg-slate-950/80 text-amber-400' : 'border-slate-200 bg-amber-50/60 text-amber-700 font-bold']">
              <tr>
                <th scope="col" class="p-3">Nama Jemaat</th>
                <th scope="col" class="p-3">No. Anggota</th>
                <th scope="col" class="p-3">WhatsApp / HP</th>
                <th scope="col" class="p-3">Status</th>
                <th scope="col" class="p-3 text-right">Kode QR &amp; Bagikan</th>
              </tr>
            </thead>
            <tbody :class="[isDark ? 'divide-y divide-slate-800/80 bg-slate-900/30' : 'divide-y divide-slate-100 bg-white']">
              <tr 
                v-for="member in filteredMembers" 
                :key="member.id" 
                :class="['transition-colors', isDark ? 'hover:bg-slate-800/40 text-slate-300' : 'hover:bg-amber-50/30 text-slate-700']"
              >
                <td :class="['p-3 font-semibold', isDark ? 'text-white' : 'text-slate-900']">{{ member.name }}</td>
                <td class="p-3 font-mono text-xs text-slate-400">{{ member.member_no || `ID-${member.id}` }}</td>
                <td class="p-3 text-xs">
                  <div v-if="member.phone" class="flex items-center gap-1.5 font-mono text-emerald-500">
                    <i class="bi bi-whatsapp"></i>
                    <span>{{ member.phone }}</span>
                  </div>
                  <span v-else class="text-slate-500 italic text-[11px]">Belum tercatat</span>
                </td>
                <td class="p-3">
                  <span :class="member.attendance_status === 'Aktif' ? 'text-emerald-500 font-medium' : 'text-slate-400'">
                    {{ member.attendance_status || 'Status tidak dicatat' }}
                  </span>
                </td>
                <td class="p-3 text-right">
                  <div class="inline-flex items-center gap-1.5">
                    <button
                      type="button"
                      @click="createQrCode(member)"
                      class="inline-flex items-center gap-1.5 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-semibold text-amber-400 transition hover:bg-amber-500/20 active:scale-95 shadow-sm"
                      title="Lihat QR & Bagikan ke WhatsApp"
                    >
                      <i class="bi bi-qr-code"></i>
                      <span>QR &amp; Share</span>
                    </button>
                    <button
                      type="button"
                      @click="createQrCode(member); openWhatsApp(member)"
                      class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1.5 text-xs font-semibold text-emerald-400 transition hover:bg-emerald-500/20 active:scale-95 shadow-sm"
                      title="Kirim Kartu via WhatsApp"
                    >
                      <i class="bi bi-whatsapp"></i>
                      <span class="hidden sm:inline">Kirim WA</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div :class="['border-t px-3 py-2 text-[11px]', isDark ? 'border-slate-800 text-slate-500' : 'border-slate-100 text-slate-400']">
            Menampilkan {{ filteredMembers.length }} dari {{ members.length }} jemaat
          </div>
        </div>
      </Card>

      <!-- ═════════════════════════════════════════════════════════════════════
           RESPONSIVE & ELEGANT QR PASS POP-UP MODAL DENGAN SHARE WHATSAPP
           ═════════════════════════════════════════════════════════════════════ -->
      <Transition name="qr-modal">
        <div
          v-if="selectedMember"
          class="fixed inset-0 z-[70] flex items-center justify-center p-3 sm:p-4 md:p-6 bg-black/80 backdrop-blur-md overflow-y-auto"
          @click.self="selectedMember = null"
          @keydown.esc="selectedMember = null"
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="member-qr-title"
            :class="[
              'relative w-full max-w-sm sm:max-w-lg my-auto rounded-3xl border shadow-2xl transition-all duration-300 overflow-hidden flex flex-col max-h-[92vh]',
              isDark 
                ? 'bg-slate-900/98 border-amber-500/30 text-white shadow-[0_25px_60px_rgba(0,0,0,0.8)]' 
                : 'bg-white/98 border-amber-500/25 text-slate-800 shadow-[0_25px_60px_rgba(0,0,0,0.15)]'
            ]"
          >
            <!-- Decorative Top Border Gradient Accent -->
            <div class="h-1.5 w-full bg-gradient-to-r from-amber-500 via-amber-300 to-amber-600"></div>

            <!-- Modal Header -->
            <div 
              :class="[
                'px-5 py-4 border-b flex items-center justify-between gap-3 shrink-0',
                isDark ? 'border-slate-800 bg-slate-950/60' : 'border-slate-100 bg-amber-50/40'
              ]"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-500 to-amber-300 text-slate-950 flex items-center justify-center font-bold text-lg shadow-md shrink-0">
                  <i class="bi bi-qr-code-scan"></i>
                </div>
                <div class="min-w-0">
                  <div class="flex items-center gap-1.5 mb-0.5">
                    <span class="inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-500 border border-amber-500/20">
                      Digital Member Pass &amp; Share
                    </span>
                  </div>
                  <h2 id="member-qr-title" :class="['text-base font-bold truncate leading-tight', isDark ? 'text-white' : 'text-slate-900']">
                    Kartu Digital Jemaat
                  </h2>
                </div>
              </div>
              <button
                type="button"
                @click="selectedMember = null"
                aria-label="Tutup"
                :class="[
                  'p-2 rounded-xl transition shrink-0',
                  isDark ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-400 hover:text-slate-800 hover:bg-slate-100'
                ]"
              >
                <i class="bi bi-x-lg text-sm"></i>
              </button>
            </div>

            <!-- Scrollable Modal Content -->
            <div class="p-4 sm:p-6 overflow-y-auto space-y-4 flex-1">
              <!-- Member Profile Preview Card -->
              <div 
                :class="[
                  'p-3.5 rounded-2xl border flex items-center gap-3.5 transition',
                  isDark ? 'bg-slate-950/50 border-slate-800' : 'bg-slate-50 border-slate-200'
                ]"
              >
                <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500 to-indigo-600 text-white font-bold flex items-center justify-center text-base shadow shrink-0">
                  {{ (selectedMember.name || 'J').charAt(0).toUpperCase() }}
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2 flex-wrap">
                    <h3 :class="['font-bold text-sm sm:text-base truncate', isDark ? 'text-white' : 'text-slate-900']">
                      {{ selectedMember.name }}
                    </h3>
                    <span 
                      v-if="selectedMember.attendance_status" 
                      class="text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                    >
                      {{ selectedMember.attendance_status }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2 text-xs font-mono mt-0.5" :class="isDark ? 'text-slate-400' : 'text-slate-500'">
                    <span>{{ selectedMember.member_no || `ID-${selectedMember.id}` }}</span>
                    <span>•</span>
                    <span class="truncate">{{ churchName }}</span>
                  </div>
                </div>
              </div>

              <!-- QR Display Area (Encodes digital card URL) -->
              <div 
                :class="[
                  'relative p-4 sm:p-5 rounded-2xl border text-center flex flex-col items-center justify-center transition-all',
                  isDark ? 'bg-slate-950/80 border-slate-800' : 'bg-gradient-to-b from-slate-50 to-slate-100/70 border-slate-200'
                ]"
              >
                <!-- Frame with scanner corner brackets -->
                <div class="relative p-3 bg-white rounded-2xl shadow-md border border-slate-200/80 max-w-full">
                  <span class="absolute -top-1.5 -left-1.5 w-4 h-4 border-t-2 border-l-2 border-amber-500 rounded-tl-sm pointer-events-none"></span>
                  <span class="absolute -top-1.5 -right-1.5 w-4 h-4 border-t-2 border-r-2 border-amber-500 rounded-tr-sm pointer-events-none"></span>
                  <span class="absolute -bottom-1.5 -left-1.5 w-4 h-4 border-b-2 border-l-2 border-amber-500 rounded-bl-sm pointer-events-none"></span>
                  <span class="absolute -bottom-1.5 -right-1.5 w-4 h-4 border-b-2 border-r-2 border-amber-500 rounded-br-sm pointer-events-none"></span>

                  <div class="w-44 h-44 sm:w-52 sm:h-52 max-w-full flex items-center justify-center">
                    <div v-if="isGeneratingQr" class="flex flex-col items-center gap-2 py-8">
                      <i class="bi bi-arrow-repeat animate-spin text-2xl text-amber-500"></i>
                      <span class="text-xs font-medium text-slate-500">Membuat kode QR...</span>
                    </div>
                    <img 
                      v-else-if="selectedQrCode" 
                      :src="selectedQrCode" 
                      :alt="`Kode QR ${selectedMember.name}`" 
                      class="w-full h-full object-contain rounded-lg" 
                    />
                    <div v-else-if="qrError" class="py-6 px-4 text-center">
                      <i class="bi bi-exclamation-triangle text-2xl text-rose-500 mb-1"></i>
                      <p class="text-xs font-semibold text-rose-600">{{ qrError }}</p>
                    </div>
                  </div>
                </div>

                <!-- Digital Card Link Preview & Actions -->
                <div 
                  :class="[
                    'mt-4 w-full flex flex-col sm:flex-row items-center justify-between gap-2 p-2.5 rounded-xl text-xs border transition-colors',
                    isDark ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'
                  ]"
                >
                  <div class="truncate text-[11px] font-mono w-full sm:w-auto text-left" :class="isDark ? 'text-slate-300' : 'text-slate-600'">
                    <span class="text-amber-500 font-bold mr-1">LINK:</span>
                    <span>/kartu-jemaat/{{ selectedMember.id }}</span>
                  </div>
                  <div class="flex items-center gap-1.5 w-full sm:w-auto justify-end">
                    <router-link
                      :to="`/kartu-jemaat/${selectedMember.id}`"
                      target="_blank"
                      :class="[
                        'px-2.5 py-1 rounded-md text-[11px] font-semibold transition flex items-center gap-1 shadow-sm',
                        isDark ? 'bg-slate-800 hover:bg-slate-700 text-slate-200' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      ]"
                    >
                      <i class="bi bi-box-arrow-up-right"></i>
                      <span>Buka Kartu</span>
                    </router-link>
                    <button
                      type="button"
                      @click="copyCardUrl"
                      :class="[
                        'px-2.5 py-1 rounded-md text-[11px] font-semibold transition flex items-center gap-1 shadow-sm',
                        copiedLink 
                          ? 'bg-emerald-500 text-white' 
                          : (isDark ? 'bg-slate-800 hover:bg-slate-700 text-slate-200' : 'bg-slate-100 hover:bg-slate-200 text-slate-700')
                      ]"
                    >
                      <i :class="copiedLink ? 'bi bi-check-lg' : 'bi bi-link-45deg'"></i>
                      <span>{{ copiedLink ? 'Tersalin' : 'Salin' }}</span>
                    </button>
                  </div>
                </div>

                <p :class="['mt-2 text-[11px] leading-relaxed', isDark ? 'text-slate-400' : 'text-slate-500']">
                  <i class="bi bi-camera-fill text-amber-500 mr-1"></i>
                  Saat QR ini di-scan oleh kamera HP jemaat, halaman data identitas kartu jemaat akan terbuka secara otomatis.
                </p>
              </div>

              <!-- ═════════════════════════════════════════════════════════════
                   BAGIKAN KE JEMAAT VIA WHATSAPP (BARU)
                   ═════════════════════════════════════════════════════════════ -->
              <div 
                :class="[
                  'p-4 rounded-2xl border transition-all',
                  isDark ? 'bg-emerald-950/30 border-emerald-500/30' : 'bg-emerald-50/70 border-emerald-300/60'
                ]"
              >
                <div class="flex items-center justify-between gap-2 mb-3">
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-emerald-500 text-white flex items-center justify-center text-lg shadow-sm">
                      <i class="bi bi-whatsapp"></i>
                    </div>
                    <div>
                      <h4 :class="['text-xs font-bold leading-tight', isDark ? 'text-emerald-300' : 'text-emerald-900']">
                        Bagikan Kartu via WhatsApp
                      </h4>
                      <p class="text-[11px] text-slate-400">Kirim tautan dan data kartu langsung ke kontak jemaat</p>
                    </div>
                  </div>
                  <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    Instan
                  </span>
                </div>

                <!-- Input No HP / WhatsApp -->
                <div class="space-y-2">
                  <label class="block">
                    <span class="text-[11px] font-semibold text-slate-400 block mb-1">Nomor WhatsApp Jemaat:</span>
                    <div class="relative">
                      <i class="bi bi-telephone-fill absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                      <input
                        v-model="whatsappPhone"
                        type="tel"
                        placeholder="Contoh: 08123456789 atau 628123456789"
                        :class="[
                          'w-full rounded-xl border py-2 pl-8 pr-3 text-xs outline-none transition focus:border-emerald-500',
                          isDark ? 'border-slate-700 bg-slate-900 text-white placeholder-slate-500' : 'border-slate-300 bg-white text-slate-800 placeholder-slate-400'
                        ]"
                      />
                    </div>
                  </label>

                  <!-- WhatsApp Action Buttons -->
                  <div class="flex items-center gap-2 pt-1">
                    <button
                      type="button"
                      @click="openWhatsApp(selectedMember)"
                      class="flex-1 inline-flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#25D366] hover:bg-[#20ba5a] text-white font-bold text-xs shadow-md transition active:scale-95"
                    >
                      <i class="bi bi-whatsapp text-sm"></i>
                      <span>Kirim ke WhatsApp</span>
                    </button>

                    <button
                      type="button"
                      @click="copyWaMessage"
                      :class="[
                        'inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl border font-semibold text-xs transition active:scale-95 shadow-sm',
                        copiedWaMsg 
                          ? 'bg-emerald-500 text-white border-emerald-500' 
                          : (isDark ? 'border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-100')
                      ]"
                    >
                      <i :class="copiedWaMsg ? 'bi bi-check-lg' : 'bi bi-clipboard'"></i>
                      <span>{{ copiedWaMsg ? 'Pesan Disalin' : 'Salin Pesan' }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Modal Footer Action Buttons -->
            <div 
              :class="[
                'px-5 py-3.5 border-t flex flex-wrap items-center justify-between gap-2 shrink-0',
                isDark ? 'border-slate-800 bg-slate-950/60' : 'border-slate-100 bg-slate-50'
              ]"
            >
              <button
                type="button"
                @click="selectedMember = null"
                :class="[
                  'px-4 py-2 rounded-xl text-xs font-semibold transition',
                  isDark ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
                ]"
              >
                Tutup
              </button>

              <div class="flex items-center gap-2">
                <button
                  type="button"
                  @click="printQrCard"
                  :disabled="!selectedQrCode"
                  :class="[
                    'inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border transition disabled:opacity-50 disabled:cursor-not-allowed shadow-sm',
                    isDark 
                      ? 'border-slate-700 bg-slate-800/80 text-slate-200 hover:bg-slate-700 hover:text-white' 
                      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-100'
                  ]"
                  title="Cetak Kartu QR"
                >
                  <i class="bi bi-printer"></i>
                  <span>Cetak</span>
                </button>

                <button
                  v-if="selectedQrCode"
                  type="button"
                  @click="downloadQrCode"
                  class="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 px-4 py-2 text-xs font-bold text-slate-950 shadow-md transition hover:from-amber-400 hover:to-amber-300 hover:shadow-amber-500/20 active:scale-95"
                >
                  <i class="bi bi-download"></i>
                  <span>Unduh PNG</span>
                </button>
              </div>
            </div>
          </section>
        </div>
      </Transition>
    </div>
  </ChurchAdminLayout>
</template>

<style scoped>
/* Modal Transition */
.qr-modal-enter-active,
.qr-modal-leave-active {
  transition: all 0.25s ease-out;
}

.qr-modal-enter-from,
.qr-modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
