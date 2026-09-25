<script setup>
import { ref, reactive, onMounted } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'

// Tab Aktif
const activeTab = ref('general') // 'general' | 'church' | 'security'

// State Pengaturan
const isLoading = ref(false)
const isSaving = ref(false)
const errorMessage = ref('')
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

const triggerToast = (msg, type = 'success') => {
  toastMessage.value = msg
  toastType.value = type
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 4000)
}

// Form Options
const settings = reactive({
  // Identitas & Kontak
  site_title: 'GracePoint - Platform Pelayanan Gereja',
  site_tagline: 'Soli Deo Gloria — Melayani dengan Kasih & Kesetiaan',
  synod_name: 'Sinode Pusat GracePoint Church Network',
  admin_email: 'admin@gracepoint.org',
  support_phone: '0812-3456-7890',
  office_address: 'Graha GracePoint Lt. 5, Jl. Jend. Sudirman Kav. 21, Jakarta',
  timezone: 'Asia/Jakarta',
  date_format: 'DD/MM/YYYY',
  time_format: '24h',
  system_language: 'id',

  // Operasional Jemaat & Cabang
  allow_member_registration: true,
  require_branch_verification: true,
  enable_public_calendar: true,
  enable_finance_transparency: true,

  // Keamanan & Akses
  session_expiry_days: 7,
  max_login_attempts: 5,
  enable_audit_logging: true,
  maintenance_mode: false
})

