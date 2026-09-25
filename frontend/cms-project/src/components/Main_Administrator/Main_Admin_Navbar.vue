<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useSidebar } from '@/composables/useSidebar'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const router = useRouter()
const { logout } = useAuth()
const { toggleSidebar, closeSidebar } = useSidebar()

const isUserMenuOpen = ref(false)

const handleLogout = () => {
  logout()
  closeSidebar()
  router.push({ name: 'main-login' })
}

// Navigasi Khusus Superadmin Console
const navLinks = [
  { name: 'Console Beranda', path: '/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 00-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: 'Statistika Platform', path: '/dashboard#analytics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { name: 'Statistika Gereja', path: '/dashboard#statistika-gereja', icon: 'M4 19V5m0 14h16M8 16v-5m4 5V8m4 8V4'}, 
  { name: 'Audit IT & Keamanan', path: '/audit-it', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
  { name: 'Manajemen Data', path: '/dashboard#management', icon: 'M4 6c0-1.105 3.582-2 8-2s8 .895 8 2-3.582 2-8 2-8-.895-8-2Zm0 0v6c0 1.105 3.582 2 8 2s8-.895 8-2V6m-16 6v6c0 1.105 3.582 2 8 2s8-.895 8-2v-6'},
  { name: 'Back-Up Data', path: '/backup-database',
    icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543-.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543-.826-3.31zM12 15a3 3 0 100-6 3 3 0 000 6z' }
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

          <router-link to="/dashboard" class="flex items-center gap-2.5 group no-underline">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-600 via-amber-500 to-yellow-400 p-0.5 shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform duration-300 shrink-0">
              <div class="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center font-black text-amber-400 text-sm tracking-tighter">
                GP
              </div>
            </div>
            <div class="flex flex-col">
              <div class="flex items-center gap-2">
                <span class="text-sm font-extrabold text-white leading-none tracking-wide group-hover:text-amber-300 transition">GracePoint</span>
                <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase tracking-widest hidden lg:inline-block">Console</span>
              </div>
              <span class="text-[10px] text-slate-400 font-semibold tracking-wider mt-0.5">System Superadmin</span>
            </div>
          </router-link>
        </div>

        <!-- Center Nav Items (Flexible horizontal pills) -->
        <nav class="hidden md:flex items-center gap-1.5 bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800/90 shadow-inner max-w-full overflow-x-auto no-scrollbar">
          <router-link
            v-for="(link, i) in navLinks"
            :key="i"
            :to="link.path"
            class="px-3.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all duration-200 text-slate-300 hover:text-amber-300 hover:bg-amber-500/10 shrink-0 no-underline"
            active-class="bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm"
          >
            <svg class="w-4 h-4 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="link.icon"/>
            </svg>
            <span class="whitespace-nowrap text-slate-200 hover:text-amber-300">{{ link.name }}</span>
          </router-link>
        </nav>

        <!-- Right: Status Badge & User Dropdown -->
        <div class="flex items-center gap-2.5 sm:gap-3 shrink-0">
          <!-- Theme Toggle Button -->
          <ThemeToggleButton />

          <!-- PostgreSQL Status Indicator -->
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
              aria-label="Buka menu akun superadmin"
              :aria-expanded="isUserMenuOpen"
              class="flex items-center gap-2.5 p-1.5 pl-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 text-slate-200 hover:text-amber-300 transition duration-200 cursor-pointer shadow-sm"
            >
              <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-amber-500 to-yellow-400 text-slate-950 font-black text-xs flex items-center justify-center shadow">
                SA
              </div>
              <span class="hidden sm:inline text-xs font-bold tracking-wide">Superadmin</span>
              <svg class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200" :class="{ 'rotate-180': isUserMenuOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Dropdown Backdrop Overlay -->
            <div 
              v-if="isUserMenuOpen" 
              @click="isUserMenuOpen = false" 
              class="fixed inset-0 z-40 bg-transparent"
            ></div>

            <!-- Dropdown Menu Box -->
            <Transition name="dropdown">
              <div 
                v-if="isUserMenuOpen"
                class="absolute right-0 mt-2 w-56 bg-slate-900/95 border border-amber-500/30 rounded-2xl shadow-2xl p-2 z-50 text-xs backdrop-blur-xl"
              >
                <div class="px-3 py-2.5 border-b border-slate-800 bg-slate-950/60 rounded-xl mb-1">
                  <p class="font-extrabold text-white">Superadmin Console</p>
                  <p class="text-[10px] text-amber-400/90 font-mono truncate mt-0.5">ambatukam09@gmail.com</p>
                </div>
                
                <router-link 
                  to="/dashboard" 
                  @click="isUserMenuOpen = false"
                  class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:bg-amber-500/15 hover:text-amber-300 transition no-underline"
                >
                  <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                  <span>Overview Console</span>
                </router-link>

                <button 
                  @click="handleLogout"
                  class="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-rose-400 hover:bg-rose-500/15 transition text-left font-bold mt-1 cursor-pointer"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  <span>Keluar Console</span>
                </button>
              </div>
            </Transition>
          </div>

        </div>

      </div>

      <!-- Mobile Sub-nav Strip -->
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
/* Reset any Bootstrap pollution */
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
