<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-emerald-950 flex flex-col items-center justify-center p-6 text-center">
    <h1 class="text-7xl font-black bg-gradient-to-r from-amber-300 via-amber-400 to-amber-200 bg-clip-text text-transparent">404</h1>
    <h2 class="text-2xl font-bold text-white mt-3">Halaman Tidak Ditemukan</h2>
    <p class="text-slate-400 mt-2 max-w-md text-sm">Halaman yang Anda cari tidak tersedia atau alamat URL telah berpindah.</p>
    <RouterLink 
      to="/" 
      class="mt-6 px-5 py-2.5 bg-gradient-to-r from-emerald-700 to-emerald-600 hover:from-emerald-600 hover:to-emerald-500 text-amber-200 rounded-xl transition text-sm font-semibold shadow border border-amber-500/30"
    >
      Kembali ke Beranda
    </RouterLink>
  </div>
</template>