// Load Data dari API Backend Python
const loadSettings = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/settings/`)
    if (res.ok) {
      const data = await res.json()
      if (data.settings) {
        // Flatten grouped settings into flat object
        for (const groupKey in data.settings) {
          const groupObj = data.settings[groupKey]
          for (const k in groupObj) {
            settings[k] = groupObj[k]
          }
        }
      }
    }
  } catch (err) {
    console.warn('Gagal memuat settings dari server, menggunakan data lokal:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadSettings()
})

// Simpan Pengaturan ke Backend Python
const saveSettings = async () => {
  isSaving.value = true
  try {
    const payload = { settings: { ...settings } }
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/settings/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) throw new Error('Gagal menyimpan konfigurasi ke server.')

    triggerToast('Konfigurasi pengaturan sistem berhasil disimpan.')
  } catch (err) {
    console.error('Save settings error:', err)
    triggerToast(err.message || 'Terjadi kesalahan saat menyimpan pengaturan.', 'error')
  } finally {
    isSaving.value = false
  }
}

// Reset Pengaturan ke Default
const resetSettings = async () => {
  if (!confirm('Apakah Anda yakin ingin mengembalikan seluruh pengaturan ke standar pabrikan?')) return

  isSaving.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/settings/reset`, { method: 'POST' })
    if (!res.ok) throw new Error('Gagal mereset pengaturan.')

    await loadSettings()
    triggerToast('Pengaturan telah dikembalikan ke standar awal.')
  } catch (err) {
    triggerToast('Gagal mereset pengaturan.', 'error')
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <MainAdminLayout>
    <div class="space-y-6 text-[#EDE6D6] font-sans pb-12">

      <!-- Toast Feedback -->
      <Transition name="toast">
        <div 
          v-if="showToast"
          :class="[
            'fixed top-5 right-5 z-[100] max-w-md px-4 py-3 rounded-2xl shadow-2xl border flex items-center gap-3 backdrop-blur-xl transition-all duration-300',
            toastType === 'success' ? 'bg-emerald-950/90 text-emerald-200 border-emerald-500/50' : 'bg-rose-950/90 text-rose-200 border-rose-500/50'
          ]"
        >
          <i :class="['bi text-lg', toastType === 'success' ? 'bi-check-circle-fill text-emerald-400' : 'bi-exclamation-octagon-fill text-rose-400']"></i>
          <p class="text-xs font-semibold leading-relaxed">{{ toastMessage }}</p>
          <button @click="showToast = false" class="ml-auto text-slate-400 hover:text-white">
            <i class="bi bi-x-lg text-xs"></i>
          </button>
        </div>
      </Transition>

      <!-- HERO BANNER -->
      <section class="rounded-3xl border border-amber-500/25 bg-gradient-to-r from-[#0d1e27]/90 via-[#0b2027]/85 to-[#09151e]/90 p-6 shadow-2xl backdrop-blur-xl sm:p-8 relative overflow-hidden">
        <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-gear-wide-connected"></i>
              <span>System Configuration &amp; Control</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-100">
              Pengaturan Sistem &amp; Platform Gereja
            </h1>
            <p class="mt-1.5 text-xs sm:text-sm text-[#B8C4C2] max-w-2xl leading-relaxed">
              Atur parameter operasional platform, identitas sinode, kebijakan pendaftaran jemaat, zona waktu, dan keamanan sesi.
            </p>
          </div>

          <div class="flex items-center gap-2.5 shrink-0">
            <button 
              type="button" 
              @click="resetSettings"
              class="px-4 py-2.5 rounded-xl border border-slate-700 text-xs text-slate-300 hover:text-rose-300 hover:bg-white/5 transition cursor-pointer"
            >
              Reset Default
            </button>
            <button 
              type="button" 
              @click="saveSettings"
              :disabled="isSaving"
              class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 text-xs font-bold shadow-lg shadow-amber-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50 transition"
            >
              <i :class="['bi', isSaving ? 'bi-arrow-repeat animate-spin' : 'bi-check-lg']"></i>
              <span>{{ isSaving ? 'Menyimpan...' : 'Simpan Pengaturan' }}</span>
            </button>
          </div>
        </div>
      </section>

      <!-- NAVIGATION TABS -->
      <div class="flex items-center gap-2 border-b border-white/10 pb-3 overflow-x-auto no-scrollbar">
        <button 
          type="button"
          @click="activeTab = 'general'"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer whitespace-nowrap',
            activeTab === 'general' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm' : 'text-slate-400 hover:text-white bg-slate-950/40'
          ]"
        >
          <i class="bi bi-building"></i>
          <span>Identitas &amp; Regional</span>
        </button>

        <button 
          type="button"
          @click="activeTab = 'church'"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer whitespace-nowrap',
            activeTab === 'church' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm' : 'text-slate-400 hover:text-white bg-slate-950/40'
          ]"
        >
          <i class="bi bi-people-fill"></i>
          <span>Kebijakan Pendaftaran &amp; Layanan</span>
        </button>

        <button 
          type="button"
          @click="activeTab = 'security'"
          :class="[
            'px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer whitespace-nowrap',
            activeTab === 'security' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm' : 'text-slate-400 hover:text-white bg-slate-950/40'
          ]"
        >
          <i class="bi bi-shield-lock-fill"></i>
          <span>Keamanan, Sesi &amp; Pemeliharaan</span>
        </button>
      </div>

      <!-- TAB 1: IDENTITAS & REGIONAL -->
      <section v-if="activeTab === 'general'" class="rounded-3xl border border-white/10 bg-[#123138]/70 p-6 shadow-2xl backdrop-blur-xl space-y-6">
        <div>
          <h3 class="font-serif text-lg font-bold text-white flex items-center gap-2">
            <i class="bi bi-globe-americas text-amber-400"></i> Identitas Platform &amp; Informasi Sinode
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Pengaturan profil lembaga gereja, nama situs, dan informasi kontak publik.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
          <div>
            <label class="block font-semibold text-slate-300 mb-1" for="site-title">Nama Situs / Platform</label>
            <input 
              id="site-title"
              v-model="settings.site_title"
              type="text" 
              class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400"
            />
          </div>

          <div>
            <label class="block font-semibold text-slate-300 mb-1" for="synod-name">Nama Sinode / Badan Pengurus Pusat</label>
            <input 
              id="synod-name"
              v-model="settings.synod_name"
              type="text" 
              class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400"
            />
          </div>

          <div class="md:col-span-2">
            <label class="block font-semibold text-slate-300 mb-1" for="site-tagline">Slogan / Tagline Pelayanan</label>
            <input 
              id="site-tagline"
              v-model="settings.site_tagline"
              type="text" 
              class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400"
            />
          </div>

          <div>
            <label class="block font-semibold text-slate-300 mb-1" for="admin-email">Email Resmi Administrator</label>
            <input 
              id="admin-email"
              v-model="settings.admin_email"
              type="email" 
              class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400"
            />
          </div>

          <div>
            <label class="block font-semibold text-slate-300 mb-1" for="support-phone">Nomor Telepon Hotline / WhatsApp</label>
            <input 
              id="support-phone"
              v-model="settings.support_phone"
              type="text" 
              class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400"
            />
          </div>

          <div class="md:col-span-2">
            <label class="block font-semibold text-slate-300 mb-1" for="office-address">Alamat Kantor Pusat Sekretariat</label>
            <textarea 
              id="office-address"
              v-model="settings.office_address"
              rows="2"
              class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400"
            ></textarea>
          </div>
        </div>

        <div class="pt-4 border-t border-white/10">
          <h4 class="font-serif text-base font-bold text-white mb-3 flex items-center gap-2">
            <i class="bi bi-clock-history text-amber-400"></i> Pengaturan Waktu &amp; Bahasa
          </h4>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label class="block font-semibold text-slate-300 mb-1" for="timezone-select">Zona Waktu Sistem</label>
              <select 
                id="timezone-select"
                v-model="settings.timezone"
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400 cursor-pointer"
              >
                <option value="Asia/Jakarta">WIB (Jakarta / Sumatra / Jawa)</option>
                <option value="Asia/Makassar">WITA (Bali / Sulawesi / Kalimantan)</option>
                <option value="Asia/Jayapura">WIT (Maluku / Papua)</option>
              </select>
            </div>

            <div>
              <label class="block font-semibold text-slate-300 mb-1" for="date-format-select">Format Penanggalan</label>
              <select 
                id="date-format-select"
                v-model="settings.date_format"
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400 cursor-pointer"
              >
                <option value="DD/MM/YYYY">DD/MM/YYYY (Contoh: 12/09/2026)</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD (Standar ISO)</option>
                <option value="D MMMM YYYY">12 September 2026</option>
              </select>
            </div>

            <div>
              <label class="block font-semibold text-slate-300 mb-1" for="language-select">Bahasa Utama Antarmuka</label>
              <select 
                id="language-select"
                v-model="settings.system_language"
                class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400 cursor-pointer"
              >
                <option value="id">Bahasa Indonesia (Resmi)</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 2: KEBIJAKAN JEMAAT & CABANG -->
      <section v-if="activeTab === 'church'" class="rounded-3xl border border-white/10 bg-[#123138]/70 p-6 shadow-2xl backdrop-blur-xl space-y-6">
        <div>
          <h3 class="font-serif text-lg font-bold text-white flex items-center gap-2">
            <i class="bi bi-shield-check text-amber-400"></i> Kebijakan Pelayanan &amp; Akses Publik
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Kontrol izin pendaftaran jemaat baru, approval cabang, serta visibilitas modul publik.</p>
        </div>

        <div class="space-y-4">
          <!-- Toggle 1: Pendaftaran Jemaat Mandiri -->
          <div class="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 flex items-center justify-between gap-4">
            <div>
              <p class="text-xs font-bold text-white">Izinkan Pendaftaran Jemaat Mandiri Online</p>
              <p class="text-[11px] text-slate-400 mt-0.5">Calon warga jemaat dapat mendaftarkan akun di portal tanpa harus input manual oleh admin.</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.allow_member_registration" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
            </label>
          </div>

          <!-- Toggle 2: Verifikasi Cabang Gereja Baru -->
          <div class="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 flex items-center justify-between gap-4">
            <div>
              <p class="text-xs font-bold text-white">Wajibkan Verifikasi Manual Registrasi Cabang Gereja</p>
              <p class="text-[11px] text-slate-400 mt-0.5">Akun admin cabang yang mendaftar baru berstatus Pending hingga disetujui Superadmin.</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.require_branch_verification" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
            </label>
          </div>

          <!-- Toggle 3: Kalender Liturgi & Agenda Publik -->
          <div class="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 flex items-center justify-between gap-4">
            <div>
              <p class="text-xs font-bold text-white">Publikasikan Kalender Liturgi &amp; Kegiatan</p>
              <p class="text-[11px] text-slate-400 mt-0.5">Memungkinkan jemaat dan pengunjung umum melihat jadwal hari raya &amp; agenda di halaman publik.</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.enable_public_calendar" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
            </label>
          </div>

          <!-- Toggle 4: Transparansi Ringkasan Keuangan -->
          <div class="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 flex items-center justify-between gap-4">
            <div>
              <p class="text-xs font-bold text-white">Transparansi Statistik Keuangan di Dashboard Jemaat</p>
              <p class="text-[11px] text-slate-400 mt-0.5">Menampilkan rekapitulasi grafik pemasukan &amp; pemakaian dana di portal user jemaat.</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.enable_finance_transparency" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
            </label>
          </div>
        </div>
      </section>

      <!-- TAB 3: KEAMANAN & PEMELIHARAAN -->
      <section v-if="activeTab === 'security'" class="rounded-3xl border border-white/10 bg-[#123138]/70 p-6 shadow-2xl backdrop-blur-xl space-y-6">
        <div>
          <h3 class="font-serif text-lg font-bold text-white flex items-center gap-2">
            <i class="bi bi-shield-shaded text-rose-400"></i> Keamanan Sesi &amp; Kontrol Pemeliharaan
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Konfigurasi keamanan token JWT, pembatasan brute-force, dan mode darurat sistem.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
          <div>
            <label class="block font-semibold text-slate-300 mb-1" for="session-expiry">Masa Berlaku Sesi Login Token (Hari)</label>
            <input 
              id="session-expiry"
              v-model.number="settings.session_expiry_days"
              type="number" 
              min="1" 
              max="60" 
              class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400"
            />
            <p class="text-[10px] text-slate-500 mt-1">User otomatis logout setelah durasi ini tercapai.</p>
          </div>

          <div>
            <label class="block font-semibold text-slate-300 mb-1" for="max-login-attempts">Batas Percobaan Login Salah (Rate Limiting)</label>
            <input 
              id="max-login-attempts"
              v-model.number="settings.max_login_attempts"
              type="number" 
              min="3" 
              max="15" 
              class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400"
            />
            <p class="text-[10px] text-slate-500 mt-1">IP address akan diblokir sementara jika salah melampaui batas.</p>
          </div>
        </div>

        <div class="space-y-4 pt-4 border-t border-white/10">
          <!-- Audit Log Toggle -->
          <div class="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 flex items-center justify-between gap-4">
            <div>
              <p class="text-xs font-bold text-white">Pencatatan Jejak Audit Transaksi SHA-256</p>
              <p class="text-[11px] text-slate-400 mt-0.5">Setiap perubahan data akun, keuangan, dan sistem akan di-hash secara kriptografis.</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.enable_audit_logging" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
            </label>
          </div>

          <!-- Maintenance Mode Toggle -->
          <div class="p-4 rounded-2xl bg-rose-950/30 border border-rose-500/30 flex items-center justify-between gap-4">
            <div>
              <p class="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                <i class="bi bi-exclamation-triangle-fill"></i> Mode Pemeliharaan Sistem (Maintenance Mode)
              </p>
              <p class="text-[11px] text-rose-200/70 mt-0.5">Jika diaktifkan, halaman publik dan portal jemaat akan menampilkan halaman pemeliharaan sementara.</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="settings.maintenance_mode" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-rose-500"></div>
            </label>
          </div>
        </div>
      </section>

    </div>
  </MainAdminLayout>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
