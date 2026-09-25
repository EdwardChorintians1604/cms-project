<script setup>
defineProps({ uptime: String })
</script>

<template>
  <div class="flex items-center gap-2 p-3 bg-slate-900 border border-slate-800 rounded-lg text-xs">
    <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
    <span class="text-slate-300">Server Uptime: {{ uptime || '99.9%' }}</span>
  </div>
</template>
