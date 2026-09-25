<script setup>
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import InformasiPelayananLayout from '@/layouts/InformasiPelayananLayout.vue'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'
import AOS from 'aos'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { APP_CONFIG } from '@/config'
import { useTheme } from '@/composables/useTheme'
import { useAuth } from '@/composables/useAuth'

// --- City Center Coordinates Map (Disesuaikan dengan Lokasi Cabang Terdaftar) ---
const CITY_CENTERS = {
  Padang: { lat: -0.9540, lng: 100.3530 },
  'Kota Padang': { lat: -0.9540, lng: 100.3530 },
  Bekasi: { lat: -6.1824, lng: 106.9856 },
  'Jakarta Barat': { lat: -6.1884, lng: 106.7388 },
  Jakarta: { lat: -6.1884, lng: 106.7388 },
  Madiun: { lat: -7.6298, lng: 111.5239 },
  'Desa Sikakap': { lat: -2.7778, lng: 100.2112 },
  'Desa Makukuet': { lat: -2.7504, lng: 100.2133 },
  Surabaya: { lat: -7.2575, lng: 112.7521 }
}

const detectDenomination = (name) => {
  if (!name) return 'Cabang Gereja'
  const upper = name.toUpperCase()
  if (upper.includes('GKPM')) return 'GKPM (Gereja Kristen Protestan Mentawai)'
  if (upper.includes('GBI')) return 'GBI (Gereja Bethel Indonesia)'
  if (upper.includes('GKI')) return 'GKI (Gereja Kristen Indonesia)'
  if (upper.includes('GPDI') || upper.includes('GPdI')) return 'GPdI (Gereja Pentakosta di Indonesia)'
  if (upper.includes('GSJA')) return 'GSJA (Gereja Sidang-Sidang Jemaat Allah)'
  if (upper.includes('HKBP')) return 'HKBP (Huria Kristen Batak Protestan)'
  if (upper.includes('GMI')) return 'GMI (Gereja Methodist Indonesia)'
  return 'Cabang Gereja Terdaftar'
}

// --- Data Khusus Cabang Gereja Terdaftar di Sistem CMS ---
const fallbackBranches = [
  {
    id: 'branch-11',
    numericId: 11,
    source: 'branch',
    name: 'GKPM Cabang Padang',
    church_code: 'GKPM-PDG-012DS',
    denomination: 'GKPM (Gereja Kristen Protestan Mentawai)',
    verified: true,
    cmsIntegrated: true,
    isLive: false,
    rating: 4.9,
    reviewsCount: 38,
    image: 'https://images.unsplash.com/photo-1548625361-1854589d8161?auto=format&fit=crop&w=800&q=80',
    city: 'Kota Padang',
    address: 'Jl. Nipah No. 12, Padang Barat, Kota Padang',
    distance: 'DBMS Cabang',
    coordinates: { lat: -0.95401, lng: 100.353054 },
    schedules: [
      { name: 'Ibadah Raya Minggu', time: 'Minggu, 09.00 WIB', room: 'Sanctuary Utama' },
      { name: 'Persekutuan Doa & Pelayanan', time: 'Jumat, 18.00 WIB', room: 'Ruang Serbaguna' }
    ],
    categories: ['Jadwal Ibadah', 'Pelayanan Pemuda', 'Diakonia & Sosial'],
    facilities: ['Lokasi Terverifikasi', 'Admin Cabang Aktif', 'Terintegrasi PostgreSQL'],
    contacts: {
      phone: '0812-7788-9900',
      whatsapp: '0812-7788-9900',
      email: 'padang@gkpm.org',
      website: 'https://www.google.com/maps?q=-0.95401,100.353054'
    },
    pastors: 'Admin Cabang Padang & Tim Pelayanan',
    vision: 'Menjadi cabang persekutuan jemaat yang bertumbuh dalam iman dan kasih Kristus di Kota Padang.',
    activeMinistries: [
      { name: 'Pelayanan Ibadah & Musik', desc: 'Pelayanan pujian penyembahan dan ibadah mingguan jemaat.' },
      { name: 'Diakonia Peduli Jemaat', desc: 'Penyaluran bantuan sosial bagi jemaat dan warga sekitar cabang.' }
    ]
  },
  {
    id: 'branch-1',
    numericId: 1,
    source: 'branch',
    name: 'GKI Harapan Indah',
    church_code: 'GKI-HARAPAN-01',
    denomination: 'GKI (Gereja Kristen Indonesia)',
    verified: true,
    cmsIntegrated: true,
    isLive: true,
    rating: 4.8,
    reviewsCount: 52,
    image: 'https://images.unsplash.com/photo-1438032005730-c779502df39b?auto=format&fit=crop&w=800&q=80',
    city: 'Bekasi',
    address: 'Komp. Harapan Indah Blok DB No. 1, Medan Satria, Bekasi',
    distance: 'DBMS Cabang',
    coordinates: { lat: -6.1824, lng: 106.9856 },
    schedules: [
      { name: 'Ibadah Raya Pagi', time: 'Minggu, 08.00 WIB', room: 'Gedung Utama' },
      { name: 'Ibadah Remaja & Pemuda', time: 'Minggu, 16.00 WIB', room: 'Ruang Pemuda Lt. 2' }
    ],
    categories: ['Jadwal Ibadah', 'Pelayanan Pemuda', 'Katekisasi & Pembinaan'],
    facilities: ['Parkir Luas', 'Ruang Multimedia HD', 'Ramah Disabilitas'],
    contacts: {
      phone: '(021) 889-1234',
      whatsapp: '0813-8899-0011',
      email: 'sekretariat@gki-harapanindah.org',
      website: 'https://www.google.com/maps?q=-6.1824,106.9856'
    },
    pastors: 'Pdt. Johanes & Tim Pastoral Cabang',
    vision: 'Gereja yang berakar dalam Firman, ramah bagi sesama, dan melayani dengan kasih.',
    activeMinistries: [
      { name: 'Pembinaan Remaja & Pemuda', desc: 'Wadah persekutuan generasi muda dan pembentukan karakter Kristiani.' },
      { name: 'Pelayanan Kasih Diakonia', desc: 'Program kepedulian sosial bagi jemaat pra-sejahtera.' }
    ]
  },
  {
    id: 'branch-2',
    numericId: 2,
    source: 'branch',
    name: 'GBI Grace Community',
    church_code: 'GBI-GRACE-02',
    denomination: 'GBI (Gereja Bethel Indonesia)',
    verified: true,
    cmsIntegrated: true,
    isLive: true,
    rating: 4.9,
    reviewsCount: 45,
    image: 'https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=800&q=80',
    city: 'Jakarta Barat',
    address: 'Komp. Ruko Puri Indah Blok A, Kembangan, Jakarta Barat',
    distance: 'DBMS Cabang',
    coordinates: { lat: -6.1884, lng: 106.7388 },
    schedules: [
      { name: 'Ibadah Raya 1', time: 'Minggu, 08.30 WIB', room: 'Auditorium Lt. 3' },
      { name: 'Youth Revival NYC', time: 'Sabtu, 17.00 WIB', room: 'Youth Room' }
    ],
    categories: ['Jadwal Ibadah', 'Pelayanan Pemuda', 'Komunitas Sel', 'Live Streaming'],
    facilities: ['AC & Audio Modern', 'Live Streaming HD', 'Area Parkir'],
    contacts: {
      phone: '0812-9988-7711',
      whatsapp: '0812-9988-7711',
      email: 'info@gbigrace.org',
      website: 'https://www.google.com/maps?q=-6.1884,106.7388'
    },
    pastors: 'Pdt. Michael & Tim Pastoral Cabang',
    vision: 'Komunitas yang menyembah Tuhan dengan kesungguhan dan berdampak bagi masyarakat perkotaan.',
    activeMinistries: [
      { name: 'Family Small Group', desc: 'Kelompok sel keluarga tumbuh bersama setiap minggu.' }
    ]
  },
  {
    id: 'branch-7',
    numericId: 7,
    source: 'branch',
    name: 'GPdI Karmel 12 Padang',
    church_code: 'GPDI-CAB-01',
    denomination: 'GPdI (Gereja Pentakosta di Indonesia)',
    verified: true,
    cmsIntegrated: true,
    isLive: false,
    rating: 4.7,
    reviewsCount: 29,
    image: 'https://images.unsplash.com/photo-1543857778-c4a1a3e0b2eb?auto=format&fit=crop&w=800&q=80',
    city: 'Padang',
    address: 'Jl. Gereja No. 12, Padang Barat, Padang',
    distance: 'DBMS Cabang',
    coordinates: { lat: -0.95851, lng: 100.357481 },
    schedules: [
      { name: 'Ibadah Raya Minggu', time: 'Minggu, 09.00 WIB', room: 'Gedung Gereja' },
      { name: 'Ibadah Doa Malam', time: 'Rabu, 19.00 WIB', room: 'Ruang Doa' }
    ],
    categories: ['Jadwal Ibadah', 'Pelayanan Pemuda', 'Konseling'],
    facilities: ['Ruang Doa', 'Klinik Konseling', 'Parkir'],
    contacts: {
      phone: '0813-6655-4433',
      whatsapp: '0813-6655-4433',
      email: 'gpdikarmel12@gmail.com',
      website: 'https://www.google.com/maps?q=-0.95851,100.357481'
    },
    pastors: 'Pdt. David & Tim Gembala Cabang',
    vision: 'Menjadi gereja yang penuh kuasa Roh Kudus dan membawa pemulihan bagi jemaat.',
    activeMinistries: [
      { name: 'Persekutuan Doa & Puasa', desc: 'Gerakan doa syafaat rutin bagi kota dan bangsa.' }
    ]
  },
  {
    id: 'branch-4',
    numericId: 4,
    source: 'branch',
    name: 'GSJA Rayon 10 Padang',
    church_code: 'GP-CAB-01',
    denomination: 'GSJA (Gereja Sidang-Sidang Jemaat Allah)',
    verified: true,
    cmsIntegrated: true,
    isLive: false,
    rating: 4.8,
    reviewsCount: 31,
    image: 'https://images.unsplash.com/photo-1548625361-1854589d8161?auto=format&fit=crop&w=800&q=80',
    city: 'Padang',
    address: 'Jl. Belakang Olo No. 10, Padang Barat, Padang',
    distance: 'DBMS Cabang',
    coordinates: { lat: -0.9583, lng: 100.3582 },
    schedules: [
      { name: 'Ibadah Raya Minggu', time: 'Minggu, 08.30 WIB', room: 'Main Hall' },
      { name: 'Persekutuan Kaum Muda', time: 'Sabtu, 17.30 WIB', room: 'Youth Room' }
    ],
    categories: ['Jadwal Ibadah', 'Pelayanan Pemuda', 'Diakonia & Sosial'],
    facilities: ['Parkir', 'Sound System Modern', 'Ruang Anak Sekolah Minggu'],
    contacts: {
      phone: '0812-3344-5566',
      whatsapp: '0812-3344-5566',
      email: 'gsjarayon10@gmail.com',
      website: 'https://www.google.com/maps?q=-0.9583,100.3582'
    },
    pastors: 'Pdt. Andreas & Tim Pelayanan Cabang',
    vision: 'Membangun jemaat yang teguh dalam firman dan giat dalam penginjilan serta misi.',
    activeMinistries: [
      { name: 'Youth & Campus Ministry', desc: 'Pembinaan rohani siswa dan mahasiswa di Kota Padang.' }
    ]
  },
  {
    id: 'branch-3',
    numericId: 3,
    source: 'branch',
    name: 'GSJA Rayon 12 Madiun',
    church_code: 'GSJA-CAB-02',
    denomination: 'GSJA (Gereja Sidang-Sidang Jemaat Allah)',
    verified: true,
    cmsIntegrated: true,
    isLive: false,
    rating: 4.7,
    reviewsCount: 22,
    image: 'https://images.unsplash.com/photo-1438032005730-c779502df39b?auto=format&fit=crop&w=800&q=80',
    city: 'Madiun',
    address: 'Jl. Pahlawan No. 45, Kartoharjo, Madiun',
    distance: 'DBMS Cabang',
    coordinates: { lat: -7.6298, lng: 111.5239 },
    schedules: [
      { name: 'Ibadah Minggu Pagi', time: 'Minggu, 07.30 WIB', room: 'Ruang Ibadah' },
      { name: 'Ibadah Doa Malam', time: 'Jumat, 18.30 WIB', room: 'Kapel' }
    ],
    categories: ['Jadwal Ibadah', 'Doa & Puasa', 'Diakonia & Sosial'],
    facilities: ['Area Parkir', 'AC', 'Ruang Konseling'],
    contacts: {
      phone: '0813-2211-9988',
      whatsapp: '0813-2211-9988',
      email: 'gsjamadiun@gmail.com',
      website: 'https://www.google.com/maps?q=-7.6298,111.5239'
    },
    pastors: 'Pdt. Markus & Tim Pastoral Cabang',
    vision: 'Melayani jemaat Madiun dengan kasih Kristus dan pelayanan pastoral yang setia.',
    activeMinistries: [
      { name: 'Pelayanan Lansia & Visitas Rumah', desc: 'Kunjungan berkala dan doa bagi lansia serta warga yang sakit.' }
    ]
  },
  {
    id: 'branch-5',
    numericId: 5,
    source: 'branch',
    name: 'GBI Bethel Padang',
    church_code: 'GBI-PDG-09HGJTW',
    denomination: 'GBI (Gereja Bethel Indonesia)',
    verified: true,
    cmsIntegrated: true,
    isLive: false,
    rating: 4.8,
    reviewsCount: 34,
    image: 'https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=800&q=80',
    city: 'Padang',
    address: 'Jl. Thamrin No. 88, Padang Selatan, Padang',
    distance: 'DBMS Cabang',
    coordinates: { lat: -0.9631, lng: 100.3564 },
    schedules: [
      { name: 'Ibadah Raya 1', time: 'Minggu, 08.00 WIB', room: 'Main Sanctuary' },
      { name: 'Ibadah Raya 2', time: 'Minggu, 10.30 WIB', room: 'Main Sanctuary' }
    ],
    categories: ['Jadwal Ibadah', 'Pelayanan Pemuda', 'Komunitas Sel'],
    facilities: ['Parkir', 'AC & Multimedia', 'Live Stream'],
    contacts: {
      phone: '0812-6677-8899',
      whatsapp: '0812-6677-8899',
      email: 'gbibethelpadang@gmail.com',
      website: 'https://www.google.com/maps?q=-0.9631,100.3564'
    },
    pastors: 'Pdt. Timotius & Tim Pelayanan Cabang',
    vision: 'Melahirkan murid Kristus yang berakar, berbuah, dan menjadi terang di Kota Padang.',
    activeMinistries: [
      { name: 'Komunitas Sel Keluarga', desc: 'Persekutuan kelompok kecil di berbagai sektor perumahan Padang.' }
    ]
  },
  {
    id: 'branch-6',
    numericId: 6,
    source: 'branch',
    name: 'GKPM Jemaat Mandiri Sikakap',
    church_code: 'GKPM-CAB-09SKKP',
    denomination: 'GKPM (Gereja Kristen Protestan Mentawai)',
    verified: true,
    cmsIntegrated: true,
    isLive: false,
    rating: 4.9,
    reviewsCount: 20,
    image: 'https://images.unsplash.com/photo-1543857778-c4a1a3e0b2eb?auto=format&fit=crop&w=800&q=80',
    city: 'Desa Sikakap',
    address: 'Dusun Sikakap Timur, Kec. Sikakap, Kepulauan Mentawai',
    distance: 'DBMS Cabang',
    coordinates: { lat: -2.777801, lng: 100.211257 },
    schedules: [
      { name: 'Ibadah Raya Minggu Pagi', time: 'Minggu, 09.00 WIB', room: 'Gedung Gereja Sikakap' },
      { name: 'Ibadah Sekolah Minggu', time: 'Minggu, 07.30 WIB', room: 'Aula Sekolah Minggu' }
    ],
    categories: ['Jadwal Ibadah', 'Diakonia & Sosial', 'Pembinaan Anak'],
    facilities: ['Gedung Ibadah', 'Gedung Sekolah Minggu', 'Halaman Luas'],
    contacts: {
      phone: '0813-7766-5544',
      whatsapp: '0813-7766-5544',
      email: 'sikakap@gkpm.org',
      website: 'https://www.google.com/maps?q=-2.777801,100.211257'
    },
    pastors: 'Guru Jemaat / Pendeta Cabang Sikakap',
    vision: 'Melayani dan mendampingi jemaat pesisir Mentawai dalam persekutuan iman dan kebersamaan.',
    activeMinistries: [
      { name: 'Pelayanan Anak & Sekolah Minggu', desc: 'Pendidikan budi pekerti Kristiani dan gizi anak di pulau Mentawai.' },
      { name: 'Diakonia Nelayan & Keluarga', desc: 'Bantuan sosial dan gotong royong warga jemaat nelayan.' }
    ]
  },
  {
    id: 'branch-8',
    numericId: 8,
    source: 'branch',
    name: 'GKPM Jemaat Mandiri Makukuet',
    church_code: 'GKPM-CAB-MKKT-09CZER',
    denomination: 'GKPM (Gereja Kristen Protestan Mentawai)',
    verified: true,
    cmsIntegrated: true,
    isLive: false,
    rating: 4.8,
    reviewsCount: 18,
    image: 'https://images.unsplash.com/photo-1548625361-1854589d8161?auto=format&fit=crop&w=800&q=80',
    city: 'Desa Makukuet',
    address: 'Dusun Makukuet, Kec. Pagai Selatan, Kepulauan Mentawai',
    distance: 'DBMS Cabang',
    coordinates: { lat: -2.750401, lng: 100.213309 },
    schedules: [
      { name: 'Ibadah Raya Minggu', time: 'Minggu, 09.30 WIB', room: 'Gedung Gereja Makukuet' }
    ],
    categories: ['Jadwal Ibadah', 'Diakonia & Sosial'],
    facilities: ['Gedung Gereja', 'Area Persekutuan'],
    contacts: {
      phone: '0812-5544-3322',
      whatsapp: '0812-5544-3322',
      email: 'makukuet@gkpm.org',
      website: 'https://www.google.com/maps?q=-2.750401,100.213309'
    },
    pastors: 'Guru Jemaat / Penatua Cabang Makukuet',
    vision: 'Menjadi garam dan terang di tengah kehidupan masyarakat pedesaan Kepulauan Mentawai.',
    activeMinistries: [
      { name: 'Pelayanan Persekutuan Desa', desc: 'Ibadah dan penguatan kerohanian keluarga jemaat di Makukuet.' }
    ]
  }
]

