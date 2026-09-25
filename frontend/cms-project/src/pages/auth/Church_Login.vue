<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State Form Login Admin Gereja
const churchCode = ref('')
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)

// State Status UI
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// State Modal Lupa Password
const isForgotModalOpen = ref(false)
const forgotEmail = ref('')
const isForgotSubmitting = ref(false)
const forgotMessage = ref('')

onMounted(() => {
  if (typeof route.query.email === 'string') {
    email.value = route.query.email
  }
  if (typeof route.query.churchCode === 'string') {
    churchCode.value = route.query.churchCode
  }
})

// Handler Toggle Visibilitas Password
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// Handler Submit Login Admin Gereja
const handleLogin = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!email.value.trim() || !password.value) {
    errorMessage.value = 'Silakan masukkan Email Admin dan Kata Sandi Anda.'
    return
  }

  isLoading.value = true

  try {
    const res = await authStore.churchLogin({
      email: email.value.trim(),
      password: password.value,
      churchCode: churchCode.value || '',
    })

    if (!res || !res.token) {
      throw new Error('Gagal masuk. Periksa kembali kredensial Admin Gereja Anda.')
    }

    const adminName = authStore.user?.full_name || authStore.user?.admin_name || 'Admin Gereja'
    successMessage.value = `Otentikasi Berhasil! Selamat datang, ${adminName}. Mengalihkan ke Dashboard Cabang...`

    setTimeout(() => router.push('/dashboard-church'), 1200)
  } catch (err) {
    errorMessage.value = err.message || 'Gagal masuk. Periksa kembali kredensial Admin Gereja Anda.'
  } finally {
    isLoading.value = false
  }
}

// Handler Request Reset Password
const handleForgotPassword = async () => {
  if (!forgotEmail.value) return
  isForgotSubmitting.value = true
  forgotMessage.value = ''

  await new Promise((resolve) => setTimeout(resolve, 800))
  forgotMessage.value = 'Tautan petunjuk reset kata sandi telah dikirimkan ke email resmi Admin Gereja.'
  isForgotSubmitting.value = false

  setTimeout(() => {
    isForgotModalOpen.value = false
    forgotMessage.value = ''
    forgotEmail.value = ''
  }, 2500)
}
</script>

