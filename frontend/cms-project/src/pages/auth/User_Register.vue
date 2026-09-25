<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { authService } from '@/services/authService'
import { apiFetch } from '@/services/api'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'

const router = useRouter()

// Form Reactive State
const formData = ref({
  fullName: '',
  birthPlace: '',
  birthDate: '',
  nik: '',
  noKtp: '',
  gender: 'Laki-laki',
  education: 'S1',
  church_domisili: '',
  church_central: '', 
  married: '',
  chatecication: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  phone: '',
  origin: '',
  address: '',
  photoUrl: null
})

const photoPreview = ref(null)
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const churches = ref([])
const churchBranches = ref([])
const isLoadingChurches = ref(true)

const availableBranches = computed(() => {
  if (!formData.value.church_central) return []

  const selectedChurch = churches.value.find(
    (church) => church.church_name === formData.value.church_central
  )

  return churchBranches.value.filter((branch) => (
    selectedChurch ? branch.church_id === selectedChurch.id : false
  ))
})

const loadChurchOptions = async () => {
  try {
    const [churchesResponse, branchesResponse] = await Promise.all([
      apiFetch('/churches/?limit=100'),
      apiFetch('/church-admins/?limit=100'),
    ])

    churches.value = churchesResponse.filter((church) => church.status === 'Aktif')
    churchBranches.value = branchesResponse.filter((branch) => branch.status === 'Aktif')
  } catch (err) {
    errorMessage.value = 'Data gereja belum dapat dimuat. Silakan muat ulang halaman.'
  } finally {
    isLoadingChurches.value = false
  }
}

const handleCentralChurchChange = () => {
  const branchStillAvailable = availableBranches.value.some(
    (branch) => branch.church_name === formData.value.church_domisili
  )

  if (!branchStillAvailable) formData.value.church_domisili = ''
}

onMounted(loadChurchOptions)

