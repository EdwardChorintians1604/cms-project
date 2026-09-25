<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Card from '@/components/Card.vue'
</script>

<template>
  <DefaultLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-white">Pengaturan Aplikasi</h1>
      <Card title="Konfigurasi Umum Sistem" subtitle="Nama Gereja, Alamat, Logo, dan Parameter Aplikasi">
        <p class="text-sm text-slate-300">Kelola identitas gereja, email pengirim, dan integrasi payment gateway.</p>
      </Card>
    </div>
  </DefaultLayout>
</template>
