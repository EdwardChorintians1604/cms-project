<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useSidebar } from '@/composables/useSidebar'
import logoGracePoint from '@/assets/images/GracePoint.png'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const emit = defineEmits(['focus-search', 'toggle-timeline', 'toggle-bookmarks'])

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

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const { toggleSidebar, closeSidebar } = useSidebar()

const isMobileMenuOpen = ref(false)
const isAuthModalOpen = ref(false)

// Historical Ticker Quotes
const historicalQuotes = ref([
  '📜 "Dengan Nama Tuhan, Kami Menginjakkan Kaki di Tanah Ini" — C.W. Ottow & J.G. Geissler (Mansinam, 1855)',
  '✝ "100% Katolik, 100% Indonesia" — Mgr. Albertus Soegijapranata SJ (1940)',
  '📖 "Hidupku Telah Kuserahkan Bagi Kristus dan Bangsa Batak" — Dr. I.L. Nommensen (Silindung, 1861)',
  '🕊️ "Pemberitaan Injil Melalui Kebudayaan & Kasih Nyata" — Kyai Sadrach (Karangjoso, Jawa Tengah)',
  '⚓ Api Pentakosta Berhembus di Cepu & Surabaya Sejak 1921 — Gerakan Roh Kudus di Nusantara',
  '🌏 Soli Deo Gloria — Mengenal Akar & Jejak Iman Kristiani Lintas Generasi di Indonesia'
])

const currentQuoteIndex = ref(0)
let quoteTimer = null

onMounted(() => {
  quoteTimer = setInterval(() => {
    currentQuoteIndex.value = (currentQuoteIndex.value + 1) % historicalQuotes.value.length
  }, 4500)
})

onUnmounted(() => {
  if (quoteTimer) clearInterval(quoteTimer)
})

const handleLogout = () => {
  logout()
  closeSidebar()
}

const openAuthModal = () => {
  isAuthModalOpen.value = true
}

const navigateTo = (path) => {
  isAuthModalOpen.value = false
  isMobileMenuOpen.value = false
  router.push(path)
}

const triggerSearchFocus = () => {
  emit('focus-search')
  isMobileMenuOpen.value = false
}

const triggerTimelineToggle = (mode) => {
  emit('toggle-timeline', mode)
  isMobileMenuOpen.value = false
}

const triggerBookmarks = () => {
  emit('toggle-bookmarks')
  isMobileMenuOpen.value = false
}

