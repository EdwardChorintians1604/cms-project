<script setup>
defineProps({ subject: String, pastor: String, date: String })
</script>

<template>
  <div class="p-3 bg-slate-900 border-l-2 border-amber-400 rounded-r-lg">
    <h5 class="text-xs font-semibold text-slate-200">{{ subject }}</h5>
    <div class="flex justify-between text-[10px] text-slate-400 mt-1">
      <span>Pelayan: {{ pastor }}</span>
      <span>{{ date }}</span>
    </div>
  </div>
</template>
