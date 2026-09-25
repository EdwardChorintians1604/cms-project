# 🏛️ PERANCANGAN 3 AKTOR (THREE-TIER ACTOR ARCHITECTURE)
## Platform SystemKita — Manajemen & Pelayanan Gereja Digital

---

### 📌 Ringkasan Eksekutif
Dokumen ini berisi rancangan arsitektur dan pembagian peran **3 Aktor** pada platform **SystemKita**. Dengan menambahkan **Jemaat (User)** sebagai aktor ketiga, platform bertransformasi dari sekadar alat pencatatan administratif menjadi **Portal Ekosistem Gereja Digital Mandiri (*Self-Service Portal*)**.

---

### 👥 Pembagian & Peran 3 Aktor

```
                       ┌─────────────────────────────────────────┐
                       │           SYSTEMKITA PORTAL             │
                       └───────────────────┬─────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         │                                 │                                 │
  [ AKTOR 1 ]                       [ AKTOR 2 ]                       [ AKTOR 3 ]
Main Administrator              Church Administrator                 User / Jemaat
 (Super Admin / Dev)             (Pengurus / Majelis)             (Anggota & Pelayan)
```

---

### 🛠️ rincian Hak Akses & Fitur Masing-Masing Aktor

#### 1. 🛡️ Aktor 1: Main Administrator (Super Admin / System Developer)
* **Tanggung Jawab**: Mengelola infrastruktur sistem, database server, keamanan global, dan pengaturan multi-tenant gereja.
* **Fitur Utama**:
  - 🖥️ Monitoring Uptime Server, Latensi API, & Performa Sistem.
  - 🔒 Audit Log Keamanan & Pengaturan Hak Akses Global.
  - 💾 Backup & Pemulihan Database Server.
  - 🏛️ Pendaftaran & Pengaturan Lisensi Gereja Baru.

#### 2. ⛪ Aktor 2: Church Administrator (Pengurus / Majelis Gereja)
* **Tanggung Jawab**: Mengelola operasional harian gereja, data jemaat, keuangan, dan penjadwalan ibadah.
* **Fitur Utama**:
  - 📊 Dashboard Statistik Jemaat & Kehadiran Ibadah.
  - 👥 Manajemen Master Data Jemaat & Kartu Keluarga (KK) Gereja.
  - 💰 Pencatatan & Laporan Keuangan (Persembahan, Perpuluhan, Donasi).
  - 📅 Penjadwalan Ibadah Raya, WL, Pengkhotbah, & Pelayan Mimbar.
  - 🕊️ Registrasi Sakramen (Baptis Anak/Dewasa, SIDI, Pernikahan Kudus).
  - 📢 Publikasi Warta Jemaat Digital & Broadcast WhatsApp/Email.

#### 3. ✝️ Aktor 3: User / Jemaat (Anggota & Pelayan Gereja) — *Aktor Baru*
* **Tanggung Jawab**: Mengakses layanan mandiri, data pribadi, jadwal pelayanan, dan presensi ibadah.
* **Fitur Utama**:
  - 🪪 **Kartu Jemaat Digital & QR Code**: Untuk presensi cepat saat hadir di ibadah raya.
  - 👤 **Profil Mandiri & Keluarga**: Melihat & memperbarui alamat, no HP, dan daftar anggota keluarga.
  - 📋 **Jadwal Tugas Pelayanan**: Notifikasi khusus bagi jemaat yang bertugas (Usher, WL, Pemusik, Multimedia).
  - 💳 **Riwayat Persembahan**: Catatan transparan persembahan/perpuluhan pribadi beserta bukti kuitansi digital.
  - 📑 **Warta & Pendaftaran Event**: Membaca warta mingguan serta mendaftar acara (Retret, Seminar, Kategori).
  - 🛐 **Layanan Doa & Pastoral**: Form permohonan konseling atau kunjungan pendoa secara privat.

---

### 📊 Matriks Hak Akses (Role-Based Access Control / RBAC)

| Modul / Fitur | Main Admin | Church Admin | User / Jemaat |
| :--- | :---: | :---: | :---: |
| Monitoring Server & System Log | ✅ | ❌ | ❌ |
| Backup & Restore DB | ✅ | ❌ | ❌ |
| Master Data Jemaat & KK | ✅ | ✅ (Full Edit) | 👁️ (Lihat Profil Sendiri) |
| Keuangan & Laporan Kas | ✅ | ✅ (Full Edit) | 👁️ (Histori Sendiri) |
| Penjadwalan Ibadah & Warta | ✅ | ✅ (Full Edit) | 👁️ (Lihat Jadwal) |
| Presensi QR Code Ibadah | ✅ | ✅ (Scan Master) | 📲 (Scan QR Jemaat) |
| Permohonan Doa / Pastoral | ✅ | ✅ (Terima & Respon) | 📝 (Kirim Permohonan) |

---

### 🗺️ Rencana Struktur Rute (Frontend Router)

- **`http://localhost:5173/`** ➔ Portal Beranda Publik
- **`http://localhost:5173/login`** ➔ Portal Login Pilihan 3 Aktor
- **`http://localhost:5173/main-admin`** ➔ Dashboard Aktor 1 (Super Admin)
- **`http://localhost:5173/church-admin`** ➔ Dashboard Aktor 2 (Church Admin)
- **`http://localhost:5173/member-portal`** ➔ Dashboard Aktor 3 (User / Jemaat)

---

### 📝 Catatan Implementasi
* **Komponen Layout**:
  - `layouts/MainAdminLayout.vue`
  - `layouts/ChurchAdminLayout.vue`
  - `layouts/MemberLayout.vue`
* **File Pengingat Ini Disimpan Di**: [src/PERANCANGAN_3_AKTOR.md](file:///d:/cms-project/frontend/cms-project/src/PERANCANGAN_3_AKTOR.md)
