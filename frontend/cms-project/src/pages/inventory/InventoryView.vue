<script setup>
import { ref } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// State Fasilitas & Ruangan
const rooms = ref([
  {
    name: 'Gedung Ibadah Utama (Sanctuary)',
    capacity: '600 Kursi',
    status: 'Terjadwal',
    currentUse: 'Ibadah Raya 1 & 2 (Minggu)',
    pic: 'Bpk. Paulus Sudrajat',
    icon: '⛪'
  },
  {
    name: 'Ruang Serbaguna (Fellowship Hall)',
    capacity: '150 Orang',
    status: 'Tersedia',
    currentUse: 'Bisa dipinjam untuk ramah tamah / seminar',
    pic: 'Sekretariat Cabang',
    icon: '🏛️'
  },
  {
    name: 'Ruang Konseling & Pastoral Care',
    capacity: '8 Orang',
    status: 'Terjadwal',
    currentUse: 'Bimbingan Pranikah (Sabtu 14:00)',
    pic: 'Pdt. Andreas Wicaksono',
    icon: '🤝'
  },
  {
    name: 'Ruang Musik & Studio Pemuda',
    capacity: '20 Orang',
    status: 'Terjadwal',
    currentUse: 'Latihan Tim Pujian WL & Pemusik (Jumat 19:00)',
    pic: 'Daniel Hartono',
    icon: '🎵'
  },
  {
    name: 'Mobil Operasional Cabang (Isuzu Elf)',
    capacity: '16 Penumpang',
    status: 'Tersedia',
    currentUse: 'Siaga antar jemput lansia & kunjungan duka',
    pic: 'Bpk. Hendra Setiawan',
    icon: '🚐'
  }
])

// State Inventaris Aset Multimedia
const assets = ref([
  { id: 'AST-SND-01', name: 'Digital Sound Mixer Behringer X32', location: 'Ruang FOH Sound', condition: 'Sangat Baik', lastCheck: '2026-09-10' },
  { id: 'AST-MSK-02', name: 'Stage Piano Roland RD-2000', location: 'Panggung Utama', condition: 'Sangat Baik', lastCheck: '2026-09-12' },
  { id: 'AST-MIC-03', name: 'Wireless Mic Shure GLXD4 (4 Set)', location: 'Ruang Sound', condition: '1 Unit Perlu Servis', lastCheck: '2026-09-18' },
  { id: 'AST-PRJ-04', name: 'Laser Projector Epson 6000 Lumens', location: 'Langit-langit Sanctuary', condition: 'Sangat Baik', lastCheck: '2026-09-01' },
  { id: 'AST-CAM-05', name: 'PTZ Live Streaming Camera 4K (2 Set)', location: 'Balkon Atas', condition: 'Sangat Baik', lastCheck: '2026-09-15' },
])

const isBookingModalOpen = ref(false)
const newBooking = ref({
  roomName: 'Ruang Serbaguna (Fellowship Hall)',
  borrower: '',
  date: '',
  time: '',
  purpose: ''
})

