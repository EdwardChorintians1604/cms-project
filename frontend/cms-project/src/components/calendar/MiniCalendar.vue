<script setup>
defineProps({ monthName: String })
</script>

<template>
  <div class="p-3 bg-slate-900 border border-slate-800 rounded-lg text-center">
    <span class="text-xs font-bold text-amber-300 font-serif">{{ monthName || 'Bulan Ini' }}</span>
  </div>
</template>
