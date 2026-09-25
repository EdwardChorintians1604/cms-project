<script setup>
defineProps({ ministryName: String })
</script>

<template>
  <span class="px-2 py-1 bg-amber-950/60 border border-amber-500/40 text-amber-300 rounded text-xs font-serif">
    {{ ministryName }}
  </span>
</template>