const handleBooking = () => {
  if (!newBooking.value.borrower) return
  isBookingModalOpen.value = false
  alert(`Permohonan peminjaman "${newBooking.value.roomName}" oleh "${newBooking.value.borrower}" telah dicatat di jadwal cabang!`)
}
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">
      
      <!-- Top Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-indigo-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-indigo-400 font-bold">ASET & SARANA PRASARANA</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Peminjaman Fasilitas & Inventaris Cabang
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Atur peminjaman ruangan serbaguna, sound system, kendaraan operasional, dan pantau pemeliharaan aset gereja.
          </p>
        </div>

        <div class="flex items-center gap-3">
          <button
            @click="isBookingModalOpen = true"
            class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-400 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            <span>Booking Fasilitas</span>
          </button>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Total Fasilitas Ruang" subtitle="Kapasitas cabang">
          <div class="text-3xl font-bold text-white mt-1">{{ rooms.length }} <span class="text-xs font-normal text-slate-400">Unit</span></div>
        </Card>
        <Card title="Ruangan Tersedia" subtitle="Bisa dipinjam">
          <div class="text-3xl font-bold text-emerald-400 mt-1">
            {{ rooms.filter(r => r.status === 'Tersedia').length }} <span class="text-xs font-normal text-slate-400">Ruang</span>
          </div>
        </Card>
        <Card title="Total Aset Multimedia" subtitle="Terdaftar di sistem">
          <div class="text-3xl font-bold text-amber-400 mt-1">{{ assets.length }} <span class="text-xs font-normal text-slate-400">Item</span></div>
        </Card>
        <Card title="Perlu Servis / Cek" subtitle="Pemeliharaan">
          <div class="text-3xl font-bold text-rose-400 mt-1">
            {{ assets.filter(a => a.condition.includes('Perlu')).length }} <span class="text-xs font-normal text-slate-400">Unit</span>
          </div>
        </Card>
      </div>

      <!-- Status Peminjaman Ruangan & Fasilitas -->
      <Card title="Jadwal Penggunaan Ruangan & Kendaraan Gereja" subtitle="Mencegah bentrok jadwal antar kategorial dan persekutuan">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-1">
          <div
            v-for="(r, idx) in rooms"
            :key="idx"
            class="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-3 hover:border-indigo-500/40 transition-colors"
          >
            <div class="flex items-center justify-between">
              <span class="text-2xl">{{ r.icon }}</span>
              <span
                :class="[
                  'px-2 py-0.5 rounded-full text-[10px] font-bold border',
                  r.status === 'Tersedia'
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                ]"
              >
                {{ r.status }}
              </span>
            </div>

            <div>
              <h4 class="font-bold text-white text-xs">{{ r.name }}</h4>
              <p class="text-[11px] text-slate-400 mt-0.5">Kapasitas: {{ r.capacity }}</p>
            </div>

            <div class="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800 text-[11px] text-slate-300">
              <p class="font-semibold text-amber-300/90">Agenda:</p>
              <p class="truncate">{{ r.currentUse }}</p>
              <p class="text-[10px] text-slate-500 mt-1">Penanggung Jawab: {{ r.pic }}</p>
            </div>
          </div>
        </div>
      </Card>

      <!-- Daftar Aset Multimedia & Alat Musik -->
      <Card title="Inventaris Sound System, Alat Musik, & Proyektor" subtitle="Log kondisi aset perangkat ibadah cabang" id="inventaris">
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-3">ID Aset</th>
                <th class="p-3">Nama Perangkat / Aset</th>
                <th class="p-3">Penempatan</th>
                <th class="p-3">Kondisi Alat</th>
                <th class="p-3">Pengecekan Terakhir</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
              <tr v-for="a in assets" :key="a.id" class="hover:bg-slate-800/40 transition-colors">
                <td class="p-3 font-mono text-slate-400">{{ a.id }}</td>
                <td class="p-3 font-semibold text-white">{{ a.name }}</td>
                <td class="p-3 text-slate-300">{{ a.location }}</td>
                <td class="p-3">
                  <span
                    :class="[
                      'px-2 py-0.5 rounded text-[10px] font-bold border',
                      a.condition === 'Sangat Baik'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                    ]"
                  >
                    {{ a.condition }}
                  </span>
                </td>
                <td class="p-3 text-slate-400 font-mono">{{ a.lastCheck }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <!-- Modal Booking Ruangan -->
      <div
        v-if="isBookingModalOpen"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      >
        <div class="bg-slate-900 border border-indigo-500/40 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span class="text-indigo-400">📅</span> Formulir Peminjaman Fasilitas Cabang
            </h3>
            <button @click="isBookingModalOpen = false" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <form @submit.prevent="handleBooking" class="space-y-3.5">
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Pilih Ruangan / Sarana *</label>
              <select
                v-model="newBooking.roomName"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
              >
                <option v-for="r in rooms" :key="r.name" :value="r.name">{{ r.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Nama Pemohon / Komisi Kategorial *</label>
              <input
                v-model="newBooking.borrower"
                required
                type="text"
                placeholder="Contoh: Komisi Pemuda (Youth)"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Tanggal Peminjaman</label>
                <input
                  v-model="newBooking.date"
                  type="date"
                  required
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Waktu / Jam</label>
                <input
                  v-model="newBooking.time"
                  type="text"
                  placeholder="19:00 - 21:00 WIB"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
                />
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Keperluan Acara</label>
              <textarea
                v-model="newBooking.purpose"
                rows="2"
                placeholder="Deskripsi kegiatan..."
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
              ></textarea>
            </div>

            <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                @click="isBookingModalOpen = false"
                class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
              >
                Batal
              </button>
              <button
                type="submit"
                class="px-5 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-bold text-xs cursor-pointer shadow-lg shadow-indigo-500/20"
              >
                Simpan Booking
              </button>
            </div>
          </form>
        </div>
      </div>

    </div>
  </ChurchAdminLayout>
</template>
