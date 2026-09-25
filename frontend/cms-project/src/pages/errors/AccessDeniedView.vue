<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-emerald-950 flex flex-col items-center justify-center p-6 text-center">
    <h1 class="text-7xl font-black text-rose-500">403</h1>
    <h2 class="text-2xl font-bold text-white mt-3">Akses Ditolak</h2>
    <p class="text-slate-400 mt-2 max-w-md text-sm">Anda tidak memiliki hak akses untuk membuka halaman ini.</p>
    <RouterLink 
      to="/" 
      class="mt-6 px-5 py-2.5 bg-emerald-800 hover:bg-emerald-700 text-amber-200 rounded-xl transition text-sm font-semibold border border-amber-500/30"
    >
      Kembali ke Dashboard
    </RouterLink>
  </div>
</template>