<template>
  <div class="min-h-screen bg-[#070d19] text-slate-100 flex flex-col justify-between items-center relative overflow-hidden font-sans selection:bg-amber-500 selection:text-slate-950">
    
    <!-- Background Ambient Glow & Texture -->
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-amber-500/10 blur-[140px] pointer-events-none rounded-full"></div>
    <div class="absolute bottom-0 right-0 w-[500px] h-[500px] bg-sky-500/10 blur-[160px] pointer-events-none rounded-full"></div>

    <!-- Top Navigation Header -->
    <header class="w-full max-w-7xl mx-auto px-4 sm:px-6 py-6 flex items-center justify-between z-10 animate__animated animate__fadeInDown" data-aos="fade-down" data-aos-duration="600">
      <RouterLink to="/" class="flex items-center gap-3 group">
        <div class="w-10 h-10 rounded-full border border-amber-500/40 bg-slate-900 flex items-center justify-center shadow-lg group-hover:border-amber-400 transition transform group-hover:scale-105">
          <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="w-full h-full object-cover">
        </div>
        <div class="flex flex-col">
          <span class="font-serif font-bold text-lg text-amber-300 tracking-wider group-hover:text-amber-200 transition">GRACEPOINT</span>
          <span class="text-[10px] text-slate-400 font-serif tracking-widest uppercase">Portal Admin Gereja</span>
        </div>
      </RouterLink>

      <RouterLink 
        to="/" 
        class="text-xs font-medium text-slate-300 hover:text-amber-300 flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/60 hover:bg-slate-900 transition"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        <span>Kembali ke Beranda</span>
      </RouterLink>
    </header>

    <!-- Main Container -->
    <main class="w-full max-w-md px-4 py-8 z-10 my-auto" data-aos="zoom-in-up" data-aos-duration="800">
      <div class="bg-slate-950/85 border border-amber-500/30 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl relative animate__animated animate__fadeInUp">
        
        <!-- Header Card -->
        <div class="text-center pb-5 border-b border-slate-800/80 mb-6" data-aos="fade-up" data-aos-delay="100">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500/20 to-amber-950/40 border border-amber-400/40 text-amber-300 mb-3 shadow-lg shadow-amber-500/10 animate__animated animate__zoomIn">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <h1 class="text-2xl font-serif font-bold text-amber-300 tracking-wide animate__animated animate__fadeIn">Portal Admin Gereja</h1>
          <p class="text-xs text-slate-400 mt-1">Masuk untuk mengelola jemaat, pelayanan, dan sistem informasi gereja Anda.</p>
        </div>

        <!-- Alert Notification Messages -->
        <div v-if="errorMessage" class="mb-5 p-3.5 text-xs bg-rose-950/80 border border-rose-800 text-rose-200 rounded-xl flex items-start gap-2 animate-fadeIn">
          <span class="text-base leading-none">⚠️</span>
          <span>{{ errorMessage }}</span>
        </div>

        <div v-if="successMessage" class="mb-5 p-3.5 text-xs bg-emerald-950/80 border border-emerald-800 text-emerald-200 rounded-xl flex items-start gap-2 animate-fadeIn">
          <span class="text-base leading-none">✅</span>
          <span>{{ successMessage }}</span>
        </div>

        <!-- Form Login -->
        <form @submit.prevent="handleLogin" class="space-y-4 text-xs">
          
          <!-- Field 1: Kode Gereja -->
          <div data-aos="fade-up" data-aos-delay="150">
            <label class="block font-medium text-slate-300 mb-1">
              Nama / Kode Gereja Cabang <span class="text-slate-500 font-normal">(Opsional)</span>
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
              </div>
              <input
                v-model="churchCode"
                type="text"
                autocomplete="organization"
                placeholder="Masukkan kode gereja (opsional)"
                class="w-full pl-9 pr-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-amber-400 transition"
              />
            </div>
            <p class="mt-1 text-[11px] text-slate-500">
              Isi jika akun Anda terikat pada kode gereja tertentu.
            </p>
          </div>

          <!-- Field 2: Email Admin -->
          <div data-aos="fade-up" data-aos-delay="200">
            <label class="block font-medium text-slate-300 mb-1">Email Pengurus / Admin <span class="text-rose-400">*</span></label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
                </svg>
              </div>
              <input 
                v-model="email" 
                type="text" 
                required 
                placeholder="admin@gereja.or.id" 
                class="w-full pl-9 pr-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-amber-400 transition placeholder:text-slate-500" 
              />
            </div>
          </div>

          <!-- Field 3: Kata Sandi -->
          <div data-aos="fade-up" data-aos-delay="250">
            <div class="flex items-center justify-between mb-1">
              <label class="font-medium text-slate-300">Kata Sandi <span class="text-rose-400">*</span></label>
              <button 
                @click="isForgotModalOpen = true" 
                type="button" 
                class="text-[11px] text-amber-400 hover:text-amber-300 hover:underline cursor-pointer"
              >
                Lupa Kata Sandi?
              </button>
            </div>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
              </div>
              <input 
                v-model="password" 
                :type="showPassword ? 'text' : 'password'" 
                required 
                placeholder="••••••••••••" 
                class="w-full pl-9 pr-10 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-amber-400 transition" 
              />
              <button 
                @click="togglePasswordVisibility" 
                type="button" 
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-amber-300 transition cursor-pointer"
              >
                <svg v-if="!showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858-5.908a10.038 10.038 0 012.122-.363c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21M3 3l18 18"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Remember Me Checkbox -->
          <div class="flex items-center gap-2 pt-1">
            <input 
              v-model="rememberMe" 
              id="remember" 
              type="checkbox" 
              class="w-4 h-4 rounded bg-slate-900 border-slate-700 text-amber-500 focus:ring-amber-400 focus:ring-offset-slate-950 cursor-pointer"
            />
            <label for="remember" class="text-[11px] text-slate-300 cursor-pointer">Ingat sesi login di perangkat ini</label>
          </div>

          <!-- Submit Button -->
          <div data-aos="fade-up" data-aos-delay="300">
            <button 
              type="submit" 
              :disabled="isLoading" 
              class="w-full py-3 mt-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-serif font-bold text-xs uppercase tracking-wider rounded-xl shadow-lg shadow-amber-500/20 transition transform active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
            >
              <svg v-if="isLoading" class="w-4 h-4 animate-spin text-slate-950" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="isLoading">Mengautentikasi...</span>
              <span v-else>Masuk ke Portal Cabang</span>
            </button>
          </div>
        </form>

        <!-- Footer Card Options -->
        <div class="mt-6 pt-5 border-t border-slate-800 text-center space-y-3 text-xs font-sans" data-aos="fade-up" data-aos-delay="350">
          <p class="text-slate-400">
            Belum mendaftarkan gereja Anda?
            <RouterLink to="/church-register" class="text-amber-300 font-semibold hover:underline ml-1">
              Daftar Gereja Baru
            </RouterLink>
          </p>

          <div class="pt-2 flex justify-center items-center gap-3 text-[11px] text-slate-400">
            <span>Masuk Sebagai:</span>
            <RouterLink to="/verification-login" class="text-sky-400 hover:underline font-medium">👤 Portal Masuk Terpadu</RouterLink>
            <span>•</span>
            <RouterLink to="/main-login" class="text-amber-400 hover:underline font-medium">👑 Main Admin</RouterLink>
          </div>
        </div>

      </div>
    </main>

    <!-- Footer Copyright -->
    <footer class="w-full py-4 text-center text-xs text-slate-500 z-10">
      &copy; 2026 GracePoint — Platform Manajemen & Pelayanan Digital Gereja
    </footer>

    <!-- MODAL LUPA KATA SANDI -->
    <Teleport to="body">
      <div 
        v-if="isForgotModalOpen" 
        class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm"
        @click.self="isForgotModalOpen = false"
      >
        <div class="w-full max-w-md bg-slate-950 border border-amber-500/40 rounded-2xl p-6 shadow-2xl relative font-sans text-slate-100">
          <button 
            @click="isForgotModalOpen = false" 
            type="button" 
            class="absolute top-4 right-4 text-slate-400 hover:text-amber-300 p-1 rounded-lg border border-slate-800 transition cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>

          <div class="text-center mb-5">
            <div class="w-10 h-10 mx-auto rounded-full bg-amber-500/10 border border-amber-400/40 text-amber-300 flex items-center justify-center mb-2">
              🔑
            </div>
            <h3 class="text-lg font-serif font-bold text-amber-300">Pemulihan Kata Sandi Admin</h3>
            <p class="text-xs text-slate-400 mt-1">Masukkan email resmi pengurus gereja untuk menerima instruksi pemulihan.</p>
          </div>

          <div v-if="forgotMessage" class="mb-4 p-3 text-xs bg-emerald-950/80 border border-emerald-800 text-emerald-200 rounded-xl">
            ✅ {{ forgotMessage }}
          </div>

          <form @submit.prevent="handleForgotPassword" class="space-y-4 text-xs">
            <div>
              <label class="block font-medium text-slate-300 mb-1">Email Admin Gereja</label>
              <input 
                v-model="forgotEmail" 
                type="email" 
                required 
                placeholder="admin@gereja.or.id" 
                class="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-amber-400 transition"
              />
            </div>

            <button 
              type="submit" 
              :disabled="isForgotSubmitting" 
              class="w-full py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl transition text-xs shadow cursor-pointer"
            >
              <span v-if="isForgotSubmitting">Mengirim Petunjuk...</span>
              <span v-else>Kirim Tautan Pemulihan</span>
            </button>
          </form>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}
</style>