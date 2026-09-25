<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useSidebar } from '@/composables/useSidebar'

const { isSidebarOpen, toggleSidebar, closeSidebar } = useSidebar()

// Collapsible state for each category (8 Categories)
const openSections = ref({
  0: true,  // Dashboard & Geolocation
  1: true,  // Data Jemaat & Rayon (CRM)
  2: true,  // Operasional Ibadah & Roster
  3: true,  // Presensi & Kehadiran
  4: true,  // Sakramen & Pastoral Care
  5: true,  // Keuangan & Persembahan Cabang
  6: true,  // Aset & Fasilitas Cabang
  7: false, // Publikasi & Pengaturan Cabang
})

const toggleSection = (idx) => {
  openSections.value[idx] = !openSections.value[idx]
}

// Menu khusus Admin Gereja (Church Admin Portal)
const menuSections = [
  {
    title: 'Dashboard Gereja',
    items: [
      {
        name: 'Dashboard Utama',
        path: '/dashboard-church#dashboard-utama',
        icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
        badge: 'Live', badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
      },
      {
        name: 'Statistika Cabang Gereja',
        path: '/dashboard-church#geolocation',
        icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z',
        badge: 'GPS', badgeColor: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
      }
    ]
  },
  {
    title: 'Anggota Gereja Cabang',
    items: [
      {
        name: 'Struktur Kepempinan Gereja',
        path: '/dashboard-church#dashboard-utama',
        icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
        badge: 'Live', badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
      },
      {
        name: 'Lembaga Pelayanan Cabang',
        path: '/dashboard-church#geolocation',
        icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z',
        badge: 'GPS', badgeColor: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
      }
    ]
  },
  {
    title: 'Data Jemaat',
    items: [
      {
        name: 'Database Jemaat Cabang',
        path: '/church-members',
        icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
        badge: 'CRM', badgeColor: 'bg-amber-500/15 text-amber-300 border-amber-500/30'
      },
      {
        name: 'Kartu Keluarga & Rayon Wilayah',
        path: '/church-members#keluarga',
        icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'
      },
      {
        name: 'Ulang Tahun Jemaat',
        path: '/church-members#ulang-tahun',
        icon: 'M21 15.546c-.523 0-1.046.151-1.5.454a2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-1.5-.454M9 6v2m3-2v2m3-2v2M9 3h.01M12 3h.01M15 3h.01M3 21h18M3 10h18M5 10v11h14V10',
        badge: 'Alert', badgeColor: 'bg-rose-500/15 text-rose-300 border-rose-500/30'
      },
    ]
  },
  {
    title: 'Informasi Pelayanan',
    items: [
      {
        name: 'Jadwal Ibadah dan Pelayanan Cabang',
        path: '/church-roster',
        icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z M9 14l2 2 4-4',
        badge: 'Roster', badgeColor: 'bg-purple-500/15 text-purple-300 border-purple-500/30'
      },
      {
        name: 'Jadwal Petugas Ibadah (Roster)',
        path: '/church-roster',
        icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z M9 14l2 2 4-4',
        badge: 'Roster', badgeColor: 'bg-purple-500/15 text-purple-300 border-purple-500/30'
      },
       {
        name: 'Warta & Berita Jemaat',
        path: '/berita-jemaat',
        icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z'
      },
      {
        name: 'Kalender Hari Besar Gereja',
        path: '/hari-besar',
        icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'
      },
    ]
  },
  {
    title: 'Sakramen & Pastoral Care',
    items: [
      {
        name: 'Permohonan Sakramen & Surat',
        path: '/church-sacraments',
        icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
        badge: 'Inbox', badgeColor: 'bg-sky-500/15 text-sky-300 border-sky-500/30'
      },
      {
        name: 'Pelayanan Pastoral & Doa',
        path: '/church-pastoral',
        icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
        badge: 'Privat', badgeColor: 'bg-rose-500/15 text-rose-300 border-rose-500/30'
      },
    ]
  },
  {
    title: 'Keuangan & Persembahan Cabang',
    items: [
      {
        name: 'Kasir & Input Persembahan Cepat',
        path: '/church-finance',
        icon: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
        badge: 'Kasir', badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
      },
      {
        name: 'Laporan Kas & Rekonsiliasi',
        path: '/church-finance#laporan',
        icon: 'M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z'
      },
    ]
  },
  {
    title: 'Aset & Fasilitas Cabang',
    items: [
      {
        name: 'Manajemen Inventaris & Aset',
        path: '/church-facilities',
        icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
        badge: 'Booking', badgeColor: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30'
      },
      {
        name: 'Peminjaman Ruangan & Fasilitas',
        path: '/church-facilities',
        icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
        badge: 'Booking', badgeColor: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30'
      },
      {
        name: 'Statistika Aset & Inventaris Cabang',
        path: '/church-facilities#inventaris',
        icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
      }
    ]
  },
  {
    title: 'Backup, Presensi, QR Scan',
    items: [
      {
        name: 'Scanner QR & Presensi Ibadah',
        path: '/church-attendance',
        icon: 'M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z',
        badge: 'Scan', badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
      },
      {
        name: 'Grafik Presensi Jemaat',
        path: '/church-attendance#headcount',
        icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z'
      },
      {
        name: 'Backup Data',
        path: '/church-attendance#headcount',
        icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z'
      },
    ]
  },
  {
    title: 'Pengaturan Cabang',
    items: [
      {
        name: 'Profil & Sejarah Gereja',
        path: '/sejarah-gereja',
        icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253'
      },
      {
        name: 'Pengaturan Cabang Gereja',
        path: '/church-settings',
        icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z'
      },
      {
        name: 'Titik Koordinat & Peta Cabang',
        path: '/dashboard-church#geolocation',
        icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z',
        badge: 'GPS', badgeColor: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
      },
      {
        name: 'Penerapan AI untuk Finansial',
        path: '/church-facilities',
        icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
        badge: 'Booking', badgeColor: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30'
      },
    ]
  }
]
</script>

