<script setup>
import { ref, computed } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// State Pencarian & Filter
const searchQuery = ref('')
const selectedSector = ref('all')
const selectedStatus = ref('all')
const isAddModalOpen = ref(false)

// Mock Data Jemaat Cabang
const members = ref([
  {
    id: 'JM-001',
    name: 'Budi Santoso',
    gender: 'L',
    phone: '081234567890',
    familyRole: 'Kepala Keluarga',
    sector: 'Sektor 1 - Melati',
    birthdate: '1985-09-26', // Ultah pekan ini
    statusBaptis: 'Sudah Baptis & Sidi',
    attendanceStatus: 'Aktif',
    lastAttended: '2026-09-20'
  },
  {
    id: 'JM-002',
    name: 'Maria Anggraini',
    gender: 'P',
    phone: '081298765432',
    familyRole: 'Istri',
    sector: 'Sektor 1 - Melati',
    birthdate: '1988-04-12',
    statusBaptis: 'Sudah Baptis & Sidi',
    attendanceStatus: 'Aktif',
    lastAttended: '2026-09-20'
  },
  {
    id: 'JM-003',
    name: 'David Wijaya',
    gender: 'L',
    phone: '081344556677',
    familyRole: 'Pemuda',
    sector: 'Sektor 2 - Mawar',
    birthdate: '2001-09-25', // Ultah pekan ini
    statusBaptis: 'Sudah Baptis',
    attendanceStatus: 'Perhatian Khusus', // Pasif > 3 pekan
    lastAttended: '2026-08-30'
  },
  {
    id: 'JM-004',
    name: 'Yohanes Kristianto',
    gender: 'L',
    phone: '081577889900',
    familyRole: 'Kepala Keluarga',
    sector: 'Sektor 3 - Anggrek',
    birthdate: '1979-11-03',
    statusBaptis: 'Sudah Baptis & Sidi',
    attendanceStatus: 'Aktif',
    lastAttended: '2026-09-20'
  },
  {
    id: 'JM-005',
    name: 'Ruth Natalia',
    gender: 'P',
    phone: '081711223344',
    familyRole: 'Pemudi',
    sector: 'Sektor 2 - Mawar',
    birthdate: '2003-01-19',
    statusBaptis: 'Sudah Baptis',
    attendanceStatus: 'Perhatian Khusus', // Pasif > 3 pekan
    lastAttended: '2026-08-23'
  },
  {
    id: 'JM-006',
    name: 'Hendra Setiawan',
    gender: 'L',
    phone: '081822334455',
    familyRole: 'Kepala Keluarga',
    sector: 'Sektor 4 - Kenanga',
    birthdate: '1982-09-28', // Ultah pekan ini
    statusBaptis: 'Sudah Baptis & Sidi',
    attendanceStatus: 'Aktif',
    lastAttended: '2026-09-20'
  }
])

// Form Tambah Jemaat Baru
const newMember = ref({
  name: '',
  gender: 'L',
  phone: '',
  familyRole: 'Kepala Keluarga',
  sector: 'Sektor 1 - Melati',
  birthdate: '',
  statusBaptis: 'Sudah Baptis & Sidi'
})

// Filter Data
const filteredMembers = computed(() => {
  return members.value.filter(m => {
    const matchQuery = m.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                       m.phone.includes(searchQuery.value) ||
                       m.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchSector = selectedSector.value === 'all' || m.sector === selectedSector.value
    const matchStatus = selectedStatus.value === 'all' || m.attendanceStatus === selectedStatus.value
    return matchQuery && matchSector && matchStatus
  })
})

// Jemaat yang berulang tahun pekan ini (23 - 30 Sept)
const birthdayThisWeek = computed(() => {
  return members.value.filter(m => {
    return ['JM-001', 'JM-003', 'JM-006'].includes(m.id)
  })
})

// Jemaat pasif (> 3 minggu tidak absen)
const inactiveAlerts = computed(() => {
  return members.value.filter(m => m.attendanceStatus === 'Perhatian Khusus')
})

