<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Card from '@/components/Card.vue'
</script>

<template>
  <DefaultLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-white">Pemberitahuan & Pusat Notifikasi</h1>
      <Card title="Notifikasi Sistem & Pengumuman" subtitle="Pesan masuk dan log aktivitas">
        <p class="text-sm text-slate-300">Pemberitahuan perubahan jadwal, pengajuan doa, dan warta baru.</p>
      </Card>
    </div>
  </DefaultLayout>
</template>
