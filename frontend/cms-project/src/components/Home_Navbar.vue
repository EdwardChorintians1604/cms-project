<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useSidebar } from '@/composables/useSidebar'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const { user, isAuthenticated, logout } = useAuth()
const { toggleSidebar, closeSidebar } = useSidebar()
const router = useRouter()

const isMobileMenuOpen = ref(false)
const isAuthModalOpen = ref(false)

const navItems = [
  { label: 'Beranda', href: '#home' },
  { label: 'Tentang GracePoint', href: '#about' },
  { label: 'Gereja', href: '#church' },
  { label: 'Pelayanan', href: '#service' },
  { label: 'Statistik', href: '#statistic' },
  { label: 'Fitur', href: '#features' },
  { label: 'Donasi', href: '#donasi' },
]

const announcements = ref([
  '✝ Soli Deo Gloria — Pelayanan Jemaat & Sistem Informasi Gereja',
  '⛪ Jadwal Ibadah Raya Minggu: Sesi I (08:00 WIB) & Sesi II (17:00 WIB)',
  '📞 Kontak Sekretariat & Layanan Doa: (021) 555-0199 / WhatsApp 0812-3456-7890',
  '📖 Warta Jemaat: Pendataan Ulang Anggota & Keluarga Jemaat Telah Dibuka',
  '🕊️ Perjamuan Kudus Dilaksanakan Pada Minggu Pertama Setiap Bulan',
])

const currentAnnouncementIndex = ref(0)
let announcementTimer = null

onMounted(() => {
  announcementTimer = setInterval(() => {
    currentAnnouncementIndex.value = (currentAnnouncementIndex.value + 1) % announcements.value.length
  }, 4500)
})

onUnmounted(() => {
  if (announcementTimer) clearInterval(announcementTimer)
})

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

const openAuthModal = () => {
  isAuthModalOpen.value = true
}

const navigateTo = (path) => {
  isAuthModalOpen.value = false
  closeMobileMenu()
  router.push(path)
}

const handleLogout = () => {
  logout()
  isAuthModalOpen.value = false
  closeMobileMenu()
  closeSidebar()
  router.push('/')
}
</script>

