<script setup>
import { ref, computed } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// Tab mode: 'qr' atau 'headcount'
const activeTab = ref('qr')

// State Scanner QR
const manualIdInput = ref('')
const scanSuccessMsg = ref('')
const recentScans = ref([
  { id: 'JM-001', name: 'Budi Santoso', time: '06:48 WIB', status: 'Hadir Tepat Waktu' },
  { id: 'JM-002', name: 'Maria Anggraini', time: '06:50 WIB', status: 'Hadir Tepat Waktu' },
  { id: 'JM-004', name: 'Yohanes Kristianto', time: '06:55 WIB', status: 'Hadir Tepat Waktu' },
])

// State Headcount
const headcount = ref({
  pria: 145,
  wanita: 182,
  pemuda: 64,
  anak: 58,
})

const totalHeadcount = computed(() => {
  return Number(headcount.value.pria) + Number(headcount.value.wanita) + Number(headcount.value.pemuda) + Number(headcount.value.anak)
})

const adjustHeadcount = (category, amount) => {
  headcount.value[category] = Math.max(0, headcount.value[category] + amount)
}

const handleManualScan = () => {
  if (!manualIdInput.value) return
  const id = manualIdInput.value.toUpperCase()
  recentScans.value.unshift({
    id: id,
    name: id === 'JM-003' ? 'David Wijaya' : `Jemaat ${id}`,
    time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WIB',
    status: 'Hadir Terverifikasi'
  })
  scanSuccessMsg.value = `Berhasil mencatat presensi untuk ${id}!`
  manualIdInput.value = ''
  setTimeout(() => {
    scanSuccessMsg.value = ''
  }, 3500)
}

