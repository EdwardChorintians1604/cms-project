<script setup>
defineProps({ title: String, channel: String })
</script>

<template>
  <div class="p-3 bg-slate-900 border border-slate-800 rounded-lg">
    <div class="flex justify-between text-xs">
      <span class="font-bold text-amber-300">{{ title }}</span>
      <span class="text-[10px] text-sky-400 font-mono">{{ channel }}</span>
    </div>
  </div>
</template>
