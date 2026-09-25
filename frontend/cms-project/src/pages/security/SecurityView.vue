<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Card from '@/components/Card.vue'
</script>

<template>
  <DefaultLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-white">Keamanan & Audit Log</h1>
      <Card title="Hak Akses & Log Aktivitas Admin" subtitle="Manajemen role dan riwayat sesi pengguna">
        <p class="text-sm text-slate-300">Pengaturan autentikasi dua faktor, perizinan role, dan log keamanan audit.</p>
      </Card>
    </div>
  </DefaultLayout>
</template>
