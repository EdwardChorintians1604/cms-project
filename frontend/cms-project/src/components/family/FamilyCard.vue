<script setup>
defineProps({ familyName: String, headOfFamily: String, memberCount: Number })
</script>

<template>
  <div class="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
    <h4 class="text-sm font-bold text-amber-300">{{ familyName }}</h4>
    <p class="text-xs text-slate-400 mt-1">Kepala Keluarga: {{ headOfFamily }}</p>
    <span class="text-[10px] text-slate-500 mt-2 block">{{ memberCount }} Anggota Terdaftar</span>
  </div>
</template>
