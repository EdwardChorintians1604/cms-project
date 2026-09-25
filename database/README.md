# DOKUMENTASI DATABASE POSTGRESQL - GRACEPOINT CMS

Repositori ini menyimpan skrip DDL & DML PostgreSQL lengkap untuk platform **GracePoint CMS**.

---

## 📁 Berkas SQL yang Tersedia

1. **[schema_master_gracepoint.sql](file:///d:/cms-project/database/schema_master_gracepoint.sql)**  
   *Master Database Schema* lengkap yang mencakup **seluruh 17 tabel utama**, *ENUM types*, *foreign keys*, *triggers auto-updated_at*, *indexes*, serta *initial seed data*.

2. **[postgres_user_auth.sql](file:///d:/cms-project/database/postgres_user_auth.sql)**  
   Skrip khusus untuk modul **User Login, Registration, & Manajemen Biodata Jemaat** beserta contoh query SQL *CRUD/Integration API*.

---

## 🏛️ Daftar 17 Tabel Utama GracePoint CMS

| No | Nama Tabel | Deskripsi & Kegunaan |
|---|---|---|
| 1 | `main_admin` | Data Super Admin / Developer (Aktor 1) |
| 2 | `churches` | Profil & Multi-Tenant Cabang Gereja |
| 3 | `users` | Akun Autentikasi & Login (Email/Username/Password) |
| 4 | `families` | Pendataan Kartu Keluarga (KK) Gereja |
| 5 | `members` | Biodata Detail Jemaat (NIK, NIJ, Status Baptis/Sidi, Alamat, QR Token) |
| 6 | `ministries` | Struktur Komisi & Divisi Pelayanan |
| 7 | `ministry_members` | Penugasan Anggota Pelayanan (WL, Singer, Musician, Operator) |
| 8 | `service_schedules` | Penjadwalan Ibadah Mingguan & Pelayan |
| 9 | `attendances` | Presensi / Kehadiran Ibadah & Pelayanan (Scan QR / Manual) |
| 10 | `church_events` | Kalender Event & Hari Besar Gereja |
| 11 | `sacraments` | Riwayat Penerimaan Sakramen (Baptis, Sidi, Nikah, Anak) |
| 12 | `finances` | Transaksi Kas Persembahan, Persepuluhan, QRIS, & Pengeluaran |
| 13 | `announcements` | Warta Jemaat & Pengumuman Sistem |
| 14 | `password_resets` | Token Lupa Password & Verifikasi OTP |
| 15 | `user_sessions` | Sesi Login & Refresh Token |

---

## 🚀 Cara Menjalankan Skrip ke Database PostgreSQL / Neon Cloud

### 1. Ke Cloud PostgreSQL (Neon Serverless)
Gunakan `psql` dengan connection string dari `backend/.env`:
```bash
psql "postgresql://username:password@ep-cool-name-123456.ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require" -f database/schema_master_gracepoint.sql
```

### 2. Ke Local PostgreSQL Instance
```bash
psql -U postgres -d gracepoint_db -f database/schema_master_gracepoint.sql
```