<template>
  <header class="classic-navbar sticky top-0 z-50 bg-[#0f172a] text-slate-100 shadow-2xl border-b border-amber-500/30">
    <div class="bg-slate-800 border-b border-amber-500/40 text-amber-100 py-1 px-3 sm:px-4 text-center font-serif text-[10px] sm:text-xs tracking-wider uppercase flex justify-center items-center h-7 sm:h-8 relative overflow-hidden shadow-inner">
      <Transition name="fade-slide" mode="out-in">
        <div :key="currentAnnouncementIndex" class="flex items-center justify-center gap-1.5 sm:gap-2 w-full text-amber-200 font-semibold drop-shadow-sm px-1 sm:px-2">
          <span class="truncate max-w-[92vw] sm:max-w-none">{{ announcements[currentAnnouncementIndex] }}</span>
        </div>
      </Transition>
    </div>

    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 sm:h-20">
        <!-- Brand & Sidebar Toggle -->
        <div class="flex items-center gap-1.5 sm:gap-3 min-w-0">
          <button
            type="button"
            @click="toggleSidebar"
            title="Tampilkan / Sembunyikan Sidebar"
            aria-label="Toggle sidebar"
            class="p-1.5 sm:p-2 text-amber-300 hover:text-amber-100 hover:bg-slate-900 border border-amber-500/30 rounded transition flex items-center justify-center cursor-pointer flex-shrink-0"
          >
            <svg class="nav-icon w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h10M4 18h16" />
            </svg>
          </button>

          <RouterLink to="/" class="flex items-center gap-2 sm:gap-3.5 group cursor-pointer min-w-0">
            <div class="w-8 h-8 sm:w-11 sm:h-11 rounded-full border-2 border-slate-400/70 bg-gradient-to-b from-slate-900 to-slate-950 flex items-center justify-center shadow-lg shadow-slate-500/10 group-hover:border-slate-200 transition-all duration-300 flex-shrink-0 overflow-hidden">
              <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="w-full h-full object-cover">
            </div>

            <div class="flex flex-col min-w-0">
              <span class="font-serif text-base sm:text-xl font-bold tracking-wider text-amber-300 group-hover:text-amber-200 transition leading-tight truncate">
                GRACEPOINT
              </span>
              <span class="text-[9px] sm:text-[10px] font-serif text-white tracking-widest uppercase opacity-95 leading-tight truncate hidden xs:inline-block">
                Gereja &amp; Pelayanan Jemaat
              </span>
            </div>
          </RouterLink>
        </div>

        <!-- Desktop Navigation Links -->
        <nav class="hidden md:flex items-center gap-3 lg:gap-6" aria-label="Navigasi utama">
          <a
            v-for="item in navItems"
            :key="item.href"
            :href="item.href"
            class="classic-link font-sans text-[11px] uppercase font-medium tracking-wider text-white hover:text-amber-300 py-1 transition-colors duration-200 relative"
          >
            {{ item.label }}
          </a>
        </nav>

        <!-- Right Side Cluster: Auth / User Info + Theme Toggle + Mobile Menu Trigger -->
        <div class="flex items-center gap-1.5 sm:gap-3 flex-shrink-0">
          <div v-if="isAuthenticated && user?.role !== 'superadmin'" class="flex items-center gap-2 sm:gap-3 pl-2 sm:pl-3 border-l border-amber-500/20">
            <div class="hidden sm:flex flex-col text-right">
              <span class="font-serif text-[11px] font-bold text-amber-300 tracking-wide truncate max-w-[120px]">
                {{ user?.full_name || user?.name || user?.admin_name || 'Anggota Jemaat' }}
              </span>
              <span class="text-[9px] font-serif uppercase tracking-widest text-slate-200">
                {{ user?.role === 'church_admin' ? 'Admin Gereja' : 'Jemaat Terdaftar' }}
              </span>
            </div>

            <button
              type="button"
              @click="handleLogout"
              title="Keluar"
              class="p-1.5 text-amber-300/80 hover:text-amber-300 hover:bg-amber-950/60 rounded border border-amber-500/30 transition cursor-pointer"
            >
              <svg class="nav-icon w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>

          <button
            v-else
            type="button"
            @click.stop="openAuthModal"
            title="Masuk atau Daftar"
            class="group relative inline-flex items-center justify-center gap-1 sm:gap-2 overflow-hidden rounded-lg border border-amber-400/50 bg-gradient-to-r from-amber-500/10 via-amber-400/5 to-transparent px-2 sm:px-2.5 py-1.5 sm:py-2 text-[10px] font-serif uppercase tracking-[0.14em] sm:tracking-[0.18em] text-amber-200 shadow-[0_0_0_1px_rgba(251,191,36,0.08)] transition-all duration-200 ease-out hover:-translate-y-0.5 hover:border-amber-300 hover:bg-amber-400/10 hover:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400/50 cursor-pointer min-h-[32px] sm:min-h-[36px]"
          >
            <span class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.12),_transparent_60%)] opacity-80"></span>
            <span class="relative flex items-center justify-center gap-1 sm:gap-1.5">
              <span class="flex h-4 w-4 sm:h-5 sm:w-5 items-center justify-center rounded-full border border-amber-300/60 bg-slate-950/40 text-amber-200 transition group-hover:bg-amber-300/10 group-hover:text-amber-100">
                <svg class="h-2.5 w-2.5 sm:h-3 sm:w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </span>
              <span class="hidden sm:inline">Masuk</span>
              <span class="sm:hidden text-[9px] font-bold">Akses</span>
            </span>
          </button>

          <!-- Theme Switcher Button -->
          <div class="flex-shrink-0">
            <ThemeToggleButton />
          </div>

          <!-- Hamburger Button (Mobile / Tablet) -->
          <button
            type="button"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            aria-label="Buka menu mobile"
            class="md:hidden p-1.5 sm:p-2 text-amber-300 hover:bg-slate-900 border border-amber-500/40 rounded-lg cursor-pointer flex-shrink-0"
          >
            <svg class="nav-icon w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Responsive Mobile Menu Drawer -->
    <Transition name="mobile-menu">
      <div v-if="isMobileMenuOpen" class="mobile-drawer fixed inset-0 z-[60] p-4 sm:p-6 flex flex-col justify-between overflow-y-auto">
        <!-- Top Drawer Bar -->
        <div class="flex items-center justify-between pb-3 border-b border-amber-500/30">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-full border border-amber-400/50 overflow-hidden bg-slate-950 flex items-center justify-center">
              <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="w-full h-full object-cover">
            </div>
            <span class="font-serif text-sm font-bold tracking-wider text-amber-300">GRACEPOINT</span>
          </div>

          <button
            type="button"
            @click="closeMobileMenu"
            aria-label="Tutup menu mobile"
            class="p-1.5 text-amber-300 hover:bg-slate-900/60 border border-amber-500/40 rounded-lg cursor-pointer transition"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Navigation Links Grid/List -->
        <nav class="my-auto py-6 flex flex-col items-center justify-center space-y-4 w-full">
          <a
            v-for="item in navItems"
            :key="item.href"
            :href="item.href"
            @click="closeMobileMenu"
            class="mobile-nav-link w-full text-center py-2.5 px-4 rounded-xl font-serif text-sm uppercase tracking-wider font-semibold transition-all duration-200"
          >
            {{ item.label }}
          </a>
        </nav>

        <!-- Bottom Quick Actions inside Drawer -->
        <div class="pt-4 border-t border-amber-500/30 space-y-2.5">
          <button
            type="button"
            @click="openAuthModal(); closeMobileMenu()"
            class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-serif font-bold text-xs uppercase tracking-wider shadow-lg flex items-center justify-center gap-2 cursor-pointer transition active:scale-[0.98]"
          >
            <i class="bi bi-shield-lock-fill"></i>
            <span>Portal Akses &amp; Masuk</span>
          </button>

          <p class="text-center text-[10px] font-sans text-slate-400 pt-1">
            © GracePoint Indonesia • Soli Deo Gloria ✝
          </p>
        </div>
      </div>
    </Transition>
  </header>

  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="isAuthModalOpen"
        class="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-slate-950/85 backdrop-blur-md"
        @click.self="isAuthModalOpen = false"
      >
        <div class="w-full max-w-2xl max-h-[92vh] overflow-y-auto custom-scrollbar bg-[#091129] border border-amber-500/40 rounded-2xl p-4 sm:p-6 md:p-8 shadow-2xl relative font-serif text-slate-100 animate-scaleUp">
          <button
            type="button"
            @click="isAuthModalOpen = false"
            class="absolute top-3 right-3 sm:top-4 sm:right-4 text-slate-300 hover:text-amber-300 p-1.5 rounded-lg border border-slate-700 hover:bg-[#0b1435] transition cursor-pointer z-10 flex items-center justify-center"
          >
            <i class="bi bi-x-lg fs-5"></i>
          </button>

          <div class="text-center pb-4 sm:pb-5 border-b border-amber-500/20 mb-4 sm:mb-6">
            <div class="w-11 h-11 sm:w-12 sm:h-12 mx-auto rounded-full bg-amber-500/10 border border-amber-400/40 text-amber-300 flex items-center justify-center mb-2 shadow-inner">
              <i class="bi bi-shield-lock-fill text-amber-300 fs-4"></i>
            </div>
            <h2 class="text-xl sm:text-2xl font-bold text-amber-300 tracking-wide">PORTAL AKSES GRACEPOINT</h2>
            <p class="text-xs sm:text-sm text-slate-200 font-sans mt-1.5 font-medium">Pilih jenis akun untuk masuk atau daftarkan akun baru Anda.</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5 md:gap-6 font-sans">
            <div class="space-y-3 p-3.5 sm:p-4 bg-slate-900/90 border border-amber-500/30 rounded-xl flex flex-col justify-between">
              <div class="space-y-3">
                <div class="flex items-center gap-2 pb-2.5 border-b border-amber-500/30 text-amber-300 text-xs sm:text-sm font-bold uppercase tracking-wider font-serif">
                  <i class="bi bi-box-arrow-in-right me-1 text-amber-400 fs-6"></i>
                  <span>1. PILIHAN MASUK (LOGIN)</span>
                </div>

                <button
                  type="button"
                  @click="navigateTo('/verification-login')"
                  class="w-full p-4 sm:p-5 bg-[#070c1e] hover:bg-amber-950/40 border border-amber-500/40 hover:border-amber-400 rounded-xl text-left transition group flex items-center gap-4 cursor-pointer shadow-lg"
                >
                  <div class="w-12 h-12 rounded-xl bg-amber-500/15 border border-amber-500/40 flex items-center justify-center text-amber-300 flex-shrink-0 group-hover:scale-110 transition shadow-inner">
                    <i class="bi bi-shield-lock-fill fs-3"></i>
                  </div>
                  <div>
                    <h4 class="text-base font-bold text-white group-hover:text-amber-300 leading-tight">Masuk ke Sistem</h4>
                    <p class="text-xs text-slate-300 group-hover:text-slate-100 mt-1">Portal Otentikasi &amp; Verifikasi Satu Jalur Terpadu</p>
                  </div>
                </button>

                <div class="p-3 bg-[#070c1e]/70 border border-amber-500/15 rounded-xl space-y-2 text-xs text-slate-300">
                  <div class="flex items-center gap-2 text-amber-300 font-semibold font-serif">
                    <i class="bi bi-info-circle-fill"></i>
                    <span>Satu Akses untuk Semua:</span>
                  </div>
                  <p class="text-[11px] leading-relaxed text-slate-400">
                    Gunakan portal ini untuk masuk sebagai Pengurus Gereja, Pelayan, maupun Anggota Jemaat. Sistem otomatis memvalidasi role akun Anda.
                  </p>
                </div>
              </div>

              <div class="p-2.5 bg-[#070c1e] border border-amber-500/20 rounded-lg text-xs text-slate-300 text-center font-sans mt-2">
                <i class="bi bi-shield-check text-emerald-400 me-1"></i> Dilindungi Enkripsi &amp; Verifikasi Berlapis
              </div>
            </div>

            <div class="space-y-3 p-3.5 sm:p-4 bg-slate-900/90 border border-amber-500/30 rounded-xl flex flex-col justify-between">
              <div class="space-y-3">
                <div class="flex items-center gap-2 pb-2.5 border-b border-amber-500/30 text-amber-300 text-xs sm:text-sm font-bold uppercase tracking-wider font-serif">
                  <i class="bi bi-person-badge-fill me-1 text-amber-400 fs-6"></i>
                  <span>2. PILIHAN PENDAFTARAN (REGISTER)</span>
                </div>

                <button
                  type="button"
                  @click="navigateTo('/user-register')"
                  class="w-full p-3 sm:p-3.5 bg-[#070c1e] hover:bg-emerald-950/40 border border-emerald-500/30 hover:border-emerald-400 rounded-lg text-left transition group flex items-center gap-3.5 cursor-pointer shadow-sm"
                >
                  <div class="w-9 h-9 rounded-lg bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-center text-emerald-300 flex-shrink-0 group-hover:scale-110 transition">
                    <i class="bi bi-person-plus-fill fs-5"></i>
                  </div>
                  <div>
                    <h4 class="text-sm sm:text-base font-bold text-white group-hover:text-emerald-300 leading-tight">Daftar Sebagai User / Jemaat</h4>
                    <p class="text-xs text-slate-300 group-hover:text-slate-100 mt-0.5">Pendaftaran anggota jemaat baru</p>
                  </div>
                </button>

                <button
                  type="button"
                  @click="navigateTo('/church-register')"
                  class="w-full p-3 sm:p-3.5 bg-[#070c1e] hover:bg-emerald-950/40 border border-emerald-500/30 hover:border-emerald-400 rounded-lg text-left transition group flex items-center gap-3.5 cursor-pointer shadow-sm"
                >
                  <div class="w-9 h-9 rounded-lg bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-center text-emerald-300 flex-shrink-0 group-hover:scale-110 transition">
                    <i class="bi bi-building-add fs-5"></i>
                  </div>
                  <div>
                    <h4 class="text-sm sm:text-base font-bold text-white group-hover:text-emerald-300 leading-tight">Daftar Sebagai Admin Gereja</h4>
                    <p class="text-xs text-slate-300 group-hover:text-slate-100 mt-0.5">Registrasi institusi/organisasi gereja baru</p>
                  </div>
                </button>
              </div>

              <div class="p-2.5 sm:p-3 bg-[#070c1e] border border-amber-500/25 rounded-lg text-xs text-slate-200 text-center font-sans mt-3">
                <i class="bi bi-headset text-amber-300 me-1"></i> Need Help? Hubungi Layanan Dukungan di <span class="text-amber-300 font-bold">(021) 555-0199</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

