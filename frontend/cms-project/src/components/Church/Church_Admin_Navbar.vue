<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useSidebar } from '@/composables/useSidebar'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const router = useRouter()
const { user, logout } = useAuth()
const { toggleSidebar, closeSidebar } = useSidebar()

const isUserMenuOpen = ref(false)

const handleLogout = () => {
  logout()
  closeSidebar()
  router.push('/verification-login')
}

// Navigasi Khusus Admin Gereja
const navLinks = [
  { name: 'Dashboard', path: '/dashboard-church', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: 'Geolocation', path: '/dashboard-church#geolocation', icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z' },
  { name: 'Pelayanan', path: '/dashboard-church#pelayanan-cabang', icon: 'M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z' },
  { name: 'Peta Gereja', path: '/informasi-pelayanan', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
  { name: 'Hari Besar', path: '/hari-besar', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
  { name: 'Berita', path: '/berita-jemaat', icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z' }
]
</script>

<template>
  <header class="bg-[#070b15] border-b border-amber-500/20 text-slate-100 sticky top-0 z-40 shadow-xl backdrop-blur-2xl transition-all duration-300 w-full">
    <div class="w-full px-4 sm:px-6">
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

          <router-link to="/dashboard-church" class="flex items-center gap-2.5 group no-underline">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-600 via-amber-500 to-yellow-400 p-0.5 shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform duration-300 shrink-0">
              <div class="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center font-black text-amber-400 text-sm tracking-tighter">
                CA
              </div>
            </div>
            <div class="flex flex-col">
              <div class="flex items-center gap-2">
                <span class="text-sm font-extrabold text-white leading-none tracking-wide group-hover:text-amber-300 transition">GracePoint</span>
                <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase tracking-widest hidden lg:inline-block">Church Admin</span>
              </div>
              <span class="text-[10px] text-slate-400 font-semibold tracking-wider mt-0.5">Portal Pengurus Gereja</span>
            </div>
          </router-link>
        </div>

        <!-- Center Nav Items (horizontal pills, md+) -->
        <nav class="hidden md:flex items-center gap-1.5 bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800/90 shadow-inner max-w-full overflow-x-auto no-scrollbar">
          <router-link
            v-for="(link, i) in navLinks"
            :key="i"
            :to="link.path"
            class="px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all duration-200 text-slate-300 hover:text-amber-300 hover:bg-amber-500/10 shrink-0 no-underline"
            active-class="bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm"
          >
            <svg class="w-4 h-4 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="link.icon"/>
            </svg>
            <span class="whitespace-nowrap hidden lg:inline text-slate-200 hover:text-amber-300">{{ link.name }}</span>
          </router-link>
        </nav>

        <!-- Right: Theme + Status + User Dropdown -->
        <div class="flex items-center gap-2.5 sm:gap-3 shrink-0">
          <!-- Theme Toggle -->
          <ThemeToggleButton />

          <!-- DB Status (xl+ only) -->
          <div class="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-xs font-semibold">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>PostgreSQL Active</span>
          </div>

          <!-- User Menu Dropdown -->
          <div class="relative">
            <button
              @click="isUserMenuOpen = !isUserMenuOpen"
              aria-label="Buka menu akun admin gereja"
              :aria-expanded="isUserMenuOpen"
              class="flex items-center gap-2.5 p-1.5 pl-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 text-slate-200 hover:text-amber-300 transition duration-200 cursor-pointer shadow-sm"
            >
              <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-amber-500 to-yellow-400 text-slate-950 font-black text-xs flex items-center justify-center shadow">
                {{ user?.full_name?.charAt(0) || user?.name?.charAt(0) || 'A' }}
              </div>
              <span class="hidden sm:inline text-xs font-bold tracking-wide truncate max-w-[90px]">
                {{ user?.full_name || user?.name || 'Admin Gereja' }}
              </span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200" :class="{ 'rotate-180': isUserMenuOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Dropdown Backdrop -->
            <div
              v-if="isUserMenuOpen"
              @click="isUserMenuOpen = false"
              class="fixed inset-0 z-40 bg-transparent"
            ></div>

            <!-- Dropdown Box -->
            <Transition name="dropdown">
              <div
                v-if="isUserMenuOpen"
                class="absolute right-0 mt-2 w-60 bg-slate-900/95 border border-amber-500/30 rounded-2xl shadow-2xl p-2 z-50 text-xs backdrop-blur-xl"
              >
                <div class="px-3 py-2.5 border-b border-slate-800 bg-slate-950/60 rounded-xl mb-1">
                  <p class="font-extrabold text-white truncate">{{ user?.full_name || user?.name || 'Admin Gereja' }}</p>
                  <p class="text-[10px] text-amber-400/90 font-mono truncate mt-0.5">{{ user?.email || 'church.admin@gracepoint.org' }}</p>
                  <p class="text-[9px] text-slate-500 mt-0.5 uppercase tracking-wider">Portal Pengurus Gereja</p>
                </div>

                <router-link
                  to="/dashboard-church"
                  @click="isUserMenuOpen = false"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:bg-amber-500/15 hover:text-amber-300 transition no-underline"
                >
                  <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                  </svg>
                  <span>Overview Dashboard</span>
                </router-link>

                <router-link
                  to="/informasi-pelayanan"
                  @click="isUserMenuOpen = false"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:bg-amber-500/15 hover:text-amber-300 transition no-underline"
                >
                  <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span>Halaman Publik Pelayanan</span>
                </router-link>

                <button
                  @click="handleLogout"
                  class="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-rose-400 hover:bg-rose-500/15 transition text-left font-bold mt-1 cursor-pointer"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  <span>Keluar Portal</span>
                </button>
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
          class="px-3 py-1.5 rounded-xl text-[11px] font-semibold flex items-center gap-1.5 shrink-0 bg-slate-950 border border-slate-800 text-slate-300 hover:text-amber-300 no-underline"
          active-class="bg-amber-500/20 text-amber-300 border-amber-500/40"
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

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

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
