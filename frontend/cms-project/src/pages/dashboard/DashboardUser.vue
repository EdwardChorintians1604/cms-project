<script setup>
import { computed } from 'vue'
import UserLayout from '@/layouts/UserLayout.vue'
import Card from '@/components/Card.vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const user = computed(() => authStore.user.value)
</script>

<template>
  <UserLayout>
    <div class="space-y-6 max-w-7xl mx-auto p-4 sm:p-6">
      <div>
        <p class="text-amber-400 text-xs uppercase tracking-[0.2em] font-semibold">Portal Jemaat</p>
        <h1 class="text-2xl font-bold text-white mt-1">Selamat datang, {{ user?.full_name || 'Jemaat' }}</h1>
        <p class="text-slate-400 text-sm mt-1">Ringkasan aktivitas, jadwal ibadah, dan warta jemaat minggu ini.</p>
      </div>

      <section class="relative overflow-hidden rounded-2xl border border-amber-400/25 bg-gradient-to-br from-[#17274b] via-[#101c3a] to-[#0b1428] p-6 sm:p-8">
        <div class="absolute -right-16 -top-20 w-64 h-64 rounded-full border border-amber-400/10"></div>
        <div class="absolute right-10 bottom-0 text-8xl text-amber-300/10 font-serif select-none">✝</div>
        <div class="relative max-w-2xl">
          <p class="text-xs uppercase tracking-[0.2em] text-sky-300 font-semibold">Perjalanan iman minggu ini</p>
          <h2 class="text-2xl sm:text-3xl font-serif font-bold text-white mt-2">Hadir, bertumbuh, dan melayani.</h2>
          <p class="text-sm text-slate-300 mt-3 leading-relaxed">Temukan jadwal ibadah, warta terbaru, dan layanan gereja yang dapat Anda akses dari satu beranda.</p>
          <div class="flex flex-wrap gap-3 mt-5">
            <RouterLink to="/berita-jemaat" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-amber-400 text-slate-950 text-xs font-bold hover:bg-amber-300 transition">Baca warta terbaru <span>→</span></RouterLink>
            <a href="#agenda" class="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border border-slate-600 text-slate-200 text-xs hover:border-amber-400 hover:text-amber-300 transition">Lihat agenda</a>
          </div>
        </div>
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <section id="profil" class="lg:col-span-2 rounded-2xl border border-amber-500/20 bg-slate-950/60 p-5">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs text-slate-400 uppercase tracking-widest">Profil terdaftar</p>
              <h2 class="text-lg font-semibold text-amber-300 mt-1">{{ user?.username || 'Akun jemaat' }}</h2>
              <p class="text-sm text-slate-300 mt-2">{{ user?.email }}</p>
              <p class="text-xs text-slate-500 mt-1">{{ user?.church_domisili || 'Gereja domisili belum diisi' }}</p>
            </div>
            <div class="w-16 h-16 rounded-full overflow-hidden border border-amber-500/30 bg-slate-900 flex items-center justify-center">
              <img v-if="user?.photo_url" :src="user.photo_url" :alt="`Foto ${user.full_name}`" class="w-full h-full object-cover" />
              <span v-else class="text-xl text-amber-300">{{ user?.full_name?.charAt(0) || 'J' }}</span>
            </div>
          </div>
        </section>
        <section class="rounded-2xl border border-slate-700 bg-slate-950/60 p-5">
          <p class="text-xs text-slate-400 uppercase tracking-widest">Status akun</p>
          <p class="text-emerald-400 font-semibold mt-2">Aktif</p>
          <p class="text-xs text-slate-500 mt-2">Akses portal jemaat tersedia.</p>
        </section>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <section id="agenda" class="lg:col-span-3 rounded-2xl border border-slate-700 bg-slate-950/60 p-5">
          <div class="flex items-center justify-between mb-4">
            <div>
              <p class="text-xs uppercase tracking-widest text-slate-400">Agenda terdekat</p>
              <h2 class="text-lg font-semibold text-white mt-1">Jadwal minggu ini</h2>
            </div>
            <span class="text-[10px] px-2 py-1 rounded-full bg-emerald-500/10 border border-emerald-400/20 text-emerald-300">Jadwal aktif</span>
          </div>
          <div class="space-y-3">
            <div class="flex gap-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <div class="w-11 h-11 rounded-lg bg-amber-500/15 text-amber-300 flex flex-col items-center justify-center flex-shrink-0"><span class="text-[10px] uppercase">Min</span><strong>14</strong></div>
              <div class="min-w-0"><h3 class="text-sm text-white font-semibold">Ibadah Raya Minggu</h3><p class="text-xs text-slate-400 mt-1">08:00 WIB · Gedung Utama</p></div>
            </div>
            <div class="flex gap-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <div class="w-11 h-11 rounded-lg bg-sky-500/15 text-sky-300 flex flex-col items-center justify-center flex-shrink-0"><span class="text-[10px] uppercase">Rab</span><strong>17</strong></div>
              <div class="min-w-0"><h3 class="text-sm text-white font-semibold">Persekutuan Doa Jemaat</h3><p class="text-xs text-slate-400 mt-1">19:00 WIB · Ruang Doa & Online</p></div>
            </div>
            <div class="flex gap-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <div class="w-11 h-11 rounded-lg bg-emerald-500/15 text-emerald-300 flex flex-col items-center justify-center flex-shrink-0"><span class="text-[10px] uppercase">Sab</span><strong>20</strong></div>
              <div class="min-w-0"><h3 class="text-sm text-white font-semibold">Komunitas Keluarga</h3><p class="text-xs text-slate-400 mt-1">16:30 WIB · Aula Pelayanan</p></div>
            </div>
          </div>
        </section>

        <section class="lg:col-span-2 rounded-2xl border border-slate-700 bg-slate-950/60 p-5">
          <p class="text-xs uppercase tracking-widest text-slate-400">Warta pilihan</p>
          <h2 class="text-lg font-semibold text-white mt-1">Yang perlu diketahui</h2>
          <div class="mt-4 space-y-4">
            <div><span class="text-[10px] text-amber-300 uppercase tracking-wider">Pengumuman</span><p class="text-sm text-slate-200 mt-1">Pendataan ulang anggota jemaat telah dibuka.</p></div>
            <div class="border-t border-slate-800 pt-4"><span class="text-[10px] text-sky-300 uppercase tracking-wider">Pelayanan</span><p class="text-sm text-slate-200 mt-1">Pendaftaran pelayanan dan komunitas tersedia minggu ini.</p></div>
          </div>
          <RouterLink to="/berita-jemaat" class="inline-block text-xs text-amber-300 hover:text-amber-200 mt-5">Lihat semua warta →</RouterLink>
        </section>
      </div>

      <section id="persembahan" class="rounded-2xl border border-slate-700 bg-slate-950/60 p-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div><p class="text-xs uppercase tracking-widest text-slate-400">Akses cepat</p><h2 class="text-lg font-semibold text-white mt-1">Layanan untuk Anda</h2></div>
          <span class="text-xs text-slate-500">Tersedia sepanjang hari</span>
        </div>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
          <RouterLink to="/berita-jemaat" class="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-400/50 transition"><span class="text-xl">📰</span><p class="text-sm text-white font-semibold mt-3">Warta jemaat</p><p class="text-[11px] text-slate-500 mt-1">Berita terbaru</p></RouterLink>
          <RouterLink to="/informasi-pelayanan" class="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-sky-400/50 transition"><span class="text-xl">🕊</span><p class="text-sm text-white font-semibold mt-3">Pelayanan</p><p class="text-[11px] text-slate-500 mt-1">Ajukan kebutuhan</p></RouterLink>
          <a href="#profil" class="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-400/50 transition"><span class="text-xl">👤</span><p class="text-sm text-white font-semibold mt-3">Profil saya</p><p class="text-[11px] text-slate-500 mt-1">Data keanggotaan</p></a>
          <a href="#doa" class="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-purple-400/50 transition"><span class="text-xl">🙏</span><p class="text-sm text-white font-semibold mt-3">Pokok doa</p><p class="text-[11px] text-slate-500 mt-1">Ruang doa pribadi</p></a>
        </div>
      </section>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card title="Total Jemaat" subtitle="Aktif terdaftar">
          <div class="text-3xl font-bold text-amber-400 mt-2">1,248</div>
        </Card>
        <Card title="Kehadiran Minggu Lalu" subtitle="Ibadah Raya 1 & 2">
          <div class="text-3xl font-bold text-emerald-400 mt-2">892</div>
        </Card>
        <Card title="Total Keluarga" subtitle="Kepala Keluarga">
          <div class="text-3xl font-bold text-sky-400 mt-2">340</div>
        </Card>
        <Card title="Pelayanan Aktif" subtitle="Tim Komunitas">
          <div class="text-3xl font-bold text-purple-400 mt-2">18</div>
        </Card>
      </div>
    </div>
  </UserLayout>
</template>
