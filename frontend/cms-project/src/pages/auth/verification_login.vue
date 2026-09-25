<script setup>
import { ref, reactive } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { authService } from '@/services/authService'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const router = useRouter()

// Form Data
const form = reactive({
  identifier: '',
  password: '',
  securityPin: '',
  rememberMe: true,
})

// UI & Verification State
const showPassword = ref(false)
const enableSecurityPin = ref(false)
const isVerifying = ref(false)
const verificationPhase = ref('') // 'validating' | 'role_checking' | 'authorized'
const errorMessage = ref('')
const successMessage = ref('')

// Demo fast-fill untuk testing
const fillQuickAccount = (type) => {
  errorMessage.value = ''
  if (type === 'admin') {
    form.identifier = 'admin'
    form.password = 'superadmin123'
    enableSecurityPin.value = true
    form.securityPin = '123456'
  } else if (type === 'church') {
    form.identifier = 'admin@gki-harapan.org'
    form.password = 'gereja123'
    enableSecurityPin.value = false
  } else if (type === 'jemaat') {
    form.identifier = 'paripurnaerantus1604@gmail.com'
    form.password = 'paripurna123'
    enableSecurityPin.value = false
  }
}

// Eksekusi Login & Verifikasi Satu Jalur
const handleUnifiedVerificationLogin = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!form.identifier.trim() || !form.password) {
    errorMessage.value = 'Silakan masukkan Email / Username dan Kata Sandi Anda.'
    return
  }

  if (enableSecurityPin.value && (!form.securityPin || form.securityPin.length < 6)) {
    errorMessage.value = 'PIN Keamanan 2FA wajib terdiri dari minimal 6 digit/karakter.'
    return
  }

  isVerifying.value = true
  verificationPhase.value = 'Memeriksa kredensial & enkripsi hash...'

  try {
    // 1. Eksekusi autentikasi melalui unifiedLogin
    const credentials = {
      identifier: form.identifier.trim(),
      email: form.identifier.trim(),
      username: form.identifier.trim(),
      password: form.password,
      securityPin: enableSecurityPin.value ? form.securityPin : undefined,
    }

    verificationPhase.value = 'Memverifikasi hak akses & role sistem...'

    const result = await authService.unifiedLogin(credentials)

    verificationPhase.value = 'Otorisasi Berhasil! Mengalihkan ke dashboard...'
    const detectedRole = result.role || 'jemaat'

    if (detectedRole === 'superadmin') {
      successMessage.value = 'Selamat Datang, Super Administrator! Mengalihkan ke System Console...'
      setTimeout(() => {
        router.push('/dashboard')
      }, 900)
    } else if (detectedRole === 'church_admin') {
      successMessage.value = 'Otorisasi Admin Cabang Gereja Berhasil. Mengalihkan ke Dashboard...'
      setTimeout(() => {
        router.push('/dashboard-church')
      }, 900)
    } else {
      successMessage.value = 'Otorisasi Anggota Jemaat Berhasil. Mengalihkan ke Portal Jemaat...'
      setTimeout(() => {
        router.push('/dashboard-user')
      }, 900)
    }
  } catch (err) {
    errorMessage.value = err.message || 'Verifikasi gagal. Akun tidak ditemukan atau kata sandi tidak cocok.'
    isVerifying.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[var(--theme-bg-primary)] text-[var(--theme-text-primary)] flex flex-col justify-between relative overflow-hidden font-sans transition-colors duration-300">
    
    <!-- Latar Belakang Grafis Keamanan (Security Glow) -->
    <div class="absolute inset-0 pointer-events-none z-0 opacity-40">
      <div class="absolute -top-32 -left-32 w-96 h-96 bg-amber-600/10 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-32 -right-32 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-amber-500/5 rounded-full blur-[140px]"></div>
      <div class="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:28px_28px] opacity-25"></div>
    </div>

    <!-- Header Navbar Navigasi -->
    <header class="relative z-10 w-full max-w-7xl mx-auto px-5 sm:px-8 py-5 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/40 p-1 flex items-center justify-center text-amber-400 shadow-md">
          <i class="bi bi-shield-check fs-5"></i>
        </div>
        <div>
          <span class="text-lg font-bold font-serif tracking-wider text-amber-300">GracePoint</span>
          <span class="ml-2 text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase tracking-widest">
            Portal Masuk Satu Jalur
          </span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <ThemeToggleButton />
        <RouterLink 
          to="/" 
          class="text-xs font-medium text-slate-300 hover:text-amber-300 flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg border border-slate-700 bg-slate-900/70 hover:bg-slate-900 transition cursor-pointer"
        >
          <i class="bi bi-arrow-left"></i>
          <span>Kembali ke Beranda</span>
        </RouterLink>
      </div>
    </header>

    <!-- Konten Utama: Card Login Satu Jalur -->
    <main class="relative z-10 w-full max-w-md mx-auto px-4 py-4 my-auto">
      <div class="bg-[var(--theme-bg-surface)] border border-[var(--theme-border)] rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
        
        <!-- Header Form -->
        <div class="text-center mb-6">
          <div class="w-13 h-13 mx-auto rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-300 flex items-center justify-center mb-3 shadow-inner">
            <i class="bi bi-shield-lock-fill fs-3"></i>
          </div>
          <h1 class="text-xl sm:text-2xl font-bold font-serif text-white tracking-wide">
            PORTAL MASUK TERPADU
          </h1>
          <p class="text-xs text-slate-300 mt-1 font-sans">
            Satu pintu masuk cerdas untuk Seluruh Pengurus, Pelayan, & Jemaat.
          </p>
        </div>

        <!-- Alert Error Feedback -->
        <div v-if="errorMessage" class="mb-4 p-3 bg-red-950/80 border border-red-500/50 rounded-xl text-xs text-red-200 flex items-start gap-2.5 animate-fadeIn">
          <i class="bi bi-exclamation-triangle-fill text-red-400 flex-shrink-0 mt-0.5 fs-6"></i>
          <div class="flex-1 leading-relaxed">{{ errorMessage }}</div>
        </div>

        <!-- Alert Success Feedback -->
        <div v-if="successMessage" class="mb-4 p-3 bg-emerald-950/80 border border-emerald-500/50 rounded-xl text-xs text-emerald-200 flex items-start gap-2.5 animate-fadeIn">
          <i class="bi bi-check-circle-fill text-emerald-400 flex-shrink-0 mt-0.5 fs-6"></i>
          <div class="flex-1 leading-relaxed">{{ successMessage }}</div>
        </div>

        <!-- Form Login & Verifikasi -->
        <form @submit.prevent="handleUnifiedVerificationLogin" class="space-y-4">
          
          <!-- Input 1: Email / Username / NIK -->
          <div>
            <label class="block text-xs font-semibold text-slate-200 mb-1.5">
              Email / ID Pengguna / NIK Jemaat
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-amber-400/80">
                <i class="bi bi-person-fill"></i>
              </div>
              <input 
                v-model="form.identifier"
                type="text" 
                required
                autocomplete="username"
                placeholder="Masukkan email, username, atau NIK"
                class="w-full pl-10 pr-3.5 py-2.5 text-xs sm:text-sm bg-[var(--theme-bg-primary)] border border-[var(--theme-border)] rounded-xl text-[var(--theme-text-primary)] placeholder-slate-400 focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400 transition"
              />
            </div>
          </div>

          <!-- Input 2: Kata Sandi -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-semibold text-slate-200">Kata Sandi</label>
              <span class="text-[11px] text-slate-400">Tersandi aman</span>
            </div>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-amber-400/80">
                <i class="bi bi-lock-fill"></i>
              </div>
              <input 
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="Masukkan kata sandi Anda"
                class="w-full pl-10 pr-10 py-2.5 text-xs sm:text-sm bg-[var(--theme-bg-primary)] border border-[var(--theme-border)] rounded-xl text-[var(--theme-text-primary)] placeholder-slate-400 focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400 transition"
              />
              <button 
                type="button" 
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-amber-300 transition cursor-pointer"
                title="Tampilkan / Sembunyikan Kata Sandi"
              >
                <i :class="showPassword ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill'"></i>
              </button>
            </div>
          </div>

          <!-- Tools Verifikasi Keamanan Tambahan (2FA / PIN Akses Ketat) -->
          <div class="pt-1 pb-1">
            <div class="flex items-center justify-between">
              <label class="flex items-center gap-2 cursor-pointer select-none">
                <input 
                  type="checkbox" 
                  v-model="enableSecurityPin"
                  class="rounded bg-slate-900 border-slate-700 text-amber-500 focus:ring-amber-400"
                >
                <span class="text-xs text-slate-300 flex items-center gap-1">
                  <i class="bi bi-shield-check text-emerald-400"></i> Aktifkan PIN Keamanan
                </span>
              </label>
            </div>

            <!-- PIN Input (Muncul jika dicentang) -->
            <div v-if="enableSecurityPin" class="mt-2.5 p-3 rounded-xl bg-slate-950/80 border border-amber-500/30">
              <label class="block text-[11px] font-semibold text-amber-300 mb-1">
                PIN Akses Tambahan (2FA Layer)
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <i class="bi bi-key-fill"></i>
                </div>
                <input 
                  v-model="form.securityPin"
                  type="password" 
                  maxlength="6"
                  placeholder="Masukkan 6 digit PIN"
                  class="w-full pl-9 pr-3 py-1.5 text-xs bg-[var(--theme-bg-primary)] border border-[var(--theme-border)] rounded-lg text-[var(--theme-text-primary)] placeholder-slate-400 tracking-widest focus:outline-none focus:border-amber-400 transition"
                />
              </div>
            </div>
          </div>

          <!-- Tombol Submit Verifikasi -->
          <button 
            type="submit" 
            :disabled="isVerifying"
            class="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold font-serif text-sm uppercase tracking-wider rounded-xl shadow-lg hover:shadow-amber-500/25 transition duration-200 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
          >
            <span v-if="isVerifying" class="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
            <i v-else class="bi bi-box-arrow-in-right fs-5"></i>
            <span>{{ isVerifying ? (verificationPhase || 'Memverifikasi...') : 'Verifikasi & Masuk ke Sistem' }}</span>
          </button>
        </form>

        <!-- Indikator Keamanan Sistem -->
        <div class="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400 font-mono">
          <span class="flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            WAF Active
          </span>
          <span>Prepared Query (Anti-SQLi)</span>
          <span>SHA-256 Auth</span>
        </div>

        <!-- Opsi Pendaftaran Bagi yang Belum Punya Akun -->
        <div class="mt-4 pt-3 text-center text-xs text-slate-300">
          <span>Belum memiliki akun terdaftar? </span>
          <div class="inline-flex gap-2 font-medium">
            <RouterLink to="/user-register" class="text-amber-400 hover:underline">Daftar Jemaat</RouterLink>
            <span>•</span>
            <RouterLink to="/church-register" class="text-amber-400 hover:underline">Daftar Gereja</RouterLink>
          </div>
        </div>

      </div>
    </main>

    <!-- Footer Status -->
    <footer class="relative z-10 w-full text-center py-4 text-xs text-slate-400 font-serif">
      <span>✝ Soli Deo Gloria — Sistem Informasi & Keamanan GracePoint &copy; 2026</span>
    </footer>

  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.25s ease-out forwards;
}

:global(html[data-theme="light"]) {
  .text-white {
    color: #0f172a !important;
  }
  .text-slate-100 {
    color: #0f172a !important;
  }
  .text-slate-200 {
    color: #1e293b !important;
  }
  .text-slate-300 {
    color: #334155 !important;
  }
  .text-slate-400 {
    color: #64748b !important;
  }
  .text-amber-300,
  .text-amber-400 {
    color: #b45309 !important;
  }
}
</style>
