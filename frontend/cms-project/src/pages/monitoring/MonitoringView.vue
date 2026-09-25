<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Card from '@/components/Card.vue'
</script>

<template>
  <DefaultLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-white">Monitoring Performa & Sistem</h1>
      <Card title="Status Server & API Service" subtitle="Kondisi kesehatan database dan layanan jaringan">
        <p class="text-sm text-slate-300">Pengawasan latensi API, statistik penggunaan memori server, dan uptime.</p>
      </Card>
    </div>
  </DefaultLayout>
</template>
