<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ChurchAdminLayout from '@/layouts/ChurchAdminLayout.vue'
import Card from '@/components/Card.vue'

// Base URL API
const apiBaseUrl = ref(import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1')

// Status Koneksi DBMS PostgreSQL
const dbmsStatus = reactive({
  connected: false,
  engine: 'PostgreSQL',
  tables: 'church_inventories & church_inventory_loans',
  lastStatus: 'Menghubungkan ke DBMS...',
})

// Konteks Cabang Gereja Aktif
const activeChurch = reactive({
  id: null,
  code: 'GBI-PAD-11',
  name: 'Gereja Bethel Indonesia Cabang',
  adminName: 'Admin Gereja',
})

// Helper Auth Token & Headers
const getAuthToken = () => {
  return (
    localStorage.getItem('cms_auth_token') ||
    localStorage.getItem('gp_auth_token') ||
    localStorage.getItem('token') ||
    ''
  )
}

const getAuthHeaders = () => {
  const token = getAuthToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

// Inisialisasi Konteks Cabang dari Login / Session
const initChurchContext = async () => {
  try {
    const rawUser = localStorage.getItem('user_data') || localStorage.getItem('user')
    if (rawUser) {
      const u = JSON.parse(rawUser)
      if (u.church_code) activeChurch.code = u.church_code
      if (u.church_name) activeChurch.name = u.church_name
      if (u.admin_name || u.full_name) activeChurch.adminName = u.admin_name || u.full_name
      if (u.church_id) activeChurch.id = u.church_id
    }

    const token = getAuthToken()
    if (token) {
      const meRes = await fetch(`${apiBaseUrl.value}/users/me`, { headers: getAuthHeaders() })
      if (meRes.ok) {
        const me = await meRes.json()
        if (me.church_code) activeChurch.code = me.church_code
        if (me.church_name) activeChurch.name = me.church_name
        if (me.admin_name || me.full_name) activeChurch.adminName = me.admin_name || me.full_name
        if (me.church_id) activeChurch.id = me.church_id
      }
    }
  } catch (err) {
    console.warn('Gagal memuat profil cabang otomatis:', err)
  }
}

// Tab Aktif: 'loans' (Peminjaman & Pihak Luar), 'rooms' (Gedung & Ruangan), 'assets' (Inventaris Multimedia/Alat)
const activeTab = ref('loans')

// State Data dari PostgreSQL
const inventories = ref([])
const loans = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)

// State Filter Tab Peminjaman
const loanSearch = ref('')
const selectedBorrowerType = ref('Semua')
const selectedLoanStatus = ref('Semua')

// State Filter Tab Inventaris
const invSearch = ref('')
const selectedInvCategory = ref('Semua')

// Toast Notification
const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

const showToast = (message, type = 'success') => {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 4500)
}

// Modal States
const isLoanModalOpen = ref(false)
const isReturnModalOpen = ref(false)
const isAddInvModalOpen = ref(false)
const isDeleteLoanModalOpen = ref(false)
const selectedLoan = ref(null)

// Form Peminjaman Baru (Mendukung Pihak Luar Gereja & Internal)
const defaultLoanForm = () => ({
  id: null,
  church_code: activeChurch.code,
  loan_code: '',
  inventory_id: null,
  inventory_name: '',
  borrower_type: 'Pihak Luar Gereja / Eksternal',
  borrower_name: '',
  borrower_institution: '',
  borrower_phone: '',
  borrower_email: '',
  borrower_identity_no: '',
  event_purpose: '',
  start_date: new Date().toISOString().split('T')[0],
  start_time: '09:00 WIB',
  end_date: new Date().toISOString().split('T')[0],
  end_time: '17:00 WIB',
  loan_status: 'Disetujui / Aktif',
  initial_condition: 'Kondisi ruangan/alat bersih dan siap digunakan',
  return_condition: '',
  infaq_or_fee: 0,
  admin_notes: '',
  auto_wa: true // otomatis buka WhatsApp setelah simpan
})

const loanForm = reactive(defaultLoanForm())

// Form Tambah Inventaris / Gedung Baru
const defaultInvForm = () => ({
  id: null,
  church_code: activeChurch.code,
  item_code: '',
  name: '',
  category: 'Gedung & Ruangan',
  capacity_or_qty: '',
  location: '',
  condition: 'Sangat Baik',
  is_loanable: true,
  status: 'Tersedia',
  operational_fee_note: '',
  pic_name: '',
  pic_phone: '',
  icon: '🏛️',
  description: ''
})

const invForm = reactive(defaultInvForm())

// Form Pengembalian Inventaris
const returnForm = reactive({
  return_condition: 'Dikembalikan dalam kondisi sangat baik, bersih, dan lengkap',
  admin_notes: 'Pemeriksaan akhir selesai. Fasilitas telah diterima kembali oleh pengurus gereja.',
  send_wa: true
})

// Fetch Data Inventaris & Peminjaman dari API PostgreSQL
const fetchData = async () => {
  isLoading.value = true
  dbmsStatus.lastStatus = 'Mengambil data dari PostgreSQL...'
  try {
    let codeParam = ''
    if (activeChurch.code && activeChurch.code !== 'DEFAULT') {
      codeParam = `?church_code=${encodeURIComponent(activeChurch.code)}`
    }

    const [invRes, loanRes] = await Promise.all([
      fetch(`${apiBaseUrl.value}/church-inventories/${codeParam}`, { headers: getAuthHeaders() }),
      fetch(`${apiBaseUrl.value}/church-inventories/loans/all${codeParam}`, { headers: getAuthHeaders() })
    ])

    if (invRes.ok && loanRes.ok) {
      inventories.value = await invRes.json()
      loans.value = await loanRes.json()
      dbmsStatus.connected = true
      dbmsStatus.lastStatus = `Tersinkron (${inventories.value.length} inventaris, ${loans.value.length} peminjaman)`
    } else {
      throw new Error('Gagal memuat respons database')
    }
  } catch (err) {
    console.error('Fetch inventory error:', err)
    dbmsStatus.connected = false
    dbmsStatus.lastStatus = 'Koneksi ke DBMS terputus'
    showToast('Gagal memuat data inventaris dari server', 'error')
  } finally {
    isLoading.value = false
  }
}