// File Upload Handler with Preview
const handlePhotoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 2 * 1024 * 1024) {
      errorMessage.value = 'Ukuran foto maksimal 2MB.'
      return
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      photoPreview.value = e.target.result
      formData.value.photoUrl = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// Form Submit Handler
const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (formData.value.password !== formData.value.confirmPassword) {
    errorMessage.value = 'Konfirmasi kata sandi tidak cocok!'
    return
  }

  isSubmitting.value = true

  try {
    await authService.register(formData.value)
    successMessage.value = 'Pendaftaran Jemaat berhasil! Mengalihkan ke halaman login...'
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    errorMessage.value = err.message || 'Gagal melakukan pendaftaran. Silakan coba lagi.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="page-root bg-[var(--theme-bg-primary,#070d19)] text-[var(--theme-text-primary,#f8fafc)] flex flex-col justify-between items-center px-3 sm:px-4 font-sans relative overflow-hidden transition-colors duration-300">
    
    <!-- Dynamic Ambient Background Glows -->
    <div aria-hidden="true" class="absolute top-0 left-1/2 -translate-x-1/2 w-[min(750px,120vw)] h-[350px] bg-amber-500/10 dark:bg-amber-500/15 blur-[140px] pointer-events-none rounded-full"></div>
    <div aria-hidden="true" class="absolute bottom-0 right-0 w-[min(450px,90vw)] h-[350px] bg-cyan-500/5 dark:bg-cyan-500/10 blur-[130px] pointer-events-none rounded-full"></div>

    <!-- Top Navigation Header -->
    <header class="w-full max-w-7xl mx-auto px-1 sm:px-6 py-4 flex items-center justify-between gap-3 z-20 relative mb-4">
      <RouterLink 
        to="/" 
        class="brand-link flex items-center gap-3 group cursor-pointer no-underline min-w-0"
        style="text-decoration: none !important;"
      >
        <div class="w-10 h-10 rounded-full border-2 border-slate-400/60 dark:border-amber-500/40 bg-slate-100 dark:bg-slate-900 flex items-center justify-center shadow-lg group-hover:border-amber-400 transition shrink-0 overflow-hidden">
          <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="w-full h-full object-cover">
        </div>
        <div class="flex flex-col min-w-0">
          <span class="truncate font-serif font-bold text-lg text-amber-600 dark:text-amber-300 tracking-wider group-hover:text-amber-500 dark:group-hover:text-amber-200 transition leading-tight">
            GRACEPOINT
          </span>
          <span class="truncate text-[10px] text-slate-500 dark:text-slate-400 font-serif tracking-widest uppercase leading-tight">
            Pendaftaran Jemaat Baru
          </span>
        </div>
      </RouterLink>

      <!-- Header Controls: Theme Toggle & Back Button -->
      <div class="flex items-center gap-2.5 sm:gap-3 shrink-0">
        <ThemeToggleButton />
        
        <RouterLink 
          to="/" 
          class="text-xs font-medium text-slate-700 dark:text-slate-200 hover:text-amber-600 dark:hover:text-amber-300 flex items-center gap-1.5 px-3 sm:px-3.5 py-2 rounded-xl border border-slate-300 dark:border-slate-700/80 bg-white/90 dark:bg-slate-900/80 hover:bg-slate-50 dark:hover:bg-slate-800 transition shadow-sm cursor-pointer no-underline"
          style="text-decoration: none !important;"
          title="Kembali ke Beranda Utama"
        >
          <svg class="w-4 h-4 text-amber-500 dark:text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          <span class="hidden sm:inline font-sans">Kembali ke Beranda</span>
          <span class="sm:hidden font-sans">Beranda</span>
        </RouterLink>
      </div>
    </header>

    <!-- Main Registration Card -->
    <div class="w-full max-w-4xl bg-white/95 dark:bg-slate-950/90 border border-slate-200 dark:border-amber-500/30 rounded-2xl p-5 sm:p-8 lg:p-10 shadow-2xl backdrop-blur-xl z-10 my-auto transition-colors duration-300">
      
      <!-- Form Header -->
      <div class="text-center pb-6 border-b border-slate-200 dark:border-amber-500/20 mb-6">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/30 dark:border-amber-400/40 text-amber-600 dark:text-amber-300 mb-3 shadow-inner">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
          </svg>
        </div>
        <h1 class="text-2xl sm:text-3xl font-bold font-serif text-amber-600 dark:text-amber-300 tracking-wide">
          Pendaftaran Anggota Jemaat Baru
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1 font-sans">
          Lengkapi formulir di bawah ini untuk terdaftar dalam database jemaat &amp; pelayanan gereja.
        </p>
      </div>

      <!-- Alert Messages -->
      <div v-if="errorMessage" class="mb-6 p-4 text-xs font-sans bg-rose-50 dark:bg-rose-950/80 border border-rose-300 dark:border-rose-800 text-rose-800 dark:text-rose-200 rounded-xl flex items-center gap-2">
        <span class="text-base">⚠️</span>
        <span>{{ errorMessage }}</span>
      </div>

      <div v-if="successMessage" class="mb-6 p-4 text-xs font-sans bg-emerald-50 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 rounded-xl flex items-center gap-2">
        <span class="text-base">✅</span>
        <span>{{ successMessage }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-8 font-sans text-xs">
        
        <!-- SECTION 1: IDENTITAS PRIBADI -->
        <div class="space-y-4">
          <h3 class="section-title text-sm font-serif font-bold text-amber-600 dark:text-amber-300 border-b border-slate-200 dark:border-slate-800 pb-2 uppercase tracking-wider flex items-center gap-2">
            <span>👤 1. Data Identitas Pribadi</span>
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Nama Lengkap -->
            <div class="md:col-span-2">
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Nama Lengkap (Sesuai KTP) <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.fullName" 
                type="text" 
                required 
                placeholder="Masukkan nama lengkap" 
                class="form-control"
              />
            </div>

            <!-- NIK Jemaat -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">NIK (Nomor Induk Kependudukan) <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.nik" 
                type="text" 
                required 
                placeholder="16 digit NIK" 
                maxlength="16"
                class="form-control"
              />
            </div>

            <!-- No. KTP -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">No. KTP / Kartu Identitas</label>
              <input 
                v-model="formData.noKtp" 
                type="text" 
                placeholder="Nomor KTP" 
                class="form-control"
              />
            </div>

            <!-- Tempat Lahir -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Tempat Lahir <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.birthPlace" 
                type="text" 
                required 
                placeholder="Kota kelahiran" 
                class="form-control"
              />
            </div>

            <!-- Tanggal Lahir -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Tanggal Lahir <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.birthDate" 
                type="date" 
                required 
                class="form-control"
              />
            </div>

            <!-- Jenis Kelamin -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Jenis Kelamin <span class="text-rose-500">*</span></label>
              <select 
                v-model="formData.gender" 
                required 
                class="form-control"
              >
                <option value="Laki-laki">Laki-laki</option>
                <option value="Perempuan">Perempuan</option>
              </select>
            </div>

            <!-- Pendidikan -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Pendidikan Terakhir <span class="text-rose-500">*</span></label>
              <select 
                v-model="formData.education" 
                required 
                class="form-control"
              >
                <option value="SD">SD / Sederajat</option>
                <option value="SMP">SMP / Sederajat</option>
                <option value="SMA/SMK">SMA / SMK / Sederajat</option>
                <option value="D3">Diploma (D3)</option>
                <option value="S1">Sarjana (S1)</option>
                <option value="S2">Magister (S2)</option>
                <option value="S3">Doktor (S3)</option>
                <option value="Lainnya">Lainnya</option>
              </select>
            </div>

            <!-- Status Pernikahan -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Status Diri <span class="text-rose-500">*</span></label>
              <select 
                v-model="formData.married" 
                required 
                class="form-control"
              >
                <option value="" disabled>Pilih Status Pernikahan</option>
                <option value="Menikah">Menikah</option>
                <option value="Belum Menikah">Belum Menikah</option>
                <option value="Bercerai">Bercerai</option>
              </select>
            </div>

            <!-- Katekisasi -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Sudah mengikuti katekisasi dan sidi? <span class="text-rose-500">*</span></label>
              <select 
                v-model="formData.chatecication" 
                required 
                class="form-control"
              >
                <option value="" disabled>Pilih sudah atau belum</option>
                <option value="Sudah">Sudah</option>
                <option value="Belum">Belum</option>
              </select>
            </div>

            <!-- Afiliasi Gereja Pusat -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Afiliasi Gereja Induk <span class="text-rose-500">*</span></label>
              <select
                v-model="formData.church_central" 
                required 
                @change="handleCentralChurchChange"
                class="form-control"
                :disabled="isLoadingChurches"
              >
                <option value="" disabled>
                  {{ isLoadingChurches ? 'Memuat data gereja induk...' : 'Pilih gereja induk' }}
                </option>
                <option
                  v-for="church in churches"
                  :key="church.id"
                  :value="church.church_name"
                >
                  {{ church.church_name }}
                </option>
              </select>
            </div>

            <!-- Cabang Gereja -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Nama Cabang / Tempat Gereja <span class="text-rose-500">*</span></label>
              <select
                v-model="formData.church_domisili" 
                required 
                class="form-control"
                :disabled="isLoadingChurches || !formData.church_central"
              >
                <option value="" disabled>
                  {{ isLoadingChurches ? 'Memuat data cabang...' : (formData.church_central ? 'Pilih cabang gereja' : 'Pilih gereja induk terlebih dahulu') }}
                </option>
                <option
                  v-for="branch in availableBranches"
                  :key="branch.id"
                  :value="branch.church_name"
                >
                  {{ branch.church_name }}{{ branch.city ? ` - ${branch.city}` : '' }}
                </option>
              </select>
            </div>

          </div>
        </div>

        <!-- SECTION 2: ALAMAT & DOMISILI -->
        <div class="space-y-4">
          <h3 class="section-title text-sm font-serif font-bold text-amber-600 dark:text-amber-300 border-b border-slate-200 dark:border-slate-800 pb-2 uppercase tracking-wider flex items-center gap-2">
            <span>🏠 2. Asal &amp; Tempat Tinggal</span>
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Daerah Asal -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Daerah / Kota Asal <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.origin" 
                type="text" 
                required 
                placeholder="Contoh: Medan, Manado, Toraja" 
                class="form-control"
              />
            </div>

            <!-- No HP / WhatsApp -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">No. HP / WhatsApp <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.phone" 
                type="tel" 
                required 
                placeholder="Contoh: 08123456789" 
                class="form-control"
              />
            </div>

            <!-- Alamat Tempat Tinggal Saat Ini -->
            <div class="md:col-span-2">
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Alamat Tempat Tinggal Saat Ini <span class="text-rose-500">*</span></label>
              <textarea 
                v-model="formData.address" 
                rows="2" 
                required 
                placeholder="Masukkan alamat domisili lengkap saat ini" 
                class="form-control"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- SECTION 3: KREDENSIAL AKUN -->
        <div class="space-y-4">
          <h3 class="section-title text-sm font-serif font-bold text-amber-600 dark:text-amber-300 border-b border-slate-200 dark:border-slate-800 pb-2 uppercase tracking-wider flex items-center gap-2">
            <span>🔐 3. Akun Login &amp; Kredensial</span>
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Username -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Username <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.username" 
                type="text" 
                required 
                placeholder="Masukkan username unik" 
                class="form-control"
              />
            </div>

            <!-- Email -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Alamat Email <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.email" 
                type="email" 
                required 
                placeholder="email@contoh.com" 
                class="form-control"
              />
            </div>

            <!-- Kata Sandi -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Kata Sandi <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.password" 
                type="password" 
                required 
                placeholder="Minimal 6 karakter" 
                class="form-control"
              />
            </div>

            <!-- Konfirmasi Kata Sandi -->
            <div>
              <label class="block font-medium text-slate-700 dark:text-slate-300 mb-1.5">Konfirmasi Kata Sandi <span class="text-rose-500">*</span></label>
              <input 
                v-model="formData.confirmPassword" 
                type="password" 
                required 
                placeholder="Ulangi kata sandi" 
                class="form-control"
              />
            </div>
          </div>
        </div>

        <!-- SECTION 4: FOTO PROFIL JEMAAT -->
        <div class="space-y-4">
          <h3 class="section-title text-sm font-serif font-bold text-amber-600 dark:text-amber-300 border-b border-slate-200 dark:border-slate-800 pb-2 uppercase tracking-wider flex items-center gap-2">
            <span>📷 4. Foto Profil Jemaat</span>
          </h3>

          <div class="flex flex-col sm:flex-row items-center gap-5 p-4 bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-xl">
            <!-- Image Preview Box -->
            <div class="w-24 h-24 rounded-full border-2 border-amber-500/40 bg-slate-200 dark:bg-slate-950 flex items-center justify-center overflow-hidden shadow-inner flex-shrink-0">
              <img v-if="photoPreview" :src="photoPreview" alt="Preview Foto" class="w-full h-full object-cover" />
              <svg v-else class="w-10 h-10 text-slate-400 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>

            <div class="flex-1 space-y-2 text-center sm:text-left">
              <label class="block font-medium text-slate-700 dark:text-slate-300">Pilih Pasfoto / Foto Formal (PNG / JPG / JPEG)</label>
              <input 
                type="file" 
                accept="image/*" 
                @change="handlePhotoUpload"
                class="block w-full text-xs text-slate-600 dark:text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-amber-500/20 file:text-amber-700 dark:file:text-amber-300 hover:file:bg-amber-500/30 file:cursor-pointer cursor-pointer"
              />
              <p class="text-[11px] text-slate-500 dark:text-slate-400">Maksimal ukuran berkas: 2 MB. Foto ini akan digunakan untuk Kartu Jemaat Digital.</p>
            </div>
          </div>
        </div>

        <!-- SUBMIT & FOOTER ACTIONS (Tanpa Garis Bawah Pada Link) -->
        <div class="pt-6 border-t border-slate-200 dark:border-amber-500/20 flex flex-col-reverse sm:flex-row items-center justify-between gap-4">
          <RouterLink 
            to="/verification-login" 
            class="text-xs font-semibold text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 no-underline transition text-center"
            style="text-decoration: none !important;"
          >
            ← Sudah punya akun? Masuk di sini
          </RouterLink>

          <button 
            type="submit"
            :disabled="isSubmitting"
            class="w-full sm:w-auto px-8 py-3 bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-serif font-bold text-xs uppercase tracking-widest rounded-xl shadow-lg shadow-amber-500/20 transition transform hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 disabled:cursor-not-allowed cursor-pointer"
          >
            <span v-if="isSubmitting">Memproses Pendaftaran...</span>
            <span v-else>Daftar Sebagai Jemaat</span>
          </button>
        </div>

      </form>
    </div>

    <!-- Footer Copyright -->
    <footer class="w-full py-4 text-center text-xs text-slate-500 dark:text-slate-400 z-10">
      &copy; 2026 GracePoint — Platform Manajemen &amp; Pelayanan Digital Gereja
    </footer>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

.font-serif {
  font-family: 'Cinzel', 'Playfair Display', Georgia, 'Times New Roman', serif;
}

/* Hilangkan semua garis bawah pada teks tautan secara mutlak */
a,
a:hover,
a:focus,
a:active,
a:visited,
.brand-link,
.brand-link * {
  text-decoration: none !important;
}

/* ===== Tata letak halaman ===== */
/* 100dvh mengikuti tinggi layar sebenarnya di HP (bar alamat naik/turun), 100vh sebagai cadangan */
.page-root {
  min-height: 100vh;
  min-height: 100dvh;
  padding-top: 1.5rem;
  padding-bottom: max(1.5rem, env(safe-area-inset-bottom, 0px));
}

h1,
h3 {
  text-wrap: balance;
}

/* Penanda judul seksi: garis emas di kiri */
.section-title {
  padding-left: 0.75rem;
  box-shadow: inset 3px 0 0 0 #f59e0b;
}

/* Fokus keyboard yang jelas untuk tautan & tombol */
a:focus-visible,
button:focus-visible {
  outline: 2px solid #f59e0b;
  outline-offset: 2px;
}

/* ===== Kontrol form: satu sumber warna lewat variabel, otomatis mengikuti tema ===== */
.form-control {
  --fc-bg: var(--theme-bg-primary, #ffffff);
  --fc-border: rgba(148, 163, 184, 0.4);
  --fc-text: var(--theme-text-primary, #0f172a);
  --fc-placeholder: #94a3b8;
  --fc-chevron: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");

  display: block;
  width: 100%;
  min-height: 2.75rem; /* target sentuh nyaman di HP */
  padding: 0.625rem 0.875rem;
  font-size: 1rem; /* 16px mencegah auto-zoom di iOS saat input difokuskan */
  line-height: 1.4;
  border-radius: 0.75rem;
  border: 1px solid;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
  background-color: var(--fc-bg) !important;
  border-color: var(--fc-border) !important;
  color: var(--fc-text) !important;
}

@media (min-width: 640px) {
  .form-control {
    font-size: 0.875rem;
  }
}

/* Tema gelap */
html[data-theme="dark"] .form-control,
html.dark .form-control {
  --fc-bg: #0f172a;
  --fc-border: rgba(71, 85, 105, 0.8);
  --fc-text: #f8fafc;
  --fc-placeholder: #64748b;
  --fc-chevron: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  color-scheme: dark; /* ikon kalender, scrollbar, & dropdown ikut gelap */
}

/* Tema terang */
html[data-theme="light"] .form-control,
html.light .form-control {
  --fc-bg: #ffffff;
  --fc-border: #cbd5e1;
  --fc-text: #0f172a;
  --fc-placeholder: #94a3b8;
  --fc-chevron: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  color-scheme: light;
}

.form-control::placeholder {
  color: var(--fc-placeholder);
  opacity: 1;
}

/* Dropdown: panah kustom yang konsisten di semua peramban */
select.form-control {
  -webkit-appearance: none;
  appearance: none;
  padding-right: 2.5rem;
  background-image: var(--fc-chevron);
  background-repeat: no-repeat;
  background-position: right 0.875rem center;
  background-size: 1rem;
  cursor: pointer;
  text-overflow: ellipsis;
}

.form-control option {
  background-color: var(--fc-bg);
}

/* Input tanggal: tidak melebar di iOS */
.form-control[type="date"] {
  -webkit-appearance: none;
  appearance: none;
  min-width: 0;
}

.form-control[type="date"]::-webkit-date-and-time-value {
  text-align: left;
}

textarea.form-control {
  resize: vertical;
}

.form-control:focus {
  outline: none;
  border-color: #f59e0b !important;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.25);
}

/* Tanda salah isi baru muncul setelah pengguna berinteraksi (tanpa JS) */
@supports selector(:user-invalid) {
  .form-control:user-invalid {
    border-color: #f43f5e !important;
  }

  .form-control:user-invalid:focus {
    box-shadow: 0 0 0 3px rgba(244, 63, 94, 0.22);
  }
}

/* Isi otomatis peramban (autofill) tetap terbaca di mode gelap */
.form-control:-webkit-autofill,
.form-control:-webkit-autofill:hover {
  -webkit-text-fill-color: var(--fc-text);
  caret-color: var(--fc-text);
  box-shadow: 0 0 0 1000px var(--fc-bg) inset;
  transition: background-color 9999s ease-out 0s;
}

.form-control:-webkit-autofill:focus {
  -webkit-text-fill-color: var(--fc-text);
  caret-color: var(--fc-text);
  box-shadow: 0 0 0 1000px var(--fc-bg) inset, 0 0 0 3px rgba(245, 158, 11, 0.25);
}

.form-control[readonly] {
  cursor: default;
}

.form-control:disabled,
select.form-control:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Hormati pengaturan "kurangi gerakan" dari sistem */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>