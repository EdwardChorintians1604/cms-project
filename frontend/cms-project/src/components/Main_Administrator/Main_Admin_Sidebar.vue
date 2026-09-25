<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useSidebar } from '@/composables/useSidebar'

// PENTING: composable useSidebar harus expose state `isSidebarOpen` (ref boolean),
// bukan cuma fungsi toggleSidebar. Kalau belum ada, lihat catatan di bawah jawaban.
const { isSidebarOpen, toggleSidebar, closeSidebar } = useSidebar()

// Collapsible state for each category
const openSections = ref({
  0: true, // Dashboard & Monitoring
  1: true, // Manajemen Cabang Gereja
  2: true, // Manajemen Data Jemaat
  3: true, // Manajemen Keuangan Gereja
  4: true, // Infrastruktur & Database
  5: true, // Hak Akses & Keamanan
  6: true  // Pengaturan (Options)
})

const toggleSection = (idx) => {
  openSections.value[idx] = !openSections.value[idx]
}

// Menu khusus Admin Utama (Superadmin Platform Infrastructure)
const menuSections = [
  {
    title: 'Dashboard & Monitoring',
    items: [
      { name: 'Console System Admin', path: '/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', badge: 'Live', badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' },
      { name: 'Kalender & Agenda Kegiatan', path: '/main_admin_calendar', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z', badge: 'Agenda', badgeColor: 'bg-amber-500/15 text-amber-300 border-amber-500/30' },
      { name: 'Statistika Platform', path: '/dashboard#analytics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' }
    ]
  },
  {
    title: 'Manajemen Cabang Gereja',
    items: [
      { name: 'Manajemen Data Gereja', path: '/data-gereja', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4', badge: 'Induk', badgeColor: 'bg-amber-500/15 text-amber-300 border-amber-500/30' },
      { name: 'Daftar Cabang Gereja', path: '/cabang-gereja', icon: 'M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z', badge: 'CRUD', badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' },
      { name: 'Pendaftaran Gereja Baru', path: '/register-gereja', icon: 'M12 4v16m8-8H4' },
      { name: 'Akun Admin Cabang', path: '/manajemen-admin-cabang', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' }
    ]
  },
  {
    title: 'Manajemen Data Jemaat',
    items: [
      { name: 'Manajemen Biodata Jemaat', path: '/data-pengguna', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' }
    ]
  }, 
  {
    title: 'Manajemen Keuangan Gereja',
    items: [
      { name: 'Pemasukan Gereja', path: '/pemasukan-gereja', icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
      { name: 'Pengeluaran Gereja', path: '/pengeluaran-gereja', icon: 'M15 12H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z' },
      { name: 'Grafik Keuangan Gereja', path: '/grafik-gereja', icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z' }
    ]
  }, 
  {
    title: 'Infrastruktur & Database',
    items: [
      { name: 'Server PostgreSQL', path: '/server-postgresql', icon: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s-8 1.79 8-4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4', badge: 'Active', badgeColor: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30' },
      { name: 'Backup & Restore Server', path: '/backup-database', icon: 'M8 4H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4-1v8m0 0l3-3m-3 3L9 8', badge: 'SQL', badgeColor: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30' }
    ]
  },
  {
    title: 'Hak Akses & Keamanan',
    items: [
      { name: 'Audit Log & Keamanan', path: '/it-audit', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
      { name: 'Deteksi Ancaman Luar-Dalam', path: '/security-view', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' }
    ]
  },
  {
    title: 'Pengaturan (Options)',
    items: [
      { name: 'Pengaturan', path: '/church-settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543-.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543-.826-3.31zM12 15a3 3 0 100-6 3 3 0 000 6z' }, 
      { name: 'Theme & Tampilan', path: '/theme-settings', icon: 'M7 21a4 4 0 01-4-4 5 5 0 013-4.5V11a7 7 0 1114 0v1.5a5 5 0 013 4.5 4 4 0 01-4 4h-2a2 2 0 01-2-2v-1a1 1 0 00-1-1h-2a1 1 0 00-1 1v1a2 2 0 01-2 2H7z' }, 
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
          <span class="text-amber-300 font-extrabold tracking-widest text-[11px] uppercase">SUPERADMIN CONSOLE</span>
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
        GracePoint Infrastructure Console &copy; 2026
      </div>
    </div>

  </aside>
</template>

<style scoped>
/* Reset any Bootstrap pollution */
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