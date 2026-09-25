<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Card from '@/components/Card.vue'
import { useAuth } from '@/composables/useAuth'

const { user } = useAuth()
</script>

<template>
  <DefaultLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-white">Profil Pengguna</h1>
      <Card title="Detail Akun Anda" subtitle="Informasi identitas dan pengaturan keamanan kata sandi">
        <div class="space-y-2 text-sm text-slate-300">
          <p><strong class="text-slate-100">Nama Lengkap:</strong> {{ user?.name || 'Administrator SystemKita' }}</p>
          <p><strong class="text-slate-100">Alamat Email:</strong> {{ user?.email || 'admin@example.com' }}</p>
          <p><strong class="text-slate-100">Peran Sistem:</strong> {{ user?.role || 'Super Admin' }}</p>
        </div>
      </Card>
    </div>
  </DefaultLayout>
</template>
