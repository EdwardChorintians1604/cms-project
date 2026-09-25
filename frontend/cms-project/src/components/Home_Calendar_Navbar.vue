<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useSidebar } from '@/composables/useSidebar'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const { user, isAuthenticated, logout } = useAuth()
const { isSidebarOpen, toggleSidebar, closeSidebar } = useSidebar()
const router = useRouter()

const isMobileMenuOpen = ref(false)
const isAuthModalOpen = ref(false) // Modal Pilihan Auth

// Dynamic Announcement Ticker State
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


</script>

<template>
  <header class="classic-navbar sticky top-0 z-50 bg-[#0f172a] text-slate-100 shadow-2xl border-b border-amber-500/30">
    <!-- Top Announcement Bar -->
    <div class="bg-slate-800 border-b border-amber-500/40 text-amber-100 py-1.5 px-4 text-center font-serif text-[11px] sm:text-xs tracking-wider uppercase flex justify-center items-center h-8 relative overflow-hidden shadow-inner">
      <Transition name="fade-slide" mode="out-in">
        <div 
          :key="currentAnnouncementIndex" 
          class="flex items-center justify-center gap-2 w-full text-amber-200 font-semibold drop-shadow-sm px-2"
        >
          <span class="truncate">{{ announcements[currentAnnouncementIndex] }}</span>
        </div>
      </Transition>
    </div>

    <div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 sm:h-20 gap-3 sm:gap-6">
        <!-- Left: Sidebar Toggle Button & Church Brand Logo -->
        <div class="flex min-w-0 shrink-0 items-center gap-1.5 sm:gap-3.5">
          <button 
            @click="toggleSidebar" 
            title="Tampilkan / Sembunyikan Sidebar"
            class="p-1.5 sm:p-2 text-amber-300 hover:text-amber-100 hover:bg-slate-900 border border-amber-500/30 rounded transition flex items-center justify-center shrink-0 cursor-pointer"
          >
            <svg class="nav-icon w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h10M4 18h16"/>
            </svg>
          </button>

          <RouterLink to="/" class="flex min-w-0 items-center gap-2 sm:gap-3.5 group cursor-pointer no-underline">
            <div class="h-8 w-8 shrink-0 overflow-hidden rounded-full border-2 border-slate-400/70 bg-gradient-to-b from-slate-900 to-slate-950 shadow-lg shadow-slate-500/10 transition-all duration-300 group-hover:border-slate-200 sm:h-11 sm:w-11">
              <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="h-full w-full object-cover">
            </div>

            <div class="flex min-w-0 flex-col">
              <div class="flex items-center gap-1.5">
                <span class="block truncate font-serif text-base font-bold tracking-wider text-amber-300 transition group-hover:text-amber-200 sm:text-xl">
                  GRACEPOINT
                </span>
              </div>
              <span class="hidden truncate text-[9px] font-serif uppercase tracking-widest text-slate-200 opacity-95 sm:inline-block sm:text-[10px]">
                Gereja &amp; Pelayanan Jemaat
              </span>
            </div>
          </RouterLink>
        </div>

        <!-- Middle: Classic Navigation Links -->
        <nav class="hidden md:flex items-center gap-3 lg:gap-6 whitespace-nowrap shrink-0" aria-label="Navigasi kalender">
          <RouterLink 
            to="/" 
            class="classic-link font-sans text-[11px] uppercase font-medium tracking-wider text-white hover:text-amber-300 py-1 transition-colors duration-200 relative"
          >
            Beranda
          </RouterLink>

          <a href="#kalender" class="classic-link font-sans text-[11px] uppercase font-medium tracking-wider text-white hover:text-amber-300 py-1 transition-colors duration-200 relative">
            Lihat Kalender
          </a>

          <a href="#bigday" class="classic-link font-sans text-[11px] uppercase font-medium tracking-wider text-white hover:text-amber-300 py-1 transition-colors duration-200 relative">
            Hari Besar Gereja
          </a>

        </nav>

        <!-- Right: Action CTA & User Profile -->
        <div class="flex items-center gap-1.5 sm:gap-3 shrink-0">
          <!-- User Authenticated State (If logged in as normal user or church admin) -->
          <div v-if="isAuthenticated && user?.role !== 'superadmin'" class="flex min-w-0 items-center gap-2 border-l border-amber-500/20 pl-2 sm:pl-3">
            <div class="flex max-w-[90px] min-w-0 flex-col text-right xs:max-w-[120px] sm:max-w-[180px]">
              <span class="truncate font-serif text-[10px] font-bold tracking-wide text-amber-300 sm:text-xs">{{ user?.name || 'Anggota Jemaat' }}</span>
              <span class="truncate text-[7px] font-serif uppercase tracking-[0.18em] text-slate-300 sm:text-[9px]">{{ user?.role === 'church_admin' ? 'Admin Gereja' : 'Jemaat' }}</span>
            </div>
            
            <button 
              @click="handleLogout" 
              title="Keluar"
              type="button"
              class="p-1.5 text-amber-300/80 hover:text-amber-300 hover:bg-amber-950/60 rounded border border-amber-500/30 transition cursor-pointer shrink-0"
            >
              <svg class="nav-icon w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            </button>
          </div>

          <!-- Guest Option Trigger Button (If NOT logged in) -->
          <button 
            v-else
            @click.stop="openAuthModal"
            title="Masuk atau Daftar"
            type="button"
            class="inline-flex shrink-0 items-center justify-center gap-1.5 rounded border border-amber-500/60 bg-amber-500/10 px-2.5 py-1.5 text-[9px] font-serif uppercase tracking-[0.08em] text-amber-300 shadow-md transition duration-300 hover:bg-amber-400 hover:text-slate-950 sm:px-3.5 sm:py-2 sm:text-[11px]"
          >
            <svg class="h-3.5 w-3.5 shrink-0 sm:h-4 sm:w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            <span class="hidden sm:inline">Masuk / Daftar</span>
            <span class="sm:hidden text-[9px]">Akses</span>
          </button>

          <!-- Theme Toggle -->
          <div class="shrink-0 scale-90 sm:scale-100">
            <ThemeToggleButton />
          </div>

          <!-- Mobile Menu Button -->
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            type="button"
            class="md:hidden p-1.5 sm:p-2 text-amber-300 hover:bg-slate-900 border border-amber-500/40 rounded cursor-pointer shrink-0 flex items-center justify-center"
            title="Menu Navigasi Mobile"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

      </div>
    </div>

    <!-- Responsive Mobile Dropdown Drawer with Backdrop -->
    <Teleport to="body">
      <Transition name="fade">
        <div 
          v-if="isMobileMenuOpen" 
          class="lg:hidden fixed inset-0 z-50 bg-slate-950/75 backdrop-blur-sm"
          @click="isMobileMenuOpen = false"
        ></div>
      </Transition>

      <Transition name="slide-down">
        <div 
          v-if="isMobileMenuOpen" 
          class="lg:hidden fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-[#0b1329] via-[#070c1d] to-[#050814] border-b border-amber-500/40 shadow-2xl p-4 sm:p-5 text-slate-100 font-sans max-h-[85vh] overflow-y-auto"
        >
          <!-- Drawer Header -->
          <div class="flex items-center justify-between pb-3 border-b border-amber-500/20 mb-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 rounded-full border border-amber-500/40 bg-slate-900 flex items-center justify-center overflow-hidden shrink-0">
                <img src="@/assets/images/GracePoint.png" alt="logo" class="w-full h-full object-cover">
              </div>
              <div class="flex flex-col">
                <span class="font-serif text-sm font-bold text-amber-300 tracking-wider">GRACEPOINT</span>
                <span class="text-[9px] font-serif text-slate-400 uppercase tracking-wider">Kalender & Liturgi Gereja</span>
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

          <!-- Mobile Nav Links Cards -->
          <div class="space-y-1.5">
            <RouterLink 
              to="/" 
              @click="isMobileMenuOpen = false"
              class="flex items-center justify-between px-3.5 py-2 rounded-xl border border-transparent hover:border-amber-500/30 hover:bg-amber-500/10 text-slate-200 hover:text-amber-300 transition text-xs font-medium"
            >
              <span class="flex items-center gap-2.5">
                <span>🏠</span>
                <span>Beranda Utama</span>
              </span>
              <span class="text-[10px] text-amber-400 font-mono">Home</span>
            </RouterLink>

            <a 
              href="#kalender" 
              @click="isMobileMenuOpen = false"
              class="flex items-center justify-between px-3.5 py-2 rounded-xl border border-transparent hover:border-amber-500/30 hover:bg-amber-500/10 text-slate-200 hover:text-amber-300 transition text-xs font-medium"
            >
              <span class="flex items-center gap-2.5">
                <span>📅</span>
                <span>Lihat Kalender Liturgi</span>
              </span>
              <span class="text-[10px] text-amber-400 font-mono">Cal</span>
            </a>

            <a 
              href="#bigday" 
              @click="isMobileMenuOpen = false"
              class="flex items-center justify-between px-3.5 py-2 rounded-xl border border-transparent hover:border-amber-500/30 hover:bg-amber-500/10 text-slate-200 hover:text-amber-300 transition text-xs font-medium"
            >
              <span class="flex items-center gap-2.5">
                <span>✨</span>
                <span>Hari Besar Gerejawi</span>
              </span>
              <span class="text-[10px] text-amber-400 font-mono">Big Days</span>
            </a>
          </div>

          <!-- Bottom User or Login Actions in Drawer -->
          <div class="mt-4 pt-3 border-t border-amber-500/20">
            <div v-if="isAuthenticated" class="flex items-center justify-between bg-slate-900/80 p-2.5 rounded-xl border border-amber-500/20">
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

            <button 
              v-else
              @click="openAuthModal" 
              type="button"
              class="w-full py-2.5 px-4 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-serif font-bold text-xs uppercase tracking-wider rounded-xl shadow-lg transition flex items-center justify-center gap-2 cursor-pointer"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
              <span>Masuk atau Daftar Akun</span>
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </header>

  <!-- MODAL PILIHAN MASUK & DAFTAR (Teleport ke Body + Responsif Tinggi Smartphone) -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div 
        v-if="isAuthModalOpen" 
        class="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-slate-950/85 backdrop-blur-md"
        @click.self="isAuthModalOpen = false"
      >
        <div class="w-full max-w-2xl max-h-[92vh] overflow-y-auto custom-scrollbar bg-[#091129] border border-amber-500/40 rounded-2xl p-4 sm:p-6 md:p-8 shadow-2xl relative font-serif text-slate-100 animate-scaleUp">
          
          <!-- Close Button dengan Bootstrap Icon -->
          <button 
            @click="isAuthModalOpen = false"
            type="button"
            class="absolute top-3 right-3 sm:top-4 sm:right-4 text-slate-300 hover:text-amber-300 p-1.5 rounded-lg border border-slate-700 hover:bg-[#0b1435] transition cursor-pointer z-10 flex items-center justify-center"
          >
            <i class="bi bi-x-lg fs-5"></i>
          </button>

          <!-- Modal Header dengan Bootstrap Icon -->
          <div class="text-center pb-4 sm:pb-5 border-b border-amber-500/20 mb-4 sm:mb-6">
            <div class="w-11 h-11 sm:w-12 sm:h-12 mx-auto rounded-full bg-amber-500/10 border border-amber-400/40 text-amber-300 flex items-center justify-center mb-2 shadow-inner">
              <i class="bi bi-shield-lock-fill text-amber-300 fs-4"></i>
            </div>
            <h2 class="text-xl sm:text-2xl font-bold text-amber-300 tracking-wide">PORTAL AKSES GRACEPOINT</h2>
            <p class="text-xs sm:text-sm text-slate-200 font-sans mt-1.5 font-medium">Pilih jenis akun untuk masuk atau daftarkan akun baru Anda.</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5 md:gap-6 font-sans">
            
            <!-- SEKSI 1: MASUK (LOGIN) -->
            <div class="space-y-3 p-3.5 sm:p-4 bg-slate-900/90 border border-amber-500/30 rounded-xl">
              <div class="flex items-center gap-2 pb-2.5 border-b border-amber-500/30 text-amber-300 text-xs sm:text-sm font-bold uppercase tracking-wider font-serif">
                <i class="bi bi-box-arrow-in-right me-1 text-amber-400 fs-6"></i>
                <span>1. MASUK KE SISTEM (LOGIN)</span>
              </div>

              <!-- Portal Masuk Terpadu -->
              <button 
                @click="navigateTo('/verification-login')" 
                type="button"
                class="w-full p-3 sm:p-3.5 bg-[#070c1e] hover:bg-amber-950/40 border border-amber-500/30 hover:border-amber-400 rounded-lg text-left transition group flex items-center gap-3.5 cursor-pointer shadow-sm"
              >
                <div class="w-9 h-9 rounded-lg bg-amber-500/15 border border-amber-500/40 flex items-center justify-center text-amber-300 flex-shrink-0 group-hover:scale-110 transition">
                  <i class="bi bi-shield-lock-fill fs-5"></i>
                </div>
                <div>
                  <h4 class="text-sm sm:text-base font-bold text-white group-hover:text-amber-300 leading-tight">Masuk ke Sistem</h4>
                  <p class="text-xs text-slate-300 group-hover:text-slate-100 mt-0.5">Portal Otentikasi & Verifikasi Satu Jalur Terpadu</p>
                </div>
              </button>
            </div>

            <!-- SEKSI 2: DAFTAR (REGISTER) -->
            <div class="space-y-3 p-3.5 sm:p-4 bg-slate-900/90 border border-amber-500/30 rounded-xl flex flex-col justify-between">
              <div class="space-y-3">
                <div class="flex items-center gap-2 pb-2.5 border-b border-amber-500/30 text-amber-300 text-xs sm:text-sm font-bold uppercase tracking-wider font-serif">
                  <i class="bi bi-person-badge-fill me-1 text-amber-400 fs-6"></i>
                  <span>2. PILIHAN PENDAFTARAN (REGISTER)</span>
                </div>

                <!-- Daftar Sebagai User / Jemaat Baru -->
                <button 
                  @click="navigateTo('/user-register')" 
                  type="button"
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

                <!-- Daftar Sebagai Admin Gereja Baru -->
                <button 
                  @click="navigateTo('/church-register')" 
                  type="button"
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

/* Apply Classic Serif Fonts */
.font-serif {
  font-family: 'Cinzel', 'Playfair Display', Georgia, 'Times New Roman', serif;
}

.classic-link {
  color: #ffffff;
}

/* Announcement Carousel Transition */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-slide-enter-from { opacity: 0; transform: translateY(100%); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-100%); }

/* Mobile Menu Transition */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

/* Modal Fade Animation */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Slim custom scrollbar for modal mobile view */
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

/* Classic Link Underline Effect */
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
.active-link::after {
  width: 100%;
}

/* Strict SVG sizes */
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

@media (max-width: 420px) {
  .classic-link {
    font-size: 9px;
    letter-spacing: 0.08em;
  }
}

a {
  text-decoration: none;
}
</style>
