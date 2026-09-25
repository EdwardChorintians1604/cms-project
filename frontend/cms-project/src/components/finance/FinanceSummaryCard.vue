<script setup>
defineProps({ income: String, expense: String })
</script>

<template>
  <div class="grid grid-cols-2 gap-3">
    <div class="p-3 bg-emerald-950/60 border border-emerald-800 rounded-lg">
      <span class="text-[10px] text-emerald-400 font-bold uppercase">Pemasukan</span>
      <div class="text-lg font-bold text-emerald-300">{{ income || 'Rp 0' }}</div>
    </div>
    <div class="p-3 bg-rose-950/60 border border-rose-800 rounded-lg">
      <span class="text-[10px] text-rose-400 font-bold uppercase">Pengeluaran</span>
      <div class="text-lg font-bold text-rose-300">{{ expense || 'Rp 0' }}</div>
    </div>
  </div>
</template>
