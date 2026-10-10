# PROSEDUR STANDAR DEPLOYMENT CLOUD, HOSTING VERCEL, CLOUDFLARE SSL, DAN DATABASE REAL (POSTGRESQL)
## GracePoint CMS (Frontend Vue 3 + Vite, Backend FastAPI Python, & Neon Cloud PostgreSQL)

---

## 📋 DAFTAR ISI
1. [Ringkasan Eksekutif & Arsitektur Sistem Produksi](#1-ringkasan-eksekutif--arsitektur-sistem-produksi)
2. [Bab 1: Penerapan Database PostgreSQL Secara Real (Neon Cloud)](#bab-1-penerapan-database-postgresql-secara-real-neon-cloud)
   - [1.1 Mengapa Database Lokal Tidak Dapat Diakses di Internet](#11-mengapa-database-lokal-tidak-dapat-diakses-di-internet)
   - [1.2 Keunggulan Neon Serverless PostgreSQL](#12-keunggulan-neon-serverless-postgresql)
   - [1.3 Langkah Pembuatan Project & Database di Neon](#13-langkah-pembuatan-project--database-di-neon)
   - [1.4 Format Connection String & SSL Mode Required](#14-format-connection-string--ssl-mode-required)
   - [1.5 Prosedur Impor Skema 17 Tabel Master](#15-prosedur-impor-skema-17-tabel-master)
   - [1.6 Prosedur Backup & Restore Cloud Database](#16-prosedur-backup--restore-cloud-database)
3. [Bab 2: Deployment Backend FastAPI ke Cloud PaaS (Render / Railway)](#bab-2-deployment-backend-fastapi-ke-cloud-paas-render--railway)
   - [2.1 Mengapa Backend FastAPI Kurang Cocok di Vercel Serverless](#21-mengapa-backend-fastapi-kurang-cocok-di-vercel-serverless)
   - [2.2 Persiapan Berkas Konfigurasi Backend](#22-persiapan-berkas-konfigurasi-backend)
   - [2.3 Langkah Deployment di Render.com](#23-langkah-deployment-di-rendercom)
   - [2.4 Konfigurasi Environment Variables Backend](#24-konfigurasi-environment-variables-backend)
   - [2.5 Verifikasi Endpoint Backend (Root, Swagger UI `/docs`, API v1)](#25-verifikasi-endpoint-backend)
4. [Bab 3: Deployment Frontend Vue.js ke Vercel](#bab-3-deployment-frontend-vuejs-ke-vercel)
   - [3.1 Mengapa Frontend Vue Sangat Cocok di Vercel](#31-mengapa-frontend-vue-sangat-cocok-di-vercel)
   - [3.2 Menyiapkan Routing SPA (Single Page App) di `vercel.json`](#32-menyiapkan-routing-spa-di-verceljson)
   - [3.3 Langkah Import Proyek ke Dashboard Vercel](#33-langkah-import-proyek-ke-dashboard-vercel)
   - [3.4 Konfigurasi Environment Variable `VITE_API_BASE_URL`](#34-konfigurasi-environment-variable-vite_api_base_url)
5. [Bab 4: Konfigurasi Domain, DNS, & Cloudflare SSL (HTTPS)](#bab-4-konfigurasi-domain-dns--cloudflare-ssl-https)
   - [4.1 Pemahaman Konseptual: Domain, DNS Records, & Cloudflare Proxy](#41-pemahaman-konseptual-domain-dns-records--cloudflare-proxy)
   - [4.2 Langkah 1: Menghubungkan Domain ke Cloudflare Nameserver](#42-langkah-1-menghubungkan-domain-ke-cloudflare-nameserver)
   - [4.3 Langkah 2: Mengisi Catatan DNS (DNS Records) di Cloudflare](#43-langkah-2-mengisi-catatan-dns-dns-records-di-cloudflare)
   - [4.4 Langkah 3: Mengaktifkan Enkripsi SSL/TLS (HTTPS) Otomatis](#44-langkah-3-mengaktifkan-enkripsi-ssltls-https-otomatis)
6. [Bab 5: Sinkronisasi CORS & Checklist Pengujian Akhir](#bab-5-sinkronisasi-cors--checklist-pengujian-akhir)
   - [5.1 Update CORS Whitelist di Backend FastAPI](#51-update-cors-whitelist-di-backend-fastapi)
   - [5.2 Update API Base URL di Frontend Vercel](#52-update-api-base-url-di-frontend-vercel)
   - [5.3 Lembar Checklist Pengujian Sistem Produksi (End-to-End)](#53-lembar-checklist-pengujian-sistem-produksi)
7. [Bab 6: Panduan Troubleshooting & FAQ](#bab-6-panduan-troubleshooting--faq)

---

## 1. Ringkasan Eksekutif & Arsitektur Sistem Produksi

Sistem aplikasi **GracePoint CMS** dirancang dengan arsitektur modern yang memisahkan antara antarmuka pengguna (*Frontend*) dan pemrosesan data (*Backend API*). 

Agar aplikasi dapat diakses secara publik dengan protokol terenkripsi **HTTPS (SSL)** dan database dapat menyimpan data secara persisten dan aman secara *real*, strategi deployment dibagi menjadi beberapa komponen spesifik:

| Komponen Sistem | Stack Teknologi | Platform Hosting yang Dipilih | Alasan & Peran Utama |
| :--- | :--- | :--- | :--- |
| **Frontend Web** | Vue 3, Vite, Tailwind CSS, ApexCharts | **Vercel** (Free Tier) | Berkas statis di-cache di seluruh CDN global Vercel, super cepat, build otomatis dari GitHub, dan SSL bawaan. |
| **Backend REST API** | Python 3.11+, FastAPI, SQLAlchemy | **Render.com** / **Railway** | Menjalankan server aplikasi kontinu (Uvicorn), memproses token JWT, menangani koneksi database pool, ekspor PDF/Excel. |
| **Database Relasional** | PostgreSQL 16 (17 Tabel Skema Master) | **Neon.tech** (Cloud Serverless) | Database cloud online 24 jam dengan koneksi aman ber-SSL (`sslmode=require`) tanpa perlu mengelola server fisik. |
| **Domain Resmi** | Custom Domain (`.com` / `.org` / `.id`) | **Registrar Domain** | Alamat resmi web gereja yang ramah dan mudah diingat oleh jemaat dan pengurus. |
| **DNS & Proteksi SSL** | DNS Management & Reverse Proxy | **Cloudflare** (Free Tier) | Menerjemahkan domain, menangkal DDoS, dan memberikan **SSL HTTPS otomatis (gembok hijau)** tanpa instal sertifikat manual. |

### Diagram Alur Komunikasi Sistem Produksi:
```
                      [ PENGUNJUNG / BROWSER INTERNET ]
                                     │
                                     │ (HTTPS Port 443 / SSL Cloudflare)
                                     ▼
               ┌───────────────────────────────────────────┐
               │          CLOUDFLARE DNS & PROXY           │
               │  • Manajemen DNS (CNAME & A Records)      │
               │  • Enkripsi SSL/TLS Otomatis (HTTPS)      │
               │  • Proteksi DDoS & Edge Caching CDN       │
               └─────────────┬─────────────────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │ Akses Web                           │ Request API (/api/v1)
          │ (namagereja.com)                    │ (api.namagereja.com)
          ▼                                     ▼
   ┌─────────────────────┐             ┌─────────────────────┐
   │   VERCEL HOSTING    │             │   RENDER / RAILWAY  │
   │  Frontend Vue 3     │ ── AJAX ──> │  Backend FastAPI   │
   │  Output: 'dist/'    │ <─ JSON ─── │  Python 3.11+ / APP │
   └─────────────────────┘             └──────────┬──────────┘
                                                  │
                                                  │ DATABASE_URL
                                                  │ (SSL Mode Required)
                                                  ▼
                                       ┌─────────────────────┐
                                       │   NEON POSTGRESQL   │
                                       │  (Cloud Database)   │
                                       │  17 Master Tables   │
                                       └─────────────────────┘
```

---

## Bab 1: Penerapan Database PostgreSQL Secara Real (Neon Cloud)

### 1.1 Mengapa Database Lokal Tidak Dapat Diakses di Internet
Saat mengembangkan aplikasi di laptop, database berjalan di `localhost:5432` atau container Docker lokal. Ketika frontend di-deploy ke Vercel dan backend di-deploy ke cloud, server-server tersebut berada di internet publik dan **sama sekali tidak bisa mengakses `localhost` laptop Anda** (kecuali laptop Anda dinyalakan 24 jam nonstop dengan IP Publik statis).

Oleh karena itu, database harus ditempatkan di penyedia database cloud yang:
1. Memiliki IP / Hostname publik yang dapat diakses 24/7.
2. Terkunci dengan autentikasi kata sandi kuat.
3. Seluruh lalu lintas data dienkripsi dengan SSL/TLS (`sslmode=require`).

### 1.2 Keunggulan Neon Serverless PostgreSQL
Sesuai rancangan pada berkas `PROSEDUR_BACKEND_DAN_API_GRACEPOINT.md`, platform yang sangat direkomendasikan adalah **Neon (https://neon.tech)**:
* **Zero Server Management:** Tidak perlu setup OS Linux, update patch, atau setting firewall manual.
* **Auto-SSL:** Mewajibkan enkripsi TLS bawaan (`?sslmode=require`).
* **Database Branching:** Fitur kloning database untuk staging/development dalam hitungan detik tanpa memengaruhi database produksi.
* **Free Tier Melimpah:** Menyediakan penyimpanan 0.5 GB gratis (sangat cukup untuk menampung data ribuan jemaat, transaksi kas, presensi, dan histori sakramen).

### 1.3 Langkah Pembuatan Project & Database di Neon
1. Buka situs [https://neon.tech](https://neon.tech) dan daftar menggunakan akun GitHub Anda.
2. Klik tombol **New Project**.
3. Beri nama project: `gracepoint-cms`.
4. Pilih Region terdekat: **Asia Pacific (Singapore) - `ap-southeast-1`** (sangat penting untuk menjaga latensi query tetap rendah di bawah 30ms).
5. Nama database default: `gracepoint_db` atau `neondb`.
6. Simpan password database yang dihasilkan secara aman.

### 1.4 Format Connection String & SSL Mode Required
Setelah project dibuat, Neon Dashboard akan memberikan satu baris *Connection String*. Formatnya adalah:

```env
DATABASE_URL="postgresql://[user]:[password]@[endpoint-id].ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require"
```

> **Contoh Real:**
> ```env
> DATABASE_URL="postgresql://gracepoint_admin:SecretPass90@ep-cool-butterfly-123456.ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require"
> ```

> [!IMPORTANT]
> Parameter `?sslmode=require` di bagian akhir connection string wajib ada. Tanpa parameter ini, koneksi dari backend FastAPI akan ditolak oleh sistem keamanan Neon.

### 1.5 Prosedur Impor Skema 17 Tabel Master
Struktur tabel aplikasi GracePoint CMS telah dirancang lengkap di berkas `database/schema_master_gracepoint.sql` (mencakup tabel `main_admin`, `churches`, `users`, `families`, `members`, `ministries`, `finances`, `church_inventory`, dll).

Ada dua cara untuk mengunggah skema ini ke Neon:

#### Metode A: Menggunakan Neon Web SQL Editor (Paling Mudah / Tanpa Install Apapun)
1. Buka dashboard Neon Anda di browser.
2. Masuk ke tab **SQL Editor** pada menu navigasi sebelah kiri.
3. Buka berkas `database/schema_master_gracepoint.sql` di editor Anda, salin (**Copy**) seluruh isinya.
4. Tempel (**Paste**) ke dalam SQL Editor di Neon.
5. Klik tombol **Run**. Seluruh 17 tabel, tipe ENUM, relasi foreign key, trigger, dan initial seed data akan langsung terbentuk di cloud.

#### Metode B: Menggunakan Command Line (Terminal `psql`)
Jika di komputer Anda sudah terpasang PostgreSQL client:
```bash
psql "postgresql://gracepoint_admin:SecretPass90@ep-cool-butterfly-123456.ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require" -f database/schema_master_gracepoint.sql
```

### 1.6 Prosedur Backup & Restore Cloud Database
Untuk mengantisipasi kehilangan data, buat cadangan (*backup*) secara berkala ke komputer lokal:
```bash
# Perintah Backup Remote ke berkas .sql lokal:
pg_dump "postgresql://gracepoint_admin:SecretPass90@ep-cool-butterfly-123456.ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require" > backups/neon_backup_$(date +%Y%m%d).sql
```

---

## Bab 2: Deployment Backend FastAPI ke Cloud PaaS (Render / Railway)

### 2.1 Mengapa Backend FastAPI Kurang Cocok di Vercel Serverless
Meskipun Vercel mendukung fungsi Python, Vercel bekerja berbasis *Serverless Function*, bukan server aktif terus-menerus. Untuk aplikasi CMS gereja ini, model serverless Vercel memiliki kelemahan kritis:
1. **Batas Waktu Eksekusi (Timeout):** Paket gratis Vercel membatasi waktu eksekusi request 10–15 detik. Pembuatan berkas laporan PDF/Excel yang besar akan langsung mengalami *504 Gateway Timeout*.
2. **Cold Starts:** Jika tidak ada akses selama beberapa menit, fungsi Python akan "tidur". Pengguna pertama yang membuka web akan merasakan loading lambat (3–8 detik).
3. **Database Connection Exhaustion:** Setiap request serverless membuka koneksi database baru yang dapat menghabiskan kuota koneksi PostgreSQL dengan sangat cepat.
4. **Tidak Mendukung Background Task Panjang:** Modul backup database atau audit log tidak dapat berjalan di background.

> **Solusi:** Gunakan platform **Render.com** atau **Railway.app** yang menyediakan runtime server Python berkelanjutan (*PaaS Web Service*).

### 2.2 Persiapan Berkas Konfigurasi Backend
Pastikan berkas `backend/requirements.txt` telah mencakup seluruh library yang diperlukan:
```txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
sqlalchemy>=2.0.28
alembic>=1.13.1
pydantic[email]>=2.6.4
pydantic-settings>=2.2.1
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.0.0
python-multipart>=0.0.9
python-dotenv>=1.0.1
psycopg2-binary>=2.9.9
slowapi>=0.1.9
httpx>=0.28.1
openpyxl>=3.1.0
reportlab>=4.0.0
gunicorn>=21.2.0
```

### 2.3 Langkah Deployment di Render.com
1. Buka [https://render.com](https://render.com) dan buat akun (bisa login via GitHub).
2. Di dashboard Render, klik tombol **New +** lalu pilih **Web Service**.
3. Pilih opsi **Build and deploy from a Git repository** dan hubungkan repositori GitHub Anda.
4. Atur spesifikasi layanan:
   * **Name:** `gracepoint-backend-api`
   * **Region:** `Singapore (Southeast Asia)`
   * **Branch:** `main` (atau `master`)
   * **Root Directory:** `backend`
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   * **Instance Type:** `Free`
5. Gulir ke bawah ke bagian **Environment Variables** (lihat sub-bab 2.4).
6. Klik **Create Web Service**.

### 2.4 Konfigurasi Environment Variables Backend
Di tab **Environment** pada dashboard Render, masukkan variabel-variabel berikut:

| Key (Nama Variabel) | Nilai Rekomendasi Produksi | Fungsi |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://...neon.tech/gracepoint_db?sslmode=require` | Connection string Neon PostgreSQL dari Bab 1. |
| `SECRET_KEY` | *(Generate string acak minimal 32 karakter)* | Kunci enkripsi token autentikasi JWT. |
| `ALGORITHM` | `HS256` | Algoritma tanda tangan token JWT. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | Masa aktif token login (10080 menit = 7 hari). |
| `DEBUG` | `False` | Mematikan mode debug untuk mencegah kebocoran informasi error. |
| `BACKEND_CORS_ORIGINS` | `["https://namagereja.com","https://www.namagereja.com","http://localhost:5173"]` | Daftar domain frontend yang diizinkan memanggil API. |

### 2.5 Verifikasi Endpoint Backend
Setelah status deploy di Render berubah menjadi **Live**, Render akan memberikan URL publik resmi, misalnya: `https://gracepoint-backend-api.onrender.com`.

Uji endpoint berikut di browser:
* `https://gracepoint-backend-api.onrender.com/` $\rightarrow$ Menampilkan respons JSON: `{"message": "Welcome to CMS Project Backend", ...}`
* `https://gracepoint-backend-api.onrender.com/docs` $\rightarrow$ Menampilkan halaman interaktif Swagger UI.
* `https://gracepoint-backend-api.onrender.com/api/v1/churches` $\rightarrow$ Menguji query data ke database Neon.

---

## Bab 3: Deployment Frontend Vue.js ke Vercel

### 3.1 Mengapa Frontend Vue Sangat Cocok di Vercel
Frontend GracePoint CMS dibangun dengan **Vue 3 + Vite**. Vercel adalah platform terbaik untuk aplikasi jenis ini karena:
* Menghasilkan proses kompilasi (*build*) yang sangat cepat (`vite build`).
* Hasil build (folder `dist/`) disebarkan ke ratusan titik edge server (CDN) di seluruh dunia.
* Menyediakan domain gratis `.vercel.app` ber-SSL langsung tanpa setup sertifikat.
* Otomatis melakukan rebuild setiap kali Anda melakukan `git push` ke repositori.

### 3.2 Menyiapkan Routing SPA di `vercel.json`
Aplikasi Vue Anda menggunakan **Vue Router dengan HTML5 History Mode**. Tanpa konfigurasi khusus, jika pengguna mengakses URL secara langsung seperti `https://namagereja.com/inventory` atau menekan tombol F5 (Refresh), Vercel akan mengembalikan pesan error **404 Not Found** karena berkas `inventory.html` memang tidak ada secara fisik.

Untuk mengatasinya, pastikan terdapat berkas `frontend/cms-project/vercel.json` dengan konfigurasi rewrite:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 3.3 Langkah Import Proyek ke Dashboard Vercel
1. Buka [https://vercel.com](https://vercel.com) dan login dengan akun GitHub Anda.
2. Klik tombol **Add New...** $\rightarrow$ **Project**.
3. Pilih repositori GitHub proyek GracePoint CMS Anda, lalu klik **Import**.
4. Di halaman konfigurasi proyek (**Configure Project**), sesuaikan pengaturan berikut:
   * **Project Name:** `gracepoint-frontend` (atau nama lain yang Anda sukai).
   * **Framework Preset:** Pilih `Vite` (biasanya terdeteksi otomatis).
   * **Root Directory:** Klik tombol **Edit** di sebelahnya, lalu pilih folder `frontend/cms-project`.
   * **Build Command:** Biarkan default (`npm run build` atau `vite build`).
   * **Output Directory:** Biarkan default (`dist`).
5. Buka bagian **Environment Variables** (lihat sub-bab 3.4).
6. Klik tombol **Deploy**.

### 3.4 Konfigurasi Environment Variable `VITE_API_BASE_URL`
Pada formulir Environment Variables di Vercel, tambahkan variabel:
* **Key:** `VITE_API_BASE_URL`
* **Value:** `https://gracepoint-backend-api.onrender.com/api/v1` *(atau `https://api.namagereja.com/api/v1` jika domain kustom sudah aktif)*

Setelah beberapa detik, Vercel akan menyelesaikan proses build dan memberikan URL aktif seperti: `https://gracepoint-frontend.vercel.app`.

---

## Bab 4: Konfigurasi Domain, DNS, & Cloudflare SSL (HTTPS)

### 4.1 Pemahaman Konseptual: Domain, DNS Records, & Cloudflare Proxy
* **Domain:** Nama alamat web resmi yang Anda beli di registrar (misalnya di Niagahoster, Domainesia, Namecheap, atau Cloudflare Registrar), contoh: `namagereja.com`.
* **DNS (Domain Name System):** Mengarahkan nama domain ke server hosting fisik yang sebenarnya.
* **CNAME Record:** Catatan DNS yang mengarahkan satu nama domain/subdomain ke nama domain hosting lain.
* **Cloudflare Proxy (Ikon Awan Oranye ☁️):** Lalu lintas pengunjung disaring terlebih dahulu oleh Cloudflare sebelum diteruskan ke Vercel atau Render. Cloudflare otomatis menerbitkan **Sertifikat SSL Gratis**, menangkal DDoS, dan mengaktifkan Web Application Firewall.

### 4.2 Langkah 1: Menghubungkan Domain ke Cloudflare Nameserver
1. Masuk ke [https://cloudflare.com](https://cloudflare.com) (buat akun jika belum punya).
2. Klik **Add a Site**, lalu masukkan nama domain yang Anda miliki (misal: `namagereja.com`).
3. Pilih paket **Free ($0)**.
4. Cloudflare akan memindai record DNS yang ada dan menampilkan **2 Name Server Cloudflare**, misalnya:
   * `amir.ns.cloudflare.com`
   * `chloe.ns.cloudflare.com`
5. Buka dashboard tempat Anda membeli domain (Registrar). Masuk ke menu **Name Servers / Kelola DNS**, lalu ubah Name Server bawaan registrar menjadi 2 Name Server Cloudflare tersebut.
6. Tunggu proses propagasi DNS (biasanya 5–30 menit). Status domain di Cloudflare akan menjadi **Active**.

### 4.3 Langkah 2: Mengisi Catatan DNS (DNS Records) di Cloudflare
Masuk ke menu **DNS** $\rightarrow$ **Records** di dashboard Cloudflare, lalu tambahkan baris-baris berikut:

| Type | Name | Target (Points to) | Proxy Status | Keterangan & Tujuan |
| :---: | :---: | :--- | :---: | :--- |
| **CNAME** | `@` | `cname.vercel-dns.com` | **Proxied** (Awan Oranye) | Mengarahkan domain utama `https://namagereja.com` ke Frontend Vercel. |
| **CNAME** | `www` | `cname.vercel-dns.com` | **Proxied** (Awan Oranye) | Mengarahkan alias `https://www.namagereja.com` ke Frontend Vercel. |
| **CNAME** | `api` | `gracepoint-backend-api.onrender.com` | **Proxied** (Awan Oranye) | Mengarahkan subdomain `https://api.namagereja.com` ke Backend Render. |

> **Catatan:** Di Vercel Dashboard, masuk ke menu **Settings** $\rightarrow$ **Domains** $\rightarrow$ Tambahkan domain `namagereja.com` dan `www.namagereja.com`. Vercel akan otomatis mengenali record DNS yang Anda buat di Cloudflare.

### 4.4 Langkah 3: Mengaktifkan Enkripsi SSL/TLS (HTTPS) Otomatis
Agar website Anda langsung memiliki lambang gembok aman dan tidak dapat dibuka lewat HTTP biasa:
1. Di Cloudflare, masuk ke menu **SSL/TLS** $\rightarrow$ **Overview**.
2. Pilih mode enkripsi: **Full** (atau **Full (Strict)**).
3. Buka sub-menu **Edge Certificates**:
   * **Always Use HTTPS:** Ubah menjadi **ON** (Setiap pengunjung yang membuka `http://` akan otomatis dipaksa berpindah ke `https://`).
   * **Automatic HTTPS Rewrites:** Ubah menjadi **ON** (Memperbaiki URL aset gambar/skrip agar tidak terjadi error *Mixed Content*).
   * **Minimum TLS Version:** Pilih **TLS 1.2** (Standar keamanan tertinggi).

---

## Bab 5: Sinkronisasi CORS & Checklist Pengujian Akhir

### 5.1 Update CORS Whitelist di Backend FastAPI
Setelah domain aktif, backend FastAPI harus diberitahu agar mengizinkan request yang datang dari domain baru Anda.

Buka Render Dashboard $\rightarrow$ Masuk ke service `gracepoint-backend-api` $\rightarrow$ **Environment Variables** $\rightarrow$ Perbarui nilai `BACKEND_CORS_ORIGINS`:

```json
BACKEND_CORS_ORIGINS=["https://namagereja.com","https://www.namagereja.com","http://localhost:5173"]
```
*(Klik Save Changes. Render akan melakukan redeploy otomatis dalam beberapa detik).*

### 5.2 Update API Base URL di Frontend Vercel
Buka Vercel Dashboard $\rightarrow$ Pilih project `gracepoint-frontend` $\rightarrow$ **Settings** $\rightarrow$ **Environment Variables**:
* Ubah `VITE_API_BASE_URL` menjadi: `https://api.namagereja.com/api/v1`
* Masuk ke tab **Deployments** $\rightarrow$ Klik menu titik tiga (...) pada deployment terakhir $\rightarrow$ Pilih **Redeploy** agar frontend dikompilasi ulang dengan URL API resmi.

### 5.3 Lembar Checklist Pengujian Sistem Produksi

Lakukan pengujian menyeluruh pada domain resmi:

- [ ] **Protokol SSL/HTTPS:** Akses `http://namagereja.com` di browser. Pastikan otomatis dialihkan ke `https://namagereja.com` dengan status gembok aman (Secure).
- [ ] **Routing Frontend:** Buka halaman menu seperti `/inventory`, lalu tekan tombol F5 (Refresh). Pastikan halaman termuat normal tanpa error 404.
- [ ] **Autentikasi Multi-Aktor:** Lakukan login sebagai Super Admin, Church Admin, dan Akun Jemaat. Pastikan JWT token tersimpan di LocalStorage dan diarahkan ke dashboard masing-masing.
- [ ] **Konektivitas Database Cloud:** Buka menu Biodata Jemaat, lakukan penambahan satu data anggota baru. Pastikan data langsung tersimpan di Neon Cloud PostgreSQL.
- [ ] **Fitur Ekspor Laporan:** Lakukan ekspor laporan kas keuangan ke format PDF (ReportLab) dan Excel (OpenPyXL). Pastikan berkas dapat diunduh tanpa timeout.
- [ ] **Presensi QR Code:** Uji fitur scan token QR presensi ibadah. Pastikan data presensi tercatat otomatis ke tabel `attendances`.

---

## Bab 6: Panduan Troubleshooting & FAQ

#### 1. Muncul error "Blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present"
* **Penyebab:** Domain frontend Anda belum terdaftar di whitelist `BACKEND_CORS_ORIGINS` pada backend.
* **Solusi:** Pastikan domain frontend ditulis lengkap dengan protokolnya, misalnya `https://namagereja.com` (tanpa tanda garis miring `/` di bagian akhir), lalu simpan dan restart service backend di Render.

#### 2. Saat halaman di-refresh di Vercel muncul error "404: NOT_FOUND"
* **Penyebab:** Vercel menganggap rute tersebut sebagai file statis yang tidak ada di server.
* **Solusi:** Pastikan berkas `frontend/cms-project/vercel.json` telah dibuat dan berisi konfigurasi rewrite ke `/index.html` sesuai Bab 3.2.

#### 3. Error database "SSL connection has been closed unexpectedly" atau "sslmode required"
* **Penyebab:** Backend mencoba terhubung ke Neon PostgreSQL tanpa enkripsi SSL.
* **Solusi:** Pastikan pada akhir connection string `DATABASE_URL` selalu terdapat parameter `?sslmode=require`.

#### 4. Apakah saya bisa menguji seluruh alur online ini secara gratis tanpa membeli domain?
* **Jawab:** **SANGAT BISA.**
  Anda tidak wajib membeli domain kustom sekarang. Anda bisa menjalankan sistem secara online sepenuhnya menggunakan domain gratis bawaan:
  * **Frontend:** `https://gracepoint-frontend.vercel.app` (disediakan gratis oleh Vercel, otomatis SSL).
  * **Backend:** `https://gracepoint-backend-api.onrender.com` (disediakan gratis oleh Render, otomatis SSL).
  * **Database:** `Neon Serverless PostgreSQL` (Free Tier).
  
  Ketika nantinya gereja sudah siap membeli domain resmi (`.com` / `.org` / `.id`), Anda tinggal mengikuti langkah di **Bab 4** dan **Bab 5** tanpa perlu mengubah kode sumber aplikasi sama sekali!

---
*Dokumen ini disusun untuk melengkapi dokumentasi arsitektur resmi GracePoint CMS.*
