<script setup>
defineProps({ label: String, value: [String, Number], change: String })
</script>

<template>
  <div class="bg-slate-950/80 border border-amber-500/20 rounded-xl p-4 shadow-md">
    <span class="text-xs text-slate-400 font-serif tracking-wider uppercase">{{ label }}</span>
    <div class="text-2xl font-bold text-amber-300 mt-1">{{ value }}</div>
    <span v-if="change" class="text-[10px] text-emerald-400 font-medium">{{ change }}</span>
  </div>
</template>
