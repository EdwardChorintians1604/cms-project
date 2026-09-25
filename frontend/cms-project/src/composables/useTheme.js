/**
 * useTheme.js — Sistem Manajemen Tema Global Terpadu GracePoint
 *
 * Sinkronisasi penuh:
 * - data-theme="dark" | "light"
 * - class="dark" | "light" (Tailwind CSS v4 variant)
 * - class="theme-dark" | "theme-light"
 * - Mode: 'dark' | 'light' | 'system'
 * - LocalStorage persistence & real-time system color scheme listener
 */

import { ref, computed } from 'vue'

export const THEME_KEY = 'gracepoint_theme_mode'
export const SYSTEM_THEME_KEY = 'gracepoint_system_theme'

// Reactive state — singleton global
export const isDark = ref(true)
export const themeMode = ref('dark') // 'dark' | 'light' | 'system'

let _initialized = false
let _mediaQueryListener = null

function getSystemPrefersDark() {
  if (typeof window === 'undefined') return true
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}

function computeIsDark(mode) {
  if (mode === 'system') {
    return getSystemPrefersDark()
  }
  return mode === 'dark'
}

export function applyThemeToDOM(dark) {
  if (typeof document === 'undefined') return
  const root = document.documentElement

  if (dark) {
    root.setAttribute('data-theme', 'dark')
    root.classList.remove('theme-light', 'light')
    root.classList.add('theme-dark', 'dark')
  } else {
    root.setAttribute('data-theme', 'light')
    root.classList.remove('theme-dark', 'dark')
    root.classList.add('theme-light', 'light')
  }
}

function syncLocalStorage(mode, dark) {
  try {
    localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light')
    
    const savedSys = localStorage.getItem(SYSTEM_THEME_KEY)
    const sysState = savedSys ? JSON.parse(savedSys) : {}
    sysState.mode = mode
    localStorage.setItem(SYSTEM_THEME_KEY, JSON.stringify(sysState))
  } catch (_) {}
}

function readSavedMode() {
  try {
    // Cek system theme key dulu
    const savedSys = localStorage.getItem(SYSTEM_THEME_KEY)
    if (savedSys) {
      const parsed = JSON.parse(savedSys)
      if (parsed && parsed.mode) return parsed.mode
    }
    // Fallback ke simple key
    const saved = localStorage.getItem(THEME_KEY)
    if (saved !== null) {
      return saved === 'light' ? 'light' : 'dark'
    }
  } catch (_) {}
  return 'dark'
}

export function useTheme() {
  const init = () => {
    if (_initialized) return
    _initialized = true

    themeMode.value = readSavedMode()
    isDark.value = computeIsDark(themeMode.value)
    applyThemeToDOM(isDark.value)

    // Setup listener untuk prefers-color-scheme
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mql = window.matchMedia('(prefers-color-scheme: dark)')
      const handler = (e) => {
        if (themeMode.value === 'system') {
          isDark.value = e.matches
          applyThemeToDOM(isDark.value)
        }
      }
      if (mql.addEventListener) {
        mql.addEventListener('change', handler)
      } else if (mql.addListener) {
        mql.addListener(handler)
      }
      _mediaQueryListener = handler
    }
  }

  const setMode = (mode) => {
    themeMode.value = mode
    isDark.value = computeIsDark(mode)
    applyThemeToDOM(isDark.value)
    syncLocalStorage(mode, isDark.value)
  }

  const toggleTheme = () => {
    const nextDark = !isDark.value
    const nextMode = nextDark ? 'dark' : 'light'
    setMode(nextMode)
  }

  const setDark = () => setMode('dark')
  const setLight = () => setMode('light')
  const setSystem = () => setMode('system')

  return {
    isDark,
    themeMode,
    toggleTheme,
    setDark,
    setLight,
    setSystem,
    setMode,
    init,
  }
}
