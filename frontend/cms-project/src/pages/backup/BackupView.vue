<script setup>
import { computed, onMounted, ref } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'

const backups = ref([])
const isLoading = ref(true)
const isCreating = ref(false)
const isDownloading = ref(false)
const downloadKey = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const backupOptions = ref([])
const downloadScope = ref('all')
const selectedTables = ref([])

const completedBackups = computed(() => backups.value.filter((backup) => backup.status === 'Completed').length)
const latestBackup = computed(() => backups.value[0]?.created_at || 'Belum ada snapshot')
const canDownloadSelected = computed(() => selectedTables.value.length > 0)

const loadBackups = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/superadmin-summary`)
    if (!response.ok) throw new Error('Daftar backup tidak dapat dimuat dari server.')

    const data = await response.json()
    backups.value = data.backups || []
  } catch (error) {
    errorMessage.value = error.message || 'Terjadi kesalahan saat memuat daftar backup.'
  } finally {
    isLoading.value = false
  }
}

const triggerBackup = async () => {
  isCreating.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/trigger-backup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ note: 'Manual Trigger by Superadmin' })
    })
    if (!response.ok) throw new Error('Backup baru gagal dibuat.')

    const data = await response.json()
    if (data.backup) backups.value.unshift(data.backup)
    successMessage.value = 'Snapshot database berhasil dibuat dan tercatat di registry.'
  } catch (error) {
    errorMessage.value = error.message || 'Terjadi kesalahan saat membuat backup.'
  } finally {
    isCreating.value = false
  }
}

const loadBackupOptions = async () => {
  try {
    const response = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/backup-options`)
    if (!response.ok) throw new Error('Pilihan bagian backup tidak dapat dimuat.')
    const data = await response.json()
    backupOptions.value = data.options || []
  } catch (error) {
    errorMessage.value = error.message || 'Pilihan bagian backup tidak dapat dimuat.'
  }
}

