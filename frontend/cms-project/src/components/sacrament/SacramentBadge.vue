<script setup>
defineProps({ type: String, certificateNo: String })
</script>

<template>
  <div class="p-3 bg-slate-900 border border-slate-800 rounded-lg">
    <span class="text-xs font-bold text-amber-400 uppercase tracking-wider">{{ type }}</span>
    <p class="text-[10px] text-slate-400 mt-0.5">No. Sertifikat: {{ certificateNo }}</p>
  </div>
</template>