const churches = ref([...fallbackBranches])
const dbBranches = ref([...fallbackBranches])

// --- Hak Akses Admin ---
const { user } = useAuth()
const isMainAdmin = computed(() => user.value?.role === 'superadmin')
const isChurchAdmin = computed(() => user.value?.role === 'church_admin')

// --- Data Informasi Pelayanan Cabang Gereja Terdaftar (Database PostgreSQL) ---
const announcedServices = ref([])
const isServicesLoading = ref(false)
const rawBranchesList = ref([])

const selectedBranchFilter = ref('Semua')
const selectedServiceCategory = ref('Semua')
const serviceSearchQuery = ref('')
const selectedAnnouncementDetail = ref(null)

const serviceCategoriesList = [
  'Semua',
  'Jadwal Ibadah',
  'Pelayanan Pemuda',
  'Diakonia & Sosial',
  'Komunitas Sel',
  'Katekisasi & Pembinaan',
  'Konseling',
  'Musik & Pujian',
  'Lainnya'
]

const loadAnnouncedServices = async () => {
  isServicesLoading.value = true
  try {
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/informasi-pelayanan/?limit=200`)
    if (res.ok) {
      announcedServices.value = await res.json()
    }
  } catch (error) {
    console.warn('Gagal memuat data informasi pelayanan:', error)
  } finally {
    isServicesLoading.value = false
  }
}

const filteredAnnouncedServices = computed(() => {
  return announcedServices.value.filter(item => {
    const matchesBranch = selectedBranchFilter.value === 'Semua' || 
      item.church_name === selectedBranchFilter.value ||
      item.church_admin_id === Number(selectedBranchFilter.value)

    const matchesCat = selectedServiceCategory.value === 'Semua' || item.category === selectedServiceCategory.value

    const q = serviceSearchQuery.value.trim().toLowerCase()
    const matchesSearch = !q ||
      (item.service_name && item.service_name.toLowerCase().includes(q)) ||
      (item.church_name && item.church_name.toLowerCase().includes(q)) ||
      (item.city && item.city.toLowerCase().includes(q)) ||
      (item.description && item.description.toLowerCase().includes(q)) ||
      (item.pic_name && item.pic_name.toLowerCase().includes(q)) ||
      (item.location_room && item.location_room.toLowerCase().includes(q))

    return matchesBranch && matchesCat && matchesSearch
  })
})

const churchAnnouncedServices = computed(() => {
  if (!selectedChurchDetail.value) return []
  const ch = selectedChurchDetail.value
  const branchId = ch.source === 'branch' ? ch.dbData?.id : null
  const churchId = ch.source === 'church' ? ch.dbData?.id : null
  const churchName = (ch.name || '').toLowerCase()

  return announcedServices.value.filter(s => {
    if (branchId && s.church_admin_id === branchId) return true
    if (churchId && s.church_id === churchId) return true
    if (churchName && s.church_name && s.church_name.toLowerCase() === churchName) return true
    return false
  })
})

const openAnnouncementDetail = (item) => {
  selectedAnnouncementDetail.value = item
}

const closeAnnouncementDetail = () => {
  selectedAnnouncementDetail.value = null
}

const cleanPhone = (phone) => {
  if (!phone) return ''
  let cleaned = phone.replace(/[^0-9]/g, '')
  if (cleaned.startsWith('0')) {
    cleaned = '62' + cleaned.slice(1)
  }
  return cleaned
}

const normalizeApiChurch = (item, source = 'branch') => {
  const latitude = Number(item.latitude)
  const longitude = Number(item.longitude)

  const baseName = item.church_name || item.name || 'Cabang Gereja'
  const cityName = item.city || 'Indonesia'

  return {
    id: `branch-${item.id}`,
    numericId: item.id,
    source: 'branch',
    name: baseName,
    church_code: item.church_code || '',
    denomination: item.denomination || detectDenomination(baseName),
    verified: true,
    cmsIntegrated: true,
    isLive: Boolean(item.is_live || false),
    rating: 4.8,
    reviewsCount: 32,
    image: item.image || 'https://images.unsplash.com/photo-1548625361-1854589d8161?auto=format&fit=crop&w=800&q=80',
    city: cityName,
    address: item.address || 'Alamat belum tercatat',
    distance: 'Cabang Terdaftar',
    coordinates: {
      lat: Number.isFinite(latitude) ? latitude : -0.9540,
      lng: Number.isFinite(longitude) ? longitude : 100.3530
    },
    schedules: [
      { name: 'Ibadah Raya Mingguan', time: 'Minggu (Cek Jadwal Cabang)', room: 'Gedung Cabang' }
    ],
    categories: ['Jadwal Ibadah', 'Pelayanan Cabang Gereja'],
    facilities: ['Lokasi Terverifikasi', 'Admin Cabang Aktif', 'Terintegrasi CMS'],
    contacts: {
      phone: item.phone || '(Belum tersedia)',
      whatsapp: item.phone || item.whatsapp || '-',
      email: item.email || '-',
      website: item.google_maps_url || `https://www.google.com/maps?q=${latitude},${longitude}`
    },
    pastors: item.admin_name || 'Admin & Tim Pastoral Cabang',
    vision: item.vision || 'Cabang persekutuan jemaat yang setia bertumbuh dalam iman dan melayani sesama.',
    activeMinistries: [
      { name: 'Pelayanan Cabang', desc: 'Pelayanan aktif terdaftar di sistem CMS cabang gereja.' }
    ],
    dbData: item
  }
}

