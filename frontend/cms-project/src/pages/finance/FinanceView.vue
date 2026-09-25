<script setup>
import { ref, computed } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// Denominasi Pecahan Uang Kertas & Logam
const denominations = ref([
  { val: 100000, label: 'Rp 100.000', count: 184 },
  { val: 50000, label: 'Rp 50.000', count: 215 },
  { val: 20000, label: 'Rp 20.000', count: 140 },
  { val: 10000, label: 'Rp 10.000', count: 165 },
  { val: 5000, label: 'Rp 5.000', count: 98 },
  { val: 2000, label: 'Rp 2.000', count: 72 },
])

const coinsAmount = ref(154000)
const qrisAmount = ref(8450000)

// Subtotal Uang Tunai Pecahan
const cashTotal = computed(() => {
  const paper = denominations.value.reduce((sum, d) => sum + (d.val * (Number(d.count) || 0)), 0)
  return paper + Number(coinsAmount.value || 0)
})

// Grand Total
const grandTotal = computed(() => {
  return cashTotal.value + Number(qrisAmount.value || 0)
})

const formatRp = (num) => {
  return 'Rp ' + Number(num || 0).toLocaleString('id-ID')
}

// Histori Pemasukan Kas
const recentOfferings = ref([
  { date: '20 Sep 2026', desc: 'Persembahan Kantong Ibadah Raya 1', category: 'Kantong Ibadah', cash: 34188000, digital: 8450000, total: 42638000 },
  { date: '20 Sep 2026', desc: 'Persembahan Kantong Ibadah Raya 2', category: 'Kantong Ibadah', cash: 28450000, digital: 6120000, total: 34570000 },
  { date: '13 Sep 2026', desc: 'Persembahan Kantong Ibadah Raya 1', category: 'Kantong Ibadah', cash: 32900000, digital: 7950000, total: 40850000 },
  { date: '13 Sep 2026', desc: 'Perpuluhan & Ucapan Syukur Transfer', category: 'Perpuluhan', cash: 0, digital: 19800000, total: 19800000 },
])

