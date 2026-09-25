<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// State Form Login
const loginMode = ref('email') // 'email' | 'nik' | 'qr'
const churchBranch = ref('gki-harapan')
const identifier = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)

// State UI Status
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showForgotModal = ref(false)

// State Lupa Password Modal
const forgotIdentifier = ref('')
const forgotSuccess = ref(false)
const isForgotSubmitting = ref(false)

// Quick Demo Login Presets
const fillDemoUser = (type = 'jemaat') => {
  if (type === 'jemaat') {
    loginMode.value = 'email'
    identifier.value = 'paripurnaerantus1604@gmail.com'
    password.value = 'paripurna123'
  } else if (type === 'pelayan') {
    loginMode.value = 'nik'
    identifier.value = '3171020304950001'
    password.value = 'Pelayan#2026'
  }
}

// Toggle Show/Hide Password
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// Handle Submit Form Login
const handleLogin = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!identifier.value || !password.value) {
    errorMessage.value = 'Silakan lengkapi Email/NIK/Username dan Kata Sandi.'
    return
  }

  isLoading.value = true

  try {
    // The backend expects form data for the login
    await authStore.login({
      identifier: identifier.value,
      password: password.value,
    }, 'jemaat')

    successMessage.value = `Selamat Datang, ${authStore.user?.full_name || 'Jemaat'}! Mengalihkan ke Portal Jemaat...`

    setTimeout(() => router.push('/dashboard-user'), 1200)
  } catch (err) {
    errorMessage.value = err.message || 'Gagal masuk. Periksa kembali identifier atau kata sandi Anda.'
  } finally {
    isLoading.value = false
  }
}

// Handle Request Reset Password Modal
const handleForgotSubmit = async () => {
  if (!forgotIdentifier.value) return
  isForgotSubmitting.value = true
  await new Promise((r) => setTimeout(r, 900))
  isForgotSubmitting.value = false
  forgotSuccess.value = true
}

const closeForgotModal = () => {
  showForgotModal.value = false
  forgotSuccess.value = false
  forgotIdentifier.value = ''
}
</script>

