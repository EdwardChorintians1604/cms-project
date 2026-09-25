<script setup>
import { ref, computed } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// Sesi dan Pekan Aktif
const selectedDate = ref('2026-09-27')
const selectedSession = ref('sesi-1')

// Mock Jadwal Pelayan
const rosterData = ref({
  '2026-09-27': {
    'sesi-1': [
      { role: 'Pengkhotbah', name: 'Pdt. Andreas Wicaksono, M.Th', phone: '081211112222', status: 'Dikonfirmasi', icon: '📖' },
      { role: 'Worship Leader (WL)', name: 'Ev. Yohanes Surya', phone: '081233334444', status: 'Dikonfirmasi', icon: '🎤' },
      { role: 'Singer 1', name: 'Maria Novita', phone: '081355556666', status: 'Dikonfirmasi', icon: '🎵' },
      { role: 'Singer 2', name: 'Deborah Silaban', phone: '081377778888', status: 'Menunggu', icon: '🎵' },
      { role: 'Pemusik (Keyboard)', name: 'Daniel Hartono', phone: '081599990000', status: 'Dikonfirmasi', icon: '🎹' },
      { role: 'Pemusik (Bass / Gitar)', name: 'Kevin Christian', phone: '081622223333', status: 'Berhalangan', icon: '🎸' },
      { role: 'Pemusik (Drum)', name: 'Timothy Pratama', phone: '081744445555', status: 'Dikonfirmasi', icon: '🥁' },
      { role: 'Usher / Kolektan 1', name: 'Bpk. Paulus Sudrajat', phone: '081866667777', status: 'Dikonfirmasi', icon: '🤝' },
      { role: 'Usher / Kolektan 2', name: 'Ibu Ester Wijaya', phone: '081988889999', status: 'Dikonfirmasi', icon: '🤝' },
      { role: 'Sound & Audio Engineer', name: 'Samuel Hutapea', phone: '081122334455', status: 'Dikonfirmasi', icon: '🎛️' },
      { role: 'Multimedia & Live Stream', name: 'Jonathan Lee', phone: '081233445566', status: 'Menunggu', icon: '🎥' },
    ],
    'sesi-2': [
      { role: 'Pengkhotbah', name: 'Pdt. Markus Tanudjaja', phone: '081299998888', status: 'Dikonfirmasi', icon: '📖' },
      { role: 'Worship Leader (WL)', name: 'Ruth Claudia', phone: '081311112222', status: 'Dikonfirmasi', icon: '🎤' },
      { role: 'Singer 1', name: 'Grace Natalie', phone: '081322223333', status: 'Dikonfirmasi', icon: '🎵' },
      { role: 'Pemusik (Keyboard)', name: 'Steven Chandra', phone: '081533334444', status: 'Dikonfirmasi', icon: '🎹' },
      { role: 'Usher / Kolektan', name: 'Bpk. Gideon Kusuma', phone: '081755556666', status: 'Dikonfirmasi', icon: '🤝' },
      { role: 'Multimedia', name: 'Bryan Aristo', phone: '081977778888', status: 'Dikonfirmasi', icon: '🎥' },
    ]
  }
})

// Liturgi dan Tema Ibadah
const liturgyPlan = ref({
  theme: 'Berakar dan Berbuah di Dalam Kasih Kristus',
  scripture: 'Kolose 2:6-7',
  songs: [
    { title: 'Kebaikan-Mu Tak Pernah Gagal', key: 'Do = G', tempo: 'Medium' },
    { title: 'Nyanyi Bagi Dia (Sebab Dia Baik)', key: 'Do = D', tempo: 'Upbeat' },
    { title: 'Sentuh Hatiku Tuhan', key: 'Do = F', tempo: 'Slow / Penyembahan' },
    { title: 'Bapa Engkau Sungguh Baik', key: 'Do = C', tempo: 'Persembahan' },
  ]
})

const currentRoster = computed(() => {
  const byDate = rosterData.value[selectedDate.value] || {}
  return byDate[selectedSession.value] || []
})

const sendReminderWA = (item) => {
  const sessionName = selectedSession.value === 'sesi-1' ? 'Ibadah Raya 1 (07:00 WIB)' : 'Ibadah Raya 2 (10:00 WIB)'
  const msg = `Shalom ${item.name},\n\nMengingatkan jadwal tugas pelayanan di GracePoint pada Minggu, 27 Sept 2026:\n• Sesi: ${sessionName}\n• Tugas: ${item.role}\n• Doa Bersama: 30 menit sebelum ibadah.\n\nMohon konfirmasi kehadiran Saudara. Tuhan Yesus memberkati pelayanan kita!`
  const cleanPhone = item.phone.replace(/^0/, '62')
  window.open(`https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`, '_blank')
}

