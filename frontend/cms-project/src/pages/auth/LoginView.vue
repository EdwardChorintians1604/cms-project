<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

// Form State
const email = ref('')
const username = ref('')
const password = ref('')
const securityPin = ref('')
const rememberMe = ref(true)
const showPassword = ref(false)
const enable2FA = ref(true)

// Status State
const errorMsg = ref('')
const successMsg = ref('')
const isModalHelpOpen = ref(false)

const { login, isLoading } = useAuth()
const router = useRouter()

const handleSubmit = async () => {
  errorMsg.value = ''
  successMsg.value = ''

  const loginIdentifier = email.value || username.value
  if (!loginIdentifier || !password.value) {
    errorMsg.value = 'Email / Username dan Password Wajib Diisi.'
    return
  }

  if (enable2FA.value && (!securityPin.value || securityPin.value.length < 6)) {
    errorMsg.value = 'Pin Keamanan 2FA (6 Karakter / Digit) Diperlukan untuk Mode Akses Ketat.'
    return
  }

  try {
    // Memanggil composable auth
    await login({ 
      identifier: loginIdentifier,
      email: email.value,
      username: username.value,
      password: password.value,
      securityPin: securityPin.value,
      role: 'superadmin'
    })
    
    successMsg.value = 'Autentikasi Master Berhasil. Mengalihkan ke System Console...'
    
    setTimeout(() => {
      router.push('/dashboard')
    }, 1000)

  } catch (err) {
    errorMsg.value = err?.message || 'Akses Ditolak. Kredensial Developer/System Admin tidak valid atau tidak memiliki izin Super Admin.'
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between relative overflow-hidden font-sans">
    <!-- Visual Background Glow & Cyber Grid -->
    <div class="absolute inset-0 pointer-events-none z-0">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-emerald-600/15 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-cyan-600/15 rounded-full blur-3xl animate-pulse" style="animation-delay: 1.5s;"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-900/10 rounded-full blur-[120px]"></div>
      <!-- Subtle Grid Pattern -->
      <div class="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-30"></div>
    </div>

    <!-- Top Navigation Header -->
    <header data-aos="fade-down" data-aos-duration="600" class="animate__animated animate__fadeInDown relative z-10 w-full max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-cyan-500 p-0.5 shadow-lg shadow-emerald-900/40">
          <div class="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <div>
          <span class="text-lg font-bold tracking-wider bg-gradient-to-r from-slate-100 via-slate-200 to-slate-400 bg-clip-text text-transparent">GracePoint</span>
          <span class="ml-2 text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 uppercase tracking-widest">Main Admin Portal</span>
        </div>
      </div>

      <!-- Operational Badge -->
      <router-link 
        to="/" 
        class="text-xs font-medium text-slate-300 hover:text-amber-300 flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/60 hover:bg-slate-900 transition"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        <span>Kembali ke Beranda</span>
      </router-link>
    </header>

    <!-- Main Content Container -->
    <main class="relative z-10 flex-1 flex items-center justify-center px-4 py-8">
      <div class="w-full max-w-md">
        
        <!-- Top Security Notice Banner -->
        <div data-aos="fade-up" data-aos-duration="600" class="mb-5 bg-gradient-to-r from-amber-950/40 via-amber-900/30 to-amber-950/40 border border-amber-500/30 rounded-xl p-3.5 backdrop-blur-md shadow-lg flex items-start space-x-3">
          <div class="p-1.5 bg-amber-500/10 rounded-lg text-amber-400 shrink-0">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
          </div>
          <div class="text-xs text-amber-200/90 leading-relaxed">
            <span class="font-semibold text-amber-400 block mb-0.5">RESTRICTED DEVELOPER ACCESS</span>
            Portal ini khusus untuk <strong class="text-white">Admin Utama & Developer SystemKita</strong>. Pendaftaran publik tidak tersedia untuk level hak akses ini.
          </div>
        </div>

        <!-- Glassmorphic Form Card -->
        <div data-aos="zoom-in-up" data-aos-duration="650" class="animate__animated animate__fadeInUp bg-slate-900/80 border border-slate-800/90 rounded-2xl p-6 sm:p-8 shadow-2xl shadow-black/80 backdrop-blur-xl relative group hover:border-emerald-500/30 transition-all duration-500">
          
          <!-- Subtle Top Glowing Line -->
          <div class="absolute top-0 left-8 right-8 h-[2px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-70"></div>

          <!-- Card Header -->
          <div class="mb-6 text-center" data-aos="fade-up" data-aos-delay="50">
            <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-slate-950 border border-slate-800 mb-3 shadow-inner text-emerald-400 animate__animated animate__zoomIn">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
              </svg>
            </div>
            <h1 class="text-xl font-bold text-white tracking-tight">Otentikasi System Admin</h1>
            <p class="text-xs text-slate-400 mt-1">Masukkan kredensial pengembang & token enkripsi master</p>
          </div>
          <br>
          <!-- Alert Notifications -->
          <div v-if="errorMsg" class="mb-4 p-3 bg-rose-950/70 border border-rose-800/80 rounded-xl text-xs text-rose-200 flex items-start space-x-2 animate-shake">
            <svg class="w-4 h-4 text-rose-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="flex-1">{{ errorMsg }}</span>
          </div>

          <div v-if="successMsg" class="mb-4 p-3 bg-emerald-950/70 border border-emerald-800/80 rounded-xl text-xs text-emerald-200 flex items-start space-x-2">
            <svg class="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span class="flex-1">{{ successMsg }}</span>
          </div>

          <!-- Login Form -->
          <form @submit.prevent="handleSubmit" class="space-y-4">
            
            <!-- Email Input -->
            <div data-aos="fade-up" data-aos-delay="100">
              <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Developer ID / Email Root
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
                  </svg>
                </div>
                <input 
                  v-model="email"
                  type="email" 
                  required
                  placeholder="dev.admin@systemkita.id"
                  class="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition font-mono"
                />
              </div>
            </div>

            <!-- Admin Name Input -->
            <div data-aos="fade-up" data-aos-delay="150">
              <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Username
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
                  </svg>
                </div>
                <input 
                  v-model="username"
                  type="username" 
                  required
                  placeholder="adminKita_76$321"
                  class="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition font-mono"
                />
              </div>
            </div>

            <!-- Password Input -->
            <div data-aos="fade-up" data-aos-delay="200">
              <div class="flex items-center justify-between mb-1.5">
                <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Master Password
                </label>
                <button 
                  type="button" 
                  @click="isModalHelpOpen = true"
                  class="text-[11px] text-emerald-400 hover:text-emerald-300 transition hover:underline cursor-pointer"
                >
                  Lupa Akses?
                </button>
              </div>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                </div>
                <input 
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'" 
                  required
                  placeholder="••••••••••••"
                  class="w-full pl-10 pr-10 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition font-mono"
                />
                <button 
                  type="button" 
                  @click="showPassword = !showPassword"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-300 transition"
                >
                  <svg v-if="!showPassword" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858-5.908a10.046 10.046 0 013.682-.733c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21M3 3l18 18"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Required 2FA PIN / Dev Key -->
            <div data-aos="fade-up" data-aos-delay="250" class="pt-1">
              <div class="flex items-center justify-between mb-1.5">
                <label class="text-xs text-slate-300 font-medium">PIN Keamanan 2FA Superadmin</label>
              </div>
              
              <div class="mt-2 transition-all duration-300">
                <input 
                  v-model="securityPin"
                  type="text" 
                  maxlength="6"
                  placeholder="Kode Security 6-Digit (mis: 894210)"
                  class="w-full px-3.5 py-2 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-emerald-400 placeholder-slate-600 focus:outline-none focus:border-emerald-500 transition font-mono text-center tracking-widest"
                />
              </div>
            </div>

            <!-- Options: Remember Me -->
            <div data-aos="fade-up" data-aos-delay="300" class="flex items-center justify-between pt-1">
              <label class="flex items-center space-x-2 text-xs text-slate-400 cursor-pointer">
                <input 
                  type="checkbox" 
                  v-model="rememberMe"
                  class="rounded bg-slate-950 border-slate-700 text-emerald-600 focus:ring-emerald-500 focus:ring-offset-slate-900" 
                />
                <span>Simpan Sesi Pengembang</span>
              </label>

              <span class="text-[11px] text-slate-500 font-mono">TLS 1.3 / AES-256</span>
            </div>

            <!-- Submit Button -->
            <div data-aos="fade-up" data-aos-delay="350">
              <button 
                type="submit"
                :disabled="isLoading"
                class="w-full mt-3 py-3 px-4 bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 disabled:opacity-50 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-emerald-950/60 flex items-center justify-center space-x-2 group/btn border border-emerald-400/20 cursor-pointer"
              >
                <template v-if="isLoading">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span class="text-sm">Memverifikasi Otentikasi...</span>
                </template>
                <template v-else>
                  <span class="text-sm tracking-wide">MASUK KE ADMIN UTAMA GRACEPOINT</span>
                  <svg class="w-4 h-4 transform group-hover/btn:translate-x-1 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                  </svg>
                </template>
              </button>
            </div>

          </form>

          <!-- System Info Footer inside Card -->
          <div class="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
            <span class="flex items-center space-x-1">
              <svg class="w-3.5 h-3.5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Developer Workspace</span>
            </span>
            <span class="text-slate-400 font-mono">NO PUBLIC REGISTRATION</span>
          </div>

        </div>

        <!-- Quick Switcher to Other Portals -->
        <div data-aos="fade-up" data-aos-delay="400" class="mt-6 text-center space-y-2">
          <p class="text-xs text-slate-400">Login untuk jemaat atau admin gereja?</p>
          <div class="flex items-center justify-center space-x-4 text-xs">
            <router-link to="/verification-login" class="text-amber-400 hover:text-amber-300 transition hover:underline flex items-center space-x-1">
              <i class="bi bi-shield-lock-fill w-3.5 h-3.5"></i>
              <span>Portal Masuk Terpadu</span>
            </router-link>
          </div>
        </div>

      </div>
    </main>

    <!-- Page Footer -->
    <footer class="relative z-10 py-4 text-center text-xs text-slate-600 border-t border-slate-900 bg-slate-950/90">
      <p>&copy; 2026 SystemKita Platform Infrastructure. Protected by Developer Authentication Protocol.</p>
    </footer>

    <!-- Help / Forgot Credential Modal -->
    <div v-if="isModalHelpOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
        <button 
          @click="isModalHelpOpen = false"
          class="absolute top-4 right-4 text-slate-400 hover:text-white transition"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div class="flex items-center space-x-3 mb-4">
          <div class="p-2.5 bg-amber-500/10 rounded-xl text-amber-400">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          <div>
            <h3 class="text-base font-bold text-white">Reset Kredensial Developer</h3>
            <p class="text-xs text-slate-400">Panduan pemulihan akun System Admin</p>
          </div>
        </div>

        <div class="space-y-3 text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800">
          <p>
            🔒 Untuk alasan keamanan tingkat tinggi, <strong class="text-emerald-400">Portal Root System Admin tidak memiliki fitur reset password publik atau pendaftaran mandiri.</strong>
          </p>
          <p>
            Jika Anda kehilangan kredensial developer Anda, silakan jalankan perintah CLI berikut di server local/production:
          </p>
          <div class="bg-slate-900 p-2.5 rounded border border-slate-800 font-mono text-emerald-300 text-[11px] overflow-x-auto">
            npm run system:reset-admin -- --email=admin@master
          </div>
          <p class="text-slate-400">
            Atau hubungi Lead Infrastructure Architect melalui channel internal DevOps.
          </p>
        </div>

        <div class="mt-5 flex justify-end">
          <button 
            @click="isModalHelpOpen = false"
            class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition"
          >
            Mengerti & Tutup
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-4px); }
  40%, 80% { transform: translateX(4px); }
}
.animate-shake {
  animation: shake 0.4s ease-in-out;
}
</style>

