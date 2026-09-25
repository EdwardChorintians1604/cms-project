<script setup>
import 'aos/dist/aos.css'
import 'animate.css'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'
</script>

<template>
  <div class="min-h-screen bg-[var(--theme-bg-primary)] text-[var(--theme-text-primary)] flex flex-col items-center justify-center p-4 relative transition-colors duration-300">
    <!-- Floating Theme Toggle in Top-Right -->
    <div class="absolute top-4 right-4 z-50">
      <ThemeToggleButton />
    </div>
    <div class="w-full max-w-md">
      <slot />
    </div>
  </div>
</template>

<style scoped></style>