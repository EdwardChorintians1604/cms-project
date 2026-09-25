<script setup>
defineProps({ eventTitle: String, date: String, location: String })
</script>

<template>
  <div class="p-4 bg-slate-950 border border-amber-500/30 rounded-xl">
    <h4 class="text-sm font-bold text-amber-300 font-serif">{{ eventTitle }}</h4>
    <p class="text-xs text-slate-400 mt-1">🗓️ {{ date }} | 📍 {{ location }}</p>
  </div>
</template>
