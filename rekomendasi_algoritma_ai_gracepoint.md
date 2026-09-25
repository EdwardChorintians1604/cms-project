# Panduan & Rekomendasi Algoritma AI untuk GracePoint CMS

Dokumen ini disusun sebagai panduan dan pengingat rencana integrasi fitur **Artificial Intelligence (AI) / Machine Learning (ML)** pada platform **GracePoint (Sistem Informasi & Pelayanan Gereja)** setelah seluruh perancangan antarmuka (UI/UX) selesai.

 Seluruh rekomendasi difokuskan pada algoritma yang **bermanfaat tinggi, bernilai nyata bagi gereja, namun mudah diimplementasikan** tanpa menggunakan *Digital Image Processing (DIP)* maupun *Natural Language Processing (NLP)*.

---

## 📋 Daftar Opsi Algoritma AI

### 1. Prediksi Kehadiran Jemaat (*Attendance Forecasting*)
* **Tujuan**: Memprediksi estimasi jumlah jemaat yang akan hadir pada Ibadah Minggu berikutnya atau ibadah hari raya (Natal, Paskah, Tahun Baru).
* **Manfaat**: Membantu tim operasional gereja menyiapkan kapasitas kursi, area parkir, serta konsumsi dengan presisi.
* **Algoritma**: **Regresi Linear (*Linear Regression*)** atau **Exponential Smoothing / Moving Average**.
* **Kebutuhan Data Input**:
  - Tanggal / Minggu ke-x dalam bulan
  - Sesi Ibadah (Sesi I / Sesi II)
  - Penanda Hari Raya (Ya / Tidak)
  - Data Historis Kehadiran Masa Lalu
* **Tingkat Kesulitan**: ⭐ (Sangat Mudah) — Dapat dibuat di Python (`scikit-learn`) dalam ~10 baris kode atau di Node.js/JavaScript (`simple-statistics`).

---

### 2. Rekomendasi Pelayanan & Komunitas Sel (*Ministry & Cell Group Recommender*)
* **Tujuan**: Memberikan saran otomatis bidang pelayanan yang cocok (*Pemusuk, Usher, Multimedia, Diakonia, Sekolah Minggu*) atau Kelompok Sel (*Komsel*) terdekat bagi jemaat baru.
* **Manfaat**: Membantu jemaat baru langsung terlibat dalam komunitas dan pelayanan yang sesuai minat & lokasinya.
* **Algoritma**: **K-Nearest Neighbors (KNN)** atau **Decision Tree (Pohon Keputusan)**.
* **Kebutuhan Data Input**:
  - Profil Jemaat (Usia, Domisili, Ketersediaan Waktu, Minat/Bakat)
  - Kebutuhan Pelayanan / Komsel Terdekat
* **Tingkat Kesulitan**: ⭐⭐ (Mudah) — Mencocokkan skor kemiripan variabel profil jemaat.

---

### 3. Otomatisasi Penjadwalan Pelayan Ibadah (*Smart Duty Roster Scheduler*)
* **Tujuan**: Membuat draf jadwal tugas pelayanan bulanan secara otomatis tanpa bentrok jadwal antar-pelayan.
* **Manfaat**: Menghemat waktu pengurus gereja dan mencegah *over-scheduling* (pelayan kelelahan karena bertugas terus-menerus).
* **Algoritma**: **Constraint Satisfaction Problem (CSP)** / **Rule-Based Heuristic Algorithm**.
* **Kebutuhan Data Input**:
  - Daftar Pelayan & Skill/Peran
  - Jadwal Halangan/Absen Pelayan
  - Batas Maksimal Tugas per Bulan (misal: Maks. 2x seminggu)
* **Tingkat Kesulitan**: ⭐⭐ (Mudah) — Logika aturan pencocokan (*match & check constraints*).

---

### 4. Deteksi Anomali Keuangan & Pengeluaran (*Financial Anomaly Detection*)
* **Tujuan**: Menandai transaksi pengeluaran atau persembahan yang tidak biasa secara otomatis (misal pengeluaran mendadak yang melampaui batas kewajaran bulanan).
* **Manfaat**: Membantu verifikasi transparansi laporan keuangan dan mencegah *human error* saat input angka.
* **Algoritma**: **Z-Score Analysis** atau **Isolation Forest**.
* **Kebutuhan Data Input**:
  - Kategori Pengeluaran / Persembahan
  - Nominal Angka Transaksi
  - Histori Pengeluaran Rata-rata Bulanan
* **Tingkat Kesulitan**: ⭐ (Sangat Mudah) — Menggunakan standar deviasi statistik sederhana.

---

### 5. Segmentasi Demografi Jemaat (*Jemaat Clustering*)
* **Tujuan**: Mengelompokkan jemaat secara otomatis berdasarkan tingkat keaktifan, usia, dan partisipasi acara gereja.
* **Manfaat**: Membantu pendeta & majelis gereja merancang program pelayanan dan kegiatan jemaat yang tepat sasaran.
* **Algoritma**: **K-Means Clustering**.
* **Kebutuhan Data Input**:
  - Frekuensi Kehadiran Jemaat
  - Kelompok Usia
  - Jumlah Keikutsertaan Kegiatan
* **Tingkat Kesulitan**: ⭐⭐ (Mudah) — Paket standar `sklearn.cluster.KMeans`.

---

## 📊 Perbandingan Algoritma

| Fitur AI | Algoritma | Tingkat Kesulitan | Kebutuhan Data | Estimasi Waktu Buat |
| :--- | :--- | :---: | :---: | :---: |
| **1. Prediksi Kehadiran** | Linear Regression | Sangat Mudah | Tabel Kehadiran | 1-2 Jam |
| **2. Rekomendasi Pelayanan** | KNN / Decision Tree | Mudah | Form Profil Jemaat | 2-3 Jam |
| **3. Penjadwalan Otomatis** | Constraint Logic / CSP | Mudah | Data Pelayan & Jadwal | 3-4 Jam |
| **4. Deteksi Anomali Keuangan**| Z-Score / IQR | Sangat Mudah | Laporan Keuangan | 1 Jam |
| **5. Segmentasi Jemaat** | K-Means | Mudah | Data Demografi | 2 Jam |

---

## 🚀 Langkah Selanjutnya (Setelah UI Selesai)
1. **Pilih 1-2 Fitur Utama**: Direkomendasikan memulai dari **Prediksi Kehadiran Jemaat** atau **Rekomendasi Pelayanan**.
2. **Siapkan API Backend**: Buat endpoint API sederhana (misal di Express.js / Python FastAPI) yang mengembalikan data hasil kalkulasi AI.
3. **Hubungkan ke Dashboard UI GracePoint**: Tampilkan grafik hasil prediksi / rekomendasi di halaman Dashboard GracePoint.