// Filter Peminjaman
const filteredLoans = computed(() => {
  return loans.value.filter(l => {
    const q = loanSearch.value.toLowerCase()
    const nameMatch = (l.borrower_name || '').toLowerCase().includes(q)
    const instMatch = (l.borrower_institution || '').toLowerCase().includes(q)
    const invMatch = (l.inventory_name || '').toLowerCase().includes(q)
    const phoneMatch = (l.borrower_phone || '').includes(q)
    const codeMatch = (l.loan_code || '').toLowerCase().includes(q)
    const matchSearch = !q || nameMatch || instMatch || invMatch || phoneMatch || codeMatch

    const matchType = selectedBorrowerType.value === 'Semua' || l.borrower_type === selectedBorrowerType.value
    const matchStatus = selectedLoanStatus.value === 'Semua' || l.loan_status === selectedLoanStatus.value

    return matchSearch && matchType && matchStatus
  })
})

// Filter Inventaris Gedung & Ruangan
const roomInventories = computed(() => {
  return inventories.value.filter(i => i.category === 'Gedung & Ruangan')
})

// Filter Inventaris Alat / Multimedia / Kendaraan
const assetInventories = computed(() => {
  return inventories.value.filter(i => {
    const isAsset = i.category !== 'Gedung & Ruangan'
    const q = invSearch.value.toLowerCase()
    const matchSearch = !q || i.name.toLowerCase().includes(q) || (i.item_code || '').toLowerCase().includes(q)
    const matchCat = selectedInvCategory.value === 'Semua' || i.category === selectedInvCategory.value
    return isAsset && matchSearch && matchCat
  })
})

// Buka Modal Catat Peminjaman Baru
const openCreateLoanModal = (preselectedInv = null) => {
  Object.assign(loanForm, defaultLoanForm())
  loanForm.church_code = activeChurch.code

  if (preselectedInv) {
    loanForm.inventory_id = preselectedInv.id
    loanForm.inventory_name = preselectedInv.name
  } else if (inventories.value.length > 0) {
    loanForm.inventory_id = inventories.value[0].id
    loanForm.inventory_name = inventories.value[0].name
  }

  isLoanModalOpen.value = true
}

// Saat user ganti dropdown inventaris di form peminjaman
const onInventorySelect = () => {
  const selected = inventories.value.find(i => i.id === loanForm.inventory_id)
  if (selected) {
    loanForm.inventory_name = selected.name
  }
}

