<script setup>
import { ref, computed } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// State Filter Kategori Sakramen
const selectedCategory = ref('all')
const previewCert = ref(null)

// Mock Data Permohonan Sakramen
const sacramentRequests = ref([
  {
    ticketId: 'REQ-BAP-012',
    type: 'Baptisan Kudus Dewasa',
    applicant: 'David Wijaya',
    phone: '081344556677',
    plannedDate: '2026-10-18',
    status: 'Disetujui',
    minister: 'Pdt. Andreas Wicaksono, M.Th',
    regDate: '2026-09-15'
  },
  {
    ticketId: 'REQ-ANK-008',
    type: 'Penyerahan Anak',
    applicant: 'Keluarga Budi Santoso & Maria Anggraini (Anak: Chloe Santoso)',
    phone: '081234567890',
    plannedDate: '2026-10-04',
    status: 'Menunggu Majelis',
    minister: 'Pdt. Markus Tanudjaja',
    regDate: '2026-09-20'
  },
  {
    ticketId: 'REQ-SDI-005',
    type: 'Katekisasi & SIDI',
    applicant: 'Ruth Natalia',
    phone: '081711223344',
    plannedDate: '2026-11-22',
    status: 'Menunggu Majelis',
    minister: 'Ev. Yohanes Surya',
    regDate: '2026-09-22'
  },
  {
    ticketId: 'REQ-NIK-003',
    type: 'Pemberkatan Pernikahan Kudus',
    applicant: 'Michael Pratama & Stephanie Wijaya',
    phone: '081922334455',
    plannedDate: '2026-12-12',
    status: 'Disetujui',
    minister: 'Pdt. Andreas Wicaksono, M.Th',
    regDate: '2026-09-10'
  },
  {
    ticketId: 'REQ-ATT-007',
    type: 'Surat Atestasi Pindah Jemaat',
    applicant: 'Hendra Setiawan',
    phone: '081822334455',
    plannedDate: '2026-09-30',
    status: 'Selesai Terbit',
    minister: 'Sekretariat Cabang',
    regDate: '2026-09-18'
  }
])

const filteredRequests = computed(() => {
  if (selectedCategory.value === 'all') return sacramentRequests.value
  return sacramentRequests.value.filter(r => r.type.toLowerCase().includes(selectedCategory.value.toLowerCase()))
})

const approveRequest = (item) => {
  item.status = 'Disetujui'
}

