<script setup>
defineProps({ message: String, time: String })
</script>

<template>
  <div class="p-2.5 bg-slate-900 border-b border-slate-800 text-xs">
    <p class="text-slate-200">{{ message }}</p>
    <span class="text-[10px] text-slate-500 font-mono">{{ time }}</span>
  </div>
</template>
