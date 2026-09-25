# 📁 Folder `src/components/`

Folder ini berisi komponen-komponen antarmuka pengguna (**UI Components**) yang bersifat **reusabel** (dapat digunakan kembali di berbagai halaman aplikasi).

## 📌 Fungsi & Kegunaan
1. **Dapat Digunakan Kembali (*Reusability*)**: Menghindari pengulangan kode HTML & CSS di banyak halaman.
2. **Kemudahan Pemeliharaan (*Maintainability*)**: Jika ada perubahan tampilan pada bagian seperti *Navbar* atau *Card*, Anda hanya perlu mengubah satu berkas di folder ini.
3. **Modularitas**: Memecah halaman web yang kompleks menjadi bagian-bagian kecil yang lebih mudah dikelola.

## ⚖️ Perbedaan `components/` vs `pages/`
- **`components/`**: Bagian-bagian kecil dari UI yang **tidak memiliki rute URL sendiri** (misal: `Navbar.vue`, `Card.vue`, `Sidebar.vue`).
- **`pages/`**: Komponen tingkat halaman yang **terhubung ke rute URL** di `router/index.js` (misal: `HomeView.vue`, `LoginView.vue`).

## 🧩 Komponen dalam Proyek Ini
- **[Navbar.vue](file:///d:/cms-project/frontend/cms-project/src/components/Navbar.vue)**: Navigasi utama bertema gerejawi.
- **[Sidebar.vue](file:///d:/cms-project/frontend/cms-project/src/components/Sidebar.vue)**: Menu navigasi samping.
- **[Card.vue](file:///d:/cms-project/frontend/cms-project/src/components/Card.vue)**: Kontainer kartu informasi reusabel dengan dukungan *props* & *slots*.
