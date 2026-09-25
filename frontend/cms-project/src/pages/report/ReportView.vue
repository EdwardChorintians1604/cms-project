<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Card from '@/components/Card.vue'
</script>

<template>
  <DefaultLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-white">Laporan & Analitik Gereja</h1>
      <Card title="Laporan Pertumbuhan Jemaat & Keuangan" subtitle="Ekspor data PDF/Excel untuk Rapat Majelis">
        <p class="text-sm text-slate-300">Grafik statistik pertumbuhan jemaat, laporan kas, dan kehadiran harian.</p>
      </Card>
    </div>
  </DefaultLayout>
</template>
