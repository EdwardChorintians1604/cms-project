<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
    <h1 class="text-6xl font-extrabold text-sky-500">404</h1>
    <h2 class="text-2xl font-bold text-white mt-2">Halaman Tidak Ditemukan</h2>
    <p class="text-slate-400 mt-2 max-w-md">Halaman yang Anda cari mungkin telah dipindahkan atau tidak ada.</p>
    <RouterLink 
      to="/" 
      class="mt-6 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition text-sm font-medium"
    >
      Kembali ke Beranda
    </RouterLink>
  </div>
</template>
