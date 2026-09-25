<script setup>
defineProps({ reportName: String })
</script>

<template>
  <button class="px-3 py-1.5 bg-amber-600/30 hover:bg-amber-600 text-amber-200 border border-amber-500/40 rounded text-xs font-serif transition">
    📥 Unduh {{ reportName || 'Laporan' }}
  </button>
</template>