<template>
  <div class="min-h-screen bg-[#070d19] text-slate-100 flex flex-col justify-between items-center font-sans relative overflow-hidden selection:bg-amber-500 selection:text-slate-950">
    <!-- Dynamic Ambient Background Glows -->
    <div class="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-amber-500/10 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute bottom-10 right-10 w-[400px] h-[400px] bg-sky-500/10 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="absolute top-10 left-10 w-[350px] h-[350px] bg-emerald-500/10 rounded-full blur-[100px] pointer-events-none"></div>

    <!-- Top Navigation Header -->
    <header class="w-full max-w-7xl mx-auto px-4 sm:px-6 py-6 flex items-center justify-between z-20 relative animate__animated animate__fadeInDown" data-aos="fade-down" data-aos-duration="600">
      <RouterLink to="/" class="flex items-center gap-3 group">
        <div class="w-10 h-10 rounded-full border border-amber-500/40 bg-slate-900 flex items-center justify-center shadow-lg group-hover:border-amber-400 transition transform group-hover:scale-105">
          <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="w-full h-full object-cover">
        </div>
        <div class="flex flex-col">
          <span class="font-serif font-bold text-lg text-amber-300 tracking-wider group-hover:text-amber-200 transition">GRACEPOINT</span>
          <span class="text-[10px] text-slate-400 font-serif tracking-widest uppercase">Portal Jemaat</span>
        </div>
      </RouterLink>

      <RouterLink 
        to="/" 
        class="text-xs font-medium text-slate-300 hover:text-amber-300 flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-slate-800 bg-slate-900/80 hover:bg-slate-900 transition shadow cursor-pointer"
      >
        <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        <span>Kembali ke Beranda</span>
      </RouterLink>
    </header>

    <div class="w-full max-w-md relative z-10 my-auto px-4 py-6">
      
      <!-- Top Branding Card -->
      <div class="text-center mb-6" data-aos="fade-up" data-aos-duration="700">
        <!-- Logo / Icon Badge -->
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500/20 via-slate-900 to-amber-500/10 border border-amber-500/40 text-amber-300 mb-4 shadow-xl shadow-amber-500/10 group hover:scale-105 transition-transform duration-300 animate__animated animate__zoomIn">
          <svg class="w-8 h-8 text-amber-400 group-hover:rotate-6 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 21v-6m0 0V4m0 11h5m-5 0H7m5-11L8 8m4-4l4 4M5 21h14"/>
          </svg>
        </div>

        <!-- Role Badge -->
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-400/30 text-amber-300 text-xs font-mono font-semibold tracking-wide uppercase mb-3 animate__animated animate__fadeIn">
          <span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
          <span>Aktor 3 • Portal Jemaat Mandiri</span>
        </div>

        <h1 class="text-2xl sm:text-3xl font-serif font-bold text-slate-50 tracking-tight animate__animated animate__fadeInUp">
          Masuk Akun Jemaat
        </h1>
        <p class="text-xs sm:text-sm text-slate-400 mt-1.5 max-w-xs mx-auto leading-relaxed animate__animated animate__fadeInUp">
          Akses Kartu Digital, Jadwal Pelayanan, Presensi QR Code, & Warta Gereja.
        </p>
      </div>

      <!-- Main Login Card -->
      <div class="bg-slate-950/85 backdrop-blur-2xl border border-amber-500/25 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-black/80 relative animate__animated animate__fadeInUp" data-aos="zoom-in-up" data-aos-duration="800">

        <!-- Mode Login Selection Tabs -->
        <div class="flex bg-slate-900/90 p-1 rounded-xl border border-slate-800 mb-6 text-xs font-medium" data-aos="fade-up" data-aos-delay="100">
          <button 
            type="button" 
            @click="loginMode = 'email'" 
            :class="[loginMode === 'email' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-400 hover:text-slate-200']"
            class="flex-1 py-2 px-3 rounded-lg transition-all text-center flex items-center justify-center gap-1.5"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <span>Email / User</span>
          </button>

          <button 
            type="button" 
            @click="loginMode = 'nik'" 
            :class="[loginMode === 'nik' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-400 hover:text-slate-200']"
            class="flex-1 py-2 px-3 rounded-lg transition-all text-center flex items-center justify-center gap-1.5"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V4a2 2 0 012-2h2a2 2 0 012 2v2m-4 0h4"/>
            </svg>
            <span>No. NIK KTP</span>
          </button>
        </div>

        <!-- Alert Error -->
        <div v-if="errorMessage" class="mb-5 p-3.5 text-xs bg-rose-950/80 border border-rose-800/80 text-rose-200 rounded-xl flex items-start gap-2.5 shadow-lg">
          <svg class="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span class="leading-snug">{{ errorMessage }}</span>
        </div>

        <!-- Alert Success -->
        <div v-if="successMessage" class="mb-5 p-3.5 text-xs bg-emerald-950/80 border border-emerald-800/80 text-emerald-200 rounded-xl flex items-start gap-2.5 shadow-lg animate-pulse">
          <svg class="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <span class="leading-snug">{{ successMessage }}</span>
        </div>

        <!-- Form Login -->
        <form @submit.prevent="handleLogin" class="space-y-4 text-xs">
          <!-- Email / Username / NIK Input -->
          <div data-aos="fade-up" data-aos-delay="150">
            <label class="block font-medium text-slate-300 mb-1.5">
              <span v-if="loginMode === 'email'">Alamat Email / Username Jemaat <span class="text-amber-400">*</span></span>
              <span v-else>Nomor Induk Kependudukan (NIK) <span class="text-amber-400">*</span></span>
            </label>
            <div class="relative">
              <input 
                v-model="identifier"
                :type="loginMode === 'email' ? 'text' : 'text'"
                :placeholder="loginMode === 'email' ? 'jemaat@email.com atau username' : '16 digit nomor NIK di KTP'"
                required
                class="w-full pl-9 pr-3.5 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-slate-100 text-xs placeholder:text-slate-600 focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400 transition"
              />
              <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">
                <svg v-if="loginMode === 'email'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V4a2 2 0 012-2h2a2 2 0 012 2v2m-4 0h4"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- Password Input -->
          <div data-aos="fade-up" data-aos-delay="200">
            <div class="flex items-center justify-between mb-1.5">
              <label class="font-medium text-slate-300">Kata Sandi <span class="text-amber-400">*</span></label>
              <button 
                type="button" 
                @click="showForgotModal = true" 
                class="text-[11px] text-amber-400 hover:text-amber-300 hover:underline transition"
              >
                Lupa Kata Sandi?
              </button>
            </div>
            <div class="relative">
              <input 
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Masukkan kata sandi akun"
                required
                class="w-full pl-9 pr-10 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-slate-100 text-xs placeholder:text-slate-600 focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400 transition"
              />
              <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
              </div>
              <button 
                type="button"
                @click="togglePasswordVisibility"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition"
                title="Tampilkan / Sembunyikan Password"
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
          <div class="flex items-center justify-between pt-1" data-aos="fade-up" data-aos-delay="220">
            <label class="flex items-center gap-2 cursor-pointer text-slate-400 select-none">
              <input 
                type="checkbox"
                v-model="rememberMe"
                class="w-4 h-4 bg-slate-900 border-slate-700 rounded text-amber-500 focus:ring-amber-500 focus:ring-offset-slate-950 cursor-pointer"
              />
              <span class="text-xs">Simpan sesi login di perangkat ini</span>
            </label>
          </div>

          <!-- Submit Button -->
          <div data-aos="fade-up" data-aos-delay="250">
            <button 
              type="submit"
              :disabled="isLoading"
              class="w-full py-3 mt-2 bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-serif font-bold text-xs uppercase tracking-widest rounded-xl shadow-lg shadow-amber-500/25 transition transform active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
            >
              <svg v-if="isLoading" class="w-4 h-4 animate-spin text-slate-950" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="isLoading">Memverifikasi Kredensial...</span>
              <span v-else>Masuk ke Portal Jemaat</span>
            </button>
          </div>
        </form>

        <!-- Divider -->
        <div class="relative my-6 text-center">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-slate-800"></div>
          </div>
          <span class="relative px-3 bg-slate-950 text-[10px] text-slate-500 font-mono uppercase tracking-wider">
            Opsi Uji Coba Cepat
          </span>
        </div>

        <!-- Quick Demo Presets -->
        <div class="grid grid-cols-2 gap-2.5">
          <button 
            type="button" 
            @click="fillDemoUser('jemaat')"
            class="py-2 px-3 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-amber-500/40 rounded-xl text-[11px] text-slate-300 hover:text-amber-300 transition flex items-center justify-center gap-1.5 text-center"
          >
            <span>👤 Demo Jemaat</span>
          </button>

          <button 
            type="button" 
            @click="fillDemoUser('pelayan')"
            class="py-2 px-3 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-amber-500/40 rounded-xl text-[11px] text-slate-300 hover:text-amber-300 transition flex items-center justify-center gap-1.5 text-center"
          >
            <span>✝️ Demo Pelayan</span>
          </button>
        </div>

        <!-- Footer Links -->
        <div class="mt-6 pt-5 border-t border-slate-800/80 text-center space-y-2 text-xs">
          <p class="text-slate-400">
            Belum terdaftar sebagai jemaat? 
            <RouterLink to="/user-register" class="text-amber-400 font-medium hover:underline ml-1">
              Daftar Akun Baru →
            </RouterLink>
          </p>

          <div class="flex items-center justify-center gap-3 pt-2 text-[11px] text-slate-500 font-sans">
            <RouterLink to="/church-admin" class="hover:text-slate-300 transition">
              Aktor 2: Admin Gereja
            </RouterLink>
            <span>•</span>
            <RouterLink to="/main-admin" class="hover:text-slate-300 transition">
              Aktor 1: Super Admin
            </RouterLink>
            <span>•</span>
            <RouterLink to="/" class="hover:text-amber-400 transition">
              Beranda
            </RouterLink>
          </div>
        </div>

      </div>
    </div>

    <!-- Modal Lupa Kata Sandi -->
    <div 
      v-if="showForgotModal" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in"
    >
      <div class="w-full max-w-sm bg-slate-900 border border-amber-500/30 rounded-2xl p-6 shadow-2xl space-y-4">
        
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 class="font-serif font-bold text-amber-300 text-sm flex items-center gap-2">
            🔑 Pulihkan Kata Sandi
          </h3>
          <button @click="closeForgotModal" class="text-slate-400 hover:text-slate-100 text-lg">
            ✕
          </button>
        </div>

        <div v-if="!forgotSuccess" class="space-y-3 text-xs">
          <p class="text-slate-400 leading-relaxed">
            Masukkan Alamat Email atau NIK KTP Anda yang terdaftar. Sistem akan mengirimkan instruksi pemulihan kata sandi.
          </p>

          <div>
            <label class="block font-medium text-slate-300 mb-1">Email / NIK Jemaat</label>
            <input 
              v-model="forgotIdentifier" 
              type="text" 
              placeholder="Contoh: jemaat@email.com atau NIK" 
              class="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-xs focus:outline-none focus:border-amber-400"
            />
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button 
              type="button" 
              @click="closeForgotModal" 
              class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
            >
              Batal
            </button>
            <button 
              type="button" 
              @click="handleForgotSubmit" 
              :disabled="isForgotSubmitting"
              class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg disabled:opacity-50"
            >
              <span v-if="isForgotSubmitting">Sending...</span>
              <span v-else>Kirim Link OTP</span>
            </button>
          </div>
        </div>

        <div v-else class="space-y-3 text-xs text-center py-2">
          <div class="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center mx-auto text-lg">
            ✓
          </div>
          <h4 class="font-bold text-emerald-300 text-sm">Instruksi Terkirim!</h4>
          <p class="text-slate-300">
            Tautan verifikasi telah dikirimkan ke kontak <strong>{{ forgotIdentifier }}</strong>. Silakan periksa kotak masuk atau WhatsApp Anda.
          </p>
          <button 
            type="button" 
            @click="closeForgotModal" 
            class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-100 font-medium rounded-lg mt-2"
          >
            Tutup & Kembali
          </button>
        </div>

      </div>
    </div>

    <!-- Footer Copyright -->
    <footer class="w-full py-4 text-center text-xs text-slate-500 z-10">
      &copy; 2026 GracePoint — Platform Manajemen & Pelayanan Digital Gereja
    </footer>

  </div>
</template>
