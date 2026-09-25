<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useSidebar } from '@/composables/useSidebar'

const route = useRoute()
const { isSidebarOpen, closeSidebar } = useSidebar()

// Accordion: semua section terbuka secara default
const openSections = ref({
  0: true,  // Beranda & Profil
  1: true,  // Warta & Pelayanan
  2: true,  // Komunitas & Kegiatan
  3: true,  // Informasi Gereja
})

const toggleSection = (idx) => {
  openSections.value[idx] = !openSections.value[idx]
}

const handleLinkClick = () => {
  closeSidebar()
}

const isActiveRoute = (path) => {
  const basePath = path.split('#')[0]
  if (basePath === '/dashboard-user') return route.path === '/dashboard-user'
  return route.path.startsWith(basePath)
}

// Menu khusus Jemaat — isi dapat disesuaikan user
const menuSections = [
  {
    title: 'Beranda & Profil',
    items: [
      {
        name: 'Beranda Jemaat',
        path: '/dashboard-user',
        icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
        badge: 'Live', badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
      },
      {
        name: 'Profil & Data Pribadi',
        path: '/dashboard-user#profil',
        icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
      },
      {
        name: 'Pokok Doa & Konseling',
        path: '/dashboard-user#doa',
        icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.684a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
        badge: 'Pastoral', badgeColor: 'bg-purple-500/15 text-purple-300 border-purple-500/30'
      },
    ]
  },
  {
    title: 'Warta & Pelayanan',
    items: [
      {
        name: 'Warta & Berita Jemaat',
        path: '/berita-jemaat',
        icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z',
        badge: 'Baru', badgeColor: 'bg-sky-500/15 text-sky-300 border-sky-500/30'
      },
      {
        name: 'Informasi Pelayanan',
        path: '/informasi-pelayanan',
        icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
      },
      {
        name: 'Agenda & Jadwal Ibadah',
        path: '/dashboard-user#agenda',
        icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
      },
    ]
  },
  {
    title: 'Komunitas & Kegiatan',
    items: [
      {
        name: 'Kalender Hari Besar',
        path: '/hari-besar',
        icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
        badge: 'Liturgi', badgeColor: 'bg-amber-500/15 text-amber-300 border-amber-500/30'
      },
      {
        name: 'Persembahan & Donasi',
        path: '/dashboard-user#persembahan',
        icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
      },
    ]
  },
  {
    title: 'Informasi Gereja',
    items: [
      {
        name: 'Sejarah Gereja',
        path: '/sejarah-gereja',
        icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
      },
      {
        name: 'Peta Lokasi Gereja',
        path: '/informasi-pelayanan',
        icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7'
      },
      {
        name: 'Beranda Utama Publik',
        path: '/',
        icon: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9'
      },
    ]
  },
]
</script>

