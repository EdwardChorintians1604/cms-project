<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useSidebar } from '@/composables/useSidebar'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { toggleSidebar, closeSidebar } = useSidebar()

const isUserMenuOpen = ref(false)

// Robust reactive user resolution
const user = computed(() => {
  const u = authStore.user?.value !== undefined ? authStore.user.value : authStore.user
  return u || authStore.state?.user || null
})

const handleLogout = () => {
  isUserMenuOpen.value = false
  authStore.logout()
  closeSidebar()
  router.push('/verification-login')
}

// Announcement ticker
const announcements = ref([
  '✝ Selamat Datang di Portal Jemaat GracePoint — Bertumbuh & Berakar dalam Kasih Kristus',
  '⛪ Ibadah Raya Minggu: Sesi I (08:00 WIB) & Sesi II (17:00 WIB) — Gedung Utama & Live Streaming',
  '📖 "Segala perkara dapat kutanggung di dalam Dia yang memberi kekuatan kepadaku" — Filipi 4:13',
  '🕊️ Layanan Doa & Konseling Pastoral Tersedia — Hubungi Sekretariat: (021) 555-0199',
  '📰 Warta Jemaat: Pendaftaran Kelas Katekisasi & Baptisan Kudus Telah Dibuka',
])
const currentTickerIndex = ref(0)
let tickerTimer = null

// Nav links for jemaat
const navLinks = [
  {
    name: 'Beranda',
    path: '/dashboard-user',
    icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
  },
  {
    name: 'Warta Jemaat',
    path: '/berita-jemaat',
    icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z'
  },
  {
    name: 'Pelayanan',
    path: '/informasi-pelayanan',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
  },
  {
    name: 'Hari Besar',
    path: '/hari-besar',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'
  },
  {
    name: 'Sejarah Gereja',
    path: '/sejarah-gereja',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
  },
  {
    name: 'Peta Gereja',
    path: '/informasi-pelayanan#peta',
    icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7'
  },
]

const isActive = (path) => {
  if (path === '/dashboard-user') return route.path === '/dashboard-user'
  return route.path.startsWith(path.split('#')[0])
}

onMounted(() => {
  if (authStore.isAuthenticated && authStore.fetchUser) {
    authStore.fetchUser().catch(() => {})
  }
  tickerTimer = setInterval(() => {
    currentTickerIndex.value = (currentTickerIndex.value + 1) % announcements.value.length
  }, 5000)
})

onUnmounted(() => {
  if (tickerTimer) clearInterval(tickerTimer)
})
</script>

