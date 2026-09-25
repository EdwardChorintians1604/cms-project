<script setup>
import { RouterLink } from 'vue-router'
import history_church_navbar from '@/components/history_church_navbar.vue'
import Home_Sidebar from '@/components/Home_Sidebar.vue'
import { useSidebar } from '@/composables/useSidebar'

const props = defineProps({
  bookmarkCount: {
    type: Number,
    default: 0
  },
  currentView: {
    type: String,
    default: 'grid'
  }
})

const emit = defineEmits(['focus-search', 'toggle-timeline', 'toggle-bookmarks'])

const { isSidebarOpen, toggleSidebar } = useSidebar()
</script>

<template>
  <div class="history-layout min-h-screen bg-[var(--theme-bg-primary)] text-[var(--theme-text-primary)] flex flex-col relative selection:bg-amber-500 selection:text-slate-950 transition-colors duration-300">
    <!-- Navbar Sticky Sejarah Gereja -->
    <history_church_navbar 
      :bookmark-count="bookmarkCount"
      :current-view="currentView"
      @focus-search="emit('focus-search')"
      @toggle-timeline="(mode) => emit('toggle-timeline', mode)"
      @toggle-bookmarks="emit('toggle-bookmarks')"
    />

    <div class="flex flex-1 relative min-w-0">
      <!-- Backdrop Gelap di Semua Ukuran Layar -->
      <Transition name="fade">
        <div 
          v-if="isSidebarOpen" 
          @click="toggleSidebar"
          class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 transition-opacity duration-300 cursor-pointer"
        ></div>
      </Transition>

      <!-- Floating Slide-over Drawer Sidebar (Fixed Overlay) -->
      <Transition name="slide">
        <div 
          v-if="isSidebarOpen" 
          class="fixed inset-y-0 left-0 z-50 h-full w-72 sm:w-80 shadow-2xl"
        >
          <Home_Sidebar />
        </div>
      </Transition>

      <!-- Area Konten Utama Halaman Sejarah Gereja -->
      <main class="flex-1 min-w-0 transition-all duration-300">
        <slot />
      </main>
    </div>

    <!-- Footer Khusus Ensiklopedia & Sejarah Gereja -->
    <footer class="myfooter history-footer bg-[var(--theme-footer-bg)] border-t border-amber-500/30 text-slate-300">
      <div class="footer-container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
          
          <!-- Col 1: Brand & Historical Mission -->
          <div class="space-y-3">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 p-1.5 flex items-center justify-center">
                <i class="bi bi-compass text-amber-400 text-xl"></i>
              </div>
              <div>
                <span class="font-serif font-black text-lg text-white block">HISTORIA GEREJA</span>
                <span class="text-[10px] uppercase text-amber-300 tracking-wider">Arsip &amp; Search Engine</span>
              </div>
            </div>
            <p class="text-xs text-slate-400 leading-relaxed font-sans">
              Pusat dokumentasi dan mesin pencari sejarah cikal bakal gereja-gereja di Indonesia. Merajut benang merah pekabaran Injil dari era VOC, zending Eropa, kebangkitan tokoh lokal, hingga era gereja mandiri kontemporer.
            </p>
            <div class="text-xs font-serif text-amber-300/90 pt-1 flex items-center gap-1.5">
              <span>✝ Soli Deo Gloria</span> — Kemuliaan Hanya Bagi Allah
            </div>
          </div>

          <!-- Col 2: Denominasi & Sinode Utama -->
          <div>
            <h4 class="font-serif font-bold text-sm text-white mb-3 text-amber-400">Rumpun Denominasi</h4>
            <ul class="space-y-2 text-xs text-slate-400">
              <li class="hover:text-amber-300 transition-colors cursor-pointer" @click="emit('focus-search')">Persekutuan Gereja-Gereja di Indonesia (PGI)</li>
              <li class="hover:text-amber-300 transition-colors cursor-pointer" @click="emit('focus-search')">Persekutuan Gereja Pentakosta Indonesia (PGPI)</li>
              <li class="hover:text-amber-300 transition-colors cursor-pointer" @click="emit('focus-search')">Persekutuan Gereja Injili Indonesia (PGLII)</li>
              <li class="hover:text-amber-300 transition-colors cursor-pointer" @click="emit('focus-search')">Konferensi Waligereja Indonesia (KWI)</li>
              <li class="hover:text-amber-300 transition-colors cursor-pointer" @click="emit('focus-search')">Bala Keselamatan, Advent &amp; Ortodoks</li>
            </ul>
          </div>

          <!-- Col 3: Jalur Misi Bersejarah -->
          <div>
            <h4 class="font-serif font-bold text-sm text-white mb-3 text-amber-400">Jalur Misi Nusantara</h4>
            <ul class="space-y-2 text-xs text-slate-400">
              <li><span class="text-amber-300/80">1546:</span> Jalur Kepulauan Rempah Maluku</li>
              <li><span class="text-amber-300/80">1855:</span> Pulau Mansinam &amp; Tanah Papua</li>
              <li><span class="text-amber-300/80">1861:</span> Lembah Silindung &amp; Tanah Batak</li>
              <li><span class="text-amber-300/80">1860-an:</span> Padepokan Karangjoso Jawa</li>
              <li><span class="text-amber-300/80">1921:</span> Kegerakan Pentakosta Cepu</li>
            </ul>
          </div>

          <!-- Col 4: Portal GracePoint & Navigasi -->
          <div>
            <h4 class="font-serif font-bold text-sm text-white mb-3 text-amber-400">Navigasi Terkait</h4>
            <ul class="space-y-2 text-xs text-slate-400">
              <li><RouterLink to="/" class="hover:text-amber-300 transition-colors text-slate-400 text-decoration-none">Beranda Utama GracePoint</RouterLink></li>
              <li><RouterLink to="/hari-besar" class="hover:text-amber-300 transition-colors text-slate-400 text-decoration-none">Kalender Liturgi Gerejawi</RouterLink></li>
              <li><RouterLink to="/berita-jemaat" class="hover:text-amber-300 transition-colors text-slate-400 text-decoration-none">Berita &amp; Warta Jemaat</RouterLink></li>
              <li><RouterLink to="/informasi-pelayanan" class="hover:text-amber-300 transition-colors text-slate-400 text-decoration-none">Informasi Pelayanan</RouterLink></li>
              <li><RouterLink to="/verification-login" class="hover:text-amber-300 transition-colors text-slate-400 text-decoration-none">Portal Masuk Sistem</RouterLink></li>
            </ul>
          </div>

        </div>

        <div class="pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-300 gap-3">
          <p>© 2026 GracePoint Historia — Ensiklopedia &amp; Mesin Pencari Sejarah Gereja Indonesia.</p>
          <div class="flex items-center gap-4">
            <span>Didedikasikan untuk Pelayanan, Edukasi Teologi &amp; Persatuan Umat</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>