const downloadBackup = async ({ scope = downloadScope.value, tables = selectedTables.value, backupId = null, key = scope } = {}) => {
  if (scope === 'selected' && tables.length === 0) {
    errorMessage.value = 'Pilih minimal satu bagian database untuk diunduh.'
    return
  }

  isDownloading.value = true
  downloadKey.value = key
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await fetch(`${APP_CONFIG.apiBaseUrl}/dashboard/download-backup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scope, tables, backup_id: backupId })
    })
    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.detail || 'File backup gagal diunduh.')
    }

    const blob = await response.blob()
    const disposition = response.headers.get('Content-Disposition') || ''
    const filenameMatch = disposition.match(/filename="?([^";]+)"?/i)
    const filename = filenameMatch?.[1] || `cms_database_backup_${scope}.sql`
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    successMessage.value = `Backup ${scope === 'all' ? 'seluruh database' : 'bagian terpilih'} berhasil diunduh.`
  } catch (error) {
    errorMessage.value = error.message || 'Terjadi kesalahan saat mengunduh backup.'
  } finally {
    isDownloading.value = false
    downloadKey.value = ''
  }
}

onMounted(() => {
  loadBackups()
  loadBackupOptions()
})
</script>

<template>
  <MainAdminLayout>
    <div class="relative space-y-6 text-[#EDE6D6]">
      <div class="pointer-events-none fixed inset-0 -z-10 bg-[#0B2027]"></div>
      <div class="pointer-events-none fixed -top-40 -right-40 w-[34rem] h-[34rem] rounded-full bg-cyan-500/5 blur-3xl -z-10"></div>

      <section class="relative overflow-hidden rounded-3xl border border-cyan-500/25 bg-[#123138]/80 p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
        <div class="absolute inset-0 opacity-[0.06] pointer-events-none" style="background-image:radial-gradient(#EDE6D6 1px, transparent 1px); background-size:22px 22px;"></div>
        <div class="relative flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p class="mb-2 text-[10px] font-semibold uppercase tracking-[0.25em] text-cyan-300/80">Infrastruktur & Database</p>
            <h1 class="font-serif text-3xl font-bold text-[#F5EFE0] sm:text-4xl">Backup & Restore</h1>
            <p class="mt-2 max-w-2xl text-sm leading-relaxed text-[#B8C4C2]">Pantau snapshot database PostgreSQL dan buat cadangan manual untuk kebutuhan pemulihan sistem.</p>
          </div>
          <button
            type="button"
            :disabled="isCreating"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-3 text-xs font-bold text-[#0B2027] shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
            @click="triggerBackup"
          >
            <svg :class="['h-4 w-4', { 'animate-spin': isCreating }]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            {{ isCreating ? 'Membuat Backup...' : 'Buat Backup Sekarang' }}
          </button>
        </div>
      </section>

      <div v-if="errorMessage" class="rounded-xl border border-rose-500/30 bg-rose-950/40 px-4 py-3 text-sm text-rose-200">{{ errorMessage }}</div>
      <div v-if="successMessage" class="rounded-xl border border-emerald-500/30 bg-emerald-950/40 px-4 py-3 text-sm text-emerald-200">{{ successMessage }}</div>

      <section class="grid gap-4 sm:grid-cols-3">
        <div class="rounded-2xl border border-white/10 bg-[#123138]/70 p-5">
          <p class="text-[10px] uppercase tracking-[0.18em] text-slate-400">Total Snapshot</p>
          <p class="mt-2 text-3xl font-bold text-amber-300">{{ backups.length }}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-[#123138]/70 p-5">
          <p class="text-[10px] uppercase tracking-[0.18em] text-slate-400">Backup Berhasil</p>
          <p class="mt-2 text-3xl font-bold text-teal-300">{{ completedBackups }}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-[#123138]/70 p-5">
          <p class="text-[10px] uppercase tracking-[0.18em] text-slate-400">Snapshot Terakhir</p>
          <p class="mt-2 truncate text-sm font-semibold text-[#F5EFE0]" :title="latestBackup">{{ latestBackup }}</p>
        </div>
      </section>

      <section class="rounded-2xl border border-cyan-500/20 bg-[#123138]/70 p-5 shadow-xl backdrop-blur-md">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p class="text-[10px] uppercase tracking-[0.18em] text-cyan-300/80">Ekspor Data</p>
            <h2 class="mt-1 font-serif text-xl font-bold text-[#F5EFE0]">Pilih isi backup yang diunduh</h2>
            <p class="mt-1 text-xs text-[#8AA0A4]">Semua database membuat dump lengkap. Mode sebagian hanya menyertakan tabel yang dipilih.</p>
          </div>
          <button
            type="button"
            :disabled="isDownloading || downloadScope === 'selected' && !canDownloadSelected"
            class="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-3 text-xs font-bold text-[#0B2027] transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
            @click="downloadBackup()"
          >
            <svg :class="['h-4 w-4', { 'animate-spin': isDownloading && downloadKey === downloadScope }]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v12m0 0l4-4m-4 4l-4-4M5 21h14" /></svg>
            {{ isDownloading && downloadKey === downloadScope ? 'Menyiapkan File...' : 'Unduh Pilihan' }}
          </button>
        </div>

        <div class="mt-5 flex flex-wrap gap-2 border-b border-white/10 pb-4">
          <button type="button" class="rounded-lg px-3 py-2 text-xs font-semibold transition" :class="downloadScope === 'all' ? 'bg-cyan-400 text-[#0B2027]' : 'bg-white/5 text-slate-300 hover:bg-white/10'" @click="downloadScope = 'all'">Semua Database</button>
          <button type="button" class="rounded-lg px-3 py-2 text-xs font-semibold transition" :class="downloadScope === 'selected' ? 'bg-cyan-400 text-[#0B2027]' : 'bg-white/5 text-slate-300 hover:bg-white/10'" @click="downloadScope = 'selected'">Bagian Tertentu</button>
        </div>

        <div v-if="downloadScope === 'selected'" class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <label v-for="option in backupOptions" :key="option.name" class="flex cursor-pointer items-start gap-3 rounded-xl border border-white/10 bg-[#0B2027]/60 p-3 transition hover:border-cyan-400/40">
            <input v-model="selectedTables" type="checkbox" :value="option.name" class="mt-0.5 h-4 w-4 rounded border-slate-600 bg-slate-900 text-cyan-400 focus:ring-cyan-400" />
            <span>
              <span class="block text-xs font-semibold text-[#EDE6D6]">{{ option.label }}</span>
              <span class="mt-1 block text-[11px] text-[#8AA0A4]">{{ option.description }}</span>
            </span>
          </label>
          <p v-if="backupOptions.length === 0" class="text-xs text-rose-300">Pilihan tabel belum tersedia dari server.</p>
        </div>
      </section>

      <section class="overflow-hidden rounded-2xl border border-white/10 bg-[#123138]/70 shadow-2xl backdrop-blur-md">
        <div class="flex flex-col gap-2 border-b border-white/10 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="font-serif text-xl font-bold text-[#F5EFE0]">Registry Backup</h2>
            <p class="mt-1 text-xs text-[#8AA0A4]">Riwayat snapshot yang dilaporkan oleh server.</p>
          </div>
          <button type="button" class="self-start rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-cyan-300 transition hover:border-cyan-400/40 hover:bg-cyan-500/10 disabled:opacity-50 sm:self-auto" :disabled="isLoading" @click="loadBackups">
            {{ isLoading ? 'Memuat...' : 'Segarkan Registry' }}
          </button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full min-w-[720px] text-left text-xs">
            <thead class="border-b border-cyan-500/20 bg-[#0B2027]/80 text-cyan-300">
              <tr>
                <th class="px-5 py-3 font-bold uppercase tracking-wider">Nama Berkas</th>
                <th class="px-5 py-3 font-bold uppercase tracking-wider">Tipe</th>
                <th class="px-5 py-3 font-bold uppercase tracking-wider">Ukuran</th>
                <th class="px-5 py-3 font-bold uppercase tracking-wider">Dibuat</th>
                <th class="px-5 py-3 font-bold uppercase tracking-wider">Status</th>
                <th class="px-5 py-3 text-right font-bold uppercase tracking-wider">Unduh</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5 text-[#C6D2D0]">
              <tr v-for="backup in backups" :key="backup.id" class="transition hover:bg-white/[0.03]">
                <td class="px-5 py-4 font-mono font-bold text-[#EDE6D6]">{{ backup.filename }}</td>
                <td class="px-5 py-4 text-[#8AA0A4]">{{ backup.type }}</td>
                <td class="px-5 py-4 font-mono text-amber-300">{{ backup.size }}</td>
                <td class="px-5 py-4 whitespace-nowrap text-[#8AA0A4]">{{ backup.created_at }}</td>
                <td class="px-5 py-4"><span class="rounded-full border border-teal-500/30 bg-teal-500/10 px-2.5 py-1 text-[10px] font-bold text-teal-300">{{ backup.status }}</span></td>
                <td class="px-5 py-4 text-right">
                  <button type="button" :disabled="isDownloading" class="rounded-lg border border-cyan-500/30 px-3 py-2 text-[11px] font-semibold text-cyan-300 transition hover:bg-cyan-500/10 disabled:cursor-not-allowed disabled:opacity-50" @click="downloadBackup({ scope: 'all', backupId: backup.id, key: backup.id })">
                    {{ isDownloading && downloadKey === backup.id ? 'Menyiapkan...' : 'SQL Penuh' }}
                  </button>
                </td>
              </tr>
              <tr v-if="!isLoading && backups.length === 0">
                <td colspan="6" class="px-5 py-12 text-center text-[#8AA0A4]">Belum ada snapshot backup yang tercatat.</td>
              </tr>
              <tr v-if="isLoading">
                <td colspan="6" class="px-5 py-12 text-center text-cyan-300">Memuat registry backup...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </MainAdminLayout>
</template>