const scrollToSection = (hash) => {
  isMobileMenuOpen.value = false
  const el = document.querySelector(hash)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<template>
  <header class="classic-navbar history-navbar sticky top-0 z-40 bg-[#0f172a] text-slate-100 shadow-2xl border-b border-amber-500/30">
    
    <!-- 1. Top Historical Quotes Ticker Bar (Simetris & Elegan) -->
    <div class="history-ticker bg-slate-800 border-b border-amber-500/40 text-amber-100 py-1 px-2 xs:px-3 sm:px-4 text-center font-serif text-[9px] xs:text-[10px] sm:text-xs tracking-wider uppercase flex justify-center items-center h-7 sm:h-8 relative overflow-hidden shadow-inner">
      <Transition name="fade-slide" mode="out-in">
        <div 
          :key="currentQuoteIndex" 
          class="flex items-center justify-center gap-1.5 sm:gap-2 w-full text-amber-200 font-semibold drop-shadow-sm px-1 sm:px-2 min-w-0"
        >
          <i class="bi bi-clock-history text-amber-400 text-xs shrink-0"></i>
          <span class="ticker-text truncate block">{{ historicalQuotes[currentQuoteIndex] }}</span>
        </div>
      </Transition>
    </div>

    <!-- 2. Main Navigation Bar Content -->
    <div class="max-w-7xl mx-auto w-full px-2 xs:px-3 sm:px-5 lg:px-8">
      <div class="flex items-center justify-between h-14 xs:h-16 sm:h-18 md:h-16 lg:h-20 gap-2 xs:gap-3 sm:gap-4 lg:gap-6">
        
        <!-- Left: Sidebar Drawer Toggle & Official GracePoint Brand -->
        <div class="flex items-center gap-1.5 xs:gap-2 sm:gap-3 min-w-0 shrink-0">
          <button 
            @click="toggleSidebar" 
            title="Tampilkan / Sembunyikan Sidebar Menu"
            type="button"
            class="p-1.5 sm:p-2 text-amber-300 hover:text-amber-100 hover:bg-slate-900 border border-amber-500/30 rounded-xl transition flex items-center justify-center shrink-0 cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h10M4 18h16"/>
            </svg>
          </button>

          <!-- Authentic GracePoint Brand Link (Tanpa Garis Bawah) -->
          <RouterLink 
            to="/" 
            class="brand-link flex items-center gap-1.5 xs:gap-2 sm:gap-3 group cursor-pointer no-underline !decoration-transparent min-w-0"
            style="text-decoration: none !important;"
          >
            <div class="w-8 h-8 xs:w-9 xs:h-9 sm:w-10 sm:h-10 lg:w-11 lg:h-11 rounded-full border-2 border-slate-400/70 bg-gradient-to-b from-slate-900 to-slate-950 flex items-center justify-center shadow-lg shadow-slate-500/10 group-hover:border-amber-400 transition-all duration-300 shrink-0 overflow-hidden">
              <img :src="logoGracePoint" alt="Logo GracePoint" class="w-full h-full object-cover">
            </div>

            <div class="flex flex-col min-w-0" style="text-decoration: none !important;">
              <div class="flex items-center gap-1">
                <span class="brand-title font-serif text-sm xs:text-base sm:text-lg lg:text-xl font-bold tracking-wider text-amber-300 group-hover:text-amber-200 transition leading-tight truncate">
                  GRACEPOINT
                </span>
                <span class="hidden xs:inline-block px-1 py-0 rounded bg-amber-500/20 border border-amber-500/40 text-[8px] xs:text-[9px] font-mono text-amber-300 uppercase tracking-wider font-extrabold shrink-0">
                  HISTORIA
                </span>
              </div>
              <span class="brand-subtitle text-[8px] xs:text-[9px] sm:text-[10px] font-serif text-slate-200 tracking-widest uppercase opacity-95 leading-tight truncate">
                Sejarah Gereja Indonesia
              </span>
            </div>
          </RouterLink>
        </div>

        <!-- Center: Desktop Navigation Links (Rapi, Sejajar & Tertata) -->
        <!-- md: show compact icon-only nav, lg: show full text nav -->
        <nav class="hidden md:flex items-center gap-2 lg:gap-4 xl:gap-6 whitespace-nowrap">
          <RouterLink 
            to="/" 
            class="classic-link font-sans text-xs uppercase font-medium tracking-wider text-slate-200 hover:text-amber-300 py-1 transition-colors duration-200 flex items-center gap-1.5"
            title="Beranda"
          >
            <i class="bi bi-house-door text-amber-400 text-xs"></i>
            <span class="hidden lg:inline">Beranda</span>
          </RouterLink>

          <button 
            type="button" 
            @click="triggerSearchFocus"
            :class="[
              'classic-link font-sans text-xs uppercase font-medium tracking-wider text-slate-200 hover:text-amber-300 py-1 transition-colors duration-200 cursor-pointer bg-transparent border-none flex items-center gap-1.5',
              currentView === 'grid' ? 'text-amber-400 font-semibold active-link' : ''
            ]"
            title="Fokus ke Kolom Pencarian Gereja"
          >
            <i class="bi bi-search text-amber-400 text-xs"></i>
            <span class="hidden lg:inline">Pencarian</span>
          </button>

          <button 
            type="button" 
            @click="triggerTimelineToggle('timeline')"
            :class="[
              'classic-link font-sans text-xs uppercase font-medium tracking-wider text-slate-200 hover:text-amber-300 py-1 transition-colors duration-200 cursor-pointer bg-transparent border-none flex items-center gap-1.5',
              currentView === 'timeline' ? 'text-amber-400 font-semibold active-link' : ''
            ]"
            title="Buka Garis Waktu Sejarah Gereja"
          >
            <i class="bi bi-clock-history text-cyan-400 text-xs"></i>
            <span class="hidden lg:inline">Garis Waktu</span>
          </button>

          <!-- Bookmark Icon: Desktop Only -->
          <button
            type="button"
            @click="triggerBookmarks"
            class="classic-link relative font-sans text-xs uppercase font-medium tracking-wider text-slate-200 hover:text-amber-300 py-1 transition-colors duration-200 cursor-pointer bg-transparent border-none flex items-center gap-1.5"
            title="Daftar Gereja yang Disimpan"
          >
            <i class="bi bi-bookmark-star-fill text-amber-400 text-xs"></i>
            <span class="hidden lg:inline">Tersimpan</span>
            <span 
              v-if="bookmarkCount > 0"
              class="absolute -top-1.5 -right-2 min-w-[16px] h-4 px-1 bg-amber-500 text-slate-900 text-[9px] font-bold rounded-full flex items-center justify-center leading-none"
            >{{ bookmarkCount }}</span>
          </button>
        </nav>

        <!-- Right: Action Cluster (Theme Toggle, Auth, Mobile Hamburger) -->
        <div class="flex items-center gap-1.5 xs:gap-2 sm:gap-2.5 shrink-0">

          <!-- Theme Toggle -->
          <div class="shrink-0">
            <ThemeToggleButton />
          </div>

          <!-- User Authenticated State -->
          <div v-if="isAuthenticated && user?.role !== 'superadmin'" class="flex items-center gap-1.5 sm:gap-2 pl-1.5 sm:pl-2 border-l border-amber-500/20">
            <div class="hidden lg:flex flex-col text-right">
              <span class="font-serif text-[11px] font-bold text-amber-300 truncate max-w-[110px]">
                {{ user?.full_name || user?.name || 'Anggota Jemaat' }}
              </span>
              <span class="text-[8px] font-serif uppercase tracking-wider text-slate-400">
                {{ user?.role === 'church_admin' ? 'Admin Gereja' : 'Jemaat' }}
              </span>
            </div>
            
            <button 
              @click="handleLogout" 
              title="Keluar dari Akun"
              type="button"
              class="p-1.5 sm:p-2 rounded-xl bg-slate-800 hover:bg-rose-950/60 text-slate-300 hover:text-rose-400 border border-slate-700 hover:border-rose-500/40 transition cursor-pointer"
            >
              <i class="bi bi-box-arrow-right text-xs sm:text-sm"></i>
            </button>
          </div>

          <!-- Guest State: Portal Masuk -->
          <div v-else class="flex items-center">
            <!-- Icon-only on xs, full text from sm+ -->
            <button 
              @click="openAuthModal" 
              type="button"
              class="group relative inline-flex items-center justify-center gap-1 xs:gap-1.5 overflow-hidden rounded-xl border border-amber-400/50 bg-gradient-to-r from-amber-500/15 via-amber-400/10 to-transparent px-2 xs:px-2.5 sm:px-3 py-1.5 sm:py-2 text-[10px] sm:text-xs font-serif uppercase tracking-wider text-amber-200 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-amber-300 hover:bg-amber-400/20 hover:text-amber-100 cursor-pointer"
              title="Buka Portal Masuk atau Pilihan Registrasi"
            >
              <i class="bi bi-box-arrow-in-right text-amber-300 text-xs"></i>
              <span class="font-bold hidden xs:inline">Portal Masuk</span>
            </button>
          </div>

          <!-- Mobile Hamburger Toggle (hidden md+ since nav is shown) -->
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            type="button"
            class="md:hidden p-1.5 text-amber-300 hover:text-white hover:bg-slate-800 border border-amber-500/30 rounded-xl transition cursor-pointer"
            :aria-expanded="isMobileMenuOpen"
            title="Menu Navigasi Mobile"
          >
            <svg v-if="!isMobileMenuOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>

        </div>

      </div>
    </div>

    <!-- 3. Responsive Mobile Dropdown Drawer (Terstruktur & Rapi) -->
    <Teleport to="body">
      <Transition name="fade">
        <div 
          v-if="isMobileMenuOpen" 
          class="md:hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm"
          @click="isMobileMenuOpen = false"
        ></div>
      </Transition>

      <Transition name="slide-down">
        <div 
          v-if="isMobileMenuOpen" 
          class="md:hidden fixed top-0 left-0 right-0 z-50 bg-slate-900/98 backdrop-blur-xl border-b border-amber-500/40 shadow-2xl p-3 xs:p-4 sm:p-5 text-slate-100 font-sans max-h-[90vh] overflow-y-auto mobile-drawer-scroll"
        >
          <!-- Drawer Header -->
          <div class="flex items-center justify-between pb-3 border-b border-amber-500/20 mb-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-full border border-amber-500/40 bg-slate-900 flex items-center justify-center overflow-hidden shrink-0">
                <img :src="logoGracePoint" alt="logo" class="w-full h-full object-cover">
              </div>
              <div class="flex flex-col">
                <div class="flex items-center gap-1.5">
                  <span class="font-serif text-sm font-bold text-amber-300 tracking-wider">GRACEPOINT</span>
                  <span class="text-[8px] uppercase tracking-wider font-extrabold px-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">HISTORIA</span>
                </div>
                <span class="text-[9px] font-serif text-slate-400 uppercase tracking-wider">Sejarah Gereja Indonesia</span>
              </div>
            </div>

            <button 
              @click="isMobileMenuOpen = false" 
              class="p-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-400 hover:text-white transition cursor-pointer"
              title="Tutup Menu"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          <!-- Quick Action Buttons: Search, Timeline, & Bookmarks -->
          <div class="grid grid-cols-2 xs:grid-cols-3 gap-1.5 xs:gap-2 mb-3">
            <button 
              type="button" 
              @click="triggerSearchFocus"
              class="p-2 xs:p-2.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold text-[10px] xs:text-xs flex items-center justify-center gap-1.5 xs:gap-2 cursor-pointer transition"
            >
              <i class="bi bi-search text-amber-400"></i>
              <span>Pencarian</span>
            </button>

            <button 
              type="button" 
              @click="triggerTimelineToggle('timeline')"
              class="p-2 xs:p-2.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-semibold text-[10px] xs:text-xs flex items-center justify-center gap-1.5 xs:gap-2 cursor-pointer transition"
            >
              <i class="bi bi-clock-history text-cyan-400"></i>
              <span>Garis Waktu</span>
            </button>

            <!-- Bookmark quick-action (only on xs+ to fill 3rd column) -->
            <button 
              type="button" 
              @click="triggerBookmarks"
              class="p-2 xs:p-2.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold text-[10px] xs:text-xs flex items-center justify-center gap-1.5 xs:gap-2 cursor-pointer transition relative"
            >
              <i class="bi bi-bookmark-star-fill text-amber-400"></i>
              <span class="hidden xs:inline">Tersimpan</span>
              <span 
                v-if="bookmarkCount > 0"
                class="absolute -top-1 -right-1 min-w-[15px] h-4 px-1 bg-amber-500 text-slate-900 text-[9px] font-bold rounded-full flex items-center justify-center leading-none"
              >{{ bookmarkCount }}</span>
            </button>
          </div>

          <!-- Mobile Nav Links -->
          <nav class="flex flex-col gap-1 text-sm font-medium">
            <RouterLink 
              to="/" 
              @click="isMobileMenuOpen = false"
              class="flex items-center justify-between px-3.5 py-2 rounded-xl text-slate-300 hover:bg-slate-800 hover:text-amber-300 transition text-xs font-medium"
            >
              <span class="flex items-center gap-2.5">
                <i class="bi bi-house-door text-amber-400"></i>
                <span>Beranda Utama</span>
              </span>
              <span class="text-[10px] text-amber-400 font-mono">Home</span>
            </RouterLink>

            <a 
              href="#jalur-misi" 
              @click.prevent="scrollToSection('#jalur-misi')"
              class="flex items-center justify-between px-3.5 py-2 rounded-xl text-slate-300 hover:bg-slate-800 hover:text-amber-300 transition text-xs font-medium cursor-pointer"
            >
              <span class="flex items-center gap-2.5">
                <i class="bi bi-compass text-amber-400"></i>
                <span>5 Koridor Jalur Misi Nusantara</span>
              </span>
              <span class="text-[10px] text-amber-400 font-mono">Mission</span>
            </a>

            <RouterLink 
              to="/hari-besar" 
              @click="isMobileMenuOpen = false"
              class="flex items-center justify-between px-3.5 py-2 rounded-xl text-slate-300 hover:bg-slate-800 hover:text-amber-300 transition text-xs font-medium"
            >
              <span class="flex items-center gap-2.5">
                <i class="bi bi-calendar3 text-slate-400"></i>
                <span>Kalender Liturgi Gerejawi</span>
              </span>
              <span class="text-[10px] text-slate-400 font-mono">Liturgi</span>
            </RouterLink>

            <RouterLink 
              to="/berita-jemaat" 
              @click="isMobileMenuOpen = false"
              class="flex items-center justify-between px-3.5 py-2 rounded-xl text-slate-300 hover:bg-slate-800 hover:text-amber-300 transition text-xs font-medium"
            >
              <span class="flex items-center gap-2.5">
                <i class="bi bi-newspaper text-slate-400"></i>
                <span>Berita &amp; Warta Jemaat</span>
              </span>
              <span class="text-[10px] text-slate-400 font-mono">News</span>
            </RouterLink>

            <RouterLink 
              to="/informasi-pelayanan" 
              @click="isMobileMenuOpen = false"
              class="flex items-center justify-between px-3.5 py-2 rounded-xl text-slate-300 hover:bg-slate-800 hover:text-amber-300 transition text-xs font-medium"
            >
              <span class="flex items-center gap-2.5">
                <i class="bi bi-buildings text-slate-400"></i>
                <span>Informasi Pelayanan &amp; Peta</span>
              </span>
              <span class="text-[10px] text-slate-400 font-mono">Ministry</span>
            </RouterLink>
          </nav>

          <!-- Mobile Saved / Bookmarks -->
          <div class="mt-2 pt-2 border-t border-slate-800">
            <button 
              type="button" 
              @click="triggerBookmarks"
              class="w-full flex items-center justify-between px-3.5 py-2 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-slate-700 text-amber-300 text-xs font-medium cursor-pointer transition"
            >
              <div class="flex items-center gap-2">
                <i class="bi bi-bookmark-star-fill text-amber-400"></i>
                <span>Daftar Gereja yang Disimpan</span>
              </div>
              <span class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/30">
                {{ bookmarkCount }} Item
              </span>
            </button>
          </div>

          <!-- Bottom Auth Actions in Mobile Drawer -->
          <div class="mt-3 pt-3 border-t border-amber-500/20">
            <div v-if="isAuthenticated" class="flex items-center justify-between bg-slate-950/80 p-2.5 rounded-xl border border-amber-500/20">
              <div class="flex items-center gap-2 min-w-0">
                <div class="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 flex items-center justify-center font-bold text-xs shrink-0">
                  {{ user?.name?.charAt(0) || 'U' }}
                </div>
                <div class="min-w-0">
                  <div class="text-xs font-bold text-amber-300 truncate">{{ user?.name }}</div>
                  <div class="text-[9px] text-slate-400 uppercase tracking-wider">{{ user?.role }}</div>
                </div>
              </div>
              <button 
                @click="handleLogout" 
                class="px-2.5 py-1 text-[11px] bg-red-950/60 hover:bg-red-900 border border-red-500/40 text-red-300 rounded-lg transition"
              >
                Keluar
              </button>
            </div>

            <div v-else class="grid grid-cols-2 gap-2">
              <button 
                type="button"
                @click="openAuthModal(); isMobileMenuOpen = false"
                class="p-2 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/40 text-amber-300 font-semibold text-xs flex items-center justify-center gap-1.5 transition cursor-pointer"
              >
                <i class="bi bi-box-arrow-in-right"></i>
                <span>Portal Masuk</span>
              </button>

              <RouterLink 
                to="/user-register"
                @click="isMobileMenuOpen = false"
                class="p-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center justify-center gap-1.5 shadow transition text-center no-underline cursor-pointer"
              >
                <i class="bi bi-person-plus-fill"></i>
                <span>Daftar User</span>
              </RouterLink>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 4. GracePoint Access Modal (3 Opsi Lengkap Terstruktur) -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div 
          v-if="isAuthModalOpen" 
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md"
          @click.self="isAuthModalOpen = false"
        >
          <div class="bg-slate-900 border border-amber-500/40 rounded-2xl p-5 sm:p-6 w-full max-w-md shadow-2xl space-y-4">
            
            <div class="flex items-center justify-between pb-3 border-b border-slate-800">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
                  <i class="bi bi-shield-lock-fill"></i>
                </div>
                <div>
                  <h3 class="font-serif font-bold text-white text-base">Portal Akses GracePoint</h3>
                  <span class="text-[10px] text-slate-400 font-sans">Pilih pintu masuk atau pendaftaran sesuai kebutuhan Anda</span>
                </div>
              </div>
              <button 
                type="button" 
                @click="isAuthModalOpen = false" 
                class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 cursor-pointer text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <!-- Options Cards -->
            <div class="space-y-2.5 font-sans">
              <!-- 1. Portal Masuk Terpadu -->
              <button 
                type="button" 
                @click="navigateTo('/verification-login')"
                class="w-full p-3 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 hover:border-amber-500/50 transition flex items-center justify-between group cursor-pointer text-left"
              >
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0 group-hover:scale-105 transition-transform">
                    <i class="bi bi-box-arrow-in-right text-base"></i>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-white group-hover:text-amber-300 transition">Portal Masuk Terpadu</div>
                    <div class="text-[10px] text-slate-400">Masuk untuk Jemaat, Admin Gereja &amp; Sinode</div>
                  </div>
                </div>
                <i class="bi bi-chevron-right text-slate-500 group-hover:text-amber-400 text-xs"></i>
              </button>

              <!-- 2. Daftar Sebagai User / Jemaat -->
              <button 
                type="button" 
                @click="navigateTo('/user-register')"
                class="w-full p-3 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 hover:border-emerald-500/50 transition flex items-center justify-between group cursor-pointer text-left"
              >
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 group-hover:scale-105 transition-transform">
                    <i class="bi bi-person-plus-fill text-base"></i>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-white group-hover:text-emerald-300 transition">Daftar Sebagai User / Jemaat</div>
                    <div class="text-[10px] text-slate-400">Registrasi akun anggota jemaat baru GracePoint</div>
                  </div>
                </div>
                <i class="bi bi-chevron-right text-slate-500 group-hover:text-emerald-400 text-xs"></i>
              </button>

              <!-- 3. Registrasi Gereja Baru -->
              <button 
                type="button" 
                @click="navigateTo('/church-register')"
                class="w-full p-3 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 hover:border-cyan-500/50 transition flex items-center justify-between group cursor-pointer text-left"
              >
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0 group-hover:scale-105 transition-transform">
                    <i class="bi bi-buildings text-base"></i>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-white group-hover:text-cyan-300 transition">Registrasi Gereja Baru</div>
                    <div class="text-[10px] text-slate-400">Daftarkan gereja atau cabang pelayanan baru</div>
                  </div>
                </div>
                <i class="bi bi-chevron-right text-slate-500 group-hover:text-cyan-400 text-xs"></i>
              </button>
            </div>

            <!-- Footer Motto -->
            <div class="pt-2 border-t border-slate-800 text-center text-[11px] text-slate-400 font-serif">
              ✝ Soli Deo Gloria — Sistem Informasi &amp; Sejarah Gereja
            </div>

          </div>
        </div>
      </Transition>
    </Teleport>
  </header>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

