<script setup>
defineProps({ serviceName: String, time: String, speaker: String })
</script>

<template>
  <div class="p-4 bg-slate-950/80 border border-amber-500/30 rounded-xl">
    <div class="flex justify-between items-center">
      <h4 class="text-sm font-bold text-amber-300">{{ serviceName }}</h4>
      <span class="text-xs text-amber-400 font-mono">{{ time }}</span>
    </div>
    <p class="text-xs text-slate-300 mt-2">Pengkhotbah: {{ speaker }}</p>
  </div>
</template>
