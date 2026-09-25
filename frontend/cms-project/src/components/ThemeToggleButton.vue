<script setup>
import { useTheme } from '@/composables/useTheme'

const { isDark, toggleTheme } = useTheme()
</script>

<template>
  <button
    class="theme-toggle-btn"
    :aria-label="isDark ? 'Beralih ke Mode Terang' : 'Beralih ke Mode Gelap'"
    :title="isDark ? 'Beralih ke Mode Terang (Putih, Biru Muda, Hijau Muda, Emas) ☀️' : 'Beralih ke Mode Gelap (Hitam, Biru Tua, Hijau Tua, Emas) 🌙'"
    @click="toggleTheme"
    type="button"
  >
    <!-- Knob with Sun/Moon Icon -->
    <span class="theme-toggle-knob">
      <span v-if="isDark" class="knob-icon">🌙</span>
      <span v-else class="knob-icon">☀️</span>
    </span>

    <!-- Text Label -->
    <span class="theme-label hidden sm:inline">
      {{ isDark ? 'Gelap' : 'Terang' }}
    </span>

    <!-- Visual Color Palette Indicator Dots -->
    <span class="palette-dots hidden md:inline-flex" :title="isDark ? 'Palet Gelap: Hitam, Biru Tua, Hijau Tua, Emas' : 'Palet Terang: Putih, Biru Muda, Hijau Muda, Emas'">
      <template v-if="isDark">
        <span class="dot bg-[#070b19]" title="Hitam"></span>
        <span class="dot bg-[#1d4ed8]" title="Biru Tua"></span>
        <span class="dot bg-[#15803d]" title="Hijau Tua"></span>
        <span class="dot bg-[#f59e0b]" title="Emas"></span>
      </template>
      <template v-else>
        <span class="dot bg-[#ffffff] border border-slate-300" title="Putih"></span>
        <span class="dot bg-[#38bdf8]" title="Biru Muda"></span>
        <span class="dot bg-[#86efac]" title="Hijau Muda"></span>
        <span class="dot bg-[#d97706]" title="Emas"></span>
      </template>
    </span>
  </button>
</template>

<style scoped>
.theme-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.knob-icon {
  line-height: 1;
  display: block;
}

.palette-dots {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: 2px;
  padding-left: 5px;
  border-left: 1px solid var(--theme-border-soft);
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
}
</style>
