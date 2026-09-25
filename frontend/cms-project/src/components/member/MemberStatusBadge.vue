<script setup>
defineProps({ status: { type: String, default: 'active' } })
</script>

<template>
  <span 
    class="px-2.5 py-0.5 text-[10px] font-semibold rounded-full uppercase tracking-wider"
    :class="status === 'active' ? 'bg-emerald-950 text-emerald-300 border border-emerald-700' : 'bg-slate-800 text-slate-400 border border-slate-700'"
  >
    {{ status === 'active' ? 'Aktif' : 'Non-Aktif' }}
  </span>
</template>