const saveSuccess = ref(false)
const saveOffering = () => {
  saveSuccess.value = true
  setTimeout(() => {
    saveSuccess.value = false
  }, 4000)
}
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">
      
      <!-- Top Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-emerald-400 font-bold">KEUANGAN & KASIR CABANG</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Kasir Persembahan & Manajemen Kas Ibadah
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Hitung cepat perolehan persembahan kantong mingguan per pecahan lembar rupiah dan rekonsiliasi donasi QRIS digital.
          </p>
        </div>

        <div class="flex items-center gap-2.5">
          <span class="px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-mono font-bold">
            Kas Masuk: {{ formatRp(grandTotal) }}
          </span>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Grand Total Ibadah" subtitle="Tunai + QRIS">
          <div class="text-2xl sm:text-3xl font-bold text-emerald-400 mt-1">{{ formatRp(grandTotal) }}</div>
        </Card>
        <Card title="Uang Tunai Fisik" subtitle="Pecahan lembar kasir">
          <div class="text-2xl sm:text-3xl font-bold text-amber-400 mt-1">{{ formatRp(cashTotal) }}</div>
        </Card>
        <Card title="QRIS / Transfer Bank" subtitle="Digital payment">
          <div class="text-2xl sm:text-3xl font-bold text-sky-400 mt-1">{{ formatRp(qrisAmount) }}</div>
        </Card>
        <Card title="Saldo Kas Cabang" subtitle="Posisi kas saat ini">
          <div class="text-2xl sm:text-3xl font-bold text-white mt-1">Rp 128.450.000</div>
        </Card>
      </div>

      <!-- Kasir Lembar Pecahan -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- Kalkulator Pecahan -->
        <div class="lg:col-span-8 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="font-bold text-white text-sm flex items-center gap-2">
              <span>💵</span> Kalkulator Pecahan Uang Kertas (Fast Cashier Counter)
            </h3>
            <span class="text-[11px] text-amber-400 font-mono">Sesi Ibadah Raya 1</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div
              v-for="d in denominations"
              :key="d.val"
              class="flex items-center justify-between p-3 bg-slate-950/80 border border-slate-800 rounded-xl"
            >
              <div>
                <p class="font-mono font-bold text-amber-300 text-xs">{{ d.label }}</p>
                <p class="text-[10px] text-slate-400 font-mono">
                  Subtotal: <span class="text-slate-200">{{ formatRp(d.val * (d.count || 0)) }}</span>
                </p>
              </div>
              <div class="flex items-center gap-1.5">
                <input
                  v-model.number="d.count"
                  type="number"
                  min="0"
                  class="w-20 px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-right text-white focus:outline-none focus:border-amber-400"
                />
                <span class="text-[10px] text-slate-400 font-sans">lbr</span>
              </div>
            </div>
          </div>

          <!-- Non-Tunai & Koin -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800">
            <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1.5">
              <label class="block text-xs font-medium text-slate-300">Total Uang Koin / Logam (Rp)</label>
              <input
                v-model.number="coinsAmount"
                type="number"
                class="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1.5">
              <label class="block text-xs font-medium text-sky-300">Total Donasi QRIS / Transfer Bank (Rp)</label>
              <input
                v-model.number="qrisAmount"
                type="number"
                class="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-white focus:outline-none focus:border-amber-400"
              />
            </div>
          </div>

          <div class="flex items-center justify-between pt-3 border-t border-slate-800">
            <span v-if="saveSuccess" class="text-xs text-emerald-400 font-bold animate-pulse">
              ✅ Berita acara berhasil disimpan ke DBMS Keuangan Cabang!
            </span>
            <span v-else class="text-xs text-slate-400">Pastikan jumlah fisik telah dihitung oleh 2 orang saksi/kasir.</span>

            <button
              @click="saveOffering"
              class="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 cursor-pointer transition-all"
            >
              💾 Simpan & Cetak Berita Acara
            </button>
          </div>
        </div>

        <!-- Berita Acara Ringkasan -->
        <div class="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div class="pb-3 border-b border-slate-800">
            <h3 class="font-bold text-white text-sm">Berita Acara Penghitungan</h3>
            <p class="text-[11px] text-slate-400">Ringkasan penyerahan kasir ibadah</p>
          </div>

          <div class="space-y-3 font-mono text-xs">
            <div class="flex justify-between text-slate-300">
              <span>Total Uang Kertas:</span>
              <span class="text-white font-bold">{{ formatRp(cashTotal - coinsAmount) }}</span>
            </div>
            <div class="flex justify-between text-slate-300">
              <span>Total Koin:</span>
              <span class="text-white">{{ formatRp(coinsAmount) }}</span>
            </div>
            <div class="flex justify-between text-sky-300">
              <span>Total QRIS & Bank:</span>
              <span class="font-bold">{{ formatRp(qrisAmount) }}</span>
            </div>
            <div class="p-3 bg-slate-950 rounded-xl border border-amber-500/30 flex justify-between items-center text-sm font-bold">
              <span class="text-amber-400">Grand Total:</span>
              <span class="text-emerald-400">{{ formatRp(grandTotal) }}</span>
            </div>
          </div>

          <div class="pt-3 border-t border-slate-800 space-y-2 text-[11px] text-slate-400 font-sans">
            <p>Petugas Penghitung: <span class="text-white font-medium">Bpk. Paulus Sudrajat & Ibu Ester Wijaya</span></p>
            <p>Bendahara Penerima: <span class="text-white font-medium">Ibu Martha Silaban</span></p>
          </div>
        </div>
      </div>

      <!-- History offering table -->
      <Card title="Catatan Persembahan Terakhir" subtitle="Riwayat penghitungan persembahan ibadah cabang" id="laporan">
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th class="p-3">Tanggal</th>
                <th class="p-3">Keterangan</th>
                <th class="p-3">Kategori</th>
                <th class="p-3 text-right">Uang Tunai</th>
                <th class="p-3 text-right">QRIS / Non-Tunai</th>
                <th class="p-3 text-right">Total Persembahan</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
              <tr v-for="(o, idx) in recentOfferings" :key="idx" class="hover:bg-slate-800/40 transition-colors">
                <td class="p-3 font-semibold text-white">{{ o.date }}</td>
                <td class="p-3 text-slate-200">{{ o.desc }}</td>
                <td class="p-3">
                  <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                    {{ o.category }}
                  </span>
                </td>
                <td class="p-3 text-right font-mono text-slate-300">{{ formatRp(o.cash) }}</td>
                <td class="p-3 text-right font-mono text-sky-300">{{ formatRp(o.digital) }}</td>
                <td class="p-3 text-right font-mono font-bold text-emerald-400">{{ formatRp(o.total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

    </div>
  </ChurchAdminLayout>
</template>
