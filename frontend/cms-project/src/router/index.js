import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/pages/HomeView.vue'
import LoginView from '@/pages/LoginView.vue'
import VerificationLogin from '@/pages/auth/verification_login.vue'
import UserRegister from '@/pages/auth/User_Register.vue'
import ChurchRegister from '@/pages/auth/Church_Register.vue'
import HariBesarGereja from '@/pages/HariBesarGereja.vue'
import InformasiPelayanan from '@/pages/InformasiPelayanan.vue'
import BeritaJemaat from '@/pages/BeritaJemaat.vue'
import PetaBeranda from '@/pages/PetaBeranda.vue'
import NotFound from '@/pages/NotFound.vue'
import ChurchHistory from '@/pages/history_church/church_history.vue'
import { authGuard } from '@/middleware/authGuard'
import DashboardMainAdministrator from '@/pages/dashboard/DashboardMainAdministrator.vue'
import DashboardChurchAdmin from '@/pages/dashboard/DashboardChurchAdmin.vue'
import DashboardUser from '@/pages/dashboard/DashboardUser.vue'
import DataGerejaAdminUtama from '@/pages/church/DataGerejaAdminUtama.vue'
import DataGerejaRegisterAdminUtama from '@/pages/church/DataGerejaRegisterAdminUtama.vue'
import Manajemen_admin_cabang_untuk_admin_utama from '@/pages/church_admin/Manajemen_admin_cabang_untuk_admin_utama.vue'
import namapenggunaUntukAdminUtama from '@/pages/user/namapenggunaUntukAdminUtama.vue'
import ChurchBranch from '@/pages/cabang_church/church_branch.vue'
import ITAudit from '@/pages/audit/it-audit.vue'
import { useSidebar } from '@/composables/useSidebar'
import BackupView from '@/pages/backup/BackupView.vue'
import MainAdminCalendar from '@/pages/calendar/Main_Admin_Calendar.vue'
import PostgreSQLView from '@/pages/postgreSQLview/postgreSQLView.vue'
import PemasukanGereja from '@/pages/finance/Main_Admin_Pemasukan_Gereja.vue'
import PengeluaranGereja from '@/pages/finance/Main_Admin_Pengeluaran_Gereja.vue'
import GrafikKeuanganGereja from '@/pages/finance/Main_Admin_Grafik_Keuangan_Gereja.vue'
import MainAdminOptionsSettings from '@/components/settings/Main_Admin_Options_Settings.vue'
import MainAdminThemesSettings from '@/components/settings/Main_Admin_Themes_Settings.vue'
import SecurityView from '@/components/settings/SecurityView.vue'
import MemberListView from '@/pages/member/MemberListView.vue'
import WorshipScheduleView from '@/pages/worship/WorshipScheduleView.vue'
import AttendanceView from '@/pages/attendance/AttendanceView.vue'
import SacramentView from '@/pages/sacrament/SacramentView.vue'
import PastoralCareView from '@/pages/pastoral/PastoralCareView.vue'
import FinanceView from '@/pages/finance/FinanceView.vue'
import InventoryView from '@/pages/inventory/InventoryView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
        top: 90
      }
    }
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0, behavior: 'smooth' }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: false, title: 'Platform Manajemen & Pelayanan Gereja' },
    },
    {
      path: '/peta-beranda',
      alias: ['/peta-gereja', '/peta', '/peta-lokasi'],
      name: 'peta-beranda',
      component: PetaBeranda,
      meta: { requiresAuth: false, title: 'Peta Geolocation & Lokasi Gereja Terdaftar' },
    },
    {
      path: '/informasi-pelayanan',
      name: 'informasi-pelayanan',
      component: InformasiPelayanan,
      meta: { requiresAuth: false, title: 'Informasi Pelayanan' },
    },
    {
      path: '/berita-jemaat',
      name: 'berita-jemaat',
      component: BeritaJemaat,
      meta: { requiresAuth: false, title: 'Berita & Warta Jemaat' },
    },
    {
      path: '/hari-besar',
      name: 'hari-besar',
      component: HariBesarGereja,
      meta: { requiresAuth: false, title: 'Hari Besar Gereja' },
    },
    {
      path: '/sejarah-gereja',
      alias: ['/history-church', '/church-history', '/cikal-bakal-gereja', '/sejarah'],
      name: 'sejarah-gereja',
      component: ChurchHistory,
      meta: { requiresAuth: false, title: 'Search Engine Sejarah & Cikal Bakal Gereja Indonesia' },
    },
    {
      path: '/verification-login',
      alias: ['/login', '/masuk-sistem', '/portal-login'],
      name: 'verification-login',
      component: VerificationLogin,
      meta: { requiresAuth: false, title: 'Portal Masuk & Verifikasi Terpadu' },
    },
    {
      path: '/user-login',
      redirect: '/verification-login',
    },
    {
      path: '/church-login',
      redirect: '/verification-login',
    },
    {
      path: '/user-register',
      name: 'user-register',
      component: UserRegister,
      meta: { title: 'Pendaftaran Jemaat' },
    },
    {
      path: '/church-register',
      name: 'church-register',
      component: ChurchRegister,
      meta: { title: 'Pendaftaran Gereja' },
    },
    {
      path: '/data-gereja',
      name: 'data-gereja',
      component: DataGerejaAdminUtama,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Manajemen Data Gereja' },
    },
    {
      path: '/cabang-gereja',
      alias: ['/data-cabang', '/church-branch'],
      name: 'cabang-gereja',
      component: ChurchBranch,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Manajemen Cabang Gereja' },
    },
    {
      path: '/grace-console-x99',
      name: 'main-login',
      component: LoginView,
      meta: { title: 'Masuk ke Akun' },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardMainAdministrator,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Dashboard Utama Admin System' },
    },
    {
      path: '/system-admin',
      name: 'system-admin',
      component: DashboardMainAdministrator,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Sistem Admin Utama GracePoint' },
    },
    {
      path: '/dashboard-church',
      name: 'dashboard-church',
      component: DashboardChurchAdmin,
      meta: { requiresAuth: true, role: 'church_admin', title: 'Dashboard Admin Gereja' },
    },
    {
      path: '/church-members',
      alias: ['/jemaat-cabang', '/data-jemaat-cabang'],
      name: 'church-members',
      component: MemberListView,
      meta: { requiresAuth: true, role: 'church_admin', title: 'Database Jemaat & Rayon Cabang' },
    },
    {
      path: '/church-roster',
      alias: ['/roster-pelayanan', '/jadwal-pelayan-ibadah'],
      name: 'church-roster',
      component: WorshipScheduleView,
      meta: { requiresAuth: true, role: 'church_admin', title: 'Jadwal Petugas & Roster Pelayanan' },
    },
    {
      path: '/church-attendance',
      alias: ['/presensi-ibadah', '/kehadiran-ibadah'],
      name: 'church-attendance',
      component: AttendanceView,
      meta: { requiresAuth: true, role: 'church_admin', title: 'Presensi QR & Kehadiran Ibadah' },
    },
    {
      path: '/church-sacraments',
      alias: ['/sakramen-pelayanan', '/permohonan-sakramen'],
      name: 'church-sacraments',
      component: SacramentView,
      meta: { requiresAuth: true, role: 'church_admin', title: 'Permohonan Sakramen & Surat Resmi' },
    },
    {
      path: '/church-pastoral',
      alias: ['/pastoral-care', '/konseling-doa'],
      name: 'church-pastoral',
      component: PastoralCareView,
      meta: { requiresAuth: true, role: 'church_admin', title: 'Pelayanan Pastoral & Konseling Doa' },
    },
    {
      path: '/church-finance',
      alias: ['/keuangan-cabang', '/kasir-persembahan'],
      name: 'church-finance',
      component: FinanceView,
      meta: { requiresAuth: true, role: 'church_admin', title: 'Kasir Persembahan & Keuangan Cabang' },
    },
    {
      path: '/church-facilities',
      alias: ['/fasilitas-cabang', '/booking-ruangan', '/inventaris-cabang'],
      name: 'church-facilities',
      component: InventoryView,
      meta: { requiresAuth: true, role: 'church_admin', title: 'Aset & Peminjaman Fasilitas Cabang' },
    },
    {
      path: '/dashboard-user',
      name: 'dashboard-user',
      component: DashboardUser,
      meta: { requiresAuth: true, role: 'jemaat', title: 'Dashboard Jemaat' },
    },
    {
      path: '/server-postgresql',
      name: 'server-postgresql',
      component: PostgreSQLView,
      meta: { requiresAuth: true, role: 'superadmin', title: 'PostgreSQL Control Center' },
    },
    {
      path: '/register-gereja',
      name: 'register-gereja',
      component: DataGerejaRegisterAdminUtama,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Registrasi Data Gereja' },
    },
    {
      path: '/manajemen-admin-cabang',
      alias: '/manajemen-admin-gereja',
      name: 'manajemen-admin-cabang',
      component: Manajemen_admin_cabang_untuk_admin_utama,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Manajemen Admin Cabang' }
    },
    {
      path: '/data-pengguna',
      name: 'data-pengguna',
      component: namapenggunaUntukAdminUtama,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Manajemen Biodata Jemaat' }
    },
    {
      path: '/audit-it',
      alias: ['/it-audit', '/audit', '/audit-log'],
      name: 'it-audit',
      component: ITAudit,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Audit IT & Catatan Aktivitas Sistem' }
    },
    {
      path: '/backup-database',
      alias: ['/backup', '/backup-data', '/backup-database'],
      name: 'backup-database',
      component: BackupView,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Backup Database & Restore' }
    },
    {
      path: '/main_admin_calendar',
      name: 'main_admin_calendar',
      component: MainAdminCalendar,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Kalender & Jadwal Kegiatan Gereja' }
    },
    {
      path: '/pemasukan-gereja',
      alias: ['/pemasukan'],
      name: 'pemasukan-gereja',
      component: PemasukanGereja,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Pemasukan Gereja' }
    },
    {
      path: '/pengeluaran-gereja',
      name: 'pengeluaran-gereja',
      component: PengeluaranGereja,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Pengeluaran Gereja' }
    },
    {
      path: '/grafik-keuangan-gereja',
      alias: ['/grafik-gereja'],
      name: 'grafik-keuangan-gereja',
      component: GrafikKeuanganGereja,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Grafik Keuangan Gereja' }
    },
    {
      path: '/church-settings',
      alias: ['/settings', '/pengaturan'],
      name: 'church-settings',
      component: MainAdminOptionsSettings,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Pengaturan Sistem & Gereja' }
    },
    {
      path: '/theme-settings',
      alias: ['/themes', '/tampilan'],
      name: 'theme-settings',
      component: MainAdminThemesSettings,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Pengaturan Tema & Tampilan' }
    },
    {
      path: '/security-view',
      alias: ['/security', '/security-scan', '/deteksi-ancaman'],
      name: 'security-view',
      component: SecurityView,
      meta: { requiresAuth: true, role: 'superadmin', title: 'Deteksi Keamanan & Pemindaian Kerentanan' }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFound,
      meta: { title: 'Halaman Tidak Ditemukan' },
    }
  ],
})

router.beforeEach(authGuard)

router.afterEach((to) => {
  const { closeSidebar } = useSidebar()
  closeSidebar()

  const defaultTitle = 'GracePoint | Platform Manajemen & Pelayanan Gereja'
  if (to.meta && to.meta.title) {
    document.title = `GracePoint | ${to.meta.title}`
  } else {
    document.title = defaultTitle
  }
})

export default router
