<script setup>
import { ref, computed } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// Filter Kategori
const selectedCategory = ref('all')

// Mock Data Pastoral Care
const prayerRequests = ref([
  {
    id: 'REQ-DOA-041',
    applicant: 'Ibu Ruth Natalia',
    phone: '081711223344',
    category: 'Doa Pemulihan Kesehatan',
    privacy: 'Doa Bersama Mimbar',
    notes: 'Mohon dukungan doa untuk kesembuhan orang tua yang sedang dirawat di RS Santo Borromeus.',
    status: 'Sedang Dilayani',
    assignedPastor: 'Ev. Yohanes Surya',
    date: '2026-09-22'
  },
  {
    id: 'REQ-DOA-042',
    applicant: 'Bpk. Hendra Setiawan',
    phone: '081822334455',
    category: 'Konseling Keluarga & Pernikahan',
    privacy: 'Rahasia / Privat',
    notes: 'Memohon waktu konseling pastoral dengan Pendeta terkait bimbingan komunikasi keluarga.',
    status: 'Menunggu Gembala',
    assignedPastor: 'Pdt. Andreas Wicaksono, M.Th',
    date: '2026-09-23'
  },
  {
    id: 'REQ-DOA-043',
    applicant: 'David Wijaya',
    phone: '081344556677',
    category: 'Pekerjaan & Studi',
    privacy: 'Doa Tim Pastoral',
    notes: 'Mohon dukungan doa agar proses wawancara kerja dan penyelesaian skripsi minggu depan berjalan lancar.',
    status: 'Selesai Didoakan',
    assignedPastor: 'Ev. Yohanes Surya',
    date: '2026-09-19'
  }
])

const filteredRequests = computed(() => {
  if (selectedCategory.value === 'all') return prayerRequests.value
  return prayerRequests.value.filter(r => r.category.toLowerCase().includes(selectedCategory.value.toLowerCase()))
})

const sendPastoralWA = (item) => {
  const msg = `Shalom ${item.applicant}, kami dari tim Pastoral GracePoint telah menerima pokok doa Saudara: "${item.notes}". Kami terus mendukung dalam doa, dan ${item.assignedPastor} rindu terhubung secara pribadi dengan Saudara. Tuhan Yesus memberkati dan memberi damai sejahtera.`
  const cleanPhone = item.phone.replace(/^0/, '62')
  window.open(`https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`, '_blank')
}

const markAsCompleted = (item) => {
  item.status = 'Selesai Didoakan'
}
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">
      
      <!-- Top Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-rose-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-rose-400 font-bold">PENGGEMBALAAN & KONSELING</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Pelayanan Pastoral & Permohonan Doa
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Kelola permohonan doa, bimbingan konseling rohani, dan koordinasi kunjungan pastoral jemaat secara privat.
          </p>
        </div>

        <div class="flex items-center gap-2.5">
          <select
            v-model="selectedCategory"
            class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400 cursor-pointer"
          >
            <option value="all">Semua Kategori Konseling</option>
            <option value="Kesehatan">Doa Pemulihan Sakit</option>
            <option value="Keluarga">Konseling Keluarga</option>
            <option value="Pekerjaan">Pekerjaan & Studi</option>
          </select>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Total Permohonan" subtitle="Bulan September">
          <div class="text-3xl font-bold text-white mt-1">{{ prayerRequests.length }} <span class="text-xs font-normal text-slate-400">Permohonan</span></div>
        </Card>
        <Card title="Menunggu Respons" subtitle="Perlu ditindaklanjuti">
          <div class="text-3xl font-bold text-rose-400 mt-1">
            {{ prayerRequests.filter(r => r.status === 'Menunggu Gembala').length }} <span class="text-xs font-normal text-slate-400">Jiwa</span>
          </div>
        </Card>
        <Card title="Sedang Didampingi" subtitle="Proses konseling">
          <div class="text-3xl font-bold text-amber-400 mt-1">
            {{ prayerRequests.filter(r => r.status === 'Sedang Dilayani').length }} <span class="text-xs font-normal text-slate-400">Kasus</span>
          </div>
        </Card>
        <Card title="Selesai Didoakan" subtitle="Telah tertangani">
          <div class="text-3xl font-bold text-emerald-400 mt-1">
            {{ prayerRequests.filter(r => r.status === 'Selesai Didoakan').length }} <span class="text-xs font-normal text-slate-400">Jiwa</span>
          </div>
        </Card>
      </div>

      <!-- Main Pastoral Table -->
      <Card title="Inbox Pokok Doa & Konseling Jemaat" subtitle="Menjaga kerahasiaan dan pendampingan rohani jemaat">
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-3">No. Tiket</th>
                <th class="p-3">Jemaat Pemohon</th>
                <th class="p-3">Kategori</th>
                <th class="p-3">Kerahasiaan</th>
                <th class="p-3">Pokok Doa / Kebutuhan</th>
                <th class="p-3">Status</th>
                <th class="p-3 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
              <tr
                v-for="item in filteredRequests"
                :key="item.id"
                class="hover:bg-slate-800/40 transition-colors"
              >
                <td class="p-3 font-mono text-slate-400">{{ item.id }}</td>
                <td class="p-3 font-semibold text-white">
                  <p>{{ item.applicant }}</p>
                  <p class="text-[10px] text-slate-400 font-mono">{{ item.phone }}</p>
                </td>
                <td class="p-3 text-sky-300">{{ item.category }}</td>
                <td class="p-3">
                  <span
                    :class="[
                      'px-2 py-0.5 rounded text-[10px] font-bold border',
                      item.privacy.includes('Rahasia')
                        ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                        : 'bg-slate-800 text-slate-300 border-slate-700'
                    ]"
                  >
                    {{ item.privacy }}
                  </span>
                </td>
                <td class="p-3 text-slate-300 max-w-xs leading-relaxed text-[11px]">
                  {{ item.notes }}
                </td>
                <td class="p-3">
                  <span
                    :class="[
                      'px-2.5 py-1 rounded-full text-[10px] font-bold border',
                      item.status === 'Selesai Didoakan'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : item.status === 'Sedang Dilayani'
                        ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                        : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                    ]"
                  >
                    {{ item.status }}
                  </span>
                </td>
                <td class="p-3 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <button
                      @click="sendPastoralWA(item)"
                      title="Hubungi & Beri Penguatan"
                      class="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-[11px] font-medium flex items-center gap-1 cursor-pointer"
                    >
                      <span>💬 Respons WA</span>
                    </button>
                    <button
                      v-if="item.status !== 'Selesai Didoakan'"
                      @click="markAsCompleted(item)"
                      title="Tandai Selesai"
                      class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] cursor-pointer"
                    >
                      ✓ Selesai
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

    </div>
  </ChurchAdminLayout>
</template>