/* =========================================================
   RESPONSIVE BREAKPOINTS CUSTOM
   xs  = 360px  (very small phones)
   sm  = 640px  (Tailwind default)
   md  = 768px  (tablet)
   lg  = 1024px (desktop)
   ========================================================= */

.font-serif {
  font-family: 'Cinzel', 'Playfair Display', Georgia, 'Times New Roman', serif;
}

.classic-navbar {
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

a {
  text-decoration: none !important;
}

.brand-link,
.brand-link:hover,
.brand-link:focus,
.brand-link:active,
.brand-link:visited {
  text-decoration: none !important;
}

.brand-link *,
.brand-link:hover * {
  text-decoration: none !important;
}

.classic-link {
  position: relative;
  text-decoration: none !important;
  letter-spacing: 0.08em;
}

.classic-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  width: 0;
  height: 2px;
  background-color: #fbbf24;
  transition: all 0.25s ease;
  transform: translateX(-50%);
  border-radius: 9999px;
}

.classic-link:hover::after,
.classic-link.active-link::after {
  width: 100%;
}

:global(html[data-theme="light"]) .history-navbar .classic-link {
  color: #334155 !important;
}

:global(html[data-theme="light"]) .history-navbar .classic-link:hover,
:global(html[data-theme="light"]) .history-navbar .classic-link.active-link {
  color: #b45309 !important;
}

