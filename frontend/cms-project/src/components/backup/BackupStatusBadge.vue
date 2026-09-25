<script setup>
defineProps({ lastBackupDate: String })
</script>

<template>
  <div class="p-3 bg-slate-900 border border-slate-800 rounded-lg text-xs">
    <span class="text-slate-400">Backup Terakhir:</span>
    <span class="text-emerald-400 font-bold ml-1">{{ lastBackupDate || 'Hari ini' }}</span>
  </div>
</template>
