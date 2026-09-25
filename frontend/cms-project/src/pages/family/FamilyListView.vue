<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Card from '@/components/Card.vue'
</script>

<template>
  <DefaultLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-white">Manajemen Kepala Keluarga (KK)</h1>
      <Card title="Data Keluarga" subtitle="Pengelompokan jemaat berdasarkan Kartu Keluarga Gereja">
        <p class="text-sm text-slate-300">Daftar kepala keluarga dan anggota keluarga terdaftar.</p>
      </Card>
    </div>
  </DefaultLayout>
</template>
