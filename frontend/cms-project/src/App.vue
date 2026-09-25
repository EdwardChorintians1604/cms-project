<script setup>
import { nextTick } from 'vue'
import { RouterView } from 'vue-router'
import AOS from 'aos'
import { useTheme } from '@/composables/useTheme'

// Inisialisasi tema dari localStorage — harus sebelum component apapun render
const { init: initTheme } = useTheme()
initTheme()

const onAfterEnter = () => {
  nextTick(() => {
    try {
      AOS.refreshHard()
    } catch (e) {
      // Catch silently
    }
  })
}
</script>

<template>
  <RouterView v-slot="{ Component, route }">
    <Transition
      mode="out-in"
      enter-active-class="animate__animated animate__fadeIn animate__faster"
      leave-active-class="animate__animated animate__fadeOut animate__faster"
      @after-enter="onAfterEnter"
    >
      <component :is="Component" :key="route.path" />
    </Transition>
  </RouterView>
</template>

<style>
.animate__faster {
  animation-duration: 250ms !important;
}
</style>