<template>
  <!-- Backdrop: fixed overlay di bawah sidebar, mencakup seluruh layar -->
  <Transition name="fade">
    <div
      v-if="isSidebarOpen"
      @click="closeSidebar"
      class="fixed inset-0 z-[55] bg-black/60 backdrop-blur-sm transition-opacity duration-300"
    ></div>
  </Transition>

  <!-- Aside: Fixed overlay dari top-0 (z-[60]), mencakup navbar sepenuhnya -->
  <aside
    :class="[
      'w-[82vw] sm:w-72 max-w-[300px] bg-[var(--theme-bg-secondary)] text-[var(--theme-text-primary)] border-r border-[var(--theme-border-soft)] p-3.5 sm:p-4 flex flex-col justify-between font-sans text-xs shadow-2xl shrink-0 backdrop-blur-xl overflow-y-auto custom-scrollbar',
      'fixed inset-y-0 left-0 top-0 z-[60] h-screen transition-transform duration-300 ease-in-out',
      isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
    ]"
  >

    <!-- Top Content Container -->
    <div class="space-y-4">

      <!-- Sidebar Header & Close -->
      <div class="flex items-center justify-between pb-3 border-b border-amber-500/20">
        <div class="flex items-center gap-2.5">
          <div class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
          </div>
          <span class="text-amber-300 font-extrabold tracking-widest text-[11px] uppercase font-serif">PORTAL JEMAAT</span>
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
          <!-- Section Header Toggle -->
          <button
            @click="toggleSection(sIdx)"
            :aria-expanded="openSections[sIdx]"
            class="w-full px-2.5 py-1.5 rounded-lg bg-slate-950/70 border border-slate-800/80 text-[10px] font-extrabold text-amber-400/90 tracking-widest uppercase transition cursor-pointer select-none group flex items-center justify-between hover:bg-slate-900 hover:text-amber-300"
          >
            <span>{{ section.title }}</span>
            <svg
              class="w-3 h-3 text-slate-500 group-hover:text-amber-400 transition-transform duration-200"
              :class="{ 'rotate-180': openSections[sIdx] }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          <!-- Section Links -->
          <Transition name="accordion">
            <div v-if="openSections[sIdx]" class="space-y-0.5 pt-1 pl-1">
              <RouterLink
                v-for="(item, iIdx) in section.items"
                :key="iIdx"
                :to="item.path"
                @click="handleLinkClick"
                class="group px-3 py-2 rounded-xl transition-all duration-200 font-medium flex items-center justify-between leading-tight border border-transparent hover:border-amber-500/30 no-underline"
                :class="isActiveRoute(item.path)
                  ? 'bg-gradient-to-r from-amber-500/25 via-amber-500/10 to-transparent text-amber-300 font-bold border-l-2 border-amber-400 shadow-md shadow-amber-500/10'
                  : 'text-slate-300 hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-amber-500/5 hover:text-amber-300'"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <svg
                    v-if="item.icon"
                    class="w-4 h-4 text-amber-400/80 group-hover:text-amber-300 shrink-0 transition-transform group-hover:scale-110"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
                  </svg>
                  <span class="truncate text-xs text-slate-200 group-hover:text-amber-300 leading-snug">{{ item.name }}</span>
                </div>

                <!-- Badge -->
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

      <!-- Widget Info Ibadah -->
      <div class="pt-2 border-t border-slate-800/80">
        <div class="p-3 bg-slate-950/70 border border-amber-500/20 rounded-xl space-y-1.5 text-[10px]">
          <p class="text-[10px] font-extrabold text-amber-400/90 tracking-widest uppercase mb-2">⛪ Jadwal Ibadah</p>
          <div class="flex items-center justify-between text-amber-300 font-semibold">
            <span>Ibadah Raya Minggu</span>
            <span class="text-slate-100 font-mono">08:00 &amp; 17:00</span>
          </div>
          <div class="flex items-center justify-between text-slate-300 border-t border-slate-800/80 pt-1.5">
            <span>Persekutuan Doa</span>
            <span class="text-slate-200 font-mono">Rabu 19:00</span>
          </div>
          <div class="flex items-center justify-between text-slate-400 border-t border-slate-800/80 pt-1.5">
            <span>📞 Sekretariat</span>
            <span class="text-slate-300 font-semibold font-mono">(021) 555-0199</span>
          </div>
        </div>
      </div>

    </div>

    <!-- Bottom Status Card -->
    <div class="pt-3 border-t border-amber-500/20 mt-4 text-xs text-slate-400 font-sans space-y-2 shrink-0">
      <div class="bg-slate-950/90 border border-slate-800/90 rounded-xl p-3 space-y-1.5 shadow-inner">
        <div class="flex items-center justify-between text-[11px]">
          <span class="text-slate-400 font-medium">Status Portal:</span>
          <span class="text-emerald-400 font-bold flex items-center gap-1.5">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Aktif &amp; Online
          </span>
        </div>
        <div class="flex items-center justify-between text-[10px] text-slate-500 font-mono">
          <span>GracePoint Jemaat</span>
          <span>v1.0</span>
        </div>
      </div>

      <div class="text-center text-[10px] text-slate-500 font-medium">
        GracePoint Church Portal &copy; 2026
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

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: rgba(6, 9, 19, 0.8); }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(245, 158, 11, 0.35); border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(245, 158, 11, 0.65); }

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
