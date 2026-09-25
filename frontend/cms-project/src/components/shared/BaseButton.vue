<script setup>
defineProps({ variant: { type: String, default: 'primary' } })
</script>

<template>
  <button 
    class="px-4 py-2 text-xs font-serif uppercase tracking-wider rounded transition shadow-sm"
    :class="variant === 'primary' ? 'bg-amber-500/20 text-amber-300 border border-amber-400/60 hover:bg-amber-400 hover:text-slate-950' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'"
  >
    <slot />
  </button>
</template>