// Simpan Peminjaman Baru ke PostgreSQL
const handleSaveLoan = async () => {
  if (!loanForm.borrower_name || !loanForm.borrower_phone || !loanForm.inventory_id) {
    showToast('Nama peminjam, nomor WhatsApp, dan fasilitas wajib diisi', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      ...loanForm,
      church_code: activeChurch.code,
      church_id: activeChurch.id,
      infaq_or_fee: Number(loanForm.infaq_or_fee) || 0
    }

    const res = await fetch(`${apiBaseUrl.value}/church-inventories/loans/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })

    if (res.ok) {
      const created = await res.json()
      loans.value.unshift(created)
      isLoanModalOpen.value = false
      showToast(`Peminjaman "${created.inventory_name}" oleh "${created.borrower_name}" berhasil dicatat!`, 'success')

      // Jika opsi WhatsApp aktif, langsung kirim notifikasi WA konfirmasi
      if (loanForm.auto_wa) {
        sendLoanWhatsApp(created, 'confirmation')
      }

      await fetchData()
    } else {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Gagal menyimpan data peminjaman')
    }
  } catch (err) {
    console.error('Save loan error:', err)
    showToast(err.message || 'Terjadi kesalahan saat menyimpan peminjaman', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Buka Modal Pengembalian
const openReturnModal = (loan) => {
  selectedLoan.value = loan
  returnForm.return_condition = 'Dikembalikan dalam kondisi sangat baik, bersih, dan lengkap'
  returnForm.admin_notes = `Pemeriksaan selesai pada ${new Date().toLocaleDateString('id-ID')}. Telah diterima kembali.`
  isReturnModalOpen.value = true
}

// Proses Pengembalian Inventaris
const handleConfirmReturn = async () => {
  if (!selectedLoan.value) return
  isSubmitting.value = true
  try {
    const payload = {
      loan_status: 'Selesai / Dikembalikan',
      return_condition: returnForm.return_condition,
      admin_notes: returnForm.admin_notes
    }

    const res = await fetch(`${apiBaseUrl.value}/church-inventories/loans/${selectedLoan.value.id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })

    if (res.ok) {
      const updated = await res.json()
      const idx = loans.value.findIndex(l => l.id === updated.id)
      if (idx !== -1) loans.value[idx] = updated

      isReturnModalOpen.value = false
      showToast(`Inventaris "${updated.inventory_name}" telah dikonfirmasi selesai dikembalikan!`, 'success')

      if (returnForm.send_wa) {
        sendLoanWhatsApp(updated, 'return')
      }

      await fetchData()
    } else {
      throw new Error('Gagal memperbarui status pengembalian')
    }
  } catch (err) {
    console.error('Return error:', err)
    showToast(err.message || 'Gagal memproses pengembalian', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Buka Modal Hapus Peminjaman
const openDeleteLoanModal = (loan) => {
  selectedLoan.value = loan
  isDeleteLoanModalOpen.value = true
}

const handleDeleteLoan = async () => {
  if (!selectedLoan.value) return
  isSubmitting.value = true
  try {
    const res = await fetch(`${apiBaseUrl.value}/church-inventories/loans/${selectedLoan.value.id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    if (res.ok) {
      loans.value = loans.value.filter(l => l.id !== selectedLoan.value.id)
      isDeleteLoanModalOpen.value = false
      showToast(`Data peminjaman ${selectedLoan.value.loan_code} berhasil dihapus.`, 'success')
      selectedLoan.value = null
      await fetchData()
    } else {
      throw new Error('Gagal menghapus data peminjaman')
    }
  } catch (err) {
    console.error('Delete loan error:', err)
    showToast(err.message || 'Gagal menghapus', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Buka Modal Tambah Inventaris
const openAddInvModal = () => {
  Object.assign(invForm, defaultInvForm())
  invForm.church_code = activeChurch.code
  isAddInvModalOpen.value = true
}

const handleSaveInventory = async () => {
  if (!invForm.name) {
    showToast('Nama inventaris/gedung wajib diisi', 'error')
    return
  }
  isSubmitting.value = true
  try {
    const payload = {
      ...invForm,
      church_code: activeChurch.code,
      church_id: activeChurch.id
    }
    const res = await fetch(`${apiBaseUrl.value}/church-inventories/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      const created = await res.json()
      inventories.value.push(created)
      isAddInvModalOpen.value = false
      showToast(`Inventaris "${created.name}" berhasil ditambahkan ke database!`, 'success')
      await fetchData()
    } else {
      throw new Error('Gagal menyimpan inventaris baru')
    }
  } catch (err) {
    console.error('Save inv error:', err)
    showToast(err.message || 'Terjadi kesalahan saat menyimpan inventaris', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// ==============================================================================
// SISTEM NOTIFIKASI WHATSAPP OTOMATIS KE PEMINJAM
// ==============================================================================
const sendLoanWhatsApp = (loan, type = 'confirmation') => {
  if (!loan || !loan.borrower_phone) {
    showToast('Nomor WhatsApp peminjam tidak ditemukan', 'error')
    return
  }

  const cleanPhone = loan.borrower_phone.replace(/^0/, '62').replace(/[^0-9]/g, '')
  let msg = ''

  if (type === 'confirmation') {
    msg = `*SURAT KONFIRMASI PEMINJAMAN FASILITAS / INVENTARIS GEREJA*\n` +
      `⛪ *${activeChurch.name}*\n` +
      `No. Registrasi: *${loan.loan_code || 'PINJAM'}*\n\n` +
      `Shalom Saudara/i *${loan.borrower_name}*${loan.borrower_institution ? ' (' + loan.borrower_institution + ')' : ''},\n` +
      `Permohonan peminjaman fasilitas gereja Anda telah terdata di sistem administrasi kami dengan rincian sebagai berikut:\n\n` +
      `🏛️ *Fasilitas/Inventaris:* ${loan.inventory_name}\n` +
      `📌 *Keperluan Acara:* ${loan.event_purpose}\n` +
      `📅 *Jadwal Pemakaian:* ${loan.start_date} (${loan.start_time || '09:00 WIB'})\n` +
      `⏳ *Batas Pengembalian:* ${loan.end_date} (${loan.end_time || '17:00 WIB'})\n` +
      `🏷️ *Status:* ✅ *${loan.loan_status || 'DISETUJUI / AKTIF'}*\n` +
      (loan.infaq_or_fee > 0 ? `💰 *Infaq/Operasional:* Rp ${Number(loan.infaq_or_fee).toLocaleString('id-ID')}\n` : '') +
      `\n⚠️ *Ketentuan Penggunaan & Pengembalian:*\n` +
      `1. Menjaga kebersihan, kesopanan, dan ketertiban fasilitas/lingkungan gereja.\n` +
      `2. Mengembalikan inventaris tepat waktu dalam kondisi bersih, lengkap, dan berfungsi normal.\n` +
      `3. Jika membutuhkan teknisi sound system/kelistrikan, silakan menghubungi sekretariat pengurus gereja.\n\n` +
      `Kiranya kegiatan yang diselenggarakan dapat berjalan lancar dan menjadi berkat. Tuhan Yesus Memberkati! 🙏`
  } else if (type === 'return') {
    msg = `*KONFIRMASI PENGEMBALIAN FASILITAS / INVENTARIS GEREJA*\n` +
      `⛪ *${activeChurch.name}*\n` +
      `No. Registrasi: *${loan.loan_code || 'PINJAM'}*\n\n` +
      `Shalom Saudara/i *${loan.borrower_name}*${loan.borrower_institution ? ' (' + loan.borrower_institution + ')' : ''},\n\n` +
      `Kami mengonfirmasi bahwa peminjaman fasilitas *${loan.inventory_name}* telah *SELESAI DIKEMBALIKAN* dengan baik.\n\n` +
      `📋 *Kondisi Pengembalian:* ${loan.return_condition || 'Lengkap & Baik'}\n` +
      `Terima kasih telah menggunakan fasilitas dan inventaris gereja kami secara bertanggung jawab. Sampai jumpa di kegiatan pelayanan berikutnya. Tuhan Yesus Memberkati! 🙏`
  }

  // Buka WhatsApp Web / Mobile
  window.open(`https://wa.me/${cleanPhone}?text=${encodeURIComponent(msg)}`, '_blank')
}

onMounted(async () => {
  await initChurchContext()
  await fetchData()
})
</script>

<template>
  <ChurchAdminLayout>
    <div class="space-y-6">

      <!-- Toast Notification -->
      <transition
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="toast.show"
          class="fixed bottom-5 right-5 z-[100] max-w-sm w-full rounded-2xl shadow-2xl p-4 border flex items-start gap-3 backdrop-blur-md"
          :class="[
            toast.type === 'error'
              ? 'bg-rose-950/90 border-rose-500/50 text-rose-200'
              : 'bg-slate-900/95 border-indigo-500/40 text-indigo-200'
          ]"
        >
          <span class="text-xl">{{ toast.type === 'error' ? '⚠️' : '✅' }}</span>
          <div class="flex-1 text-xs leading-relaxed font-medium">
            {{ toast.message }}
          </div>
          <button @click="toast.show = false" class="text-slate-400 hover:text-white">&times;</button>
        </div>
      </transition>
      
      <!-- Top Header Banner -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-amber-500/20">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-indigo-400 animate-pulse"></span>
            <span class="text-xs uppercase tracking-widest text-indigo-400 font-bold">MANAJEMEN INVENTARIS & GEDUNG GEREJA</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold font-serif text-white tracking-wide">
            Inventaris & Peminjaman Fasilitas Gereja
          </h1>
          <p class="text-slate-400 text-sm mt-1">
            Kelola inventaris dan gedung milik gereja, layani peminjaman pihak luar / internal secara transparan, serta kirim konfirmasi otomatis via WhatsApp.
          </p>
        </div>

        <div class="flex items-center gap-2.5 flex-wrap">
          <button
            @click="openAddInvModal"
            class="px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 hover:text-white font-semibold text-xs flex items-center gap-2 transition cursor-pointer"
          >
            <span>🏛️</span>
            <span>Tambah Gedung / Aset</span>
          </button>

          <button
            @click="openCreateLoanModal()"
            class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-400 hover:to-indigo-500 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-indigo-500/25 transition-all cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            <span>Catat Peminjaman Baru</span>
          </button>
        </div>
      </div>

      <!-- PostgreSQL Database Live Connection Status Banner -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-2xl bg-slate-950/70 border border-slate-800 backdrop-blur-md">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700/80">
            <span
              class="w-2.5 h-2.5 rounded-full"
              :class="dbmsStatus.connected ? 'bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400/50' : 'bg-rose-400'"
            ></span>
            <span class="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
              DBMS: <span class="text-cyan-300">{{ dbmsStatus.engine }}</span>
            </span>
          </div>
          <div class="text-xs text-slate-400 flex items-center gap-2">
            <span>Tabel: <code class="text-amber-300 font-mono font-semibold">{{ dbmsStatus.tables }}</code></span>
            <span class="text-slate-600">•</span>
            <span>Cabang: <strong class="text-white">{{ activeChurch.name }}</strong> ({{ activeChurch.code }})</span>
          </div>
        </div>

        <div class="flex items-center gap-3 self-end sm:self-auto">
          <span class="text-[11px] text-slate-400">
            Status: <span :class="dbmsStatus.connected ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'">{{ dbmsStatus.lastStatus }}</span>
          </span>
          <button
            @click="fetchData"
            :disabled="isLoading"
            class="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 hover:text-white flex items-center gap-1.5 transition cursor-pointer"
            title="Refresh Data dari DBMS"
          >
            <svg class="w-3.5 h-3.5" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <span>Sync</span>
          </button>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title="Total Gedung & Ruang" subtitle="Fasilitas milik gereja">
          <div class="text-3xl font-bold text-white mt-1">
            {{ roomInventories.length }} <span class="text-xs font-normal text-slate-400">Gedung / Unit</span>
          </div>
        </Card>
        <Card title="Aset Siap Dipinjam" subtitle="Status Tersedia">
          <div class="text-3xl font-bold text-emerald-400 mt-1">
            {{ inventories.filter(i => i.status === 'Tersedia').length }} <span class="text-xs font-normal text-slate-400">Unit</span>
          </div>
        </Card>
        <Card title="Sedang Dipinjam" subtitle="Pihak luar & internal">
          <div class="text-3xl font-bold text-amber-400 mt-1">
            {{ loans.filter(l => l.loan_status === 'Disetujui / Aktif').length }} <span class="text-xs font-normal text-slate-400">Peminjaman</span>
          </div>
        </Card>
        <Card title="Total Riwayat Peminjaman" subtitle="Tercatat di DBMS">
          <div class="text-3xl font-bold text-indigo-400 mt-1">
            {{ loans.length }} <span class="text-xs font-normal text-slate-400">Transaksi</span>
          </div>
        </Card>
      </div>

      <!-- Tab Navigasi Manajemen -->
      <div class="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          @click="activeTab = 'loans'"
          class="px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer"
          :class="[
            activeTab === 'loans'
              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
          ]"
        >
          <span>📋</span>
          <span>Buku Peminjaman & Penggunaan (Pihak Luar & Internal)</span>
          <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-indigo-500/30 text-indigo-200">
            {{ loans.length }}
          </span>
        </button>

        <button
          @click="activeTab = 'rooms'"
          class="px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer"
          :class="[
            activeTab === 'rooms'
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
          ]"
        >
          <span>🏛️</span>
          <span>Gedung & Ruangan Gereja</span>
          <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-500/30 text-amber-200">
            {{ roomInventories.length }}
          </span>
        </button>

        <button
          @click="activeTab = 'assets'"
          class="px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer"
          :class="[
            activeTab === 'assets'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
          ]"
        >
          <span>📦</span>
          <span>Aset Sound, Musik, Proyektor & Kendaraan</span>
          <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-cyan-500/30 text-cyan-200">
            {{ assetInventories.length }}
          </span>
        </button>
      </div>

      <!-- ==================================================================== -->
      <!-- TAB 1: BUKU PEMINJAMAN & PENGGUNAAN (PIHAK LUAR & INTERNAL) -->
      <!-- ==================================================================== -->
      <div v-if="activeTab === 'loans'" class="space-y-4">
        <Card title="Daftar Peminjaman Fasilitas & Gedung Gereja" subtitle="Pendataan peminjaman oleh pihak luar gereja maupun komisi internal dengan integrasi pesan WhatsApp">
          
          <!-- Filter Bar -->
          <div class="flex flex-col sm:flex-row gap-3 items-center justify-between pt-2 pb-4">
            <div class="relative w-full sm:w-80">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              </span>
              <input
                v-model="loanSearch"
                type="text"
                placeholder="Cari peminjam, institusi, gedung, No. WA..."
                class="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-400"
              />
            </div>

            <div class="flex items-center gap-2.5 w-full sm:w-auto flex-wrap">
              <select
                v-model="selectedBorrowerType"
                class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-400 cursor-pointer"
              >
                <option value="Semua">Semua Asal Peminjam</option>
                <option value="Pihak Luar Gereja / Eksternal">Pihak Luar Gereja / Eksternal</option>
                <option value="Internal Komisi Gereja">Internal Komisi Gereja</option>
                <option value="Jemaat / Keluarga Peminjam">Jemaat / Keluarga Peminjam</option>
              </select>

              <select
                v-model="selectedLoanStatus"
                class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-400 cursor-pointer"
              >
                <option value="Semua">Semua Status</option>
                <option value="Diajukan">Diajukan</option>
                <option value="Disetujui / Aktif">Disetujui / Aktif</option>
                <option value="Selesai / Dikembalikan">Selesai / Dikembalikan</option>
                <option value="Ditolak">Ditolak</option>
              </select>
            </div>
          </div>

          <!-- Table Responsive Peminjaman -->
          <div class="overflow-x-auto rounded-xl border border-slate-800">
            <table class="w-full text-left text-xs text-slate-300">
              <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th class="p-3">No. Peminjaman</th>
                  <th class="p-3">Peminjam & Asal</th>
                  <th class="p-3">Fasilitas / Gedung</th>
                  <th class="p-3">Jadwal Penggunaan</th>
                  <th class="p-3">Keperluan Acara</th>
                  <th class="p-3">Status</th>
                  <th class="p-3 text-right">Aksi & Notifikasi WA</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
                <tr v-if="isLoading" class="text-center">
                  <td colspan="7" class="p-8 text-slate-400">
                    <div class="flex items-center justify-center gap-2">
                      <svg class="w-5 h-5 animate-spin text-indigo-400" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                      <span>Memuat data peminjaman dari PostgreSQL...</span>
                    </div>
                  </td>
                </tr>
                <tr v-else-if="filteredLoans.length === 0" class="text-center">
                  <td colspan="7" class="p-8 text-slate-400">
                    Tidak ada transaksi peminjaman yang sesuai kriteria filter.
                  </td>
                </tr>
                <tr
                  v-else
                  v-for="l in filteredLoans"
                  :key="l.id"
                  class="hover:bg-slate-800/40 transition-colors"
                >
                  <td class="p-3 font-mono text-slate-400">
                    {{ l.loan_code }}
                  </td>
                  <td class="p-3">
                    <div>
                      <p class="font-bold text-white">{{ l.borrower_name }}</p>
                      <p class="text-[11px] text-slate-400">{{ l.borrower_institution || 'Perorangan' }}</p>
                      <div class="mt-1 flex items-center gap-1.5 flex-wrap">
                        <span
                          class="px-1.5 py-0.2 rounded text-[9px] font-bold border"
                          :class="[
                            l.borrower_type.includes('Luar')
                              ? 'bg-purple-500/20 text-purple-300 border-purple-500/40'
                              : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                          ]"
                        >
                          {{ l.borrower_type.includes('Luar') ? '🌐 Pihak Luar' : '⛪ Internal' }}
                        </span>
                        <span class="text-[10px] text-emerald-400 font-mono font-medium">
                          {{ l.borrower_phone }}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td class="p-3">
                    <span class="font-semibold text-white block">{{ l.inventory_name }}</span>
                    <span v-if="l.infaq_or_fee > 0" class="text-[10px] text-amber-300/80">
                      Infaq: Rp {{ Number(l.infaq_or_fee).toLocaleString('id-ID') }}
                    </span>
                  </td>
                  <td class="p-3">
                    <div class="text-[11px]">
                      <p class="text-slate-200 font-medium">Mulai: {{ l.start_date }} ({{ l.start_time || '09:00 WIB' }})</p>
                      <p class="text-slate-400">Sampai: {{ l.end_date }} ({{ l.end_time || '17:00 WIB' }})</p>
                    </div>
                  </td>
                  <td class="p-3 max-w-[200px]">
                    <p class="text-[11px] text-slate-300 truncate" :title="l.event_purpose">
                      {{ l.event_purpose }}
                    </p>
                  </td>
                  <td class="p-3">
                    <span
                      class="px-2 py-0.5 rounded-full text-[10px] font-bold border block text-center max-w-[130px]"
                      :class="[
                        l.loan_status.includes('Disetujui') || l.loan_status.includes('Aktif')
                          ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                          : l.loan_status.includes('Selesai')
                            ? 'bg-sky-500/15 text-sky-300 border-sky-500/30'
                            : l.loan_status.includes('Ditolak')
                              ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                              : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                      ]"
                    >
                      {{ l.loan_status }}
                    </span>
                  </td>
                  <td class="p-3 text-right">
                    <div class="flex items-center justify-end gap-1.5 flex-wrap">
                      <!-- Tombol Kirim Notifikasi WhatsApp Peminjaman -->
                      <button
                        @click="sendLoanWhatsApp(l, 'confirmation')"
                        title="Kirim Konfirmasi Peminjaman via WhatsApp"
                        class="px-2 py-1 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold flex items-center gap-1 transition cursor-pointer"
                      >
                        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/></svg>
                        <span>WA Pinjam</span>
                      </button>

                      <!-- Tombol Verifikasi Pengembalian -->
                      <button
                        v-if="!l.loan_status.includes('Selesai')"
                        @click="openReturnModal(l)"
                        title="Verifikasi Pengembalian Inventaris"
                        class="px-2 py-1 rounded-lg bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border border-sky-500/30 text-[10px] font-bold flex items-center gap-1 transition cursor-pointer"
                      >
                        <span>🔄 Kembali</span>
                      </button>

                      <!-- Tombol Kirim WA Pengembalian jika sudah selesai -->
                      <button
                        v-else
                        @click="sendLoanWhatsApp(l, 'return')"
                        title="Kirim Konfirmasi Pengembalian via WhatsApp"
                        class="px-2 py-1 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/30 text-[10px] font-bold flex items-center gap-1 transition cursor-pointer"
                      >
                        <span>💬 WA Selesai</span>
                      </button>

                      <!-- Hapus -->
                      <button
                        @click="openDeleteLoanModal(l)"
                        title="Hapus Catatan Peminjaman"
                        class="p-1 rounded-lg bg-rose-500/15 text-rose-400 hover:bg-rose-500/25 border border-rose-500/30 transition cursor-pointer"
                      >
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      <!-- ==================================================================== -->
      <!-- TAB 2: GEDUNG & RUANGAN GEREJA -->
      <!-- ==================================================================== -->
      <div v-else-if="activeTab === 'rooms'" class="space-y-4">
        <Card title="Gedung & Ruangan Milik Gereja" subtitle="Fasilitas utama yang dapat digunakan untuk ibadah maupun dipinjamkan kepada pihak luar gereja">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-1">
            <div
              v-for="r in roomInventories"
              :key="r.id"
              class="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-3.5 hover:border-amber-500/40 transition-all flex flex-col justify-between"
            >
              <div>
                <div class="flex items-center justify-between">
                  <span class="text-3xl">{{ r.icon || '🏛️' }}</span>
                  <span
                    :class="[
                      'px-2 py-0.5 rounded-full text-[10px] font-bold border',
                      r.status === 'Tersedia'
                        ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                    ]"
                  >
                    {{ r.status }}
                  </span>
                </div>

                <div class="mt-2">
                  <span class="text-[10px] font-mono text-amber-400 block font-semibold">{{ r.item_code }}</span>
                  <h4 class="font-bold text-white text-sm">{{ r.name }}</h4>
                  <p class="text-xs text-slate-400 mt-0.5">Kapasitas: <strong class="text-slate-200">{{ r.capacity_or_qty }}</strong> • {{ r.location }}</p>
                </div>

                <p v-if="r.description" class="text-[11px] text-slate-400 leading-relaxed mt-2 line-clamp-2">
                  {{ r.description }}
                </p>

                <div v-if="r.operational_fee_note" class="mt-2 p-2 bg-slate-900/90 rounded-lg border border-slate-800 text-[11px] text-amber-300/90">
                  <span>💡 {{ r.operational_fee_note }}</span>
                </div>
              </div>

              <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span class="text-slate-400 text-[11px]">PIC: {{ r.pic_name || 'Sekretariat' }}</span>
                <button
                  @click="openCreateLoanModal(r)"
                  class="px-2.5 py-1.5 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/40 text-[11px] font-bold transition flex items-center gap-1 cursor-pointer"
                >
                  <span>📋 Pinjamkan Gedung</span>
                </button>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <!-- ==================================================================== -->
      <!-- TAB 3: ASET SOUND, MUSIK, PROYEKTOR & KENDARAAN -->
      <!-- ==================================================================== -->
      <div v-else-if="activeTab === 'assets'" class="space-y-4">
        <Card title="Inventaris Sound System, Alat Musik, & Kendaraan Gereja" subtitle="Daftar sarana prasarana ibadah yang terdata di sistem inventaris PostgreSQL">
          <!-- Filter Controls -->
          <div class="flex flex-col sm:flex-row gap-3 items-center justify-between pt-2 pb-4">
            <div class="relative w-full sm:w-80">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              </span>
              <input
                v-model="invSearch"
                type="text"
                placeholder="Cari nama alat atau kode aset..."
                class="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div class="flex items-center gap-2.5 w-full sm:w-auto">
              <select
                v-model="selectedInvCategory"
                class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                <option value="Semua">Semua Kategori</option>
                <option value="Sound & Multimedia">Sound & Multimedia</option>
                <option value="Alat Musik">Alat Musik</option>
                <option value="Kendaraan">Kendaraan</option>
                <option value="Sarana Prasarana">Sarana Prasarana</option>
              </select>
            </div>
          </div>

          <!-- Table Responsive Aset -->
          <div class="overflow-x-auto rounded-xl border border-slate-800">
            <table class="w-full text-left text-xs text-slate-300">
              <thead class="bg-slate-950/80 text-amber-400 text-[11px] uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th class="p-3">Kode Aset</th>
                  <th class="p-3">Nama Perangkat / Aset</th>
                  <th class="p-3">Kategori</th>
                  <th class="p-3">Penempatan</th>
                  <th class="p-3">Kondisi</th>
                  <th class="p-3">Status</th>
                  <th class="p-3 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800/80 bg-slate-900/30">
                <tr v-for="a in assetInventories" :key="a.id" class="hover:bg-slate-800/40 transition-colors">
                  <td class="p-3 font-mono text-slate-400">{{ a.item_code }}</td>
                  <td class="p-3">
                    <div class="flex items-center gap-2">
                      <span class="text-lg">{{ a.icon || '📦' }}</span>
                      <div>
                        <p class="font-bold text-white">{{ a.name }}</p>
                        <p class="text-[10px] text-slate-400">Qty/Kapasitas: {{ a.capacity_or_qty || '1 Unit' }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="p-3 text-slate-300">{{ a.category }}</td>
                  <td class="p-3 text-slate-300">{{ a.location }}</td>
                  <td class="p-3">
                    <span
                      class="px-2 py-0.5 rounded text-[10px] font-bold border"
                      :class="[
                        a.condition === 'Sangat Baik' || a.condition === 'Baik'
                          ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                          : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                      ]"
                    >
                      {{ a.condition }}
                    </span>
                  </td>
                  <td class="p-3">
                    <span
                      class="px-2 py-0.5 rounded-full text-[10px] font-bold border"
                      :class="[
                        a.status === 'Tersedia'
                          ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                          : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                      ]"
                    >
                      {{ a.status }}
                    </span>
                  </td>
                  <td class="p-3 text-right">
                    <button
                      @click="openCreateLoanModal(a)"
                      class="px-2.5 py-1 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 text-[11px] font-semibold transition cursor-pointer"
                    >
                      Pinjamkan Aset
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL CATAT PEMINJAMAN BARU (MENDUKUNG PIHAK LUAR GEREJA) -->
      <!-- ==================================================================== -->
      <div
        v-if="isLoanModalOpen"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto"
      >
        <div class="bg-slate-900 border border-indigo-500/40 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4 my-8">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span class="text-indigo-400">📋</span> Formulir Peminjaman Fasilitas / Gedung Gereja
            </h3>
            <button @click="isLoanModalOpen = false" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <form @submit.prevent="handleSaveLoan" class="space-y-3.5">
            <!-- Pilihan Fasilitas / Gedung -->
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Pilih Fasilitas / Gedung / Inventaris *</label>
              <select
                v-model="loanForm.inventory_id"
                @change="onInventorySelect"
                required
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
              >
                <option v-for="inv in inventories" :key="inv.id" :value="inv.id">
                  {{ inv.icon }} {{ inv.name }} ({{ inv.category }} - {{ inv.capacity_or_qty || '1 Unit' }})
                </option>
              </select>
            </div>

            <!-- Asal Peminjam -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Kategori Peminjam *</label>
                <select
                  v-model="loanForm.borrower_type"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400 font-semibold text-cyan-300"
                >
                  <option value="Pihak Luar Gereja / Eksternal">🌐 Pihak Luar Gereja / Eksternal</option>
                  <option value="Internal Komisi Gereja">⛪ Internal Komisi Gereja</option>
                  <option value="Jemaat / Keluarga Peminjam">👤 Jemaat / Keluarga Peminjam</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Institusi / Lembaga / Keluarga Luar</label>
                <input
                  v-model="loanForm.borrower_institution"
                  type="text"
                  placeholder="Contoh: Yayasan Lentera Kasih / Keluarga Bpk. Santoso"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
                />
              </div>
            </div>

            <!-- Identitas Pemohon -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Nama Lengkap Penanggung Jawab *</label>
                <input
                  v-model="loanForm.borrower_name"
                  required
                  type="text"
                  placeholder="Nama peminjam sesuai KTP"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">No. WhatsApp Utama (Untuk Notifikasi) *</label>
                <input
                  v-model="loanForm.borrower_phone"
                  required
                  type="text"
                  placeholder="0812xxxxxxx"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-emerald-400 font-mono focus:outline-none focus:border-indigo-400"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">No. KTP / NIK Peminjam Luar</label>
                <input
                  v-model="loanForm.borrower_identity_no"
                  type="text"
                  placeholder="16 Digit NIK KTP"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Infaq / Biaya Operasional Kebersihan (Rp)</label>
                <input
                  v-model="loanForm.infaq_or_fee"
                  type="number"
                  placeholder="0"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-amber-300 font-mono focus:outline-none focus:border-indigo-400"
                />
              </div>
            </div>

            <!-- Jadwal Pemakaian -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 bg-slate-950/70 p-3 rounded-xl border border-slate-800">
              <div>
                <label class="block text-[11px] font-medium text-slate-400 mb-1">Tanggal Mulai *</label>
                <input
                  v-model="loanForm.start_date"
                  type="date"
                  required
                  class="w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none"
                />
              </div>

              <div>
                <label class="block text-[11px] font-medium text-slate-400 mb-1">Jam Mulai</label>
                <input
                  v-model="loanForm.start_time"
                  type="text"
                  placeholder="09:00 WIB"
                  class="w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none"
                />
              </div>

              <div>
                <label class="block text-[11px] font-medium text-slate-400 mb-1">Tanggal Selesai *</label>
                <input
                  v-model="loanForm.end_date"
                  type="date"
                  required
                  class="w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none"
                />
              </div>

              <div>
                <label class="block text-[11px] font-medium text-slate-400 mb-1">Jam Selesai</label>
                <input
                  v-model="loanForm.end_time"
                  type="text"
                  placeholder="17:00 WIB"
                  class="w-full px-2 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none"
                />
              </div>
            </div>

            <!-- Keperluan Acara -->
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Keperluan Pemakaian Acara *</label>
              <textarea
                v-model="loanForm.event_purpose"
                required
                rows="2"
                placeholder="Contoh: Resepsi Pernikahan Kristen, Ibadah Syukuran Keluarga, Seminar Pendidikan..."
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-400"
              ></textarea>
            </div>

            <!-- Status Awal & Checkbox Notifikasi WA -->
            <div class="p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-xl flex items-center justify-between">
              <label class="flex items-center gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="loanForm.auto_wa"
                  class="w-4 h-4 rounded text-emerald-500 focus:ring-0 cursor-pointer"
                />
                <span class="text-xs text-emerald-200 font-medium">
                  💬 Langsung Buka WhatsApp untuk Notifikasi Resmi ke Peminjam
                </span>
              </label>
            </div>

            <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
              <button
                type="button"
                @click="isLoanModalOpen = false"
                class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
              >
                Batal
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs cursor-pointer shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-1.5"
              >
                <svg v-if="isSubmitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                <span>{{ isSubmitting ? 'Menyimpan...' : 'Simpan Peminjaman' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL VERIFIKASI PENGEMBALIAN INVENTARIS & NOTIFIKASI WA -->
      <!-- ==================================================================== -->
      <div
        v-if="isReturnModalOpen && selectedLoan"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      >
        <div class="bg-slate-900 border border-sky-500/40 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span class="text-sky-400">🔄</span> Konfirmasi Pengembalian Fasilitas / Inventaris
            </h3>
            <button @click="isReturnModalOpen = false" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1 text-xs">
            <p class="font-bold text-white">{{ selectedLoan.inventory_name }}</p>
            <p class="text-slate-400">
              Peminjam: <strong class="text-slate-200">{{ selectedLoan.borrower_name }}</strong> ({{ selectedLoan.borrower_institution || selectedLoan.borrower_type }})
            </p>
            <p class="text-emerald-400 font-mono font-medium">WhatsApp: {{ selectedLoan.borrower_phone }}</p>
          </div>

          <form @submit.prevent="handleConfirmReturn" class="space-y-3.5">
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Kondisi Saat Dikembalikan *</label>
              <textarea
                v-model="returnForm.return_condition"
                required
                rows="2"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-sky-400"
              ></textarea>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Catatan Verifikasi Admin</label>
              <input
                v-model="returnForm.admin_notes"
                type="text"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-sky-400"
              />
            </div>

            <div class="p-3 bg-sky-950/20 border border-sky-500/30 rounded-xl flex items-center justify-between">
              <label class="flex items-center gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="returnForm.send_wa"
                  class="w-4 h-4 rounded text-sky-500 focus:ring-0 cursor-pointer"
                />
                <span class="text-xs text-sky-200 font-medium">
                  💬 Kirim Pesan Konfirmasi Pengembalian Selesai ke WhatsApp Peminjam
                </span>
              </label>
            </div>

            <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
              <button
                type="button"
                @click="isReturnModalOpen = false"
                class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
              >
                Batal
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs cursor-pointer shadow-lg shadow-sky-600/30 flex items-center justify-center gap-1.5"
              >
                <span>{{ isSubmitting ? 'Memproses...' : 'Konfirmasi Selesai Dikembalikan' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL TAMBAH GEDUNG / ASET BARU KE DBMS -->
      <!-- ==================================================================== -->
      <div
        v-if="isAddInvModalOpen"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto"
      >
        <div class="bg-slate-900 border border-amber-500/30 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 my-8">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span class="text-amber-400">🏛️</span> Tambah Data Inventaris / Gedung Baru
            </h3>
            <button @click="isAddInvModalOpen = false" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
          </div>

          <form @submit.prevent="handleSaveInventory" class="space-y-3.5">
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Nama Fasilitas / Gedung / Alat *</label>
              <input
                v-model="invForm.name"
                required
                type="text"
                placeholder="Contoh: Gedung Serbaguna Sayap Timur"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Kategori</label>
                <select
                  v-model="invForm.category"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Gedung & Ruangan">Gedung & Ruangan</option>
                  <option value="Sound & Multimedia">Sound & Multimedia</option>
                  <option value="Alat Musik">Alat Musik</option>
                  <option value="Kendaraan">Kendaraan</option>
                  <option value="Sarana Prasarana">Sarana Prasarana</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Kapasitas / Jumlah</label>
                <input
                  v-model="invForm.capacity_or_qty"
                  type="text"
                  placeholder="Contoh: 200 Orang / 2 Set"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Lokasi Penempatan</label>
                <input
                  v-model="invForm.location"
                  type="text"
                  placeholder="Lantai 1 / Ruang Musik"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
                />
              </div>

              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Kondisi Alat / Fasilitas</label>
                <select
                  v-model="invForm.condition"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-amber-400"
                >
                  <option value="Sangat Baik">Sangat Baik</option>
                  <option value="Baik">Baik</option>
                  <option value="Perlu Perbaikan">Perlu Perbaikan</option>
                  <option value="Rusak">Rusak</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Estimasi Infaq / Biaya Kebersihan</label>
              <input
                v-model="invForm.operational_fee_note"
                type="text"
                placeholder="Contoh: Infaq Rp 300.000 / acara"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">Nama PIC Pengurus Fasilitas</label>
              <input
                v-model="invForm.pic_name"
                type="text"
                placeholder="Bpk. Paulus Sudrajat"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:border-amber-400"
              />
            </div>

            <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
              <button
                type="button"
                @click="isAddInvModalOpen = false"
                class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
              >
                Batal
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs cursor-pointer shadow-lg shadow-amber-500/20"
              >
                <span>Simpan Inventaris</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL HAPUS CATATAN PEMINJAMAN -->
      <!-- ==================================================================== -->
      <div
        v-if="isDeleteLoanModalOpen && selectedLoan"
        class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
      >
        <div class="bg-slate-900 border border-rose-500/40 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
          <div class="flex items-center gap-3 text-rose-400">
            <div class="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-xl">
              🗑️
            </div>
            <div>
              <h3 class="text-base font-bold text-white">Hapus Catatan Peminjaman?</h3>
              <p class="text-xs text-slate-400">Tindakan ini akan menghapus riwayat peminjaman dari database.</p>
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <p class="text-xs font-semibold text-white">{{ selectedLoan.inventory_name }}</p>
            <p class="text-[11px] text-slate-400">
              Peminjam: {{ selectedLoan.borrower_name }} • {{ selectedLoan.loan_code }}
            </p>
          </div>

          <div class="sticky bottom-0 -mx-4 -mb-4 mt-2 flex flex-col-reverse gap-3 border-t border-slate-800 bg-slate-900/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end sm:px-6">
            <button
              type="button"
              @click="isDeleteLoanModalOpen = false"
              class="px-4 py-2 rounded-xl border border-slate-700 text-xs text-slate-400 hover:text-white cursor-pointer"
            >
              Batal
            </button>
            <button
              @click="handleDeleteLoan"
              :disabled="isSubmitting"
              class="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs cursor-pointer shadow-lg shadow-rose-600/30 flex items-center justify-center gap-1.5"
            >
              <span>{{ isSubmitting ? 'Menghapus...' : 'Ya, Hapus Data' }}</span>
            </button>
          </div>
        </div>
      </div>

    </div>
  </ChurchAdminLayout>
</template>
