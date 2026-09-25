import { reactive, watch } from 'vue'
import {
  isDark,
  themeMode,
  useTheme,
  applyThemeToDOM,
  SYSTEM_THEME_KEY
} from './useTheme'

// Palet warna aksen hex & RGB
export const ACCENT_PALETTES = {
  amber: { name: 'Amber Gold', hex: '#f59e0b', hover: '#fbbf24', rgb: '245, 158, 11', badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40' },
  emerald: { name: 'Emerald Sanctuary', hex: '#10b981', hover: '#34d399', rgb: '16, 185, 129', badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' },
  sky: { name: 'Celestial Sky', hex: '#0ea5e9', hover: '#38bdf8', rgb: '14, 165, 233', badge: 'bg-sky-500/20 text-sky-300 border-sky-500/40' },
  purple: { name: 'Royal Purple', hex: '#8b5cf6', hover: '#a78bfa', rgb: '139, 92, 246', badge: 'bg-purple-500/20 text-purple-300 border-purple-500/40' },
  rose: { name: 'Crimson Rose', hex: '#f43f5e', hover: '#fb7185', rgb: '244, 63, 94', badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40' }
}

const themeState = reactive({
  mode: themeMode.value, // 'dark' | 'light' | 'system'
  accent: 'amber',
  headingFont: 'Cinzel',
  uiDensity: 'comfortable',
  glassmorphism: true,
  animations: true,
  cardRadius: 'rounded-2xl'
})

// Sync mode two-way with themeMode
watch(themeMode, (newVal) => {
  if (themeState.mode !== newVal) {
    themeState.mode = newVal
  }
})

export function useSystemTheme() {
  const { setMode } = useTheme()

  const initTheme = () => {
    if (typeof window === 'undefined') return
    try {
      const saved = localStorage.getItem(SYSTEM_THEME_KEY)
      if (saved) {
        Object.assign(themeState, JSON.parse(saved))
        if (themeState.mode) {
          setMode(themeState.mode)
        }
      }
    } catch (e) {
      console.warn('Gagal membaca tema dari storage:', e)
    }
    applyTheme()
  }

  const applyTheme = () => {
    if (typeof document === 'undefined') return
    const root = document.documentElement

    // 1. Sinkronkan dark/light mode menggunakan useTheme
    setMode(themeState.mode)

    // 2. CSS Custom Properties Aksen
    const palette = ACCENT_PALETTES[themeState.accent] || ACCENT_PALETTES.amber
    root.style.setProperty('--accent-color', palette.hex)
    root.style.setProperty('--accent-hover', palette.hover)
    root.style.setProperty('--accent-rgb', palette.rgb)
    root.style.setProperty('--ui-density', themeState.uiDensity === 'compact' ? '0.85' : '1')

    // 3. Simpan ke LocalStorage
    try {
      localStorage.setItem(SYSTEM_THEME_KEY, JSON.stringify(themeState))
    } catch (e) {}
  }

  const setThemeMode = (mode) => {
    themeState.mode = mode
    setMode(mode)
    applyTheme()
  }

  const setAccent = (accentKey) => {
    if (ACCENT_PALETTES[accentKey]) {
      themeState.accent = accentKey
      applyTheme()
    }
  }

  const resetTheme = () => {
    Object.assign(themeState, {
      mode: 'dark',
      accent: 'amber',
      headingFont: 'Cinzel',
      uiDensity: 'comfortable',
      glassmorphism: true,
      animations: true,
      cardRadius: 'rounded-2xl'
    })
    applyTheme()
  }

  return {
    themeState,
    palettes: ACCENT_PALETTES,
    initTheme,
    applyTheme,
    setThemeMode,
    setAccent,
    resetTheme
  }
}