// Histori 4 Pekan Terakhir
const attendanceHistory = ref([
  { date: '20 Sep 2026', session: 'Ibadah Raya 1', total: 449, pria: 145, wanita: 182, pemuda: 64, anak: 58 },
  { date: '13 Sep 2026', session: 'Ibadah Raya 1', total: 432, pria: 140, wanita: 175, pemuda: 60, anak: 57 },
  { date: '06 Sep 2026', session: 'Ibadah Raya 1', total: 418, pria: 135, wanita: 170, pemuda: 58, anak: 55 },
  { date: '30 Agu 2026', session: 'Ibadah Raya 1', total: 425, pria: 138, wanita: 172, pemuda: 61, anak: 54 },
])
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">
      
      <!-- Top Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-emerald-400 font-bold">PRESENSI & KEHADIRAN IBADAH</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Scanner QR & Rekap Kehadiran Jemaat
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Catat kehadiran ibadah raya menggunakan barcode/QR scanner atau hitung cepat jumlah jemaat fisik (headcount).
          </p>
        </div>

        <!-- Mode Toggle -->
        <div class="flex items-center bg-slate-900 p-1 rounded-xl border border-slate-800">
          <button
            @click="activeTab = 'qr'"
            :class="[
              'px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5',
              activeTab === 'qr'
                ? 'bg-amber-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            ]"
          >
            <span>📱 Scanner QR Code</span>
          </button>
          <button
            @click="activeTab = 'headcount'"
            :class="[
              'px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5',
              activeTab === 'headcount'
                ? 'bg-amber-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white'
            ]"
          >
            <span>🧮 Kalkulator Headcount</span>
          </button>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Total Hadir Hari Ini" subtitle="Semua sesi">
          <div class="text-3xl font-bold text-emerald-400 mt-1">{{ totalHeadcount }} <span class="text-xs font-normal text-slate-400">Jiwa</span></div>
        </Card>
        <Card title="Pria Dewasa" subtitle="Kehadiran">
          <div class="text-3xl font-bold text-sky-400 mt-1">{{ headcount.pria }} <span class="text-xs font-normal text-slate-400">Jiwa</span></div>
        </Card>
        <Card title="Wanita Dewasa" subtitle="Kehadiran">
          <div class="text-3xl font-bold text-pink-400 mt-1">{{ headcount.wanita }} <span class="text-xs font-normal text-slate-400">Jiwa</span></div>
        </Card>
        <Card title="Pemuda & Anak" subtitle="Generasi muda">
          <div class="text-3xl font-bold text-amber-400 mt-1">{{ headcount.pemuda + headcount.anak }} <span class="text-xs font-normal text-slate-400">Jiwa</span></div>
        </Card>
      </div>

      <!-- TAB 1: QR CODE SCANNER -->
      <div v-if="activeTab === 'qr'" class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- Scanner Cam View / Simulated Area -->
        <div class="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="font-bold text-white text-sm flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
              Kamera Pemindai QR Presensi Aktif
            </h3>
            <span class="text-[11px] text-slate-400 font-mono">USB / WebCam Ready</span>
          </div>

          <!-- Scanner Animated Frame -->
          <div class="relative w-full h-64 bg-slate-950 rounded-xl overflow-hidden border border-slate-700/60 flex flex-col items-center justify-center">
            <div class="relative w-48 h-48 border-2 border-dashed border-amber-400/70 rounded-2xl flex items-center justify-center">
              <div class="absolute inset-x-0 h-0.5 bg-gradient-to-r from-transparent via-amber-400 to-transparent animate-pulse top-1/2"></div>
              <svg class="w-16 h-16 text-slate-700 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/></svg>
            </div>
            <p class="text-[11px] text-slate-400 mt-3">Arahkan Kartu Jemaat Digital atau Barcode ke area kamera</p>
          </div>

          <!-- Manual ID fallback input -->
          <div class="space-y-2">
            <label class="block text-xs text-slate-300">Input Manual ID Jemaat (Alternatif jika tanpa kamera):</label>
            <div class="flex gap-2">
              <input
                v-model="manualIdInput"
                @keyup.enter="handleManualScan"
                type="text"
                placeholder="Contoh: JM-003"
                class="flex-1 px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white uppercase focus:outline-none focus:border-amber-400"
              />
              <button
                @click="handleManualScan"
                class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl transition-all cursor-pointer"
              >
                Catat Hadir
              </button>
            </div>
            <p v-if="scanSuccessMsg" class="text-xs text-emerald-400 font-medium animate-fadeIn">
              ✅ {{ scanSuccessMsg }}
            </p>
          </div>
        </div>

        <!-- Real-Time Scanned Feed -->
        <div class="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="font-bold text-white text-sm">Log Presensi Terakhir</h3>
            <span class="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full font-mono">Real-Time</span>
          </div>

          <div class="space-y-2.5 max-h-80 overflow-y-auto pr-1">
            <div
              v-for="(scan, sIdx) in recentScans"
              :key="sIdx"
              class="p-3 bg-slate-950/70 border border-slate-800 rounded-xl flex items-center justify-between hover:border-amber-500/30 transition-colors"
            >
              <div>
                <p class="text-xs font-semibold text-white">{{ scan.name }}</p>
                <p class="text-[10px] text-slate-400 font-mono">{{ scan.id }} • {{ scan.time }}</p>
              </div>
              <span class="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-bold">
                {{ scan.status }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: KALKULATOR HEADCOUNT CEPAT -->
      <div v-else class="space-y-5" id="headcount">
        <Card title="Kalkulator Headcount Fisik Ibadah" subtitle="Gunakan tombol cepat (+1, +5, +10) saat usher menghitung jemaat di bangku gereja">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
            <!-- Pria Dewasa -->
            <div class="bg-slate-950/80 border border-sky-500/30 rounded-xl p-4 space-y-3 text-center">
              <span class="text-2xl">👨</span>
              <p class="text-xs uppercase font-bold text-sky-400">Pria Dewasa</p>
              <div class="text-3xl font-extrabold text-white">{{ headcount.pria }}</div>
              <div class="flex items-center justify-center gap-1.5 pt-1">
                <button @click="adjustHeadcount('pria', -1)" class="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 font-bold text-xs hover:bg-slate-700 cursor-pointer">-1</button>
                <button @click="adjustHeadcount('pria', 1)" class="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-300 font-bold text-xs hover:bg-sky-500/30 cursor-pointer">+1</button>
                <button @click="adjustHeadcount('pria', 5)" class="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-300 font-bold text-xs hover:bg-sky-500/30 cursor-pointer">+5</button>
                <button @click="adjustHeadcount('pria', 10)" class="w-8 h-8 rounded-lg bg-sky-500/30 text-sky-200 font-bold text-xs hover:bg-sky-500/40 cursor-pointer">+10</button>
              </div>
            </div>

            <!-- Wanita Dewasa -->
            <div class="bg-slate-950/80 border border-pink-500/30 rounded-xl p-4 space-y-3 text-center">
              <span class="text-2xl">👩</span>
              <p class="text-xs uppercase font-bold text-pink-400">Wanita Dewasa</p>
              <div class="text-3xl font-extrabold text-white">{{ headcount.wanita }}</div>
              <div class="flex items-center justify-center gap-1.5 pt-1">
                <button @click="adjustHeadcount('wanita', -1)" class="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 font-bold text-xs hover:bg-slate-700 cursor-pointer">-1</button>
                <button @click="adjustHeadcount('wanita', 1)" class="w-8 h-8 rounded-lg bg-pink-500/20 text-pink-300 font-bold text-xs hover:bg-pink-500/30 cursor-pointer">+1</button>
                <button @click="adjustHeadcount('wanita', 5)" class="w-8 h-8 rounded-lg bg-pink-500/20 text-pink-300 font-bold text-xs hover:bg-pink-500/30 cursor-pointer">+5</button>
                <button @click="adjustHeadcount('wanita', 10)" class="w-8 h-8 rounded-lg bg-pink-500/30 text-pink-200 font-bold text-xs hover:bg-pink-500/40 cursor-pointer">+10</button>
              </div>
            </div>

            <!-- Pemuda / Remaja -->
            <div class="bg-slate-950/80 border border-purple-500/30 rounded-xl p-4 space-y-3 text-center">
              <span class="text-2xl">🧑</span>
              <p class="text-xs uppercase font-bold text-purple-400">Pemuda & Remaja</p>
              <div class="text-3xl font-extrabold text-white">{{ headcount.pemuda }}</div>
              <div class="flex items-center justify-center gap-1.5 pt-1">
                <button @click="adjustHeadcount('pemuda', -1)" class="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 font-bold text-xs hover:bg-slate-700 cursor-pointer">-1</button>
                <button @click="adjustHeadcount('pemuda', 1)" class="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-300 font-bold text-xs hover:bg-purple-500/30 cursor-pointer">+1</button>
                <button @click="adjustHeadcount('pemuda', 5)" class="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-300 font-bold text-xs hover:bg-purple-500/30 cursor-pointer">+5</button>
                <button @click="adjustHeadcount('pemuda', 10)" class="w-8 h-8 rounded-lg bg-purple-500/30 text-purple-200 font-bold text-xs hover:bg-purple-500/40 cursor-pointer">+10</button>
              </div>
            </div>

            <!-- Sekolah Minggu -->
            <div class="bg-slate-950/80 border border-amber-500/30 rounded-xl p-4 space-y-3 text-center">
              <span class="text-2xl">🧒</span>
              <p class="text-xs uppercase font-bold text-amber-400">Sekolah Minggu / Anak</p>
              <div class="text-3xl font-extrabold text-white">{{ headcount.anak }}</div>
              <div class="flex items-center justify-center gap-1.5 pt-1">
                <button @click="adjustHeadcount('anak', -1)" class="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 font-bold text-xs hover:bg-slate-700 cursor-pointer">-1</button>
                <button @click="adjustHeadcount('anak', 1)" class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-300 font-bold text-xs hover:bg-amber-500/30 cursor-pointer">+1</button>
                <button @click="adjustHeadcount('anak', 5)" class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-300 font-bold text-xs hover:bg-amber-500/30 cursor-pointer">+5</button>
                <button @click="adjustHeadcount('anak', 10)" class="w-8 h-8 rounded-lg bg-amber-500/30 text-amber-200 font-bold text-xs hover:bg-amber-500/40 cursor-pointer">+10</button>
              </div>
            </div>
          </div>

          <div class="flex justify-end pt-4 border-t border-slate-800 mt-4">
            <button
              class="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 cursor-pointer"
            >
              💾 Simpan Rekap Kehadiran (Total: {{ totalHeadcount }} Jiwa)
            </button>
          </div>
        </Card>
      </div>

      <!-- History Table -->
      <Card title="Histori Kehadiran 4 Pekan Terakhir" subtitle="Rekam jejak kehadiran jemaat cabang per minggu">
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-3">Tanggal Ibadah</th>
                <th class="p-3">Sesi</th>
                <th class="p-3">Total Jemaat</th>
                <th class="p-3">Pria</th>
                <th class="p-3">Wanita</th>
                <th class="p-3">Pemuda</th>
                <th class="p-3">Anak</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
              <tr v-for="(h, idx) in attendanceHistory" :key="idx" class="hover:bg-slate-800/40 transition-colors">
                <td class="p-3 font-semibold text-white">{{ h.date }}</td>
                <td class="p-3 text-slate-300">{{ h.session }}</td>
                <td class="p-3 font-bold text-emerald-400">{{ h.total }} Jiwa</td>
                <td class="p-3 text-slate-400">{{ h.pria }}</td>
                <td class="p-3 text-slate-400">{{ h.wanita }}</td>
                <td class="p-3 text-slate-400">{{ h.pemuda }}</td>
                <td class="p-3 text-slate-400">{{ h.anak }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

    </div>
  </ChurchAdminLayout>
</template>
