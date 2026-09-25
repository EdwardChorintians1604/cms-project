<script setup>
defineProps({ title: String, subtitle: String })
</script>

<template>
  <div class="border-b border-amber-500/20 pb-2 mb-4">
    <h3 class="text-base font-bold text-amber-300 font-serif">{{ title }}</h3>
    <p v-if="subtitle" class="text-xs text-slate-400 mt-0.5">{{ subtitle }}</p>
  </div>
</template>
