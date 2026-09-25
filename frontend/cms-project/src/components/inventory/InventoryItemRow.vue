<script setup>
defineProps({ itemName: String, condition: String, qty: Number })
</script>

<template>
  <div class="flex justify-between items-center p-3 bg-slate-900 border-b border-slate-800 text-xs">
    <span class="font-medium text-slate-200">{{ itemName }}</span>
    <span class="text-slate-400">Kondisi: {{ condition }} ({{ qty }} unit)</span>
  </div>
</template>
