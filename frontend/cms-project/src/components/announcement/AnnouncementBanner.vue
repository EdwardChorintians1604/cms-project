<script setup>
defineProps({ text: String })
</script>

<template>
  <div class="p-3 bg-amber-950/60 border border-amber-500/40 rounded-lg text-amber-200 text-xs font-serif">
    📢 {{ text }}
  </div>
</template>