<template>
  <!-- Backdrop: muncul saat sidebar terbuka di atas semua elemen termasuk navbar -->
  <Transition name="fade">
    <div
      v-if="isSidebarOpen"
      @click="closeSidebar"
      class="fixed inset-0 z-[55] bg-black/60 backdrop-blur-sm transition-opacity duration-300"
    ></div>
  </Transition>

  <!-- Aside: Menjangkau dari paling atas layar (top-0 h-screen z-[60]) di atas navbar -->
  <aside
    :class="[
      'w-[82vw] sm:w-72 lg:w-72 max-w-[300px] bg-[var(--theme-bg-secondary)] text-[var(--theme-text-primary)] border-r border-[var(--theme-border-soft)] p-3.5 sm:p-4 flex flex-col justify-between font-sans text-xs shadow-2xl shrink-0 backdrop-blur-xl overflow-y-auto custom-scrollbar',
      'fixed inset-y-0 left-0 top-0 z-[60] h-screen transition-transform duration-300 ease-in-out',
      isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
    ]"
  >

    <!-- Top Content Container -->
    <div class="space-y-4">

      <!-- Sidebar Header & Close Toggle -->
      <div class="flex items-center justify-between pb-3 border-b border-amber-500/20">
        <div class="flex items-center gap-2.5">
          <div class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
          </div>
          <span class="text-amber-300 font-extrabold tracking-widest text-[11px] uppercase">CHURCH ADMIN</span>
        </div>

        <button
          @click="closeSidebar"
          title="Tutup Sidebar"
          class="p-1.5 text-slate-400 hover:text-amber-300 hover:bg-amber-500/10 rounded-xl border border-slate-800 hover:border-amber-500/30 transition-all duration-200 flex items-center justify-center cursor-pointer"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
          </svg>
        </button>
      </div>

      <!-- Navigation Accordion Sections -->
      <div class="space-y-3">
        <div
          v-for="(section, sIdx) in menuSections"
          :key="sIdx"
          class="space-y-1"
        >
          <!-- Category Header Toggle -->
          <button
            @click="toggleSection(sIdx)"
            :aria-expanded="openSections[sIdx]"
            :aria-controls="`sidebar-section-${sIdx}`"
            class="w-full px-2.5 py-1.5 rounded-lg bg-slate-950/70 border border-slate-800/80 text-[10px] font-extrabold text-amber-400/90 tracking-widest uppercase transition cursor-pointer select-none group flex items-center justify-between hover:bg-slate-900 hover:text-amber-300"
          >
            <span>{{ section.title }}</span>
            <svg
              class="w-3 h-3 text-slate-500 group-hover:text-amber-400 transition-transform duration-200"
              :class="{ 'rotate-180': openSections[sIdx] }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          <!-- Category Links -->
          <Transition name="accordion">
            <div v-if="openSections[sIdx]" :id="`sidebar-section-${sIdx}`" class="space-y-0.5 pt-1 pl-1">
              <RouterLink
                v-for="(item, iIdx) in section.items"
                :key="iIdx"
                :to="item.path"
                @click="closeSidebar"
                class="group px-3 py-2 rounded-xl text-slate-300 hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-amber-500/5 hover:text-amber-300 transition-all duration-200 font-medium flex items-center justify-between leading-tight border border-transparent hover:border-amber-500/30 no-underline"
                active-class="bg-gradient-to-r from-amber-500/25 via-amber-500/10 to-transparent text-amber-300 font-bold border-l-2 border-amber-400 shadow-md shadow-amber-500/10"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <svg
                    v-if="item.icon"
                    class="w-4 h-4 text-amber-400/80 group-hover:text-amber-300 shrink-0 transition-transform group-hover:scale-110"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
                  </svg>
                  <span v-else class="w-1.5 h-1.5 rounded-full bg-amber-400/80 shrink-0 ml-1"></span>

                  <span class="truncate text-xs text-slate-200 group-hover:text-amber-300 leading-snug">{{ item.name }}</span>
                </div>

                <!-- Optional Badge -->
                <span
                  v-if="item.badge"
                  :class="['px-1.5 py-0.5 text-[9px] font-extrabold rounded-md border shrink-0 ml-1.5', item.badgeColor || 'bg-amber-500/15 text-amber-300 border-amber-500/30']"
                >
                  {{ item.badge }}
                </span>
              </RouterLink>
            </div>
          </Transition>

        </div>
      </div>

    </div>

    <!-- Bottom System Status Card -->
    <div class="pt-3 border-t border-amber-500/20 mt-4 text-xs text-slate-400 font-sans space-y-2 shrink-0">
      <div class="bg-slate-950/90 border border-slate-800/90 rounded-xl p-3 space-y-1.5 shadow-inner">
        <div class="flex items-center justify-between text-[11px]">
          <span class="text-slate-400 font-medium">PostgreSQL Server:</span>
          <span class="text-emerald-400 font-bold flex items-center gap-1.5">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Online
          </span>
        </div>
        <div class="flex items-center justify-between text-[10px] text-slate-500 font-mono">
          <span>Engine: Neon Cloud</span>
          <span>Port: 5432</span>
        </div>
      </div>

      <div class="text-center text-[10px] text-slate-500 font-medium">
        GracePoint Church Admin Portal &copy; 2026
      </div>
    </div>

  </aside>
</template>

<style scoped>
a, a:hover, a:focus, a:visited {
  text-decoration: none !important;
  color: inherit;
}

button:focus, button:focus-visible {
  outline: none !important;
  box-shadow: none !important;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(6, 9, 19, 0.8);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.35);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(245, 158, 11, 0.65);
}

.accordion-enter-active,
.accordion-leave-active {
  transition: max-height 0.25s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease;
  overflow: hidden;
}
.accordion-enter-from,
.accordion-leave-to {
  opacity: 0;
  max-height: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