.font-serif {
  font-family: 'Cinzel', 'Playfair Display', Georgia, 'Times New Roman', serif;
}

.classic-link {
  color: #ffffff;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

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

.classic-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 1px;
  background-color: #fbbf24;
  transition: all 0.3s ease;
  transform: translateX(-50%);
}
.classic-link:hover::after,
.classic-link:focus-visible::after {
  width: 100%;
}

svg.emblem-cross-svg {
  width: 20px !important;
  height: 20px !important;
  min-width: 20px;
  min-height: 20px;
}

svg.nav-icon {
  width: 15px !important;
  height: 15px !important;
  min-width: 15px;
  min-height: 15px;
}

a {
  text-decoration: none;
}

/* Mobile Menu Drawer Styling */
.mobile-drawer {
  background: rgba(11, 20, 53, 0.97);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.mobile-nav-link {
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(245, 158, 11, 0.15);
}

.mobile-nav-link:hover,
.mobile-nav-link:active {
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.4);
}

/* Light Mode Overrides for Mobile Navbar & Drawer */
:global(html[data-theme="light"]) .mobile-drawer {
  background: rgba(255, 255, 255, 0.98);
}

:global(html[data-theme="light"]) .mobile-nav-link {
  color: #0f172a;
  background: #f8fafc;
  border-color: rgba(217, 119, 6, 0.2);
}

:global(html[data-theme="light"]) .mobile-nav-link:hover,
:global(html[data-theme="light"]) .mobile-nav-link:active {
  color: #b45309;
  background: #fef3c7;
  border-color: #d97706;
}
</style>