const loadDatabaseChurches = async () => {
  try {
    const branchRes = await fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/?limit=200`)

    if (branchRes.ok) {
      const branchData = await branchRes.json()
      rawBranchesList.value = branchData

      const liveBranches = []
      branchData.forEach((item) => {
        if (item.latitude && item.longitude) {
          liveBranches.push(normalizeApiChurch(item, 'branch'))
        }
      })

      if (liveBranches.length > 0) {
        churches.value = liveBranches
        dbBranches.value = liveBranches
      }
    }
  } catch (error) {
    console.warn('Gagal memuat data cabang gereja dari database:', error)
  }
}

// --- State UI ---
const searchQuery = ref('')
const selectedCategory = ref('Semua')
const selectedDenomination = ref('Semua')
const selectedCity = ref('Semua')
const viewMode = ref('grid') // 'grid' | 'split'
const isSearchFocused = ref(false)
const selectedChurchDetail = ref(null)
const modalActiveTab = ref('overview')

// --- Map Specific State ---
const mapContainer = ref(null)
const modalMapContainer = ref(null)
let leafletMap = null
let modalLeafletMap = null
let activeMarkers = {}
let modalActiveMarkers = {}
let radiusCircleOverlay = null
let userMarkerOverlay = null

const { isDark } = useTheme()
const pageThemeClass = computed(() => (isDark.value ? 'theme-dark-page' : 'theme-light-page'))
const activeTileLayer = ref(isDark.value ? 'dark' : 'light') // 'dark' | 'street' | 'light'
const selectedRadiusKm = ref(0) // 0 (off), 2, 5, 10, 15
const isLocatingUser = ref(false)
const userLocation = ref(null)
const isFullscreenMapOpen = ref(false)
const activeMapHoverId = ref(null)
const mapHUDCoords = ref({ lat: '-7.2575', lng: '112.7521' })
const mapHUDZoom = ref(12)

const TILE_LAYERS = {
  dark: {
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    name: 'Dark Slate (Presisi)'
  },
  street: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    name: 'Street View'
  },
  light: {
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; CARTO',
    name: 'Light Vector'
  }
}

// Filter Lists
const categoriesList = [
  'Semua', 
  'Jadwal Ibadah', 
  'Pelayanan Pemuda', 
  'Live Streaming', 
  'Diakonia & Sosial', 
  'Komunitas Sel', 
  'Katekisasi & Pembinaan',
  'Konseling'
]

const denominationsList = computed(() => {
  const set = new Set()
  churches.value.forEach(c => {
    if (c.denomination) set.add(c.denomination)
  })
  return ['Semua', ...Array.from(set).sort()]
})

const citiesList = computed(() => {
  const set = new Set()
  churches.value.forEach(c => {
    if (c.city) set.add(c.city)
  })
  return ['Semua', ...Array.from(set).sort()]
})

// Autocomplete Suggestions
const searchSuggestions = computed(() => {
  if (!searchQuery.value.trim()) return []
  const q = searchQuery.value.toLowerCase()
  const matches = []
  
  churches.value.forEach(c => {
    if (c.name && c.name.toLowerCase().includes(q)) matches.push({ type: 'Gereja', text: c.name, icon: 'bi-church' })
    if (c.denomination && c.denomination.toLowerCase().includes(q)) matches.push({ type: 'Denominasi', text: c.denomination, icon: 'bi-bookmark-star' })
    if (c.city && c.city.toLowerCase().includes(q)) matches.push({ type: 'Kota', text: `Gereja di ${c.city}`, icon: 'bi-geo-alt' })
    if (Array.isArray(c.categories)) {
      c.categories.forEach(cat => {
        if (cat.toLowerCase().includes(q) && !matches.some(m => m.text === cat)) {
          matches.push({ type: 'Kategori Pelayanan', text: cat, icon: 'bi-tag' })
        }
      })
    }
  })
  
  return matches.slice(0, 5)
})

// Filtered Churches
const filteredChurches = computed(() => {
  return churches.value.filter(c => {
    const query = searchQuery.value.toLowerCase().trim()
    const matchesSearch = !query || 
      c.name.toLowerCase().includes(query) ||
      c.denomination.toLowerCase().includes(query) ||
      c.city.toLowerCase().includes(query) ||
      c.address.toLowerCase().includes(query) ||
      c.categories.some(cat => cat.toLowerCase().includes(query))

    const matchesCategory = selectedCategory.value === 'Semua' || c.categories.includes(selectedCategory.value)
    const matchesDenomination = selectedDenomination.value === 'Semua' || c.denomination.includes(selectedDenomination.value)
    const matchesCity = selectedCity.value === 'Semua' || c.city === selectedCity.value

    return matchesSearch && matchesCategory && matchesDenomination && matchesCity
  })
})

function selectSuggestion(text) {
  searchQuery.value = text.replace('Gereja di ', '')
  isSearchFocused.value = false
}

function openChurchModal(church) {
  selectedChurchDetail.value = church
  modalActiveTab.value = 'overview'
}

function closeChurchModal() {
  selectedChurchDetail.value = null
}

// ================= LEAFLET MAP ENGINE ================= //

function createCustomPinHtml(church, isSelected = false) {
  const isLive = church.isLive
  const liveBadge = isLive 
    ? `<span class="absolute -top-1 -right-1 flex h-3.5 w-3.5">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-3.5 w-3.5 bg-red-600 border border-white"></span>
       </span>`
    : ''

  return `
    <div class="group/pin cursor-pointer transform -translate-x-1/2 -translate-y-full transition-all duration-300 ${isSelected ? 'scale-125 z-50' : 'hover:scale-110'}">
      <div class="flex flex-col items-center">
        <div class="mb-1 px-2.5 py-1 rounded-xl bg-slate-950/90 border border-amber-400/70 text-[10px] font-bold text-amber-300 font-serif whitespace-nowrap shadow-2xl backdrop-blur-md flex items-center gap-1.5">
          <i class="bi bi-church text-amber-400"></i>
          <span>${church.name}</span>
        </div>
        <div class="relative w-9 h-9 rounded-full bg-gradient-to-br from-amber-400 via-amber-500 to-amber-600 text-slate-950 flex items-center justify-center shadow-lg shadow-amber-500/40 border-2 border-slate-950 font-bold">
          <i class="bi bi-pin-map-fill text-base"></i>
          ${liveBadge}
        </div>
        <div class="w-2 h-2 bg-amber-400 rotate-45 -mt-1.5 border-r border-b border-slate-950"></div>
      </div>
    </div>
  `
}

function createPopupHtml(church) {
  return `
    <div class="p-3 bg-slate-950 text-slate-100 rounded-2xl border border-amber-500/40 w-64 shadow-2xl space-y-2 font-sans">
      <div class="relative h-24 rounded-xl overflow-hidden bg-slate-900">
        <img src="${church.image}" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent"></div>
        <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-slate-950/80 text-[10px] font-serif text-amber-300 border border-amber-500/30">
          ${church.denomination}
        </div>
      </div>

      <div class="space-y-1">
        <div class="flex justify-between items-center text-[10px]">
          <span class="text-amber-400 font-bold flex items-center gap-1">
            <i class="bi bi-star-fill text-amber-400"></i> ${church.rating} (${church.reviewsCount})
          </span>
          <span class="text-slate-400"><i class="bi bi-geo-alt"></i> ${church.distance}</span>
        </div>

        <h4 class="font-serif font-bold text-xs text-white leading-tight">${church.name}</h4>
        <p class="text-[11px] text-slate-300 truncate"><i class="bi bi-pin-map text-amber-400"></i> ${church.address}</p>
      </div>

      <div class="pt-1 flex gap-2">
        <button 
          onclick="window.dispatchEvent(new CustomEvent('open-church-modal', { detail: ${church.id} }))" 
          class="flex-1 py-1.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-xl text-[11px] shadow-md transition-all text-center"
        >
          Lihat Detail
        </button>
        <a 
          href="https://maps.google.com/?q=${church.coordinates.lat},${church.coordinates.lng}" 
          target="_blank" 
          class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-xl text-[11px] border border-amber-500/30 flex items-center justify-center transition-colors"
          title="Google Maps"
        >
          <i class="bi bi-compass"></i>
        </a>
      </div>
    </div>
  `
}

function initMapInstance(containerEl, isModal = false) {
  if (!containerEl) return null

  const centerCoords = CITY_CENTERS[selectedCity.value] || CITY_CENTERS.Surabaya
  const map = L.map(containerEl, {
    center: [centerCoords.lat, centerCoords.lng],
    zoom: 12,
    zoomControl: false
  })

  // Add tile layer
  const layerConfig = TILE_LAYERS[activeTileLayer.value] || TILE_LAYERS.dark
  L.tileLayer(layerConfig.url, {
    attribution: layerConfig.attribution,
    maxZoom: 19
  }).addTo(map)

  // Zoom control top right
  L.control.zoom({ position: 'topright' }).addTo(map)

  // Map HUD tracker
  map.on('move', () => {
    const center = map.getCenter()
    mapHUDCoords.value = {
      lat: center.lat.toFixed(4),
      lng: center.lng.toFixed(4)
    }
    mapHUDZoom.value = map.getZoom()
  })

  return map
}

function renderMarkersOnMap(mapInstance, isModal = false) {
  if (!mapInstance) return

  const targetMarkers = isModal ? modalActiveMarkers : activeMarkers

  // Clear existing markers
  Object.values(targetMarkers).forEach(m => m.remove())
  if (isModal) modalActiveMarkers = {}
  else activeMarkers = {}

  const bounds = L.latLngBounds()

  // Add markers for filtered churches
  filteredChurches.value.forEach(church => {
    const coords = [church.coordinates.lat, church.coordinates.lng]
    bounds.extend(coords)

    const pinIcon = L.divIcon({
      html: createCustomPinHtml(church),
      className: 'custom-leaflet-div-icon',
      iconSize: [120, 60],
      iconAnchor: [60, 60]
    })

    const marker = L.marker(coords, { icon: pinIcon })
      .addTo(mapInstance)
      .bindPopup(createPopupHtml(church), {
        className: 'custom-leaflet-popup',
        closeButton: false,
        maxWidth: 280
      })

    marker.on('click', () => {
      activeMapHoverId.value = church.id
    })

    if (isModal) modalActiveMarkers[church.id] = marker
    else activeMarkers[church.id] = marker
  })

  // Auto fit map bounds if markers exist
  if (filteredChurches.value.length > 0 && bounds.isValid()) {
    mapInstance.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 })
  }

  // Render Radius Circle Overlay if enabled
  updateRadiusOverlay(mapInstance)
}

function updateRadiusOverlay(mapInstance) {
  if (!mapInstance) return

  if (radiusCircleOverlay) {
    radiusCircleOverlay.remove()
    radiusCircleOverlay = null
  }

  if (selectedRadiusKm.value > 0) {
    const center = userLocation.value 
      ? [userLocation.value.lat, userLocation.value.lng]
      : (CITY_CENTERS[selectedCity.value] ? [CITY_CENTERS[selectedCity.value].lat, CITY_CENTERS[selectedCity.value].lng] : [-7.2575, 112.7521])

    radiusCircleOverlay = L.circle(center, {
      radius: selectedRadiusKm.value * 1000,
      color: '#f59e0b',
      fillColor: '#f59e0b',
      fillOpacity: 0.12,
      weight: 1.5,
      dashArray: '4, 8'
    }).addTo(mapInstance)
  }
}

function switchTileLayer(layerKey) {
  activeTileLayer.value = layerKey
  const layerConfig = TILE_LAYERS[layerKey]

  const updateLayerForMap = (m) => {
    if (!m) return
    m.eachLayer(layer => {
      if (layer instanceof L.TileLayer) {
        m.removeLayer(layer)
      }
    })
    L.tileLayer(layerConfig.url, {
      attribution: layerConfig.attribution,
      maxZoom: 19
    }).addTo(m)
  }

  updateLayerForMap(leafletMap)
  updateLayerForMap(modalLeafletMap)
}

watch(isDark, (newVal) => {
  const nextLayer = newVal ? 'dark' : 'light'
  activeTileLayer.value = nextLayer
  switchTileLayer(nextLayer)
})

function flyToChurchLocation(church) {
  if (viewMode.value !== 'split') {
    viewMode.value = 'split'
  }

  activeMapHoverId.value = church.id

  nextTick(() => {
    if (leafletMap) {
      leafletMap.flyTo([church.coordinates.lat, church.coordinates.lng], 15, {
        animate: true,
        duration: 1.2
      })

      const marker = activeMarkers[church.id]
      if (marker) {
        setTimeout(() => marker.openPopup(), 1200)
      }
    }
  })
}

function locateUserPosition() {
  if (!navigator.geolocation) {
    alert('Browser Anda tidak mendukung deteksi lokasi Geolocation.')
    return
  }

  isLocatingUser.value = true

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      isLocatingUser.value = false
      const lat = pos.coords.latitude
      const lng = pos.coords.longitude
      userLocation.value = { lat, lng }

      if (userMarkerOverlay) userMarkerOverlay.remove()

      const userPinIcon = L.divIcon({
        html: `
          <div class="relative flex items-center justify-center">
            <span class="animate-ping absolute inline-flex h-8 w-8 rounded-full bg-sky-400 opacity-75"></span>
            <div class="w-5 h-5 rounded-full bg-sky-500 border-2 border-white shadow-xl flex items-center justify-center text-white text-[10px]">
              <i class="bi bi-person-fill"></i>
            </div>
          </div>
        `,
        className: 'user-pin-div-icon',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      })

      if (leafletMap) {
        userMarkerOverlay = L.marker([lat, lng], { icon: userPinIcon }).addTo(leafletMap)
        leafletMap.flyTo([lat, lng], 14)
      }
    },
    (err) => {
      isLocatingUser.value = false
      alert('Gagal mendeteksi lokasi Anda. Pastikan izin akses lokasi telah diaktifkan.')
    },
    { enableHighAccuracy: true }
  )
}

import { useRoute } from 'vue-router'

const route = useRoute()

function handleAnchorScroll(hash) {
  if (!hash) return
  if (hash === '#details' || hash === '#map-section' || hash === '#map') {
    viewMode.value = 'split'
    nextTick(() => {
      setTimeout(() => {
        const el = document.getElementById('map-section') || document.getElementById('details') || document.getElementById('info')
        if (el) {
          const yOffset = -90
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset
          window.scrollTo({ top: y, behavior: 'smooth' })
        }
      }, 150)
    })
  } else if (hash === '#info' || hash === '#information') {
    nextTick(() => {
      setTimeout(() => {
        const el = document.getElementById('info')
        if (el) {
          const yOffset = -90
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset
          window.scrollTo({ top: y, behavior: 'smooth' })
        }
      }, 100)
    })
  }
}

// Handle global custom event from leaflet popups and navbar anchor links
onMounted(() => {
  nextTick(() => {
    try {
      AOS.refresh()
    } catch (e) {
      // Safe fallback
    }
  })

  loadDatabaseChurches()
  loadAnnouncedServices()

  window.addEventListener('open-church-modal', (e) => {
    const churchId = e.detail
    const target = churches.value.find(c => c.id === churchId)
    if (target) openChurchModal(target)
  })

  window.addEventListener('nav-hash-scroll', (e) => {
    handleAnchorScroll(e.detail)
  })

  if (route.hash) {
    handleAnchorScroll(route.hash)
  }
})

watch(() => route.hash, (newHash) => {
  if (newHash) handleAnchorScroll(newHash)
})

// Watchers
watch(viewMode, (newVal) => {
  if (newVal === 'split') {
    nextTick(() => {
      if (!leafletMap && mapContainer.value) {
        leafletMap = initMapInstance(mapContainer.value)
      }
      if (leafletMap) {
        leafletMap.invalidateSize()
        renderMarkersOnMap(leafletMap, false)
      }
    })
  }
})

watch(filteredChurches, () => {
  nextTick(() => {
    if (leafletMap) renderMarkersOnMap(leafletMap, false)
    if (modalLeafletMap) renderMarkersOnMap(modalLeafletMap, true)
  })
})

watch(selectedCity, (newCity) => {
  const coords = CITY_CENTERS[newCity]
  if (coords) {
    if (leafletMap) leafletMap.flyTo([coords.lat, coords.lng], 12)
    if (modalLeafletMap) modalLeafletMap.flyTo([coords.lat, coords.lng], 12)
  }
})

watch(selectedRadiusKm, () => {
  if (leafletMap) updateRadiusOverlay(leafletMap)
  if (modalLeafletMap) updateRadiusOverlay(modalLeafletMap)
})

watch(isFullscreenMapOpen, (open) => {
  if (open) {
    nextTick(() => {
      if (!modalLeafletMap && modalMapContainer.value) {
        modalLeafletMap = initMapInstance(modalMapContainer.value, true)
      }
      if (modalLeafletMap) {
        modalLeafletMap.invalidateSize()
        renderMarkersOnMap(modalLeafletMap, true)
      }
    })
  }
})

onUnmounted(() => {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
  }
  if (modalLeafletMap) {
    modalLeafletMap.remove()
    modalLeafletMap = null
  }
})
</script>


<template>
  <InformasiPelayananLayout>
    <div :class="['informasi-pelayanan-page', pageThemeClass, 'py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-10']">

      <!-- ================= HERO SEARCH SECTION (GOLD & SLATE THEME) ================= -->
      <section class="relative text-center py-10 px-4 rounded-3xl bg-slate-900 border border-amber-500/30 shadow-2xl backdrop-blur-xl overflow-hidden" data-aos="fade-up">
        <!-- Ambient Gold Glow -->
        <div class="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 max-w-3xl mx-auto space-y-4" id="home">
          <!-- Header Badge -->
          <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold tracking-wider uppercase font-serif">
            <i class="bi bi-search text-amber-400"></i>
            Pusat Informasi & Klasifikasi Pelayanan Cabang Gereja
          </div>

          <!-- Title -->
          <h1 class="font-serif text-3xl sm:text-5xl font-extrabold tracking-wide text-amber-300 leading-tight">
            Temukan Informasi & Jadwal Ibadah Cabang Gereja
          </h1>
          <p class="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto font-sans leading-relaxed">
            Cari jadwal ibadah, lokasi, pelayanan diakonia, dan profil dari cabang gereja terdaftar di sistem CMS.
          </p>

          <!-- GOOGLE-STYLE SEARCH BAR -->
          <div class="relative mt-8 max-w-2xl mx-auto text-left">
            <div 
              class="flex items-center bg-slate-950 border transition-all duration-300 rounded-full px-5 py-3.5 shadow-2xl relative z-20"
              :class="isSearchFocused ? 'border-amber-400 ring-4 ring-amber-500/20' : 'border-amber-500/30 hover:border-amber-500/60'"
            >
              <i class="bi bi-search text-xl text-amber-400 mr-3"></i>

              <input 
                v-model="searchQuery"
                @focus="isSearchFocused = true"
                @blur="setTimeout(() => isSearchFocused = false, 200)"
                type="text" 
                placeholder="Cari cabang gereja (contoh: GKPM Padang, GKI Harapan Indah, GBI Grace)..."
                class="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm sm:text-base focus:outline-none"
              />

              <button 
                v-if="searchQuery" 
                @click="searchQuery = ''"
                class="text-slate-400 hover:text-white mr-3 transition-colors p-1"
              >
                <i class="bi bi-x-circle-fill text-lg"></i>
              </button>

              <button 
                class="bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold px-5 py-2.5 rounded-full text-xs sm:text-sm transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5 shrink-0"
              >
                <i class="bi bi-compass"></i>
                <span>Cari</span>
              </button>
            </div>

            <!-- Autocomplete Suggestions -->
            <Transition name="fade">
              <div 
                v-if="isSearchFocused && searchSuggestions.length > 0"
                class="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-amber-500/30 rounded-2xl shadow-2xl overflow-hidden z-30 divide-y divide-slate-800"
              >
                <div 
                  v-for="(sug, idx) in searchSuggestions" 
                  :key="idx"
                  @click="selectSuggestion(sug.text)"
                  class="px-5 py-3 hover:bg-slate-800 cursor-pointer flex items-center justify-between transition-colors text-sm text-slate-200"
                >
                  <div class="flex items-center gap-3">
                    <i :class="['bi', sug.icon, 'text-amber-400']"></i>
                    <span>{{ sug.text }}</span>
                  </div>
                  <span class="text-xs text-amber-300 px-2 py-0.5 rounded bg-slate-800 border border-amber-500/30 font-serif">{{ sug.type }}</span>
                </div>
              </div>
            </Transition>
          </div>

          <!-- Quick Category Chips -->
          <div class="pt-4 flex flex-wrap justify-center items-center gap-2 max-w-3xl mx-auto">
            <button 
              v-for="cat in categoriesList" 
              :key="cat"
              @click="selectedCategory = cat"
              :class="[
                'px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200 flex items-center gap-1.5',
                selectedCategory === cat 
                  ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-bold shadow-md shadow-amber-500/20 scale-105' 
                  : 'bg-slate-800 text-slate-300 border border-amber-500/20 hover:border-amber-400 hover:text-amber-300'
              ]"
            >
              <i v-if="cat === 'Semua'" class="bi bi-grid-fill text-xs"></i>
              <i v-else-if="cat === 'Jadwal Ibadah'" class="bi bi-clock-history"></i>
              <i v-else-if="cat === 'Live Streaming'" class="bi bi-broadcast"></i>
              <i v-else-if="cat === 'Pelayanan Pemuda'" class="bi bi-lightning-charge"></i>
              <i v-else class="bi bi-tag"></i>
              <span>{{ cat }}</span>
            </button>
          </div>
        </div>
      </section>

      <!-- ================= SEKSI PEMBERITAHUAN PELAYANAN CABANG GEREJA (DATABASE POSTGRESQL) ================= -->
      <section id="pelayanan-cabang" class="space-y-6" data-aos="fade-up">
        
        <!-- Header & Banner Seksi -->
        <div class="relative bg-slate-900 border border-amber-500/30 rounded-3xl p-6 sm:p-8 shadow-2xl overflow-hidden backdrop-blur-xl">
          <div class="absolute -right-16 -bottom-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

          <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-[11px] font-semibold tracking-wider uppercase mb-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Basis Data PostgreSQL Terintegrasi Real-Time</span>
              </div>
              <h2 class="font-serif text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2.5">
                <i class="bi bi-broadcast-pin text-amber-400"></i>
                <span>Informasi & Pemberitahuan Pelayanan Cabang Gereja</span>
              </h2>
              <p class="text-xs sm:text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
                Pemberitahuan jadwal ibadah, persekutuan, konseling, dan kegiatan sosial yang diadakan oleh tiap-tiap cabang gereja terdaftar di sistem ini.
              </p>
            </div>

            <div class="flex items-center gap-2 shrink-0">
              <button 
                @click="loadAnnouncedServices" 
                :disabled="isServicesLoading"
                class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-500/30 text-xs font-semibold flex items-center gap-1.5 transition"
                title="Segarkan data dari database"
              >
                <i :class="['bi', isServicesLoading ? 'bi-arrow-repeat animate-spin' : 'bi-arrow-clockwise']"></i>
                <span>Segarkan Data</span>
              </button>
            </div>
          </div>

          <!-- Role Banner (Admin Cabang & Admin Utama Notifikasi) -->
          <div v-if="isChurchAdmin" class="mt-4 p-3.5 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div class="flex items-center gap-2.5 text-amber-300">
              <i class="bi bi-patch-check-fill text-amber-400 text-lg shrink-0"></i>
              <span>Anda masuk sebagai <strong>Admin Cabang ({{ user?.church_name || user?.full_name || 'Gereja Anda' }})</strong>. Anda dapat menerbitkan, mengedit, atau menghapus jadwal dan pelayanan cabang Anda langsung ke database.</span>
            </div>
            <RouterLink 
              to="/dashboard-church" 
              class="px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-xl whitespace-nowrap shadow-md transition flex items-center justify-center gap-1.5"
            >
              <i class="bi bi-pencil-square"></i>
              <span>Kelola Pelayanan Cabang</span>
            </RouterLink>
          </div>

          <div v-else-if="isMainAdmin" class="mt-4 p-3.5 bg-cyan-500/10 border border-cyan-500/30 rounded-2xl flex items-center justify-between gap-3 text-xs text-cyan-300">
            <div class="flex items-center gap-2.5">
              <i class="bi bi-eye-fill text-cyan-400 text-lg shrink-0"></i>
              <span><strong>Mode Admin Utama:</strong> Menampilkan monitoring seluruh pemberitahuan pelayanan yang diterbitkan oleh masing-masing cabang gereja di sistem.</span>
            </div>
            <span class="px-3 py-1 bg-cyan-950 border border-cyan-500/40 rounded-xl font-mono text-[11px] font-bold text-cyan-300 shrink-0">
              {{ announcedServices.length }} Data Aktif
            </span>
          </div>

          <!-- Toolbar Filter & Pencarian Pelayanan Cabang -->
          <div class="mt-6 pt-5 border-t border-slate-800 grid grid-cols-1 md:grid-cols-12 gap-3.5 items-center">
            
            <!-- Filter Dropdown Cabang Gereja -->
            <div class="md:col-span-4">
              <label class="block text-[11px] text-slate-400 mb-1 font-semibold">
                <i class="bi bi-building text-amber-400 mr-1"></i> Cabang Gereja:
              </label>
              <select 
                v-model="selectedBranchFilter" 
                class="w-full bg-slate-950 border border-amber-500/30 text-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-amber-400"
              >
                <option value="Semua">Semua Cabang Gereja Terdaftar ({{ rawBranchesList.length }} Cabang)</option>
                <option v-for="b in rawBranchesList" :key="b.id" :value="b.church_name">
                  {{ b.church_name }} ({{ b.city || 'Cabang' }})
                </option>
              </select>
            </div>

            <!-- Filter Kategori Pelayanan -->
            <div class="md:col-span-3">
              <label class="block text-[11px] text-slate-400 mb-1 font-semibold">
                <i class="bi bi-tag text-amber-400 mr-1"></i> Kategori Pelayanan:
              </label>
              <select 
                v-model="selectedServiceCategory" 
                class="w-full bg-slate-950 border border-amber-500/30 text-slate-200 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-amber-400"
              >
                <option v-for="c in serviceCategoriesList" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>

            <!-- Pencarian Cepat -->
            <div class="md:col-span-5">
              <label class="block text-[11px] text-slate-400 mb-1 font-semibold">
                <i class="bi bi-search text-amber-400 mr-1"></i> Cari Pelayanan / Lokasi / PIC:
              </label>
              <div class="relative">
                <input 
                  v-model="serviceSearchQuery" 
                  type="text" 
                  placeholder="Cari contoh: Ibadah Pemuda, Diakonia, Ruang Serbaguna..."
                  class="w-full bg-slate-950 border border-amber-500/30 text-slate-200 rounded-xl px-3.5 py-2 pr-9 text-xs focus:outline-none focus:border-amber-400 placeholder-slate-500"
                />
                <button 
                  v-if="serviceSearchQuery" 
                  @click="serviceSearchQuery = ''"
                  class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  <i class="bi bi-x-circle-fill text-xs"></i>
                </button>
              </div>
            </div>

          </div>

          <!-- Loading Indicator -->
          <div v-if="isServicesLoading" class="text-center py-12">
            <div class="w-10 h-10 border-2 border-amber-400 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p class="text-xs text-slate-400 font-serif">Menghubungkan ke database dan memuat informasi pelayanan...</p>
          </div>

          <!-- EMPTY STATE: Belum Ada Data di Database -->
          <div 
            v-else-if="filteredAnnouncedServices.length === 0" 
            class="mt-6 text-center py-12 px-4 bg-slate-950/70 border border-amber-500/20 rounded-2xl space-y-4"
          >
            <div class="w-16 h-16 rounded-full bg-slate-900 border border-amber-500/30 text-amber-400 flex items-center justify-center mx-auto text-2xl shadow-xl shadow-amber-500/10">
              <i class="bi bi-megaphone"></i>
            </div>
            
            <div class="max-w-xl mx-auto space-y-2">
              <h3 class="font-serif text-lg font-bold text-amber-300">
                Belum Ada Informasi Pelayanan yang Diterbitkan Cabang Gereja
              </h3>
              <p class="text-xs text-slate-400 leading-relaxed">
                Tabel database PostgreSQL <code class="px-2 py-0.5 rounded bg-slate-900 text-amber-300 border border-amber-500/20 font-mono">informasi_pelayanan</code> telah terhubung dan aktif di server. Sesuai prosedur, data saat ini masih kosong (0 baris) karena menunggu pengisian resmi oleh masing-masing Admin Cabang Gereja terdaftar.
              </p>
            </div>

            <!-- Status Badges -->
            <div class="flex flex-wrap items-center justify-center gap-2 text-[11px] pt-1">
              <span class="px-3 py-1 rounded-full bg-slate-900 border border-amber-500/20 text-slate-300 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                Tabel DBMS: <strong class="text-amber-300 font-mono">informasi_pelayanan</strong>
              </span>
              <span class="px-3 py-1 rounded-full bg-slate-900 border border-amber-500/20 text-slate-300 flex items-center gap-1.5">
                <i class="bi bi-database text-amber-400"></i>
                Total Data: <strong class="text-amber-300">0 Pelayanan</strong>
              </span>
              <span class="px-3 py-1 rounded-full bg-slate-900 border border-amber-500/20 text-slate-300 flex items-center gap-1.5">
                <i class="bi bi-building-check text-amber-400"></i>
                Cabang Terdaftar: <strong class="text-amber-300">{{ rawBranchesList.length }} Cabang</strong>
              </span>
            </div>

            <!-- Action button for admin -->
            <div class="pt-2 flex flex-wrap justify-center gap-3">
              <RouterLink 
                to="/dashboard-church" 
                class="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-xl text-xs transition shadow-lg shadow-amber-500/20 flex items-center gap-2"
              >
                <i class="bi bi-plus-circle-fill"></i>
                <span>Buka Dashboard Admin Cabang untuk Mengisi Data</span>
              </RouterLink>

              <button 
                v-if="selectedBranchFilter !== 'Semua' || selectedServiceCategory !== 'Semua' || serviceSearchQuery"
                @click="selectedBranchFilter = 'Semua'; selectedServiceCategory = 'Semua'; serviceSearchQuery = '';"
                class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-semibold transition"
              >
                Reset Filter Pencarian
              </button>
            </div>
          </div>

          <!-- POPULATED STATE: Daftar Kartu Pelayanan Terisi -->
          <div v-else class="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <div 
              v-for="item in filteredAnnouncedServices" 
              :key="item.id"
              class="bg-slate-950/90 border border-amber-500/30 hover:border-amber-400/80 rounded-2xl p-5 flex flex-col justify-between shadow-xl transition-all duration-300 hover:shadow-amber-950/40 hover:-translate-y-1 space-y-4"
            >
              <!-- Card Header -->
              <div class="space-y-2">
                <div class="flex items-center justify-between gap-2">
                  <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    {{ item.category }}
                  </span>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    {{ item.status || 'Aktif' }}
                  </span>
                </div>

                <div>
                  <h4 class="font-serif text-base font-bold text-white leading-snug">
                    {{ item.service_name }}
                  </h4>
                  <p class="text-xs text-amber-400 flex items-center gap-1 mt-1 font-serif">
                    <i class="bi bi-building text-amber-400"></i>
                    <span>{{ item.church_name }}</span>
                    <span v-if="item.city" class="text-slate-400">({{ item.city }})</span>
                  </p>
                </div>
              </div>

              <!-- Metadata Pills -->
              <div class="space-y-1.5 text-xs text-slate-300">
                <div class="flex items-center gap-2 text-amber-300 font-medium">
                  <i class="bi bi-clock-history text-amber-400"></i>
                  <span>{{ item.schedule_day || 'Minggu' }} • {{ item.schedule_time || 'Jadwal Reguler' }}</span>
                </div>

                <div v-if="item.location_room" class="flex items-center gap-2 text-slate-400 text-[11px]">
                  <i class="bi bi-geo-alt text-amber-400"></i>
                  <span>{{ item.location_room }}</span>
                </div>

                <div v-if="item.target_audience" class="flex items-center gap-2 text-slate-400 text-[11px]">
                  <i class="bi bi-people text-amber-400"></i>
                  <span>Target: {{ item.target_audience }}</span>
                </div>
              </div>

              <!-- Description -->
              <p v-if="item.description" class="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                {{ item.description }}
              </p>

              <!-- Card Footer & Actions -->
              <div class="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                <div class="text-[11px] text-slate-400 truncate">
                  <i class="bi bi-person-badge text-amber-400 mr-1"></i>
                  <span>{{ item.pic_name || 'Admin Cabang' }}</span>
                </div>

                <div class="flex items-center gap-1.5 shrink-0">
                  <a 
                    v-if="item.pic_contact" 
                    :href="'https://wa.me/' + cleanPhone(item.pic_contact)" 
                    target="_blank"
                    class="p-2 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs transition"
                    title="Hubungi WhatsApp"
                  >
                    <i class="bi bi-whatsapp"></i>
                  </a>

                  <button 
                    @click="openAnnouncementDetail(item)"
                    class="px-3 py-1.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-xl text-xs transition shadow-sm"
                  >
                    Detail
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- ================= MAIN LAYOUT & CONTROLS ================= -->
      <div class="space-y-6">

        <!-- Bar Filter & View Switcher -->
        <div data-aos="fade-up" id="info" data-aos-delay="100" class="bg-slate-900 border border-amber-500/30 rounded-2xl p-4 sm:p-5 flex flex-col md:flex-row justify-between items-center gap-4 shadow-xl">
          
          <!-- Count Info -->
          <div class="flex items-center gap-3 text-xs sm:text-sm text-slate-300 w-full md:w-auto justify-between md:justify-start">
            <span class="font-semibold text-white flex items-center gap-2">
              <i class="bi bi-building-check text-amber-400"></i>
              Ditemukan <strong class="text-amber-300 text-base font-serif">{{ filteredChurches.length }}</strong> Cabang Gereja Terdaftar
            </span>
            <span v-if="selectedCategory !== 'Semua'" class="text-xs px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300">
              Kategori: {{ selectedCategory }}
            </span>
          </div>

          <!-- Filters & View Switcher -->
          <div class="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end" id="details">
            
            <!-- Denominasi Select -->
            <div class="flex items-center gap-1.5 text-xs text-slate-300">
              <i class="bi bi-diagram-3 text-amber-400"></i>
              <select 
                v-model="selectedDenomination" 
                class="bg-slate-800 border border-amber-500/30 text-slate-200 rounded-xl px-3 py-1.5 focus:outline-none focus:border-amber-400 text-xs"
              >
                <option value="Semua">Semua Denominasi Cabang</option>
                <option v-for="d in denominationsList.filter(x => x !== 'Semua')" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>

            <!-- Kota Select -->
            <div class="flex items-center gap-1.5 text-xs text-slate-300">
              <i class="bi bi-geo-alt text-amber-400"></i>
              <select 
                v-model="selectedCity" 
                class="bg-slate-800 border border-amber-500/30 text-slate-200 rounded-xl px-3 py-1.5 focus:outline-none focus:border-amber-400 text-xs"
              >
                <option value="Semua">Semua Kota Cabang</option>
                <option v-for="c in citiesList.filter(x => x !== 'Semua')" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>

            <!-- View Switcher -->
            <div class="bg-slate-800 p-1 rounded-xl border border-amber-500/30 flex items-center space-x-1">
              <button 
                @click="viewMode = 'grid'" 
                :class="['px-3 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1', viewMode === 'grid' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-white']"
              >
                <i class="bi bi-grid-3x3-gap-fill"></i>
                <span class="hidden sm:inline">Grid</span>
              </button>
              <button 
                @click="viewMode = 'split'" 
                :class="['px-3 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1', viewMode === 'split' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-white']"
              >
                <i class="bi bi-layout-split"></i>
                <span id="map"  class="hidden sm:inline">Map & List</span>
              </button>
            </div>

          </div>
        </div>

        <!-- ================= CONTENT DISPLAY ================= -->
        
        <!-- Empty State -->
        <div v-if="filteredChurches.length === 0" data-aos="zoom-in" class="text-center py-16 bg-slate-900 rounded-3xl border border-amber-500/30 space-y-4">
          <div class="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-amber-400 text-2xl border border-amber-500/30">
            <i class="bi bi-search animate__animated animate__headShake"></i>
          </div>
          <h3 class="font-serif text-lg font-bold text-amber-300">Cabang Gereja / Informasi Tidak Ditemukan</h3>
          <p class="text-xs text-slate-400 max-w-md mx-auto">
            Coba sesuaikan kata kunci pencarian Anda atau reset filter denominasi dan kota cabang yang Anda pilih.
          </p>
          <button 
            @click="searchQuery = ''; selectedCategory = 'Semua'; selectedDenomination = 'Semua'; selectedCity = 'Semua';"
            class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-xl text-xs font-semibold border border-amber-500/30 transition-all"
          >
            Reset Semua Filter
          </button>
        </div>

        <!-- Church Cards Grid -->
        <div 
          v-else 
          :class="[
            'grid gap-6 transition-all duration-300',
            viewMode === 'split' ? 'grid-cols-1 lg:grid-cols-12' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
          ]"
        >
          
          <div :class="[viewMode === 'split' ? 'lg:col-span-7 space-y-6' : 'contents']">
            <div 
              v-for="church in filteredChurches" 
              :key="church.id"
              data-aos="fade-up"
              data-aos-delay="150"
              class="group bg-slate-900 border border-amber-500/30 rounded-3xl overflow-hidden hover:border-amber-400/80 hover:shadow-2xl hover:shadow-amber-950/30 transition-all duration-300 flex flex-col justify-between"
            >
              <!-- Card Image Header -->
              <div class="relative h-48 overflow-hidden bg-slate-950">
                <img 
                  :src="church.image" 
                  :alt="church.name" 
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-85 group-hover:opacity-100"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/30 to-transparent"></div>

                <!-- Badges -->
                <div class="absolute top-3 left-3 flex flex-wrap gap-1.5 z-10">
                  <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-950/90 text-amber-300 border border-amber-500/40 backdrop-blur-md flex items-center gap-1">
                    <i class="bi bi-patch-check-fill text-amber-400"></i> Terintegrasi CMS
                  </span>
                  <span v-if="church.isLive" class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-600 text-white animate-pulse flex items-center gap-1 shadow">
                    <i class="bi bi-record-circle"></i> Live Stream
                  </span>
                </div>

                <div class="absolute bottom-3 right-3 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-slate-950/90 text-slate-200 border border-amber-500/30 backdrop-blur-md flex items-center gap-1">
                  <i class="bi bi-geo-alt-fill text-amber-400"></i> {{ church.distance }}
                </div>
              </div>

              <!-- Card Content Body -->
              <div class="p-5 flex-1 space-y-4 flex flex-col justify-between">
                <div>
                  <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
                    <span class="font-semibold text-amber-400 font-serif">{{ church.denomination }}</span>
                    <span class="flex items-center gap-1 text-amber-300 font-bold">
                      <i class="bi bi-star-fill text-xs text-amber-400"></i> {{ church.rating }} ({{ church.reviewsCount }})
                    </span>
                  </div>

                  <h3 class="font-serif text-lg font-bold text-white group-hover:text-amber-300 transition-colors leading-snug">
                    {{ church.name }}
                  </h3>

                  <p class="text-xs text-slate-400 mt-1 flex items-start gap-1">
                    <i class="bi bi-pin-map text-amber-400/80 shrink-0 mt-0.5"></i>
                    <span>{{ church.address }}</span>
                  </p>
                </div>

                <!-- Classification Tags -->
                <div class="space-y-2">
                  <div class="text-[10px] font-bold text-amber-300 uppercase tracking-wider font-serif">Pelayanan Terklasifikasi:</div>
                  <div class="flex flex-wrap gap-1.5">
                    <span 
                      v-for="cat in church.categories" 
                      :key="cat"
                      class="px-2 py-0.5 rounded-lg text-[10px] font-medium bg-slate-800 text-slate-200 border border-amber-500/20"
                    >
                      {{ cat }}
                    </span>
                  </div>
                </div>

                <!-- Schedule Preview Pill -->
                <div class="bg-slate-950 rounded-2xl p-3 border border-amber-500/20 space-y-1">
                  <div class="flex items-center justify-between text-[11px] text-amber-300 font-bold">
                    <span><i class="bi bi-calendar-week mr-1"></i> Ibadah Terdekat:</span>
                    <span class="text-slate-400 text-[10px]">{{ church.schedules[0].room }}</span>
                  </div>
                  <p class="text-xs font-bold text-slate-100">
                    {{ church.schedules[0].name }} — <span class="text-amber-300 font-normal">{{ church.schedules[0].time }}</span>
                  </p>
                </div>

                <!-- Action Button -->
                <div class="pt-2 flex items-center gap-2">
                  <button 
                    @click="openChurchModal(church)"
                    class="flex-1 py-2.5 px-4 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-xl text-xs transition-all duration-200 shadow-md shadow-amber-500/20 flex items-center justify-center gap-2"
                  >
                    <span>Lihat Detail Pelayanan</span>
                    <i class="bi bi-arrow-right-short text-base"></i>
                  </button>

                  <button 
                    @click="flyToChurchLocation(church)"
                    class="p-2.5 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-xl text-xs border border-amber-500/30 transition-colors flex items-center gap-1"
                    title="Fokus di Peta Presisi"
                  >
                    <i class="bi bi-crosshair text-amber-400"></i>
                    <span class="hidden sm:inline text-[11px]">Peta</span>
                  </button>

                  <a 
                    :href="'https://maps.google.com/?q=' + church.coordinates.lat + ',' + church.coordinates.lng"
                    target="_blank"
                    class="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs border border-amber-500/30 transition-colors"
                    title="Buka Google Maps"
                  >
                    <i class="bi bi-geo-alt text-amber-400"></i>
                  </a>
                </div>
              </div>

            </div>
          </div>

          <!-- SIDE MAP PREVIEW (INTERACTIVE LEAFLET PRECISION MAP) -->
          <div 
            v-if="viewMode === 'split'" 
            data-aos="fade-left"
            class="lg:col-span-5 sticky top-24 h-[680px] bg-slate-900 border border-amber-500/30 rounded-3xl overflow-hidden shadow-2xl flex flex-col justify-between"
          >
            <!-- Map Top Control Bar -->
            <div class="p-3.5 bg-slate-950 border-b border-amber-500/30 flex flex-wrap items-center justify-between gap-2 z-20">
              <div class="flex items-center gap-2 text-xs text-amber-300 font-bold font-serif">
                <i class="bi bi-map-fill text-amber-400 text-base"></i>
                <span>Peta Presisi Lokasi Cabang Gereja</span>
              </div>

              <div class="flex items-center gap-2">
                <!-- Radius Selector -->
                <div class="flex items-center gap-1 text-[11px] text-slate-300">
                  <select 
                    v-model="selectedRadiusKm" 
                    class="bg-slate-900 border border-amber-500/30 text-amber-300 rounded-lg px-2 py-1 text-[11px] focus:outline-none"
                    title="Jangkauan Radius"
                  >
                    <option :value="0">Radius: Nonaktif</option>
                    <option :value="2">Radius: 2 km</option>
                    <option :value="5">Radius: 5 km</option>
                    <option :value="10">Radius: 10 km</option>
                    <option :value="15">Radius: 15 km</option>
                  </select>
                </div>

                <!-- Locate Me Button -->
                <button 
                  @click="locateUserPosition"
                  :disabled="isLocatingUser"
                  class="p-1.5 bg-slate-900 hover:bg-slate-800 text-amber-300 rounded-lg border border-amber-500/30 text-xs transition-colors flex items-center gap-1"
                  title="Deteksi Lokasi Saya"
                >
                  <i :class="['bi', isLocatingUser ? 'bi-arrow-repeat animate-spin' : 'bi-crosshair text-amber-400']"></i>
                  <span class="hidden sm:inline text-[10px]">Lokasi Saya</span>
                </button>

                <!-- Fullscreen Toggle Button -->
                <button 
                  @click="isFullscreenMapOpen = true"
                  class="p-1.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 rounded-lg border border-amber-500/40 text-xs transition-colors"
                  title="Perluas Peta"
                >
                  <i class="bi bi-arrows-angle-expand"></i>
                </button>
              </div>
            </div>

            <!-- Map View Mode Switcher Toolbar -->
            <div class="bg-slate-950/90 px-3 py-1.5 border-b border-amber-500/20 flex items-center justify-between text-[11px] z-20">
              <div class="flex items-center gap-1">
                <span class="text-slate-400 text-[10px]">Tema Peta:</span>
                <button 
                  @click="switchTileLayer('dark')"
                  :class="['px-2 py-0.5 rounded text-[10px] font-semibold transition-all', activeTileLayer === 'dark' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-slate-200']"
                >
                  Dark Vektor
                </button>
                <button 
                  @click="switchTileLayer('street')"
                  :class="['px-2 py-0.5 rounded text-[10px] font-semibold transition-all', activeTileLayer === 'street' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-slate-200']"
                >
                  Street OSM
                </button>
              </div>

              <div class="text-[10px] text-amber-300 font-serif">
                <i class="bi bi-geo-fill text-amber-400 me-1"></i> {{ filteredChurches.length }} Pin Aktif
              </div>
            </div>

            <!-- Leaflet Container -->
            <div class="flex-1 relative z-10 w-full h-full bg-slate-950">
              <div ref="mapContainer" class="w-full h-full min-h-[450px]"></div>
            </div>

            <!-- Bottom HUD Status Bar -->
            <div class="p-3 bg-slate-950 border-t border-amber-500/30 text-[11px] text-slate-300 flex justify-between items-center z-20">
              <div class="flex items-center gap-3 text-[10px]">
                <span class="flex items-center gap-1 font-mono text-amber-300">
                  <i class="bi bi-crosshair text-amber-400"></i> {{ mapHUDCoords.lat }}, {{ mapHUDCoords.lng }}
                </span>
                <span class="text-slate-400 font-mono">Zoom: {{ mapHUDZoom }}x</span>
              </div>

              <button @click="viewMode = 'grid'" class="text-xs font-semibold text-amber-400 hover:underline flex items-center gap-1">
                <i class="bi bi-x-circle"></i> Tutup Peta
              </button>
            </div>
          </div>

        </div>

      </div>

      <!-- ================= MODAL DETAIL PELAYANAN GEREJA ================= -->
      <Transition name="fade">
        <div 
          v-if="selectedChurchDetail" 
          class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto"
          @click.self="closeChurchModal"
        >
          <div class="bg-slate-900 border border-amber-500/40 w-full max-w-4xl rounded-3xl shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col">

            <!-- Modal Header Banner -->
            <div class="relative h-44 sm:h-56 bg-slate-950 shrink-0">
              <img :src="selectedChurchDetail.image" class="w-full h-full object-cover opacity-80" />
              <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/40 to-transparent"></div>

              <button 
                @click="closeChurchModal"
                class="absolute top-4 right-4 w-9 h-9 rounded-full bg-slate-950/80 text-slate-300 hover:text-white border border-amber-500/30 flex items-center justify-center transition-all z-10"
              >
                <i class="bi bi-x-lg"></i>
              </button>

              <div class="absolute bottom-4 left-6 right-6">
                <div class="flex items-center gap-2 text-xs text-amber-300 font-semibold mb-1 font-serif">
                  <span>{{ selectedChurchDetail.denomination }}</span>
                  <span>•</span>
                  <span>{{ selectedChurchDetail.city }}</span>
                </div>
                <h2 class="font-serif text-xl sm:text-3xl font-extrabold text-white">
                  {{ selectedChurchDetail.name }}
                </h2>
              </div>
            </div>

            <!-- Modal Navigation Tabs -->
            <div class="bg-slate-950 border-b border-amber-500/30 px-6 flex space-x-6 text-xs sm:text-sm overflow-x-auto shrink-0">
              <button 
                @click="modalActiveTab = 'overview'"
                :class="['py-3 border-b-2 font-bold transition-all whitespace-nowrap', modalActiveTab === 'overview' ? 'border-amber-400 text-amber-300' : 'border-transparent text-slate-400 hover:text-slate-200']"
              >
                <i class="bi bi-info-circle mr-1"></i> Ringkasan Profil
              </button>
              <button 
                @click="modalActiveTab = 'schedules'"
                :class="['py-3 border-b-2 font-bold transition-all whitespace-nowrap', modalActiveTab === 'schedules' ? 'border-amber-400 text-amber-300' : 'border-transparent text-slate-400 hover:text-slate-200']"
              >
                <i class="bi bi-calendar-event mr-1"></i> Jadwal Ibadah Lengkap
              </button>
              <button 
                @click="modalActiveTab = 'ministries'"
                :class="['py-3 border-b-2 font-bold transition-all whitespace-nowrap', modalActiveTab === 'ministries' ? 'border-amber-400 text-amber-300' : 'border-transparent text-slate-400 hover:text-slate-200']"
              >
                <i class="bi bi-heart-pulse mr-1"></i> Klasifikasi Pelayanan
              </button>
              <button 
                @click="modalActiveTab = 'contact'"
                :class="['py-3 border-b-2 font-bold transition-all whitespace-nowrap', modalActiveTab === 'contact' ? 'border-amber-400 text-amber-300' : 'border-transparent text-slate-400 hover:text-slate-200']"
              >
                <i class="bi bi-telephone mr-1"></i> Lokasi & Kontak
              </button>
            </div>

            <!-- Modal Content Body -->
            <div class="p-6 overflow-y-auto space-y-6 text-sm text-slate-300 flex-1">

              <!-- TAB 1: OVERVIEW -->
              <div v-if="modalActiveTab === 'overview'" class="space-y-6">
                <div class="space-y-2">
                  <h4 class="font-serif text-xs font-bold text-amber-400 uppercase tracking-wider">Visi & Gembala Pembina</h4>
                  <p class="text-slate-200 leading-relaxed">{{ selectedChurchDetail.vision }}</p>
                  <p class="text-xs text-slate-400 italic">Gembala / Pastoral: {{ selectedChurchDetail.pastors }}</p>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div class="bg-slate-950 p-4 rounded-2xl border border-amber-500/20 space-y-2">
                    <h5 class="font-serif text-xs font-bold text-amber-300 flex items-center gap-1.5">
                      <i class="bi bi-check-circle-fill text-amber-400"></i> Fasilitas Tersedia
                    </h5>
                    <div class="flex flex-wrap gap-1.5">
                      <span v-for="f in selectedChurchDetail.facilities" :key="f" class="px-2 py-1 rounded bg-slate-800 text-[11px] text-slate-300 border border-amber-500/20">
                        {{ f }}
                      </span>
                    </div>
                  </div>

                  <div class="bg-slate-950 p-4 rounded-2xl border border-amber-500/20 space-y-2">
                    <h5 class="font-serif text-xs font-bold text-amber-300 flex items-center gap-1.5">
                      <i class="bi bi-broadcast text-red-400"></i> Integrasi Live Media
                    </h5>
                    <p class="text-xs text-slate-400">
                      Ibadah disiarkan secara langsung setiap Minggu di channel YouTube dan Portal Web CMS Gereja.
                    </p>
                  </div>
                </div>
              </div>

              <!-- TAB 2: SCHEDULES -->
              <div v-if="modalActiveTab === 'schedules'" class="space-y-4">
                <div class="flex items-center justify-between">
                  <h4 class="font-serif text-xs font-bold text-amber-400 uppercase tracking-wider">Jadwal Ibadah Cabang Gereja</h4>
                  <span v-if="churchAnnouncedServices.length > 0" class="text-[10px] px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1 font-semibold">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>Resmi dari Admin Cabang ({{ churchAnnouncedServices.length }} Pelayanan)</span>
                  </span>
                </div>

                <!-- Jika ada jadwal pelayanan resmi di database untuk cabang ini -->
                <div v-if="churchAnnouncedServices.length > 0" class="space-y-3">
                  <div 
                    v-for="svc in churchAnnouncedServices" 
                    :key="svc.id"
                    class="p-4 rounded-2xl bg-slate-950 border border-amber-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div>
                      <div class="flex items-center gap-2">
                        <span class="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 font-semibold">{{ svc.category }}</span>
                        <h5 class="font-bold text-white text-sm">{{ svc.service_name }}</h5>
                      </div>
                      <p class="text-xs text-amber-300 mt-1 flex items-center gap-2">
                        <span><i class="bi bi-calendar-check mr-1"></i> {{ svc.schedule_day || 'Hari Ibadah' }}</span>
                        <span>•</span>
                        <span><i class="bi bi-clock mr-1"></i> {{ svc.schedule_time || 'Jadwal Reguler' }}</span>
                      </p>
                      <p v-if="svc.description" class="text-xs text-slate-400 mt-1">{{ svc.description }}</p>
                    </div>
                    <div class="text-right shrink-0">
                      <span class="px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded-xl border border-amber-500/20 block">
                        {{ svc.location_room || 'Ruang Ibadah' }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Jika belum diisi oleh admin cabang -->
                <div v-else class="space-y-3">
                  <div class="p-3.5 rounded-2xl bg-slate-950/70 border border-amber-500/20 text-xs text-slate-400 flex items-start gap-2.5">
                    <i class="bi bi-info-circle text-amber-400 text-base shrink-0 mt-0.5"></i>
                    <div>
                      <span class="font-semibold text-slate-200">Admin cabang gereja ini belum menerbitkan jadwal pelayanan di database.</span>
                      <p class="mt-0.5 text-[11px]">Jadwal akan diperbarui secara otomatis begitu Admin Cabang mengisi data di dashboard mereka. Berikut adalah jadwal estimasi default:</p>
                    </div>
                  </div>

                  <div 
                    v-for="(sch, i) in selectedChurchDetail.schedules" 
                    :key="i"
                    class="p-4 rounded-2xl bg-slate-950 border border-amber-500/20 flex items-center justify-between"
                  >
                    <div>
                      <h5 class="font-bold text-white text-sm">{{ sch.name }}</h5>
                      <p class="text-xs text-amber-300 mt-0.5"><i class="bi bi-clock mr-1"></i> {{ sch.time }}</p>
                    </div>
                    <span class="px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded-xl border border-amber-500/20">
                      {{ sch.room }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- TAB 3: MINISTRIES -->
              <div v-if="modalActiveTab === 'ministries'" class="space-y-4">
                <h4 class="font-serif text-xs font-bold text-amber-400 uppercase tracking-wider">Klasifikasi Program & Pelayanan</h4>

                <!-- Jika ada di database -->
                <div v-if="churchAnnouncedServices.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div 
                    v-for="svc in churchAnnouncedServices" 
                    :key="svc.id"
                    class="p-4 rounded-2xl bg-slate-950 border border-amber-500/20 space-y-1.5"
                  >
                    <div class="flex items-center justify-between">
                      <h5 class="font-bold text-white text-sm flex items-center gap-2">
                        <i class="bi bi-star-fill text-amber-400 text-xs"></i> {{ svc.service_name }}
                      </h5>
                      <span class="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 font-semibold">{{ svc.category }}</span>
                    </div>
                    <p class="text-xs text-slate-400 leading-relaxed">{{ svc.description || 'Pelayanan resmi cabang gereja.' }}</p>
                    <p v-if="svc.pic_name" class="text-[11px] text-amber-400/80">PIC: {{ svc.pic_name }}</p>
                  </div>
                </div>

                <!-- Fallback jika belum diisi -->
                <div v-else class="space-y-3">
                  <div class="p-3.5 rounded-2xl bg-slate-950/70 border border-amber-500/20 text-xs text-slate-400 flex items-start gap-2.5">
                    <i class="bi bi-info-circle text-amber-400 text-base shrink-0 mt-0.5"></i>
                    <div>
                      <span class="font-semibold text-slate-200">Admin cabang gereja ini belum mengisi rincian kategorial pelayanan di database.</span>
                    </div>
                  </div>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div 
                      v-for="(m, i) in selectedChurchDetail.activeMinistries" 
                      :key="i"
                      class="p-4 rounded-2xl bg-slate-950 border border-amber-500/20 space-y-1.5"
                    >
                      <h5 class="font-bold text-white text-sm flex items-center gap-2">
                        <i class="bi bi-star-fill text-amber-400 text-xs"></i> {{ m.name }}
                      </h5>
                      <p class="text-xs text-slate-400 leading-relaxed">{{ m.desc }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- TAB 4: CONTACT & LOCATION -->
              <div v-if="modalActiveTab === 'contact'" class="space-y-4">
                <h4 class="font-serif text-xs font-bold text-amber-400 uppercase tracking-wider">Informasi Kontak & Lokasi Presisi</h4>
                
                <div class="bg-slate-950 p-4 rounded-2xl border border-amber-500/20 space-y-3 text-xs">
                  <div class="flex items-center gap-3">
                    <i class="bi bi-geo-alt-fill text-amber-400 text-lg"></i>
                    <div>
                      <p class="font-bold text-white">Alamat Lengkap</p>
                      <p class="text-slate-400">{{ selectedChurchDetail.address }}</p>
                    </div>
                  </div>

                  <div class="flex items-center gap-3">
                    <i class="bi bi-whatsapp text-emerald-400 text-lg"></i>
                    <div>
                      <p class="font-bold text-white">WhatsApp Sekretariat</p>
                      <p class="text-slate-400">{{ selectedChurchDetail.contacts.whatsapp }}</p>
                    </div>
                  </div>

                  <div class="flex items-center gap-3">
                    <i class="bi bi-envelope-at text-amber-400 text-lg"></i>
                    <div>
                      <p class="font-bold text-white">Email Resmi</p>
                      <p class="text-slate-400">{{ selectedChurchDetail.contacts.email }}</p>
                    </div>
                  </div>
                </div>

                <a 
                  :href="'https://maps.google.com/?q=' + selectedChurchDetail.coordinates.lat + ',' + selectedChurchDetail.coordinates.lng"
                  target="_blank"
                  class="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-2xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition-all"
                >
                  <i class="bi bi-box-arrow-up-right"></i>
                  <span>Buka Petunjuk Arah di Google Maps</span>
                </a>
              </div>

            </div>

            <!-- Modal Footer -->
            <div class="p-4 bg-slate-950 border-t border-amber-500/30 flex justify-end shrink-0">
              <button 
                @click="closeChurchModal" 
                class="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 text-xs font-bold border border-amber-500/30 transition-colors"
              >
                Tutup
              </button>
            </div>

          </div>
        </div>
      </Transition>

      <!-- ================= MODAL DETAIL PENGUMUMAN PELAYANAN CABANG ================= -->
      <Transition name="fade">
        <div 
          v-if="selectedAnnouncementDetail" 
          class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto"
          @click.self="closeAnnouncementDetail"
        >
          <div class="bg-slate-900 border border-amber-500/40 w-full max-w-2xl rounded-3xl shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col">
            <!-- Modal Header -->
            <div class="p-5 sm:p-6 bg-slate-950 border-b border-amber-500/30 flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  {{ selectedAnnouncementDetail.category }}
                </span>
                <span class="text-xs text-slate-400 font-serif">• {{ selectedAnnouncementDetail.church_name }}</span>
              </div>
              <button 
                @click="closeAnnouncementDetail"
                class="w-8 h-8 rounded-full bg-slate-900 text-slate-400 hover:text-white border border-amber-500/30 flex items-center justify-center transition"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>

            <!-- Modal Body -->
            <div class="p-6 overflow-y-auto space-y-6 text-slate-200 text-xs sm:text-sm">
              <div>
                <h3 class="font-serif text-xl sm:text-2xl font-bold text-white mb-1.5">
                  {{ selectedAnnouncementDetail.service_name }}
                </h3>
                <p class="text-xs text-amber-400 flex items-center gap-1.5 font-serif">
                  <i class="bi bi-building"></i>
                  <span>{{ selectedAnnouncementDetail.church_name }}</span>
                  <span v-if="selectedAnnouncementDetail.city" class="text-slate-400">({{ selectedAnnouncementDetail.city }})</span>
                </p>
              </div>

              <!-- Detail Grid -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="p-3.5 bg-slate-950 rounded-2xl border border-amber-500/20 space-y-1">
                  <span class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Jadwal & Waktu</span>
                  <p class="text-xs sm:text-sm font-semibold text-amber-300">
                    <i class="bi bi-clock-history mr-1"></i>
                    {{ selectedAnnouncementDetail.schedule_day || 'Minggu' }} • {{ selectedAnnouncementDetail.schedule_time || 'Jadwal Reguler' }}
                  </p>
                </div>

                <div class="p-3.5 bg-slate-950 rounded-2xl border border-amber-500/20 space-y-1">
                  <span class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Ruangan / Tempat</span>
                  <p class="text-xs sm:text-sm font-semibold text-slate-200">
                    <i class="bi bi-geo-alt mr-1 text-amber-400"></i>
                    {{ selectedAnnouncementDetail.location_room || 'Gedung Gereja' }}
                  </p>
                </div>

                <div class="p-3.5 bg-slate-950 rounded-2xl border border-amber-500/20 space-y-1">
                  <span class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Target Jemaat</span>
                  <p class="text-xs sm:text-sm font-semibold text-slate-200">
                    <i class="bi bi-people mr-1 text-amber-400"></i>
                    {{ selectedAnnouncementDetail.target_audience || 'Semua Jemaat' }}
                  </p>
                </div>

                <div class="p-3.5 bg-slate-950 rounded-2xl border border-amber-500/20 space-y-1">
                  <span class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Penanggung Jawab (PIC)</span>
                  <p class="text-xs sm:text-sm font-semibold text-slate-200">
                    <i class="bi bi-person-badge mr-1 text-amber-400"></i>
                    {{ selectedAnnouncementDetail.pic_name || 'Tim Pelayanan Cabang' }}
                  </p>
                </div>
              </div>

              <!-- Deskripsi Pelayanan -->
              <div class="space-y-2">
                <span class="text-xs font-bold text-amber-400 uppercase font-serif tracking-wider">Deskripsi & Rincian Informasi Pelayanan:</span>
                <div class="p-4 bg-slate-950 rounded-2xl border border-amber-500/20 text-xs sm:text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                  {{ selectedAnnouncementDetail.description || 'Tidak ada uraian tambahan untuk pelayanan ini.' }}
                </div>
              </div>

              <!-- WhatsApp & Live Streaming Actions -->
              <div class="flex flex-wrap gap-3 pt-2">
                <a 
                  v-if="selectedAnnouncementDetail.pic_contact" 
                  :href="'https://wa.me/' + cleanPhone(selectedAnnouncementDetail.pic_contact)" 
                  target="_blank"
                  class="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl text-xs flex items-center justify-center gap-2 shadow-lg transition"
                >
                  <i class="bi bi-whatsapp text-base"></i>
                  <span>Hubungi via WhatsApp ({{ selectedAnnouncementDetail.pic_contact }})</span>
                </a>

                <a 
                  v-if="selectedAnnouncementDetail.live_stream_url" 
                  :href="selectedAnnouncementDetail.live_stream_url" 
                  target="_blank"
                  class="py-3 px-4 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-2xl text-xs flex items-center justify-center gap-2 shadow-lg transition"
                >
                  <i class="bi bi-broadcast text-base"></i>
                  <span>Tonton Live Stream</span>
                </a>
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="p-4 bg-slate-950 border-t border-amber-500/30 flex justify-end">
              <button 
                @click="closeAnnouncementDetail"
                class="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 text-xs font-bold border border-amber-500/30 transition"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <!-- ================= MODAL FULLSCREEN MAP VIEW ================= -->
      <Transition name="fade">
        <div 
          v-if="isFullscreenMapOpen" 
          class="fixed inset-0 z-[999] bg-slate-950 flex flex-col font-sans"
        >
          <!-- Fullscreen Header -->
          <div class="p-4 bg-slate-900 border-b border-amber-500/30 flex items-center justify-between shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 flex items-center justify-center font-bold">
                <i class="bi bi-map-fill text-lg"></i>
              </div>
              <div>
                <h3 class="font-serif text-lg font-bold text-amber-300">Peta Presisi Pelayanan Gereja</h3>
                <p class="text-xs text-slate-300">Mode Layar Penuh dengan Koordinat & Integrasi Vektor</p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <!-- Tile Switcher -->
              <div class="hidden sm:flex bg-slate-950 p-1 rounded-xl border border-amber-500/30">
                <button 
                  @click="switchTileLayer('dark')"
                  :class="['px-3 py-1 rounded-lg text-xs font-semibold transition-all', activeTileLayer === 'dark' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white']"
                >
                  Dark Slate
                </button>
                <button 
                  @click="switchTileLayer('street')"
                  :class="['px-3 py-1 rounded-lg text-xs font-semibold transition-all', activeTileLayer === 'street' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white']"
                >
                  Street OSM
                </button>
              </div>

              <button 
                @click="isFullscreenMapOpen = false"
                class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-amber-300 font-bold rounded-xl text-xs border border-amber-500/30 flex items-center gap-1.5 transition-colors"
              >
                <i class="bi bi-x-lg"></i>
                <span>Tutup</span>
              </button>
            </div>
          </div>

          <!-- Fullscreen Content Grid -->
          <div class="flex-1 flex flex-col md:flex-row overflow-hidden relative">
            <!-- Sidebar Church List in Modal -->
            <div class="w-full md:w-80 bg-slate-900 border-r border-amber-500/30 overflow-y-auto p-4 space-y-3 shrink-0">
              <div class="text-xs font-serif font-bold text-amber-400 uppercase tracking-wider">Daftar Gereja ({{ filteredChurches.length }})</div>
              
              <div 
                v-for="c in filteredChurches" 
                :key="'fullscreen-list-' + c.id"
                @click="flyToChurchLocation(c)"
                :class="[
                  'p-3 rounded-2xl border transition-all cursor-pointer space-y-1.5',
                  activeMapHoverId === c.id ? 'bg-slate-800 border-amber-400 ring-2 ring-amber-500/30' : 'bg-slate-950 border-amber-500/20 hover:border-amber-400/50'
                ]"
              >
                <div class="flex items-center justify-between text-[11px]">
                  <span class="font-serif font-bold text-amber-300">{{ c.denomination }}</span>
                  <span class="text-slate-400">{{ c.distance }}</span>
                </div>
                <h4 class="font-serif font-bold text-sm text-white leading-tight">{{ c.name }}</h4>
                <p class="text-xs text-slate-400 truncate"><i class="bi bi-pin-map text-amber-400 me-1"></i> {{ c.address }}</p>
              </div>
            </div>

            <!-- Main Map Canvas -->
            <div class="flex-1 relative bg-slate-950">
              <div ref="modalMapContainer" class="w-full h-full min-h-[500px]"></div>
            </div>
          </div>
        </div>
      </Transition>

    </div>
  </InformasiPelayananLayout>
</template>

<style>
/* Global Custom Styles for Leaflet Elements */
.custom-leaflet-div-icon {
  background: transparent !important;
  border: none !important;
}

.user-pin-div-icon {
  background: transparent !important;
  border: none !important;
}

.custom-leaflet-popup .leaflet-popup-content-wrapper {
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.custom-leaflet-popup .leaflet-popup-tip-container {
  display: none !important;
}

.leaflet-container {
  background-color: #020617 !important;
  font-family: inherit !important;
}

.informasi-pelayanan-page {
  transition: background-color 0.3s ease, color 0.3s ease;
}

.theme-light-page {
  --page-bg: #f8fafc;
  --page-surface: #ffffff;
  --page-surface-soft: #f1f5f9;
  --page-surface-strong: #e2e8f0;
  --page-border: rgba(148, 163, 184, 0.45);
  --page-text: #0f172a;
  --page-muted: #475569;
  --page-accent: #b45309;
  --page-accent-soft: rgba(245, 158, 11, 0.12);
  --page-border-accent: rgba(245, 158, 11, 0.38);
}

.theme-dark-page {
  --page-bg: #020817;
  --page-surface: #0f172a;
  --page-surface-soft: #111827;
  --page-surface-strong: #1e293b;
  --page-border: rgba(251, 191, 36, 0.28);
  --page-text: #e2e8f0;
  --page-muted: #94a3b8;
  --page-accent: #fbbf24;
  --page-accent-soft: rgba(251, 191, 36, 0.12);
  --page-border-accent: rgba(251, 191, 36, 0.4);
}

.theme-light-page .bg-slate-900,
.theme-light-page .bg-slate-950,
.theme-light-page .bg-slate-800,
.theme-light-page .bg-slate-700,
.theme-light-page .bg-slate-100 {
  background-color: var(--page-surface) !important;
}

.theme-light-page .bg-slate-950 {
  background-color: var(--page-surface-soft) !important;
}

.theme-light-page .bg-slate-800 {
  background-color: var(--page-surface-strong) !important;
}

.theme-light-page .text-slate-100,
.theme-light-page .text-slate-200,
.theme-light-page .text-slate-300,
.theme-light-page .text-slate-400,
.theme-light-page .text-slate-500,
.theme-light-page .text-slate-600,
.theme-light-page .text-slate-700,
.theme-light-page .text-slate-800,
.theme-light-page .text-slate-900,
.theme-light-page .text-white {
  color: var(--page-text) !important;
}

.theme-light-page .text-slate-400,
.theme-light-page .text-slate-500,
.theme-light-page .text-slate-300 {
  color: var(--page-muted) !important;
}

.theme-light-page .text-amber-300,
.theme-light-page .text-amber-400 {
  color: var(--page-accent) !important;
}

.theme-light-page .border-amber-500\/30,
.theme-light-page .border-amber-500\/20,
.theme-light-page .border-amber-500\/40,
.theme-light-page .border-amber-500\/50,
.theme-light-page .border-slate-800,
.theme-light-page .border-slate-700,
.theme-light-page .border-slate-900 {
  border-color: var(--page-border) !important;
}

.theme-light-page .text-amber-300,
.theme-light-page .text-amber-400,
.theme-light-page .text-amber-500 {
  color: #b45309 !important;
}

.theme-light-page .bg-amber-500\/10,
.theme-light-page .bg-amber-500\/20,
.theme-light-page .bg-amber-500\/30,
.theme-light-page .bg-amber-500\/40 {
  background-color: var(--page-accent-soft) !important;
}

.theme-light-page .bg-gradient-to-r.from-amber-500.to-amber-600,
.theme-light-page .bg-gradient-to-r.from-amber-500.to-amber-600:hover {
  background-image: linear-gradient(to right, #f59e0b, #d97706) !important;
}

.theme-light-page .placeholder-slate-500::placeholder {
  color: var(--page-muted) !important;
}

.theme-light-page .leaflet-container {
  background-color: #e2e8f0 !important;
}

.theme-light-page .custom-leaflet-popup .leaflet-popup-content-wrapper {
  background: rgba(255, 255, 255, 0.94) !important;
}
</style>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>