const toggleStatus = (item) => {
  if (item.status === 'Menunggu') item.status = 'Dikonfirmasi'
  else if (item.status === 'Dikonfirmasi') item.status = 'Berhalangan'
  else item.status = 'Dikonfirmasi'
}
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">
      
      <!-- Top Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-purple-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-purple-400 font-bold">OPERASIONAL IBADAH</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Jadwal Petugas & Roster Pelayan Ibadah
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Atur penugasan tim mimbar, singer, pemusik, multimedia, dan pantau status konfirmasi pelayan mingguan.
          </p>
        </div>

        <!-- Filter Sesi & Pekan -->
        <div class="flex items-center gap-2.5">
          <select
            v-model="selectedDate"
            class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400 cursor-pointer"
          >
            <option value="2026-09-27">Minggu, 27 Sept 2026 (Pekan Ini)</option>
            <option value="2026-10-04">Minggu, 04 Okt 2026 (Pekan Depan)</option>
          </select>

          <select
            v-model="selectedSession"
            class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400 cursor-pointer"
          >
            <option value="sesi-1">Sesi 1 (07:00 WIB)</option>
            <option value="sesi-2">Sesi 2 (10:00 WIB)</option>
          </select>
        </div>
      </div>

      <!-- Quick Roster Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Total Posisi Tugas" subtitle="Kebutuhan pelayan">
          <div class="text-3xl font-bold text-white mt-1">{{ currentRoster.length }} <span class="text-xs font-normal text-slate-400">Posisi</span></div>
        </Card>
        <Card title="Telah Dikonfirmasi" subtitle="Siap melayani">
          <div class="text-3xl font-bold text-emerald-400 mt-1">
            {{ currentRoster.filter(r => r.status === 'Dikonfirmasi').length }} <span class="text-xs font-normal text-slate-400">Orang</span>
          </div>
        </Card>
        <Card title="Menunggu Konfirmasi" subtitle="Perlu reminder">
          <div class="text-3xl font-bold text-amber-400 mt-1">
            {{ currentRoster.filter(r => r.status === 'Menunggu').length }} <span class="text-xs font-normal text-slate-400">Orang</span>
          </div>
        </Card>
        <Card title="Berhalangan" subtitle="Perlu pengganti segera">
          <div class="text-3xl font-bold text-rose-400 mt-1">
            {{ currentRoster.filter(r => r.status === 'Berhalangan').length }} <span class="text-xs font-normal text-slate-400">Posisi</span>
          </div>
        </Card>
      </div>

      <!-- Main Duty Roster Table -->
      <Card title="Matriks Penugasan Pelayan Ibadah" subtitle="Pantau dan ingatkan pelayan ibadah satu per satu">
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-3">Posisi Pelayanan</th>
                <th class="p-3">Nama Petugas</th>
                <th class="p-3">Kontak</th>
                <th class="p-3">Status Konfirmasi</th>
                <th class="p-3 text-right">Aksi Cepat</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
              <tr
                v-for="(item, idx) in currentRoster"
                :key="idx"
                class="hover:bg-slate-800/40 transition-colors"
              >
                <td class="p-3 font-semibold text-white flex items-center gap-2">
                  <span>{{ item.icon }}</span>
                  <span>{{ item.role }}</span>
                </td>
                <td class="p-3 text-slate-200">{{ item.name }}</td>
                <td class="p-3 text-slate-400 font-mono">{{ item.phone }}</td>
                <td class="p-3">
                  <button
                    @click="toggleStatus(item)"
                    title="Klik untuk ubah status konfirmasi"
                    :class="[
                      'px-2.5 py-1 rounded-full text-[10px] font-bold border cursor-pointer transition-all',
                      item.status === 'Dikonfirmasi'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/25'
                        : item.status === 'Menunggu'
                        ? 'bg-amber-500/15 text-amber-300 border-amber-500/30 hover:bg-amber-500/25'
                        : 'bg-rose-500/15 text-rose-300 border-rose-500/30 hover:bg-rose-500/25'
                    ]"
                  >
                    {{ item.status }}
                  </button>
                </td>
                <td class="p-3 text-right">
                  <button
                    @click="sendReminderWA(item)"
                    class="px-2.5 py-1 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 text-[11px] font-medium inline-flex items-center gap-1.5 transition-all cursor-pointer"
                  >
                    <span>💬 Kirim Reminder WA</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <!-- Liturgi & Bank Lagu Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5" id="liturgi">
        <Card title="Liturgi & Tema Khotbah" subtitle="Sinkronisasi tema mimbar & bacaan firman">
          <div class="space-y-3 pt-1">
            <div class="p-3 bg-slate-900 rounded-xl border border-slate-800">
              <span class="text-[10px] uppercase font-bold text-amber-400">Tema Mingguan:</span>
              <p class="text-sm font-semibold text-white mt-0.5">{{ liturgyPlan.theme }}</p>
            </div>
            <div class="p-3 bg-slate-900 rounded-xl border border-slate-800">
              <span class="text-[10px] uppercase font-bold text-sky-400">Nats Pembimbing / Bacaan:</span>
              <p class="text-sm font-semibold text-white mt-0.5">{{ liturgyPlan.scripture }}</p>
            </div>
          </div>
        </Card>

        <Card title="Bank Lagu Pujian & Penyembahan" subtitle="Daftar lagu & nada dasar untuk pemusik & multimedia">
          <div class="space-y-2 pt-1">
            <div
              v-for="(song, sIdx) in liturgyPlan.songs"
              :key="sIdx"
              class="flex items-center justify-between p-2.5 bg-slate-900 rounded-xl border border-slate-800"
            >
              <div class="flex items-center gap-2">
                <span class="w-5 h-5 rounded-full bg-purple-500/20 text-purple-300 font-bold flex items-center justify-center text-[10px]">
                  {{ sIdx + 1 }}
                </span>
                <div>
                  <p class="text-xs font-semibold text-white">{{ song.title }}</p>
                  <p class="text-[10px] text-slate-400">{{ song.tempo }}</p>
                </div>
              </div>
              <span class="px-2 py-0.5 text-xs font-mono font-bold bg-amber-500/20 text-amber-300 rounded border border-amber-500/30">
                {{ song.key }}
              </span>
            </div>
          </div>
        </Card>
      </div>

    </div>
  </ChurchAdminLayout>
</template>
