# TODO: Perbaiki Sidebar & Koordinasi dengan HomeView

## Step 1: Perbaiki navigasi di HomeView.vue
- [x] Ubah `navigateTo('user')` → `router.push('/login?role=user')`
- [x] Ubah `navigateTo('church_admin')` → `router.push('/login?role=church_admin')`

## Step 2: Perbaiki HomeLayout.vue
- [x] Tambahkan `max-h-[calc(100vh-140px)] overflow-y-auto custom-scrollbar` pada wrapper sidebar
- [x] Atur `isSidebarOpen = true` secara default di layar >= 1024px
- [x] Tambahkan transisi margin-left pada `<main>` saat sidebar terbuka/tutup

## Step 3: Perbaiki Home_Sidebar.vue
- [x] Tambahkan class `custom-scrollbar` ke elemen `<aside>`
- [x] Tambahkan `max-h-[calc(100vh-140px)]` dan `overflow-y-auto` ke sidebar

## Step 4: Testing
- [x] Verifikasi semua perubahan berjalan dengan baik

