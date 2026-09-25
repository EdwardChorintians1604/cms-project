<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { useSystemTheme, ACCENT_PALETTES } from '@/composables/useSystemTheme'

const { themeState, palettes, applyTheme, resetTheme: resetLocalTheme, setThemeMode, setAccent } = useSystemTheme()

// Status UI
const isSaving = ref(false)
const isLoading = ref(false)
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

// Opsi Pilihan Radius
const radiusOptions = [
  { label: 'Subtle (12px)', value: 'rounded-xl' },
  { label: 'Modern (16px)', value: 'rounded-2xl' },
  { label: 'Soft Pebble (24px)', value: 'rounded-3xl' }
]

// Opsi Pilihan Font
const fontOptions = [
  { label: 'Cinzel (Serif Klasik Liturgis)', value: 'Cinzel', class: 'font-serif' },
  { label: 'Inter (Sans-Serif Modern Minimalis)', value: 'Inter', class: 'font-sans' }
]

// Load Pengaturan Tema dari Server
const loadThemeFromServer = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/settings/`)
    if (res.ok) {
      const data = await res.json()
      if (data.settings && data.settings.theme) {
        const t = data.settings.theme
        if (t.theme_mode) themeState.mode = t.theme_mode
        if (t.accent_color && palettes[t.accent_color]) themeState.accent = t.accent_color
        if (t.heading_font) themeState.headingFont = t.heading_font
        if (t.ui_density) themeState.uiDensity = t.ui_density
        applyTheme()
      }
    }
  } catch (err) {
    console.warn('Gagal memuat tema dari server:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadThemeFromServer()
})

// Simpan Perubahan Tema ke Backend Server
const saveThemeToServer = async () => {
  isSaving.value = true
  try {
    const payload = {
      settings: {
        theme_mode: themeState.mode,
        accent_color: themeState.accent,
        heading_font: themeState.headingFont,
        ui_density: themeState.uiDensity
      }
    }

    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/settings/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!res.ok) throw new Error('Gagal menyimpan tema ke server.')

    applyTheme()
    triggerToast('Konfigurasi tema & tampilan berhasil disimpan ke server!')
  } catch (err) {
    console.error('Error simpan tema:', err)
    triggerToast(err.message || 'Gagal menyimpan tema.', 'error')
  } finally {
    isSaving.value = false
  }
}

// Reset ke Pengaturan Standar
const handleReset = async () => {
  if (!confirm('Kembalikan tema dan tampilan visual ke pengaturan awal GracePoint?')) return

  resetLocalTheme()
  await saveThemeToServer()
  triggerToast('Tema telah dikembalikan ke standar awal.')
}

// Current active palette helper
const activePalette = computed(() => {
  return palettes[themeState.accent] || palettes.amber
})
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
        <div 
          class="absolute -right-16 -bottom-16 w-64 h-64 rounded-full blur-3xl pointer-events-none opacity-20"
          :style="{ backgroundColor: activePalette.hex }"
        ></div>

        <div class="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-extrabold uppercase tracking-widest mb-2">
              <i class="bi bi-palette-fill"></i>
              <span>Theme Customizer &amp; Visual Engine</span>
            </div>
            <h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-300 to-yellow-100">
              Tema &amp; Desain Tampilan Platform
            </h1>
            <p class="mt-1.5 text-xs sm:text-sm text-[#B8C4C2] max-w-2xl leading-relaxed">
              Personalisasikan mode warna gelap/terang, palet aksen liturgis, tipografi judul, dan efek visual antarmuka platform GracePoint.
            </p>
          </div>

          <div class="flex items-center gap-2.5 shrink-0">
            <button 
              type="button" 
              @click="handleReset"
              class="px-4 py-2.5 rounded-xl border border-slate-700 text-xs text-slate-300 hover:text-rose-300 hover:bg-white/5 transition cursor-pointer"
            >
              Reset Default
            </button>
            <button 
              type="button" 
              @click="saveThemeToServer"
              :disabled="isSaving"
              class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 text-xs font-bold shadow-lg shadow-amber-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50 transition"
              :style="{ background: `linear-gradient(135deg, ${activePalette.hex}, ${activePalette.hover})` }"
            >
              <i :class="['bi', isSaving ? 'bi-arrow-repeat animate-spin' : 'bi-check2-circle']"></i>
              <span>{{ isSaving ? 'Menerapkan...' : 'Simpan Tema' }}</span>
            </button>
          </div>
        </div>
      </section>

      <!-- MAIN CONTENT: GRID 2 KOLOM -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- KOLOM KIRI: CONTROLS PENGATURAN (8 KOLOM) -->
        <div class="lg:col-span-7 space-y-6">

          <!-- 1. MODE TEMA (DARK / LIGHT / SYSTEM) -->
          <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-6 shadow-2xl backdrop-blur-xl space-y-4">
            <div>
              <h3 class="font-serif text-base font-bold text-white flex items-center gap-2">
                <i class="bi bi-moon-stars-fill text-amber-400"></i> Mode Tampilan (Color Scheme)
              </h3>
              <p class="text-xs text-slate-400 mt-0.5">Pilih basis kontras tampilan antarmuka.</p>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <!-- Dark Mode -->
              <button 
                type="button"
                @click="setThemeMode('dark')"
                :class="[
                  'p-3.5 rounded-2xl border text-left transition flex flex-col items-center gap-2 cursor-pointer',
                  themeState.mode === 'dark' 
                    ? 'border-amber-500 bg-amber-500/15 text-white ring-2 ring-amber-500/40' 
                    : 'border-white/10 bg-slate-950/60 text-slate-400 hover:text-white hover:border-white/20'
                ]"
              >
                <div class="w-10 h-10 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-center text-amber-400 text-lg shadow-inner">
                  <i class="bi bi-moon-fill"></i>
                </div>
                <div class="text-center">
                  <span class="text-xs font-bold block">Dark Obsidian</span>
                  <span class="text-[10px] text-slate-400">Bawaan Liturgis</span>
                </div>
              </button>

              <!-- Light Mode -->
              <button 
                type="button"
                @click="setThemeMode('light')"
                :class="[
                  'p-3.5 rounded-2xl border text-left transition flex flex-col items-center gap-2 cursor-pointer',
                  themeState.mode === 'light' 
                    ? 'border-amber-500 bg-amber-500/15 text-white ring-2 ring-amber-500/40' 
                    : 'border-white/10 bg-slate-950/60 text-slate-400 hover:text-white hover:border-white/20'
                ]"
              >
                <div class="w-10 h-10 rounded-xl bg-slate-100 border border-slate-300 flex items-center justify-center text-amber-600 text-lg shadow-inner">
                  <i class="bi bi-sun-fill"></i>
                </div>
                <div class="text-center">
                  <span class="text-xs font-bold block">Clean Slate</span>
                  <span class="text-[10px] text-slate-400">Terang &amp; Bersih</span>
                </div>
              </button>

              <!-- System Sync -->
              <button 
                type="button"
                @click="setThemeMode('system')"
                :class="[
                  'p-3.5 rounded-2xl border text-left transition flex flex-col items-center gap-2 cursor-pointer',
                  themeState.mode === 'system' 
                    ? 'border-amber-500 bg-amber-500/15 text-white ring-2 ring-amber-500/40' 
                    : 'border-white/10 bg-slate-950/60 text-slate-400 hover:text-white hover:border-white/20'
                ]"
              >
                <div class="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-sky-400 text-lg shadow-inner">
                  <i class="bi bi-laptop"></i>
                </div>
                <div class="text-center">
                  <span class="text-xs font-bold block">Sinkron OS</span>
                  <span class="text-[10px] text-slate-400">Ikuti Perangkat</span>
                </div>
              </button>
            </div>
          </section>

          <!-- 2. PALET WARNA AKSEN -->
          <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-6 shadow-2xl backdrop-blur-xl space-y-4">
            <div>
              <h3 class="font-serif text-base font-bold text-white flex items-center gap-2">
                <i class="bi bi-brush-fill text-amber-400"></i> Warna Aksen Liturgis &amp; Primer
              </h3>
              <p class="text-xs text-slate-400 mt-0.5">Warna yang digunakan pada tombol penting, sorotan teks, tautan, dan badge status.</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <div 
                v-for="(pal, key) in palettes" 
                :key="key"
                @click="setAccent(key)"
                :class="[
                  'p-3 rounded-2xl border transition cursor-pointer flex items-center gap-3',
                  themeState.accent === key 
                    ? 'border-white/40 bg-white/10 ring-2 ring-amber-400/50' 
                    : 'border-white/10 bg-slate-950/50 hover:bg-white/5'
                ]"
              >
                <div 
                  class="w-7 h-7 rounded-full flex items-center justify-center shadow-md shrink-0 transition-transform"
                  :style="{ backgroundColor: pal.hex }"
                >
                  <i v-if="themeState.accent === key" class="bi bi-check text-slate-950 font-black text-sm"></i>
                </div>
                <div class="overflow-hidden">
                  <p class="text-xs font-bold text-white truncate">{{ pal.name }}</p>
                  <p class="text-[10px] text-slate-400 font-mono">{{ pal.hex }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- 3. TIPOGRAFI & EFEK VISUAL -->
          <section class="rounded-3xl border border-white/10 bg-[#123138]/70 p-6 shadow-2xl backdrop-blur-xl space-y-4">
            <div>
              <h3 class="font-serif text-base font-bold text-white flex items-center gap-2">
                <i class="bi bi-type text-amber-400"></i> Tipografi &amp; Kerapatan Visual
              </h3>
              <p class="text-xs text-slate-400 mt-0.5">Sesuaikan kenyamanan membaca dan kepadatan antarmuka pengguna.</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <!-- Font Header -->
              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="heading-font">Font Judul / Heading</label>
                <select 
                  id="heading-font"
                  v-model="themeState.headingFont" 
                  @change="applyTheme"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400 cursor-pointer"
                >
                  <option v-for="font in fontOptions" :key="font.value" :value="font.value">
                    {{ font.label }}
                  </option>
                </select>
              </div>

              <!-- Radius Kartu -->
              <div>
                <label class="block font-semibold text-slate-300 mb-1" for="card-radius">Lengkungan Sudut Kartu (Radius)</label>
                <select 
                  id="card-radius"
                  v-model="themeState.cardRadius" 
                  @change="applyTheme"
                  class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-white outline-none focus:border-amber-400 cursor-pointer"
                >
                  <option v-for="rad in radiusOptions" :key="rad.value" :value="rad.value">
                    {{ rad.label }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Toggles Efek -->
            <div class="space-y-3 pt-3 border-t border-white/10">
              <div class="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-center justify-between gap-4">
                <div>
                  <p class="text-xs font-bold text-white">Efek Kaca Akrilik (Glassmorphism)</p>
                  <p class="text-[11px] text-slate-400">Menampilkan efek blur tembus pandang pada panel kontrol.</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="themeState.glassmorphism" @change="applyTheme" class="sr-only peer">
                  <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                </label>
              </div>

              <div class="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-center justify-between gap-4">
                <div>
                  <p class="text-xs font-bold text-white">Animasi &amp; Transisi Halus</p>
                  <p class="text-[11px] text-slate-400">Animasi micro-interactions saat beralih tab, hover kartu, dan navigasi.</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="themeState.animations" @change="applyTheme" class="sr-only peer">
                  <div class="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500"></div>
                </label>
              </div>
            </div>
          </section>

        </div>

        <!-- KOLOM KANAN: LIVE INTERACTIVE PREVIEW SANDBOX (5 KOLOM) -->
        <div class="lg:col-span-5">
          <div class="sticky top-20 space-y-4">

            <div class="rounded-3xl border border-white/15 bg-gradient-to-b from-[#0e242c] to-[#071318] p-5 shadow-2xl overflow-hidden relative">
              <div class="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
                <div class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span class="text-xs font-black uppercase tracking-wider text-slate-300">Live Preview Sandbox</span>
                </div>
                <span 
                  class="text-[10px] font-bold px-2 py-0.5 rounded-full border"
                  :style="{
                    backgroundColor: `${activePalette.hex}22`,
                    borderColor: `${activePalette.hex}55`,
                    color: activePalette.hover
                  }"
                >
                  {{ activePalette.name }}
                </span>
              </div>

              <!-- PREVIEW CARD SAMPLE -->
              <div 
                :class="[
                  'p-5 border transition-all duration-300 space-y-4',
                  themeState.cardRadius,
                  themeState.glassmorphism ? 'bg-[#123138]/80 backdrop-blur-md' : 'bg-[#123138]',
                  'border-white/10 shadow-xl'
                ]"
              >
                <div class="flex items-center justify-between">
                  <span 
                    class="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-1 rounded-full border"
                    :style="{
                      backgroundColor: `${activePalette.hex}20`,
                      borderColor: `${activePalette.hex}60`,
                      color: activePalette.hover
                    }"
                  >
                    Warta Jemaat Terbaru
                  </span>
                  <span class="text-[10px] text-slate-400">12 Sep 2026</span>
                </div>

                <div>
                  <h4 
                    :class="[
                      'text-base font-bold text-white leading-snug',
                      themeState.headingFont === 'Cinzel' ? 'font-serif' : 'font-sans'
                    ]"
                  >
                    Ibadah Raya Syukur &amp; Perjamuan Kudus
                  </h4>
                  <p class="text-xs text-slate-300 mt-1 line-clamp-2 leading-relaxed">
                    Sesi ibadah offline dan streaming YouTube Live bertempat di Gedung Gratia Utama GracePoint.
                  </p>
                </div>

                <!-- Live Metrics Mock -->
                <div class="grid grid-cols-2 gap-3 pt-3 border-t border-white/10">
                  <div class="p-2.5 rounded-xl bg-slate-950/60 border border-white/5">
                    <p class="text-[10px] text-slate-400">Kehadiran Jemaat</p>
                    <p 
                      class="text-sm font-black mt-0.5"
                      :style="{ color: activePalette.hex }"
                    >
                      1,482 Jiwa
                    </p>
                  </div>
                  <div class="p-2.5 rounded-xl bg-slate-950/60 border border-white/5">
                    <p class="text-[10px] text-slate-400">Pelayan Bertugas</p>
                    <p class="text-sm font-black text-white mt-0.5">36 Tim</p>
                  </div>
                </div>

                <!-- Input Preview -->
                <div>
                  <label class="block text-[10px] font-bold text-slate-400 mb-1" for="preview-input">Kotak Input Form</label>
                  <input 
                    id="preview-input"
                    type="text" 
                    value="Contoh input teks responsif" 
                    class="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white outline-none"
                    :style="{ borderColor: `${activePalette.hex}80` }"
                  />
                </div>

                <!-- Buttons Preview -->
                <div class="flex items-center gap-2 pt-1">
                  <button 
                    type="button"
                    class="flex-1 py-2 px-3 rounded-xl text-xs font-bold text-slate-950 shadow-md transition"
                    :style="{ backgroundColor: activePalette.hex }"
                  >
                    Aksi Utama
                  </button>
                  <button 
                    type="button"
                    class="flex-1 py-2 px-3 rounded-xl text-xs font-bold border transition text-white"
                    :style="{ borderColor: activePalette.hex, color: activePalette.hover }"
                  >
                    Aksi Sekunder
                  </button>
                </div>
              </div>

              <!-- Theme State Info Specs -->
              <div class="mt-4 p-3 rounded-2xl bg-slate-950/80 border border-white/5 text-[11px] font-mono text-slate-400 space-y-1">
                <div class="flex justify-between">
                  <span>CSS Var:</span>
                  <span class="text-slate-200">--accent-color: {{ activePalette.hex }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Mode Kelas:</span>
                  <span class="text-slate-200">{{ themeState.mode }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Font:</span>
                  <span class="text-slate-200">{{ themeState.headingFont }}</span>
                </div>
              </div>

            </div>

          </div>
        </div>

      </div>

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
