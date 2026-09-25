# Implementation Plan: UI/UX Contrast, Readability & Typography Enhancements

Perbaikan tampilan UI/UX pada halaman utama GracePoint difokuskan pada peningkatan kontras keterbacaan teks di Hero Section, penyempurnaan tombol Call-to-Action (CTA), serta penyelarasan tipografi dan hirarki visual.

## User Review Required

> [!IMPORTANT]
> **Perubahan Utama yang Diterapkan:**
> 1. **Hero Section Background Overlay**: Menambahkan lapisan *dark overlay* (~35-40% opacity) di atas gambar latar belakang bertekstur agar seluruh elemen di atasnya memiliki kontras yang tinggi.
> 2. **Keterbacaan Teks (Readability)**: Memperbaiki warna font judul ("Selamat Datang di GracePoint") dan subteks ("Kelola konten dan sistem Anda dengan mudah dan efisien") dari warna gelap menjadi warna terang (`#ffffff` & `#f1f5f9`) dengan efek *drop shadow*.
> 3. **Peningkatan Kontras Tombol CTA**: Mengubah tombol "Mulai Menjadi JEMAAT" dan "Mulai Sebagai Admin Gereja" dari transparan tipis (`10% opacity`) menjadi tombol *high-contrast* dengan warna latar yang jelas dan tegas (*solid/semi-solid background*).
> 4. **Hirarki Tipografi & Spacing**:
>    - Mempertahankan font Serif (`Cinzel`) untuk judul utama yang elegan dengan *font-weight bold* & *letter-spacing* yang pas.
>    - Menyelaraskan font Sans-Serif (`Lato` / `Inter`) untuk navigasi dan deskripsi teks agar konsisten dan mudah dibaca.
>    - Menghilangkan *negative margin* serta memberikan *padding/margin* ruang bernapas (*breathing room*) di antara elemen-elemen Hero Section.

---

## Proposed Changes

### [Frontend Component]

#### [MODIFY] [HomeView.vue](file:///d:/cms-project/frontend/cms-project/src/pages/HomeView.vue)
- Menambahkan kontainer `.hero-overlay` atau *overlay gradient* pada `.mainBody`.
- Mengubah `color: #000000;` pada `.headertext` dan `.subtext` menjadi warna putih/slate terang (`#ffffff` & `#f1f5f9`).
- Memperbarui styling `.portal-button` & tombol CTA agar memiliki latar belakang kontras tinggi (*solid/semi-transparent card CTA* dengan perpaduan warna Amber & Sky/Emerald yang kontras).
- Memperbaiki margin/padding pada `.headerLogo`, `.headertext`, `.subtext`, dan `.button-container` untuk memberikan *breathing room* yang seimbang.

#### [MODIFY] [Home_Navbar.vue](file:///d:/cms-project/frontend/cms-project/src/components/Home_Navbar.vue)
- Penyelarasan tipografi navigasi agar menggunakan font sans-serif/serif yang konsisten dan nyaman dibaca pada layar komputer maupun *mobile*.

---

## Verification Plan

### Automated Verification
- Menjalankan lint/build check atau memastikan tidak ada syntax error pada Vue components.
- Memastikan server pengembang (`npm run dev`) dapat merender halaman tanpa kesalahan console.

### Manual Verification
- **Uji Visual Hero Section**: Memastikan teks "Kelola konten dan sistem..." dan tombol "MULAI MENJADI JEMAAT" terbaca sangat jelas di atas background overlay.
- **Uji Tombol CTA**: Memastikan hover effect dan warna kontras tombol berfungsional dengan baik.
- **Uji Responsivitas**: Memeriksa tampilan di layar PC/desktop dan layar *smartphone* (mobile view).