const sendWhatsApp = (phone, name, type = 'greeting') => {
  let msg = ''
  if (type === 'birthday') {
    msg = `Shalom ${name}, segenap Gembala & Majelis Jemaat GracePoint mengucapkan Selamat Ulang Tahun! Kiranya kasih karunia dan damai sejahtera Kristus senantiasa menyertai langkah hidup Saudara. Tuhan Yesus Memberkati! 🎂🎉`
  } else if (type === 'pastoral') {
    msg = `Shalom ${name}, kami dari tim penggembalaan GracePoint rindu menanyakan kabar Saudara. Apakah ada pokok doa yang bisa kami dukung dalam doa minggu ini? Tuhan Yesus menyertai selalu.`
  } else {
    msg = `Shalom ${name}, ini pesan resmi dari sekretariat Admin GracePoint.`
  }
  const cleanPhone = phone.replace(/^0/, '62')
  window.open(`https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`, '_blank')
}

const handleAddMember = () => {
  if (!newMember.value.name) return
  const newId = `JM-00${members.value.length + 1}`
  members.value.unshift({
    id: newId,
    name: newMember.value.name,
    gender: newMember.value.gender,
    phone: newMember.value.phone,
    familyRole: newMember.value.familyRole,
    sector: newMember.value.sector,
    birthdate: newMember.value.birthdate,
    statusBaptis: newMember.value.statusBaptis,
    attendanceStatus: 'Aktif',
    lastAttended: '2026-09-20'
  })
  isAddModalOpen.value = false
  newMember.value = {
    name: '',
    gender: 'L',
    phone: '',
    familyRole: 'Kepala Keluarga',
    sector: 'Sektor 1 - Melati',
    birthdate: '',
    statusBaptis: 'Sudah Baptis & Sidi'
  }
}
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">
      
      <!-- Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-amber-400 font-bold">CRM & DATABASE JEMAAT</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Manajemen Jemaat & Rayon Cabang
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Kelola data induk warga jemaat cabang, pantau keaktifan kehadiran, dan jangkau jemaat secara pastoral.
          </p>
        </div>

        <div class="flex items-center gap-3">
          <button
            @click="isAddModalOpen = true"
            class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            <span>Tambah Jemaat Baru</span>
          </button>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Total Anggota" subtitle="Jiwa terdaftar">
          <div class="text-3xl font-bold text-amber-400 mt-1">{{ members.length }} <span class="text-xs font-normal text-slate-400">Jiwa</span></div>
        </Card>
        <Card title="Jemaat Aktif" subtitle="Hadir bulan ini">
          <div class="text-3xl font-bold text-emerald-400 mt-1">
            {{ members.filter(m => m.attendanceStatus === 'Aktif').length }} <span class="text-xs font-normal text-slate-400">Jiwa</span>
          </div>
        </Card>
        <Card title="Ulang Tahun Pekan Ini" subtitle="23 - 30 September">
          <div class="text-3xl font-bold text-sky-400 mt-1">{{ birthdayThisWeek.length }} <span class="text-xs font-normal text-slate-400">Jemaat</span></div>
        </Card>
        <Card title="Perlu Perkunjungan" subtitle="Pasif > 3 pekan">
          <div class="text-3xl font-bold text-rose-400 mt-1">{{ inactiveAlerts.length }} <span class="text-xs font-normal text-slate-400">Jiwa</span></div>
        </Card>
      </div>

      <!-- Dual Attention Panel: Ulang Tahun & Deteksi Pasif -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5" id="ulang-tahun">
        <!-- Birthday Reminder Card -->
        <div class="bg-gradient-to-br from-slate-900/90 to-slate-950/90 border border-sky-500/30 rounded-2xl p-5 shadow-xl">
          <div class="flex items-center justify-between mb-3 border-b border-sky-500/20 pb-2.5">
            <div class="flex items-center gap-2">
              <span class="text-xl">🎂</span>
              <h3 class="font-bold text-white text-sm">Ulang Tahun Jemaat Pekan Ini</h3>
            </div>
            <span class="px-2 py-0.5 text-[10px] font-bold bg-sky-500/20 text-sky-300 rounded-md border border-sky-500/40">
              Perhatian Gembala
            </span>
          </div>
          <div class="space-y-2.5">
            <div
              v-for="b in birthdayThisWeek"
              :key="b.id"
              class="flex items-center justify-between p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-sky-500/40 transition-colors"
            >
              <div>
                <p class="font-semibold text-white text-xs">{{ b.name }} ({{ b.sector }})</p>
                <p class="text-[11px] text-slate-400">Tgl Lahir: {{ b.birthdate }} • {{ b.familyRole }}</p>
              </div>
              <button
                @click="sendWhatsApp(b.phone, b.name, 'birthday')"
                class="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-[11px] font-medium flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <span>💬 Kirim WA Ultah</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Pastoral Alert Card -->
        <div class="bg-gradient-to-br from-slate-900/90 to-slate-950/90 border border-rose-500/30 rounded-2xl p-5 shadow-xl">
          <div class="flex items-center justify-between mb-3 border-b border-rose-500/20 pb-2.5">
            <div class="flex items-center gap-2">
              <span class="text-xl">⚠️</span>
              <h3 class="font-bold text-white text-sm">Early Warning: Jemaat Pasif</h3>
            </div>
            <span class="px-2 py-0.5 text-[10px] font-bold bg-rose-500/20 text-rose-300 rounded-md border border-rose-500/40">
              Absen > 3 Minggu
            </span>
          </div>
          <div class="space-y-2.5">
            <div
              v-for="m in inactiveAlerts"
              :key="m.id"
              class="flex items-center justify-between p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-rose-500/40 transition-colors"
            >
              <div>
                <p class="font-semibold text-white text-xs">{{ m.name }} ({{ m.sector }})</p>
                <p class="text-[11px] text-rose-300/80">Terakhir Hadir: {{ m.lastAttended }}</p>
              </div>
              <button
                @click="sendWhatsApp(m.phone, m.name, 'pastoral')"
                class="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 text-[11px] font-medium flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <span>🤝 Sapa & Konseling</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Member Table Filter & List -->
      <Card title="Daftar Induk Warga Jemaat" subtitle="Filter dan cari data jemaat cabang secara lengkap">
        <!-- Filter Controls -->
        <div class="flex flex-col sm:flex-row gap-3 items-center justify-between pt-2 pb-4">
          <div class="relative w-full sm:w-72">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Cari nama, no HP, atau ID..."
              class="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
            />
          </div>

          <div class="flex items-center gap-2.5 w-full sm:w-auto">
            <select
              v-model="selectedSector"
              class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-amber-400 cursor-pointer"
            >
              <option value="all">Semua Sektor / Rayon</option>
              <option value="Sektor 1 - Melati">Sektor 1 - Melati</option>
              <option value="Sektor 2 - Mawar">Sektor 2 - Mawar</option>
              <option value="Sektor 3 - Anggrek">Sektor 3 - Anggrek</option>
              <option value="Sektor 4 - Kenanga">Sektor 4 - Kenanga</option>
            </select>

            <select
              v-model="selectedStatus"
              class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-amber-400 cursor-pointer"
            >
              <option value="all">Semua Keaktifan</option>
              <option value="Aktif">Aktif</option>
              <option value="Perhatian Khusus">Perhatian Khusus</option>
            </select>
          </div>
        </div>

        <!-- Table Responsive -->
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-3">ID Jemaat</th>
                <th class="p-3">Nama Lengkap</th>
                <th class="p-3">Sektor / Rayon</th>
                <th class="p-3">Peran Keluarga</th>
                <th class="p-3">Status Sakramen</th>
                <th class="p-3">Kehadiran</th>
                <th class="p-3 text-right">Aksi Cepat</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
              <tr
                v-for="m in filteredMembers"
                :key="m.id"
                class="hover:bg-slate-800/40 transition-colors"
              >
                <td class="p-3 font-mono text-slate-400">{{ m.id }}</td>
                <td class="p-3">
                  <div class="flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-full bg-amber-500/20 text-amber-300 font-bold flex items-center justify-center text-[11px] border border-amber-500/30">
                      {{ m.name.charAt(0) }}
                    </div>
                    <div>
                      <p class="font-semibold text-white">{{ m.name }}</p>
                      <p class="text-[10px] text-slate-400">{{ m.phone }}</p>
                    </div>
                  </div>
                </td>
                <td class="p-3 text-slate-300">{{ m.sector }}</td>
                <td class="p-3">
                  <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                    {{ m.familyRole }}
                  </span>
                </td>
                <td class="p-3">
                  <span class="text-[11px] text-sky-300">{{ m.statusBaptis }}</span>
                </td>
                <td class="p-3">
                  <span
                    :class="[
                      'px-2 py-0.5 rounded-full text-[10px] font-bold border',
                      m.attendanceStatus === 'Aktif'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                    ]"
                  >
                    {{ m.attendanceStatus }}
                  </span>
                </td>
                <td class="p-3 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <button
                      @click="sendWhatsApp(m.phone, m.name)"
                      title="Hubungi WhatsApp"
                      class="p-1.5 rounded-lg bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 border border-emerald-500/30 transition-all cursor-pointer"
                    >
                      <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <!-- Modal Tambah Jemaat Baru -->
      <div
        v-if="isAddModalOpen"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      >
        <div class="bg-slate-900 border border-amber-500/30 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span class="text-amber-400">👤</span> Tambah Data Jemaat Baru
            </h3>
            <button @click="isAddModalOpen = false" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <form @submit.prevent="handleAddMember" class="space-y-3.5">
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Nama Lengkap Sesuai KTP *</label>
              <input
                v-model="newMember.name"
                required
                type="text"
                placeholder="Contoh: Samuel Alexander"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Jenis Kelamin</label>
                <select
                  v-model="newMember.gender"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="L">Laki-laki</option>
                  <option value="P">Perempuan</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">No. WhatsApp</label>
                <input
                  v-model="newMember.phone"
                  type="text"
                  placeholder="0812xxxx"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Peran dalam Keluarga</label>
                <select
                  v-model="newMember.familyRole"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Kepala Keluarga">Kepala Keluarga</option>
                  <option value="Istri">Istri</option>
                  <option value="Pemuda / Pemudi">Pemuda / Pemudi</option>
                  <option value="Anak">Anak</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Sektor / Rayon</label>
                <select
                  v-model="newMember.sector"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Sektor 1 - Melati">Sektor 1 - Melati</option>
                  <option value="Sektor 2 - Mawar">Sektor 2 - Mawar</option>
                  <option value="Sektor 3 - Anggrek">Sektor 3 - Anggrek</option>
                  <option value="Sektor 4 - Kenanga">Sektor 4 - Kenanga</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Tanggal Lahir</label>
                <input
                  v-model="newMember.birthdate"
                  type="date"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Status Rohani</label>
                <select
                  v-model="newMember.statusBaptis"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Sudah Baptis & Sidi">Sudah Baptis & Sidi</option>
                  <option value="Sudah Baptis">Sudah Baptis</option>
                  <option value="Belum Baptis">Belum Baptis (Simpatisan)</option>
                </select>
              </div>
            </div>

            <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                @click="isAddModalOpen = false"
                class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
              >
                Batal
              </button>
              <button
                type="submit"
                class="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs cursor-pointer shadow-lg shadow-amber-500/20"
              >
                Simpan Jemaat
              </button>
            </div>
          </form>
        </div>
      </div>

    </div>
  </ChurchAdminLayout>
</template>