const openCertificateModal = (item) => {
  previewCert.value = item
}
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">
      
      <!-- Top Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-sky-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-sky-400 font-bold">SAKRAMEN & DOKUMEN RESMI</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Inbox Permohonan Sakramen & Surat Gereja
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Kelola pengajuan Baptisan Kudus, Penyerahan Anak, SIDI, Pernikahan Kudus, serta cetak surat keterangan resmi.
          </p>
        </div>

        <!-- Filter Sakramen -->
        <div class="flex items-center gap-2.5">
          <select
            v-model="selectedCategory"
            class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400 cursor-pointer"
          >
            <option value="all">Semua Kategori Sakramen</option>
            <option value="Baptisan">Baptisan Kudus</option>
            <option value="Penyerahan">Penyerahan Anak</option>
            <option value="SIDI">Katekisasi / SIDI</option>
            <option value="Pernikahan">Pemberkatan Nikah</option>
            <option value="Atestasi">Atestasi Pindah</option>
          </select>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Total Pengajuan" subtitle="Bulan September">
          <div class="text-3xl font-bold text-white mt-1">{{ sacramentRequests.length }} <span class="text-xs font-normal text-slate-400">Berkas</span></div>
        </Card>
        <Card title="Menunggu Verifikasi" subtitle="Perlu rapat majelis">
          <div class="text-3xl font-bold text-amber-400 mt-1">
            {{ sacramentRequests.filter(r => r.status === 'Menunggu Majelis').length }} <span class="text-xs font-normal text-slate-400">Berkas</span>
          </div>
        </Card>
        <Card title="Telah Disetujui" subtitle="Siap pelaksanaan">
          <div class="text-3xl font-bold text-emerald-400 mt-1">
            {{ sacramentRequests.filter(r => r.status === 'Disetujui').length }} <span class="text-xs font-normal text-slate-400">Berkas</span>
          </div>
        </Card>
        <Card title="Selesai & Terbit" subtitle="Dokumen resmi dicetak">
          <div class="text-3xl font-bold text-sky-400 mt-1">
            {{ sacramentRequests.filter(r => r.status === 'Selesai Terbit').length }} <span class="text-xs font-normal text-slate-400">Surat</span>
          </div>
        </Card>
      </div>

      <!-- Inbox Table -->
      <Card title="Antrean Permohonan Pelayanan Sakramen" subtitle="Daftar berkas masuk dari jemaat cabang">
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-3">No. Tiket</th>
                <th class="p-3">Layanan Sakramen</th>
                <th class="p-3">Pemohon / Calon</th>
                <th class="p-3">Rencana Tanggal</th>
                <th class="p-3">Pelayan / Pendeta</th>
                <th class="p-3">Status Berkas</th>
                <th class="p-3 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
              <tr
                v-for="item in filteredRequests"
                :key="item.ticketId"
                class="hover:bg-slate-800/40 transition-colors"
              >
                <td class="p-3 font-mono text-slate-400">{{ item.ticketId }}</td>
                <td class="p-3 font-semibold text-white">{{ item.type }}</td>
                <td class="p-3">
                  <p class="text-slate-200">{{ item.applicant }}</p>
                  <p class="text-[10px] text-slate-400 font-mono">{{ item.phone }}</p>
                </td>
                <td class="p-3 text-sky-300 font-mono">{{ item.plannedDate }}</td>
                <td class="p-3 text-slate-300">{{ item.minister }}</td>
                <td class="p-3">
                  <span
                    :class="[
                      'px-2.5 py-1 rounded-full text-[10px] font-bold border',
                      item.status === 'Disetujui'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : item.status === 'Menunggu Majelis'
                        ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                        : 'bg-sky-500/15 text-sky-300 border-sky-500/30'
                    ]"
                  >
                    {{ item.status }}
                  </span>
                </td>
                <td class="p-3 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <button
                      v-if="item.status === 'Menunggu Majelis'"
                      @click="approveRequest(item)"
                      title="Setujui Permohonan"
                      class="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-[11px] font-semibold cursor-pointer"
                    >
                      ✓ Setujui
                    </button>
                    <button
                      @click="openCertificateModal(item)"
                      title="Lihat Draf Surat / Sertifikat"
                      class="px-2.5 py-1 rounded-lg bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-500/30 text-[11px] font-medium flex items-center gap-1 cursor-pointer"
                    >
                      <span>📄 Draf Sertifikat</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <!-- Modal Draf Surat / Sertifikat Resmi -->
      <div
        v-if="previewCert"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/75 backdrop-blur-sm p-4"
      >
        <div class="bg-slate-900 border border-amber-500/40 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="font-bold text-white text-base flex items-center gap-2">
              <span class="text-amber-400">📜</span> Draf Dokumen Resmi Gereja
            </h3>
            <button @click="previewCert = null" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <!-- Formal Paper Mockup -->
          <div class="bg-slate-950 border border-amber-500/30 rounded-xl p-6 text-center space-y-4 shadow-inner relative overflow-hidden font-serif">
            <!-- Kop Gereja -->
            <div class="border-b-2 border-amber-500/40 pb-3">
              <h2 class="text-lg font-extrabold text-amber-300 tracking-wider">GEREJA GRACEPOINT INDONESIA</h2>
              <p class="text-[11px] text-slate-400 font-sans tracking-wide">KANTOR SEKRETARIAT PENGURUS CABANG RESMI</p>
              <p class="text-[10px] text-slate-500 font-mono mt-0.5">No. Dokumen: {{ previewCert.ticketId }}/DOC/SKR/2026</p>
            </div>

            <div class="py-2 space-y-2">
              <h3 class="text-base font-bold text-white uppercase tracking-widest text-decoration-underline">
                SURAT KETERANGAN {{ previewCert.type.toUpperCase() }}
              </h3>
              <p class="text-xs text-slate-300 font-sans leading-relaxed">
                Menerangkan dengan sesungguhnya bahwa nama jemaat tertera di bawah ini telah terdaftar dan diverifikasi untuk pelayanan sakramen:
              </p>
              <div class="my-3 p-3 bg-slate-900/80 rounded-lg border border-slate-800 font-sans text-xs">
                <p class="font-bold text-amber-300 text-sm">{{ previewCert.applicant }}</p>
                <p class="text-slate-400 mt-1">Tanggal Pelaksanaan: <span class="text-white font-medium">{{ previewCert.plannedDate }}</span></p>
                <p class="text-slate-400">Pelayan Firman: <span class="text-white font-medium">{{ previewCert.minister }}</span></p>
              </div>
            </div>

            <!-- Tanda Tangan & QR Stamp -->
            <div class="flex items-center justify-between pt-3 border-t border-slate-800 text-[10px] font-sans text-slate-400">
              <div class="text-left">
                <p>Terverifikasi Sistem:</p>
                <p class="font-bold text-emerald-400">STATUS: {{ previewCert.status.toUpperCase() }}</p>
              </div>
              <div class="text-right">
                <p>GracePoint Church Secretary</p>
                <p class="font-mono text-amber-400/80">E-Signature Ver. 2.4</p>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-between pt-2">
            <span class="text-xs text-slate-400 font-sans">Format cetak siap diekspor ke PDF / Printer.</span>
            <div class="flex gap-2">
              <button
                @click="previewCert = null"
                class="px-4 py-2 border border-slate-700 text-xs text-slate-400 hover:text-white rounded-xl cursor-pointer"
              >
                Tutup
              </button>
              <button
                @click="previewCert = null"
                class="px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-amber-500/20 cursor-pointer"
              >
                🖨️ Cetak Surat Keterangan
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </ChurchAdminLayout>
</template>
