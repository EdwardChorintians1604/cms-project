<script setup>
defineProps({
  title: String,
  subtitle: String,
})
</script>

<template>
  <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 shadow-lg backdrop-blur-sm">
    <div v-if="title || subtitle" class="mb-4">
      <h3 v-if="title" class="text-lg font-semibold text-slate-100">{{ title }}</h3>
      <p v-if="subtitle" class="text-sm text-slate-400">{{ subtitle }}</p>
    </div>
    <div>
      <slot />
    </div>
  </div>
</template>
