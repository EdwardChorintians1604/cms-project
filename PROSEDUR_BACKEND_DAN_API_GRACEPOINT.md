# PROSEDUR STANDAR PENGEMBANGAN BACK-END, API, DAN INFRASTRUKTUR
## GracePoint CMS (Content & Church Management System)
### Arsitektur Cloud-Native: Docker Hosting + Neon Serverless PostgreSQL

---

## 📋 DAFTAR ISI
1. [Bab 1: Perancangan DBMS & Arsitektur Data (Neon PostgreSQL)](#bab-1-perancangan-dbms--arsitektur-data-neon-postgresql)
2. [Bab 2: Containerization Web App & Deployment Docker](#bab-2-containerization-web-app--deployment-docker)
3. [Bab 3: Pengembangan Back-End & RESTful API (FastAPI & Python)](#bab-3-pengembangan-back-end--restful-api-fastapi--python)
4. [Bab 4: Prosedur Backup & Recovery Database](#bab-4-prosedur-backup--recovery-database)
5. [Bab 5: Manajemen Logging & Monitoring Sistem](#bab-5-manajemen-logging--monitoring-sistem)
6. [Bab 6: Manajemen Media & Storage Berkas](#bab-6-manajemen-media--storage-berkas)
7. [Bab 7: Strategi Pengujian (Testing & QA)](#bab-7-strategi-pengujian-testing--qa)
8. [Bab 8: Otomasi CI/CD & GitHub Actions (`.github`)](#bab-8-otomasi-cicd--github-actions-github)
9. [Bab 9: Checklist Operasional Pengembang](#bab-9-checklist-operasional-pengembang)

---

## Bab 1: Perancangan DBMS & Arsitektur Data (Neon PostgreSQL)

### 1.1 Keunggulan Arsitektur Neon Serverless PostgreSQL
Penggunaan **Neon PostgreSQL** (neon.tech) sebagai tempat backend database terhubung dengan web application yang di-host di Docker memberikan keuntungan besar:
- **Zero Infrastructure Overhead**: Tidak perlu mengelola container database lokal, penyimpanan disk, atau rotasi memori RAM server.
- **Enkripsi SSL/TLS Otomatis**: Koneksi terlindungi enkripsi tingkat tinggi dengan parameter `sslmode=require`.
- **Database Branching**: Kemampuan membuat skenario branch database (*Development*, *Staging*, *Production*) secara instan seperti pada Git.
- **Skalabilitas Otomatis**: Menangani lonjakan beban transaksi tanpa khawatir server down.

### 1.2 Format Connection String Neon pada Backend (`backend/.env`)
```env
# Koneksi Neon Serverless PostgreSQL
DATABASE_URL="postgresql://username:password@ep-cool-name-123456.ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require"
```

### 1.3 Struktur Tabel Utama
Sistem memiliki 9 tabel terintegrasi:
1. `users`: Autentikasi, email, hashed password (Bcrypt), role (`superadmin`, `church_admin`, `leader`, `user`).
2. `families`: Pendataan Kartu Keluarga Gereja (`family_code`, `family_name`, `head_of_family_id`).
3. `members`: Profil jemaat, tempat/tgl lahir, status baptis/sidi, nomor induk jemaat (NIJ).
4. `ministries`: Struktur komisi & divisi pelayanan (Worship, Media, Sound, Usher, Sekolah Minggu).
5. `service_schedules`: Penjadwalan ibadah mingguan & penugasan pelayan (`InformasiPelayanan.vue`).
6. `church_events`: Event & hari besar gereja (`HariBesarGereja.vue`).
7. `sacraments`: Riwayat penerimaan sakramen (Baptis Air, Sidi, Pernikahan, Penyerahan Anak).
8. `finances`: Transaksi kas persembahan, persepuluhan, dan pengeluaran operasional.
9. `announcements`: Warta jemaat dan pengumuman sistem.

### 1.4 Manajemen Migrasi Skema ke Neon (Alembic)
```bash
cd backend
# 1. Pastikan DATABASE_URL di .env mengarah ke Neon
# 2. Jalankan migrasi skema langsung ke cloud Neon
alembic upgrade head
```

---

## Bab 2: Containerization Web App & Deployment Docker

Dengan memindahkan PostgreSQL ke **Neon Cloud**, container Docker difokuskan murni untuk meng-host **Web Application (FastAPI Backend + Vue.js Frontend)**.

### 2.1 Konfigurasi `docker-compose.yml` untuk Web Hosting
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: gracepoint_api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs

  frontend:
    build:
      context: ./frontend/cms-project
      dockerfile: Dockerfile
    container_name: gracepoint_web
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend
```

---

## Bab 3: Pengembangan Back-End & RESTful API (FastAPI & Python)

### 3.1 Arsitektur Folder Backend (`backend/app/`)
```
backend/app/
├── api/          # Route Handler (Endpoints REST API)
├── core/         # Config, Database Engine, Security (JWT/Bcrypt)
├── db/           # Session management & Base models
├── models/       # Model SQLAlchemy (Database entities)
├── schemas/      # Schema Pydantic (Request & Response Validation)
├── services/     # Business logic layer
└── main.py       # Entrypoint FastAPI Application
```

---

## Bab 4: Prosedur Backup & Recovery Database

Walaupun Neon memiliki fitur *Point-in-Time Restore (PITR)* bawaan, salinan backup lokal tetap disimpan di `backups/`.

### 4.1 Backup Remote dari Neon ke File Lokal (`.sql`)
```bash
pg_dump "postgresql://username:password@ep-cool-name-123456.ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require" > backups/neon_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## Bab 5 s/d 9: Operasional & CI/CD
- **Logs**: Dicatat di `logs/app.log` dan `logs/error.log`.
- **Storage**: Media di-mount pada `storage/uploads/`.
- **Testing**: Pengujian otomatis menggunakan `pytest` di folder `backend/tests/`.
- **CI/CD**: GitHub Actions workflow pada `.github/workflows/ci.yml`.

---
*Dokumen ini diperbarui untuk mendukung arsitektur Cloud Hybrid: Docker Web Hosting + Neon Serverless PostgreSQL.*
