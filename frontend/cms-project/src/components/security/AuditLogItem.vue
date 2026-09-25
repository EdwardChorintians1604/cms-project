<script setup>
defineProps({ action: String, user: String })
</script>

<template>
  <div class="p-2.5 bg-slate-950 border-b border-slate-800 text-xs flex justify-between">
    <span class="text-slate-300">{{ action }}</span>
    <span class="text-amber-400 font-mono">{{ user }}</span>
  </div>
</template>
