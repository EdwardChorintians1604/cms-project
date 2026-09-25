<script setup>
defineProps({ totalAttendance: Number })
</script>

<template>
  <div class="p-4 bg-slate-900 border border-slate-800 rounded-xl text-center">
    <span class="text-xs text-slate-400 font-serif">Total Kehadiran Ibadah</span>
    <div class="text-3xl font-bold text-emerald-400 mt-1">{{ totalAttendance || 0 }} Jemaat</div>
  </div>
</template>