<template>
  <header class="bg-[#070b15] text-slate-100 sticky top-0 z-40 shadow-xl backdrop-blur-2xl transition-all duration-300 w-full">

    <!-- Announcement Ticker Bar -->
    <div class="bg-gradient-to-r from-slate-950 via-[#0f1b33] to-slate-950 border-b border-amber-500/25 text-amber-100/90 py-1 px-4 text-center font-serif text-[11px] sm:text-xs tracking-wider flex justify-between items-center h-7 relative overflow-hidden">
      <div class="hidden sm:flex items-center gap-1.5 text-[10px] text-amber-400/80 font-sans uppercase tracking-widest">
        <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
        <span>Warta Hari Ini</span>
      </div>

      <div class="flex-1 flex items-center justify-center overflow-hidden px-2">
        <Transition name="ticker" mode="out-in">
          <span :key="currentTickerIndex" class="truncate ticker-text text-amber-200 font-medium drop-shadow-sm">
            {{ announcements[currentTickerIndex] }}
          </span>
        </Transition>
      </div>

      <div class="hidden md:flex items-center gap-1.5 text-[10px] text-slate-300 font-sans">
        <span class="flex items-center gap-1 text-emerald-400">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>Portal Aktif</span>
        </span>
      </div>
    </div>

    <!-- Main Navigation Bar -->
    <div class="border-b border-amber-500/20 w-full px-4 sm:px-6">
      <div class="flex items-center justify-between h-16 gap-3">

        <!-- Left: Sidebar Toggle & Brand -->
        <div class="flex items-center gap-3 shrink-0">
          <button
            @click="toggleSidebar"
            aria-label="Buka menu navigasi"
            class="p-2 text-slate-300 hover:text-amber-400 hover:bg-amber-500/15 rounded-xl border border-slate-800 hover:border-amber-500/30 transition-all duration-200 cursor-pointer"
            title="Toggle Menu Sidebar"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>

          <router-link to="/dashboard-user" class="flex items-center gap-2.5 group no-underline shrink-0">
            <div class="relative w-9 h-9 rounded-2xl p-[1.5px] bg-gradient-to-tr from-amber-500 via-amber-300 to-amber-600 shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform duration-300 shrink-0">
              <div class="w-full h-full rounded-[14px] bg-slate-950 flex items-center justify-center overflow-hidden">
                <img src="@/assets/images/GracePoint.png" alt="GracePoint" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              </div>
              <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 border-2 border-slate-950" title="Online"></span>
            </div>
            <div class="flex flex-col">
              <div class="flex items-center gap-1.5">
                <span class="text-sm font-extrabold text-white leading-none tracking-wide group-hover:text-amber-300 transition">GracePoint</span>
                <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase tracking-widest hidden lg:inline-block">Jemaat</span>
              </div>
              <span class="text-[10px] text-slate-400 font-semibold tracking-wider mt-0.5">Portal Jemaat &amp; Pelayanan</span>
            </div>
          </router-link>
        </div>

        <!-- Center: Nav Pills (md+) -->
        <nav class="hidden md:flex items-center gap-1 bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800/90 shadow-inner max-w-full overflow-x-auto no-scrollbar">
          <router-link
            v-for="(link, i) in navLinks"
            :key="i"
            :to="link.path"
            class="px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all duration-200 shrink-0 no-underline"
            :class="isActive(link.path)
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
              : 'text-slate-300 hover:text-amber-300 hover:bg-amber-500/10'"
          >
            <svg class="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="link.icon"/>
            </svg>
            <span class="whitespace-nowrap hidden lg:inline">{{ link.name }}</span>
          </router-link>
        </nav>

        <!-- Right: Theme + Portal Status + User Dropdown -->
        <div class="flex items-center gap-2 sm:gap-3 shrink-0">
          <!-- Theme Toggle -->
          <ThemeToggleButton />

          <!-- Portal Active Status (xl+) -->
          <div class="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-300 text-xs font-semibold">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
            </span>
            <span>Portal Jemaat</span>
          </div>

          <!-- Pokok Doa shortcut (sm+) -->
          <router-link
            to="/dashboard-user#doa"
            class="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 text-xs font-medium transition cursor-pointer no-underline"
            title="Pokok Doa & Konseling"
          >
            <span>🕊️</span>
            <span class="hidden md:inline">Pokok Doa</span>
          </router-link>

          <!-- User Dropdown -->
          <div class="relative">
            <button
              @click="isUserMenuOpen = !isUserMenuOpen"
              aria-label="Menu akun jemaat"
              :aria-expanded="isUserMenuOpen"
              class="flex items-center gap-2 p-1.5 pl-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 text-slate-200 hover:text-amber-300 transition duration-200 cursor-pointer shadow-sm"
            >
              <!-- Avatar -->
              <div class="w-7 h-7 rounded-full overflow-hidden border-2 border-amber-400/60 bg-gradient-to-tr from-amber-600 to-slate-900 flex items-center justify-center shrink-0">
                <img v-if="user?.photo_url" :src="user.photo_url" :alt="user?.full_name" class="w-full h-full object-cover" />
                <span v-else class="text-xs font-bold text-amber-300 uppercase">
                  {{ user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'J' }}
                </span>
              </div>
              <span class="hidden sm:inline text-xs font-bold tracking-wide truncate max-w-[90px]">
                {{ user?.full_name || user?.username || 'Jemaat' }}
              </span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200" :class="{ 'rotate-180': isUserMenuOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Backdrop -->
            <div
              v-if="isUserMenuOpen"
              @click="isUserMenuOpen = false"
              class="fixed inset-0 z-40 bg-transparent"
            ></div>

            <!-- Dropdown Box -->
            <Transition name="dropdown">
              <div
                v-if="isUserMenuOpen"
                class="absolute right-0 mt-2 w-64 bg-slate-900/98 border border-amber-500/30 rounded-2xl shadow-2xl p-2 z-50 text-xs backdrop-blur-xl"
              >
                <!-- User Header Card -->
                <div class="px-3 py-2.5 border-b border-slate-800 bg-slate-950/60 rounded-xl mb-1 space-y-0.5">
                  <div class="flex items-center gap-2.5">
                    <div class="w-9 h-9 rounded-full overflow-hidden border-2 border-amber-400/60 bg-slate-800 flex items-center justify-center shrink-0">
                      <img v-if="user?.photo_url" :src="user.photo_url" class="w-full h-full object-cover" />
                      <span v-else class="text-sm font-bold text-amber-300 uppercase">
                        {{ user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'J' }}
                      </span>
                    </div>
                    <div class="min-w-0">
                      <p class="font-extrabold text-white truncate">{{ user?.full_name || user?.username || 'Jemaat GracePoint' }}</p>
                      <p class="text-[10px] text-amber-400/90 font-mono truncate mt-0.5">{{ user?.email || 'jemaat@gracepoint.org' }}</p>
                      <div class="flex items-center gap-1 mt-0.5">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        <p class="text-[9px] text-slate-500 uppercase tracking-wider">{{ user?.church_domisili || 'Jemaat GracePoint' }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Menu Links -->
                <router-link
                  to="/dashboard-user"
                  @click="isUserMenuOpen = false"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:bg-amber-500/15 hover:text-amber-300 transition no-underline"
                >
                  <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                  </svg>
                  <div>
                    <p class="font-medium">Beranda &amp; Profil Saya</p>
                    <p class="text-[10px] text-slate-400">Kelola data keanggotaan jemaat</p>
                  </div>
                </router-link>

                <router-link
                  to="/berita-jemaat"
                  @click="isUserMenuOpen = false"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:bg-amber-500/15 hover:text-amber-300 transition no-underline"
                >
                  <svg class="w-4 h-4 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
                  </svg>
                  <div>
                    <p class="font-medium">Warta &amp; Berita Jemaat</p>
                    <p class="text-[10px] text-slate-400">Pengumuman &amp; informasi terkini</p>
                  </div>
                </router-link>

                <router-link
                  to="/informasi-pelayanan"
                  @click="isUserMenuOpen = false"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:bg-amber-500/15 hover:text-amber-300 transition no-underline"
                >
                  <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <div>
                    <p class="font-medium">Pelayanan &amp; Sakramen</p>
                    <p class="text-[10px] text-slate-400">Baptisan, pernikahan &amp; konseling</p>
                  </div>
                </router-link>

                <router-link
                  to="/dashboard-user#doa"
                  @click="isUserMenuOpen = false"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:bg-amber-500/15 hover:text-amber-300 transition no-underline"
                >
                  <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.684a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                  </svg>
                  <div>
                    <p class="font-medium">Pokok Doa &amp; Konseling</p>
                    <p class="text-[10px] text-slate-400">Kirimkan permohonan doa pastoral</p>
                  </div>
                </router-link>

                <!-- Logout -->
                <div class="pt-1.5 mt-1 border-t border-slate-800">
                  <button
                    @click="handleLogout"
                    class="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-rose-400 hover:bg-rose-500/15 transition text-left font-bold cursor-pointer"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                    </svg>
                    <span>Keluar dari Portal</span>
                  </button>
                </div>
              </div>
            </Transition>
          </div>
        </div>

      </div>

      <!-- Mobile Sub-nav Strip (< md) -->
      <div class="md:hidden flex items-center gap-1.5 overflow-x-auto py-2 border-t border-slate-800/80 no-scrollbar">
        <router-link
          v-for="(link, i) in navLinks"
          :key="i"
          :to="link.path"
          class="px-3 py-1.5 rounded-xl text-[11px] font-semibold flex items-center gap-1.5 shrink-0 bg-slate-950 border border-slate-800 no-underline transition-all"
          :class="isActive(link.path)
            ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
            : 'text-slate-300 hover:text-amber-300'"
        >
          <svg class="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="link.icon"/>
          </svg>
          <span>{{ link.name }}</span>
        </router-link>
      </div>
    </div>

  </header>
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

.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

/* Ticker animation */
.ticker-text {
  display: block;
  max-width: 90vw;
}

@media (min-width: 640px) {
  .ticker-text { max-width: 60vw; }
}

.ticker-enter-active,
.ticker-leave-active {
  transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.ticker-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.ticker-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Dropdown animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>