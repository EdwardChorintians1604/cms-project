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
const isAuthModalOpen = ref(false)

const announcements = ref([
  '✝ Soli Deo Gloria — Pelayanan Jemaat & Sistem Informasi Gereja',
  '⛪ Jadwal Ibadah Raya Minggu: Sesi I (08:00 WIB) & Sesi II (17:00 WIB)',
  '📞 Kontak Sekretariat & Layanan Doa: (021) 555-0199 / WhatsApp 0812-3456-7890',
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
    <div class="bg-gradient-to-r from-amber-950 via-amber-900 to-amber-950 border-b border-amber-500/40 text-amber-100 py-1.5 px-4 text-center font-serif text-[11px] sm:text-xs tracking-wider uppercase flex justify-center items-center h-8 relative overflow-hidden shadow-inner">
      <Transition name="fade-slide" mode="out-in">
        <div :key="currentAnnouncementIndex" class="flex items-center justify-center gap-2 w-full text-amber-200 font-semibold px-2">
          <span class="truncate">{{ announcements[currentAnnouncementIndex] }}</span>
        </div>
      </Transition>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        <div class="flex items-center gap-2">
          <button @click="toggleSidebar" title="Toggle Sidebar" class="p-2 text-amber-300 hover:text-amber-100 border border-amber-500/30 rounded transition mr-1">
            <svg class="nav-icon w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h10M4 18h16"/></svg>
          </button>
          <RouterLink to="/" class="flex items-center gap-3.5 group cursor-pointer">
            <div class="w-11 h-11 rounded-full border-2 border-amber-400/80 bg-slate-900 flex items-center justify-center">
              <svg class="emblem-cross-svg w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2v20m-7-14h14"></path></svg>
            </div>
            <div class="flex flex-col">
              <span class="font-serif text-xl font-bold tracking-wider text-amber-300">SYSTEMKITA</span>
              <span class="text-[10px] font-serif text-slate-300 uppercase">Gereja & Pelayanan Jemaat</span>
            </div>
          </RouterLink>
        </div>

        <div class="flex items-center gap-3 sm:gap-4">
          <ThemeToggleButton />
          <div v-if="isAuthenticated" class="flex items-center gap-3 pl-3 border-l border-amber-500/20">
            <span class="font-serif text-xs text-amber-300">{{ user?.name || 'Pelayan Jemaat' }}</span>
            <button @click="handleLogout" class="p-1.5 text-amber-300/80 hover:text-amber-300 rounded border border-amber-500/30">Logout</button>
          </div>
          <button v-else @click.stop="openAuthModal" class="px-4 py-2 text-xs font-serif uppercase tracking-widest text-amber-300 border border-amber-500/60 bg-amber-500/10 hover:bg-amber-400 hover:text-slate-950 rounded-sm transition">
            Masuk atau Daftar
          </button>
        </div>
      </div>
    </div>
  </header>

  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isAuthModalOpen" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md" @click.self="isAuthModalOpen = false">
        <div class="w-full max-w-2xl bg-[#0a101d] border border-amber-500/40 rounded-2xl p-6 sm:p-8 shadow-2xl relative font-serif text-slate-100">
          <button @click="isAuthModalOpen = false" class="absolute top-4 right-4 text-slate-400 hover:text-amber-300 p-1.5 rounded-lg border border-slate-800">✕</button>
          <div class="text-center pb-5 border-b border-amber-500/20 mb-6">
            <h2 class="text-2xl font-bold text-amber-300">Portal Akses SystemKita</h2>
            <p class="text-xs text-slate-400 font-sans mt-1">Pilih jenis akun untuk masuk atau daftarkan akun baru Anda.</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 font-sans">
            <div class="space-y-3 p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
              <span class="text-amber-400 text-xs font-bold uppercase font-serif">🔑 1. Pilihan Masuk</span>
              <button @click="navigateTo('/login?role=main_admin')" class="w-full p-3 bg-slate-950 border border-amber-500/30 hover:border-amber-400 rounded-lg text-left text-xs font-bold text-slate-100">👑 Admin Utama</button>
              <button @click="navigateTo('/login?role=church_admin')" class="w-full p-3 bg-slate-950 border border-amber-500/30 hover:border-amber-400 rounded-lg text-left text-xs font-bold text-slate-100">⛪ Admin Gereja</button>
              <button @click="navigateTo('/login?role=user')" class="w-full p-3 bg-slate-950 border border-amber-500/30 hover:border-amber-400 rounded-lg text-left text-xs font-bold text-slate-100">👤 User / Jemaat</button>
            </div>
            <div class="space-y-3 p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
              <span class="text-amber-400 text-xs font-bold uppercase font-serif">📝 2. Pilihan Pendaftaran</span>
              <button @click="navigateTo('/user-register')" class="w-full p-3 bg-slate-950 border border-emerald-500/30 hover:border-emerald-400 rounded-lg text-left text-xs font-bold text-slate-100">✝️ Daftar User / Jemaat</button>
              <button @click="navigateTo('/church-register')" class="w-full p-3 bg-slate-950 border border-emerald-500/30 hover:border-emerald-400 rounded-lg text-left text-xs font-bold text-slate-100">🏛️ Daftar Admin Gereja</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.font-serif { font-family: 'Cinzel', 'Playfair Display', serif; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
svg.emblem-cross-svg { width: 20px !important; height: 20px !important; }
svg.nav-icon { width: 15px !important; height: 15px !important; }
</style>
