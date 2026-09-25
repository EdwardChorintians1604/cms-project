<script setup>
defineProps({ name: String, address: String })
</script>

<template>
  <div class="bg-gradient-to-r from-amber-950/80 via-slate-900 to-amber-950/80 border border-amber-500/30 rounded-xl p-6 shadow-lg">
    <h1 class="text-2xl font-serif font-bold text-amber-300">{{ name || 'SystemKita Portal Gereja' }}</h1>
    <p class="text-xs text-slate-300 mt-1">{{ address || 'Layanan Pelayanan & Manajemen Jemaat' }}</p>
  </div>
</template>