:global(html[data-theme="light"]) .history-navbar .history-ticker {
  background: linear-gradient(90deg, #ecfdf5 0%, #e0f2fe 50%, #fef3c7 100%) !important;
  color: #92400e !important;
}

:global(html[data-theme="light"]) .history-navbar .history-ticker * {
  color: #92400e !important;
}

svg.nav-icon {
  width: 15px !important;
  height: 15px !important;
  min-width: 15px;
  min-height: 15px;
}

/* Ticker text responsive truncation */
.ticker-text {
  max-width: calc(100vw - 3rem);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Mobile Drawer Scrollbar */
.mobile-drawer-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(251,191,36,0.3) transparent;
}
.mobile-drawer-scroll::-webkit-scrollbar {
  width: 4px;
}
.mobile-drawer-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.mobile-drawer-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(251,191,36,0.3);
  border-radius: 9999px;
}

/* =========================================================
   XS BREAKPOINT  (≥ 360px)
   ========================================================= */
@media (min-width: 360px) {
  .ticker-text {
    max-width: calc(100vw - 4rem);
  }
}

/* =========================================================
   SM BREAKPOINT  (≥ 640px)
   ========================================================= */
@media (min-width: 640px) {
  .ticker-text {
    max-width: none;
  }
}

/* =========================================================
   SUB-360PX  — very small phones
   ========================================================= */
@media (max-width: 359px) {
  /* Collapse brand subtitle on extremely small screens */
  .brand-subtitle {
    display: none;
  }

  /* Shrink brand title slightly */
  .brand-title {
    font-size: 0.7rem;
  }

  /* Single-column quick actions */
  .mobile-quick-actions {
    grid-template-columns: 1fr 1fr !important;
  }

  /* Tighter padding in mobile drawer */
  .mobile-drawer-scroll {
    padding: 0.625rem;
  }
}

/* =========================================================
   TRANSITIONS
   ========================================================= */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.35s ease;
}
.fade-slide-enter-from { opacity: 0; transform: translateY(-6px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(6px); }

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease-out;
}
.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
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
