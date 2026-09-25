<script setup>
import { RouterLink } from 'vue-router'
import { useSidebar } from '@/composables/useSidebar'

const { toggleSidebar, closeSidebar } = useSidebar()
</script>

<template>
  <aside class="nav-sidebar">
    <!-- Header Sidebar dengan Tombol Sembunyikan -->
    <div class="flex items-center justify-between pb-2.5 border-b border-amber-500/25">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
        <span class="text-amber-300 font-bold tracking-widest text-[11px] uppercase">NAVIGASI GEREJA</span>
      </div>
      <button 
        @click="closeSidebar" 
        title="Sembunyikan Sidebar"
        class="p-1 text-slate-300 hover:text-amber-300 hover:bg-slate-800 rounded border border-amber-500/30 transition flex items-center justify-center cursor-pointer"
      >
        <i class="bi bi-chevron-double-left text-xs"></i>
      </button>
    </div>

    <!-- Menu Section: Utama -->
    <div class="space-y-1">
      <span class="px-1 text-[10px] font-bold text-amber-300/90 tracking-widest uppercase">Utama</span>
      <RouterLink 
        to="/" 
        @click="closeSidebar"
        class="sidebar-link px-3 py-2 rounded-lg text-white hover:bg-amber-500/15 hover:text-amber-300 transition-all duration-200 font-medium flex items-center gap-2 leading-tight"
        active-class="bg-amber-500/20 text-amber-300 font-semibold border-l-4 border-amber-400 shadow-sm"
      >
        <i class="bi bi-house-door text-amber-400 text-base flex-shrink-0"></i>
        <span class="truncate">Dashboard Utama</span>
      </RouterLink>
    </div>

    <!-- Menu Section: Navigasi Utama -->
    <div class="space-y-1 pt-2 border-t border-slate-800/80">
      <span class="px-1 text-[10px] font-bold text-amber-300/90 tracking-widest uppercase">Navigasi Utama</span>

      <RouterLink 
        to="/informasi-pelayanan" 
        @click="closeSidebar"
        class="sidebar-link px-3 py-2 rounded-lg text-white hover:bg-amber-500/15 hover:text-amber-300 transition-all duration-200 font-medium flex items-center gap-2 leading-tight"
        active-class="bg-amber-500/20 text-amber-300 font-semibold border-l-4 border-amber-400 shadow-sm"
      >
        <i class="bi bi-list-ul text-amber-400 text-base flex-shrink-0"></i>
        <span class="truncate">Informasi Pelayanan</span>
      </RouterLink>

      <RouterLink 
        to="/berita-jemaat" 
        @click="closeSidebar"
        class="sidebar-link px-3 py-2 rounded-lg text-white hover:bg-amber-500/15 hover:text-amber-300 transition-all duration-200 font-medium flex items-center gap-2 leading-tight"
        active-class="bg-amber-500/20 text-amber-300 font-semibold border-l-4 border-amber-400 shadow-sm"
      >
        <i class="bi bi-newspaper text-amber-400 text-base flex-shrink-0"></i>
        <span class="truncate">Berita Jemaat</span>
      </RouterLink>

      <RouterLink 
        to="/hari-besar" 
        @click="closeSidebar"
        class="sidebar-link px-3 py-2 rounded-lg text-white hover:bg-amber-500/15 hover:text-amber-300 transition-all duration-200 font-medium flex items-center gap-2 leading-tight"
        active-class="bg-amber-500/20 text-amber-300 font-semibold border-l-4 border-amber-400 shadow-sm"
      >
        <i class="bi bi-calendar-event text-amber-400 text-base flex-shrink-0"></i>
        <span class="truncate">Hari Besar Gereja</span>
      </RouterLink>

      <RouterLink 
        to="/sejarah-gereja" 
        @click="closeSidebar"
        class="sidebar-link px-3 py-2 rounded-lg text-white hover:bg-amber-500/15 hover:text-amber-300 transition-all duration-200 font-medium flex items-center justify-between gap-2 leading-tight group"
        active-class="bg-amber-500/20 text-amber-300 font-semibold border-l-4 border-amber-400 shadow-sm"
        title="Search Engine Sejarah & Cikal Bakal Gereja-Gereja di Indonesia"
      >
        <div class="flex items-center gap-2 min-w-0">
          <i class="bi bi-compass text-amber-400 text-base flex-shrink-0 group-hover:rotate-45 transition-transform duration-300"></i>
          <span class="truncate">Sejarah Gereja</span>
        </div>
        <span class="text-[9px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 shrink-0">Search</span>
      </RouterLink>

      <RouterLink 
        to="/peta-gereja" 
        @click="closeSidebar"
        class="sidebar-link px-3 py-2 rounded-lg text-white hover:bg-amber-500/15 hover:text-amber-300 transition-all duration-200 font-medium flex items-center justify-between gap-2 leading-tight group"
        active-class="bg-amber-500/20 text-amber-300 font-semibold border-l-4 border-amber-400 shadow-sm"
        title="Peta Lokasi Gereja"
      >
        <div class="flex items-center gap-2 min-w-0">
          <i class="bi bi-geo-alt-fill text-emerald-400 text-base flex-shrink-0"></i>
          <span class="truncate">Peta Lokasi (GMaps)</span>
        </div>
        <span class="text-[9px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0">GPS</span>
      </RouterLink>

    </div>

    <!-- Pembatas Garis / Divider -->
    <div class="my-2.5 h-[1px] bg-gradient-to-r from-transparent via-amber-500/40 to-transparent"></div>


    <!-- Bottom Status Card -->
    <div class="pt-2 border-t border-amber-500/20 text-[10px] text-[var(--theme-text-primary)] text-center font-sans space-y-0.5">
      <div class="flex items-center justify-center gap-1.5 text-amber-300 font-semibold">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
        <span>GracePoint CMS v1.0</span>
      </div>
      <p class="text-[9px] text-[var(--theme-text-muted)]">© 2026 Gereja & Pelayanan Jemaat</p>
    </div>
  </aside>
</template>

<style scoped>

.nav-sidebar {
  width: 100%;
  height: auto;
  min-height: 100vh;
  background-color: var(--theme-bg-secondary);
  border-right: 1px solid var(--theme-border-soft);
  transition: all 0.3s ease;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem; /* Memberi jarak antar grup menu */
}

.sidebar-link {
  color: var(--theme-text-primary) !important;
}

.sidebar-link:hover {
  color: var(--theme-gold) !important;
}

/* Slim custom scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.4);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(245, 158, 11, 0.7);
}

a {
  text-decoration: none;
}
</style>
