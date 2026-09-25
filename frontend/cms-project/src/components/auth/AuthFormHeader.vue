<script setup>
defineProps({ title: String, subtitle: String })
</script>

<template>
  <div class="text-center mb-4">
    <h2 v-if="title" class="text-xl font-bold text-amber-300 font-serif">{{ title }}</h2>
    <p v-if="subtitle" class="text-xs text-slate-400 mt-1">{{ subtitle }}</p>
  </div>
</template>
