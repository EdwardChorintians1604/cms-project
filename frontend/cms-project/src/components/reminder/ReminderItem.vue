<script setup>
defineProps({ title: String, time: String })
</script>

<template>
  <div class="flex justify-between items-center p-2.5 bg-slate-900 border border-slate-800 rounded-md text-xs">
    <span class="text-slate-200">{{ title }}</span>
    <span class="text-[10px] text-amber-400 font-mono">{{ time }}</span>
  </div>
</template>
