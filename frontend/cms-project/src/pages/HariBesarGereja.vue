<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import {
  format,
  parseISO,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  addDays,
  subDays,
  isSameMonth,
  isSameDay,
  isToday,
  getDate,
  getDay,
  differenceInDays,
  startOfDay
} from 'date-fns'
import { id as localeId } from 'date-fns/locale/id'
import CalendarLayout from '@/layouts/CalendarLayout.vue'
import { APP_CONFIG } from '@/config'
import AOS from 'aos'
import 'aos/dist/aos.css'
import 'animate.css'

const route = useRoute()

// --- State Data Jemaat & Cabang Gereja dari Database PostgreSQL ---
const jemaatMembers = ref([])
const churchBranches = ref([])
const churchAgendas = ref([])
const isLoadingData = ref(false)
const selectedBranchFilter = ref('all')
const eventTypeFilter = ref('all') // 'all' | 'liturgi' | 'kegiatan' | 'birthday'

const loadJemaatAndBranches = async () => {
  isLoadingData.value = true
  try {
    const [resUsers, resBranches, resAgendas] = await Promise.allSettled([
      fetch(`${APP_CONFIG.apiBaseUrl}/users/?limit=200`),
      fetch(`${APP_CONFIG.apiBaseUrl}/church-admins/?limit=200`),
      fetch(`${APP_CONFIG.apiBaseUrl}/agenda/?limit=300`)
    ])

    if (resUsers.status === 'fulfilled' && resUsers.value.ok) {
      jemaatMembers.value = await resUsers.value.json()
    }
    if (resBranches.status === 'fulfilled' && resBranches.value.ok) {
      churchBranches.value = await resBranches.value.json()
    }
    if (resAgendas.status === 'fulfilled' && resAgendas.value.ok) {
      churchAgendas.value = await resAgendas.value.json()
    }
  } catch (err) {
    console.warn('Gagal memuat data jemaat & cabang dari database:', err)
  } finally {
    isLoadingData.value = false
  }
}

// Inisialisasi AOS & Load Data saat komponen terpasang
onMounted(() => {
  nextTick(() => {
    try {
      AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        offset: 50
      })
      AOS.refresh()
    } catch (e) {
      // Safe fallback
    }
  })
  loadJemaatAndBranches()

  // Handle URL query parameters jika navigasi dari halaman jemaat
  if (route.query.filter === 'birthday') {
    eventTypeFilter.value = 'birthday'
  }
  if (route.query.branch) {
    selectedBranchFilter.value = route.query.branch
  }
})

// --- Daftar Cabang Gereja Unik untuk Dropdown Filter ---
const availableBranches = computed(() => {
  const branchSet = new Set()
  churchBranches.value.forEach((b) => {
    if (b.church_name) branchSet.add(b.church_name.trim())
  })
  jemaatMembers.value.forEach((u) => {
    if (u.church_domisili) branchSet.add(u.church_domisili.trim())
  })
  return Array.from(branchSet).sort()
})

// --- Algoritma Astronomis & Gregorian Computus Penentuan Hari Raya Paskah ---
// Meeus/Jones/Butcher algorithm - Presisi 100% untuk tahun 1900 s/d 2099+
function getEasterDate(year) {
  const a = year % 19
  const b = Math.floor(year / 100)
  const c = year % 100
  const d = Math.floor(b / 4)
  const e = b % 4
  const f = Math.floor((b + 8) / 25)
  const g = Math.floor((b - f + 1) / 3)
  const h = (19 * a + b - d - g + 15) % 30
  const i = Math.floor(c / 4)
  const k = c % 4
  const l = (32 + 2 * e + 2 * i - h - k) % 7
  const m = Math.floor((a + 11 * h + 22 * l) / 451)
  const month = Math.floor((h + l - 7 * m + 114) / 31) // 3 = Maret, 4 = April
  const day = ((h + l - 7 * m + 114) % 31) + 1
  return new Date(year, month - 1, day)
}

// State Kalender
const currentDate = ref(new Date())
const selectedYear = ref(currentDate.value.getFullYear())
const selectedMonth = ref(currentDate.value.getMonth()) // 0 - 11
const activeTab = ref('calendar') // 'calendar' | 'list'
const activeFilter = ref('all') // 'all' | 'paskah' | 'natal' | 'biasa'

// Daftar Tahun yang Tersedia Secara Dinamis (Fleksibel hingga 15 tahun ke depan)
const availableYears = computed(() => {
  const curYear = new Date().getFullYear()
  const start = curYear - 3
  const end = curYear + 15
  const list = []
  for (let y = start; y <= end; y++) {
    list.push(y)
  }
  return list
})

// Siklus Bacaan Alkitab Bersama / Revised Common Lectionary (RCL)
const liturgicalYearCycle = computed(() => {
  const rem = selectedYear.value % 3
  if (rem === 0) return { cycle: 'Tahun A', focus: 'Injil Matius' }
  if (rem === 1) return { cycle: 'Tahun B', focus: 'Injil Markus' }
  return { cycle: 'Tahun C', focus: 'Injil Lukas' }
})

const monthNames = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]

// --- Database & Kalkulator Hari Raya Liturgi Kristen Otomatis Sepanjang Masa ---
const getHolyDaysForYear = (year) => {
  const easter = getEasterDate(year)

  // 1. Tanggal Bergerak Siklus Paskah (Menggunakan kalkulasi date-fns)
  const rabuAbu = subDays(easter, 46)
  const mingguPalma = subDays(easter, 7)
  const kamisPutih = subDays(easter, 3)
  const jumatAgung = subDays(easter, 2)
  const sabtuSuci = subDays(easter, 1)
  const paskah = easter
  const paskah2 = addDays(easter, 1)
  const kenaikan = addDays(easter, 39) // Jatuh di hari Kamis (hari ke-40)
  const pentakosta = addDays(easter, 49) // Jatuh di hari Minggu (hari ke-50)
  const pentakosta2 = addDays(easter, 50) // Senin Pentakosta II
  const trinitas = addDays(easter, 56) // Minggu Trinitas

  // 2. Tanggal Bergerak Siklus Adven & Tutup Tahun Liturgi
  const natalDate = new Date(year, 11, 25)
  const dayOfChristmas = getDay(natalDate) // 0 = Minggu
  const adven4 = subDays(natalDate, dayOfChristmas === 0 ? 7 : dayOfChristmas)
  const adven3 = subDays(adven4, 7)
  const adven2 = subDays(adven3, 7)
  const adven1 = subDays(adven2, 7)
  const kristusRaja = subDays(adven1, 7) // Minggu terakhir sebelum Adven

  // 3. Tanggal Bergerak Awal Tahun (Epifani & Pembaptisan Tuhan)
  const epifaniDate = new Date(year, 0, 6)
  const baptisanTuhan = addDays(epifaniDate, (7 - getDay(epifaniDate)) % 7 || 7)

  // 4. Hari Perjamuan Kudus Sedunia (Minggu Pertama Oktober)
  const okt1 = new Date(year, 9, 1)
  const perjamuanSedunia = addDays(okt1, (7 - getDay(okt1)) % 7)

  const holyDaysList = [
    {
      date: `${year}-01-01`,
      title: 'Hari Tahun Baru Masehi',
      category: 'biasa',
      color: 'gold',
      colorName: 'Putih / Emas',
      icon: 'bi-stars',
      badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      description: 'Ibadah awal tahun menyambut pemeliharaan dan penyertaan Tuhan bagi gereja dan jemaat di tahun yang baru.',
      bibleVerse: 'Ratapan 3:22-23 — "Tak berkesudahan kasih setia TUHAN, tak habis-habisnya rahmat-Nya, selalu baru tiap pagi; besar kesetiaan-Mu!"'
    },
    {
      date: `${year}-01-06`,
      title: 'Hari Raya Epifani (Hari Tiga Raja)',
      category: 'natal',
      color: 'gold',
      colorName: 'Putih / Emas',
      icon: 'bi-brightness-high-fill',
      badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      description: 'Peringatan manifestasi Allah dalam Kristus kepada dunia dan kedatangan orang Majus dari Timur menyembah Sang Raja.',
      bibleVerse: 'Matius 2:11 — "Maka masuklah mereka ke dalam rumah itu dan melihat Anak itu bersama Maria, ibu-Nya, lalu sujud menyembah Dia."'
    },
    {
      date: format(baptisanTuhan, 'yyyy-MM-dd'),
      title: 'Hari Pembaptisan Tuhan Yesus',
      category: 'biasa',
      color: 'white',
      colorName: 'Putih',
      icon: 'bi-droplet-fill',
      badgeClass: 'bg-sky-950/80 text-sky-300 border-sky-500/40',
      description: 'Peringatan pembaptisan Yesus Kristus oleh Yohanes Pembaptis di Sungai Yordan dan pengurapan Roh Kudus.',
      bibleVerse: 'Markus 1:11 — "Lalu terdengarlah suara dari sorga: Engkaulah Anak-Ku yang Kukasihi, kepada-Mulah Aku berkenan."'
    },
    {
      date: format(rabuAbu, 'yyyy-MM-dd'),
      title: 'Rabu Abu (Ash Wednesday)',
      category: 'paskah',
      color: 'purple',
      colorName: 'Ungu (Penyesalan & Pertobatan)',
      icon: 'bi-moon-stars',
      badgeClass: 'bg-purple-950/80 text-purple-300 border-purple-600/50',
      description: 'Awal Masa Pra-Paskah (40 hari Puasa & Pertobatan). Jemaat diurapi abu sebagai lambang pertobatan dan penyerahan diri.',
      bibleVerse: 'Kejadian 3:19 — "Sebab engkau debu dan engkau akan kembali menjadi debu."'
    },
    {
      date: format(mingguPalma, 'yyyy-MM-dd'),
      title: 'Minggu Palma (Palm Sunday)',
      category: 'paskah',
      color: 'red',
      colorName: 'Merah / Ungu',
      icon: 'bi-tree',
      badgeClass: 'bg-rose-950/80 text-rose-300 border-rose-600/50',
      description: 'Peringatan masuknya Yesus Kristus ke Yerusalem disambut dengan daun palma sebagai Raja Damai yang rendah hati.',
      bibleVerse: 'Yohanes 12:13 — "Hosana! Diberkatilah Dia yang datang dalam nama Tuhan, Raja Israel!"'
    },
    {
      date: format(kamisPutih, 'yyyy-MM-dd'),
      title: 'Kamis Putih (Maundy Thursday)',
      category: 'paskah',
      color: 'white',
      colorName: 'Putih / Emas',
      icon: 'bi-cup-hot',
      badgeClass: 'bg-slate-100/10 text-slate-100 border-slate-400/40',
      description: 'Peringatan Perjamuan Kudus Terakhir Yesus bersama murid-murid-Nya serta pembasuhan kaki sebagai teladan kerendahan hati melayani.',
      bibleVerse: 'Yohanes 13:34 — "Aku memberikan perintah baru kepada kamu, yaitu supaya kamu saling mengasihi..."'
    },
    {
      date: format(jumatAgung, 'yyyy-MM-dd'),
      title: 'Jumat Agung (Good Friday)',
      category: 'paskah',
      color: 'black',
      colorName: 'Merah Tua / Hitam',
      icon: 'bi-plus-lg',
      badgeClass: 'bg-red-950/90 text-red-300 border-red-700/60',
      description: 'Peringatan Pengorbanan dan Wafat Yesus Kristus di kayu salib Golgotha demi menebus dosa seluruh umat manusia.',
      bibleVerse: 'Yohanes 19:30 — "Sudah selesai." Lalu Ia menundukkan kepala-Nya dan menyerahkan nyawa-Nya.'
    },
    {
      date: format(sabtuSuci, 'yyyy-MM-dd'),
      title: 'Sabtu Sunyi / Sabtu Suci (Holy Saturday)',
      category: 'paskah',
      color: 'purple',
      colorName: 'Ungu / Hitam',
      icon: 'bi-hourglass-split',
      badgeClass: 'bg-slate-900 text-slate-400 border-slate-700',
      description: 'Masa hening dan perenungan iman saat Kristus bersemayam di dalam kubur sebelum kebangkitan-Nya yang gilang-gemilang.',
      bibleVerse: 'Lukas 23:56 — "Dan pada hari Sabat mereka beristirahat menurut hukum Taurat."'
    },
    {
      date: format(paskah, 'yyyy-MM-dd'),
      title: 'Hari Raya Paskah (Easter Sunday)',
      category: 'paskah',
      color: 'gold',
      colorName: 'Putih / Emas (Kemenangan)',
      icon: 'bi-sun-fill',
      badgeClass: 'bg-amber-400/20 text-amber-200 border-amber-400/60',
      description: 'Puncak Kebangkitan Yesus Kristus dari antara orang mati! Kemenangan mutlak atas kuasa maut dan jaminan keselamatan kekal.',
      bibleVerse: '1 Korintus 15:55 — "Hai maut di manakah kemenanganmu? Hai maut, di manakah sengatmu?"'
    },
    {
      date: format(paskah2, 'yyyy-MM-dd'),
      title: 'Hari Paskah II (Easter Monday)',
      category: 'paskah',
      color: 'gold',
      colorName: 'Putih / Emas',
      icon: 'bi-sun',
      badgeClass: 'bg-amber-400/10 text-amber-300 border-amber-400/40',
      description: 'Kelanjutan perayaan sukacita kebangkitan Kristus bersama keluarga dan persekutuan jemaat gereja.',
      bibleVerse: 'Lukas 24:34 — "Sesungguhnya Tuhan telah bangkit dan telah menampakkan diri kepada Simon."'
    },
    {
      date: format(kenaikan, 'yyyy-MM-dd'),
      title: 'Kenaikan Yesus Kristus (Ascension Day)',
      category: 'paskah',
      color: 'gold',
      colorName: 'Putih / Emas',
      icon: 'bi-cloud-upload',
      badgeClass: 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50',
      description: 'Peringatan Kenaikan Kristus ke Surga pada hari ke-40 setelah kebangkitan-Nya dan janji pengutusan Roh Kudus serta kedatangan-Nya kembali.',
      bibleVerse: 'Kisah Para Rasul 1:11 — "Yesus ini, yang terangkat ke sorga meninggalkan kamu, akan datang kembali dengan cara yang sama..."'
    },
    {
      date: format(pentakosta, 'yyyy-MM-dd'),
      title: 'Hari Raya Pentakosta (Pentecost)',
      category: 'biasa',
      color: 'red',
      colorName: 'Merah (Api Roh Kudus)',
      icon: 'bi-fire',
      badgeClass: 'bg-red-600/20 text-red-400 border-red-500/50',
      description: 'Pencurahan Roh Kudus atas para rasul pada hari ke-50 setelah Paskah dan momentum berdirinya Gereja Kristus di muka bumi.',
      bibleVerse: 'Kisah Para Rasul 2:4 — "Maka penuhlah mereka dengan Roh Kudus, lalu mereka mulai berkata-kata dalam bahasa-bahasa lain..."'
    },
    {
      date: format(pentakosta2, 'yyyy-MM-dd'),
      title: 'Hari Pentakosta II (Whit Monday)',
      category: 'biasa',
      color: 'red',
      colorName: 'Merah',
      icon: 'bi-lightning-charge-fill',
      badgeClass: 'bg-red-600/15 text-red-300 border-red-500/40',
      description: 'Hari kedua perayaan Roh Kudus, menghayati pembaruan hidup rohani dan keberanian bersaksi di tengah masyarakat.',
      bibleVerse: 'Kisah Para Rasul 1:8 — "Tetapi kamu akan menerima kuasa, kalau Roh Kudus turun ke atas kamu, dan kamu akan menjadi saksi-Ku..."'
    },
    {
      date: format(trinitas, 'yyyy-MM-dd'),
      title: 'Minggu Trinitas (Trinity Sunday)',
      category: 'biasa',
      color: 'white',
      colorName: 'Putih / Emas',
      icon: 'bi-shield-check',
      badgeClass: 'bg-sky-950/80 text-sky-300 border-sky-500/40',
      description: 'Penghormatan dan pengakuan iman kepada Allah Tritunggal Maha Kudus: Bapa Sang Pencipta, Anak Sang Penebus, dan Roh Kudus Sang Penghibur.',
      bibleVerse: '2 Korintus 13:13 — "Kasih karunia Tuhan Yesus Kristus, dan kasih Allah, dan persekutuan Roh Kudus menyertai kamu sekalian."'
    },
    {
      date: `${year}-08-06`,
      title: 'Transfigurasi Kristus (Kemuliaan Wajah Yesus)',
      category: 'biasa',
      color: 'white',
      colorName: 'Putih / Emas',
      icon: 'bi-gem',
      badgeClass: 'bg-amber-400/10 text-amber-200 border-amber-400/40',
      description: 'Peringatan peristiwa Yesus berubah rupa dalam kemuliaan ilahi di atas gunung di hadapan Petrus, Yakobus, Yohanes, serta tampak Musa dan Elia.',
      bibleVerse: 'Matius 17:2 — "Lalu Yesus berubah rupa di depan mata mereka; wajah-Nya bercahaya seperti matahari dan pakaian-Nya menjadi putih bersinar seperti terang."'
    },
    {
      date: format(perjamuanSedunia, 'yyyy-MM-dd'),
      title: 'Hari Perjamuan Kudus Sedunia (World Communion Sunday)',
      category: 'biasa',
      color: 'white',
      colorName: 'Putih',
      icon: 'bi-globe2',
      badgeClass: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40',
      description: 'Perayaan persatuan ekumenis seluruh gereja Kristen di seluruh dunia dalam satu meja perjamuan Tuhan Yesus Kristus.',
      bibleVerse: '1 Korintus 10:17 — "Karena roti adalah satu, maka kita, sekalipun banyak, adalah satu tubuh, karena kita semua mendapat bagian dalam roti yang satu itu."'
    },
    {
      date: `${year}-10-31`,
      title: 'Hari Reformasi Gereja (Reformation Day)',
      category: 'biasa',
      color: 'red',
      colorName: 'Merah',
      icon: 'bi-journal-bookmark',
      badgeClass: 'bg-rose-900/40 text-rose-300 border-rose-500/40',
      description: 'Peringatan Martin Luther menempelkan 95 Tesis di Wittenberg (1517), menegakkan prinsip Sola Fide, Sola Gratia, dan Sola Scriptura.',
      bibleVerse: 'Roma 1:17 — "Sebab di dalamnya nyata kebenaran Allah, yang bertolak dari iman dan memimpin kepada iman; seperti ada tertulis: Orang benar akan hidup oleh iman."'
    },
    {
      date: `${year}-11-01`,
      title: 'Hari Semua Orang Kudus (All Saints Day)',
      category: 'biasa',
      color: 'white',
      colorName: 'Putih',
      icon: 'bi-people-fill',
      badgeClass: 'bg-slate-100/10 text-slate-200 border-slate-400/40',
      description: 'Mengenang kesaksian hidup dan warisan iman dari para martir dan orang kudus Tuhan yang telah mendahului kita dalam iman.',
      bibleVerse: 'Ibrani 12:1 — "Kita mempunyai banyak saksi, bagaikan awan yang mengelilingi kita, marilah kita menanggalkan semua beban dan dosa..."'
    },
    {
      date: format(kristusRaja, 'yyyy-MM-dd'),
      title: 'Hari Raya Kristus Raja Semesta Alam',
      category: 'biasa',
      color: 'gold',
      colorName: 'Putih / Emas',
      icon: 'bi-trophy-fill',
      badgeClass: 'bg-amber-400/20 text-amber-200 border-amber-400/50',
      description: 'Puncak penutup Tahun Liturgi Gereja, memproklamasikan kedaulatan abadi Kristus atas seluruh jagat raya sebelum memasuki masa Adven.',
      bibleVerse: 'Wahyu 19:16 — "Dan pada jubah-Nya dan paha-Nya tertulis suatu nama, yaitu: Raja segala raja dan Tuan di atas segala tuan."'
    },
    {
      date: format(adven1, 'yyyy-MM-dd'),
      title: 'Minggu Adven I',
      category: 'natal',
      color: 'purple',
      colorName: 'Ungu (Lilin Harapan)',
      icon: 'bi-suit-heart',
      badgeClass: 'bg-purple-900/40 text-purple-300 border-purple-500/40',
      description: 'Awal Tahun Baru Liturgi Gereja. Menyalakan Lilin Adven Pertama (Lilin Harapan / Prophecy Candle) menantikan penggenapan janji Allah.',
      bibleVerse: 'Yesaya 9:1 — "Bangsa yang berjalan dalam kegelapan telah melihat terang yang besar; mereka yang diam di negeri kekelaman, atasnya terang telah bersinar."'
    },
    {
      date: format(adven2, 'yyyy-MM-dd'),
      title: 'Minggu Adven II',
      category: 'natal',
      color: 'purple',
      colorName: 'Ungu (Lilin Perdamaian)',
      icon: 'bi-brightness-high',
      badgeClass: 'bg-purple-900/40 text-purple-300 border-purple-500/40',
      description: 'Menyalakan Lilin Adven Kedua (Lilin Perdamaian & Kesetiaan / Bethlehem Candle). Menyiapkan hati yang damai bagi kedatangan Sang Juruselamat.',
      bibleVerse: 'Lukas 3:4 — "Persiapkanlah jalan untuk Tuhan, luruskanlah jalan bagi-Nya."'
    },
    {
      date: format(adven3, 'yyyy-MM-dd'),
      title: 'Minggu Adven III (Gaudete)',
      category: 'natal',
      color: 'pink',
      colorName: 'Merah Muda / Ungu (Sukacita)',
      icon: 'bi-emoji-smile',
      badgeClass: 'bg-pink-950/80 text-pink-300 border-pink-500/50',
      description: 'Menyalakan Lilin Adven Ketiga (Lilin Sukacita / Shepherd Candle). Sukacita karena kedatangan Juruselamat sudah semakin dekat.',
      bibleVerse: 'Filipi 4:4 — "Bersukacitalah senantiasa dalam Tuhan! Sekali lagi kukatakan: Bersukacitalah!"'
    },
    {
      date: format(adven4, 'yyyy-MM-dd'),
      title: 'Minggu Adven IV',
      category: 'natal',
      color: 'purple',
      colorName: 'Ungu (Lilin Kasih)',
      icon: 'bi-heart-fill',
      badgeClass: 'bg-purple-900/40 text-purple-300 border-purple-500/40',
      description: 'Menyalakan Lilin Adven Keempat (Lilin Kasih / Angel Candle). Menyambut wujud cinta kasih Allah yang tak terbatas bagi dunia.',
      bibleVerse: 'Yohanes 3:16 — "Karena begitu besar kasih Allah akan dunia ini, sehingga Ia telah mengaruniakan Anak-Nya yang tunggal..."'
    },
    {
      date: `${year}-12-24`,
      title: 'Malam Natal (Christmas Eve)',
      category: 'natal',
      color: 'white',
      colorName: 'Putih / Emas / Lilin Kristus',
      icon: 'bi-moon-stars-fill',
      badgeClass: 'bg-amber-950/80 text-amber-200 border-amber-500/60',
      description: 'Ibadah Malam Kudus penyambutan kelahiran Sang Juruselamat dengan syahdu dan penyalaan Lilin Kristus bersama seluruh keluarga.',
      bibleVerse: 'Lukas 2:11 — "Hari ini telah lahir bagimu Juruselamat, yaitu Kristus, Tuhan, di kota Daud."'
    },
    {
      date: `${year}-12-25`,
      title: 'Hari Raya Natal (Christmas Day)',
      category: 'natal',
      color: 'gold',
      colorName: 'Putih / Emas',
      icon: 'bi-gift-fill',
      badgeClass: 'bg-gradient-to-r from-amber-500/30 to-emerald-500/30 text-amber-200 border-amber-400/60',
      description: 'Perayaan Agung Kelahiran Yesus Kristus Sang Terang Dunia di Betlehem membawa damai dan keselamatan abadi.',
      bibleVerse: 'Yohanes 1:14 — "Firman itu telah menjadi manusia, dan diam di antara kita, dan kita telah melihat kemuliaan-Nya..."'
    },
    {
      date: `${year}-12-26`,
      title: 'Hari Natal II (St. Stephen / Boxing Day)',
      category: 'natal',
      color: 'gold',
      colorName: 'Putih / Emas',
      icon: 'bi-gift',
      badgeClass: 'bg-amber-400/10 text-amber-200 border-amber-400/40',
      description: 'Hari perayaan Natal kedua, mengucap syukur atas damai Natal dan berbagi kasih dengan sesama.',
      bibleVerse: 'Lukas 2:14 — "Kemuliaan bagi Allah di tempat yang mahatinggi dan damai sejahtera di bumi di antara manusia yang berkenan kepada-Nya."'
    },
    {
      date: `${year}-12-31`,
      title: 'Malam Tutup Tahun / Akhir Tahun (Old Years Eve)',
      category: 'biasa',
      color: 'gold',
      colorName: 'Putih / Emas',
      icon: 'bi-hourglass-bottom',
      badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      description: 'Ibadah tutup tahun penuh syukur merefleksikan berkat dan kebaikan Tuhan sepanjang satu tahun yang telah dilalui.',
      bibleVerse: 'Mazmur 65:12 — "Engkau memahkotai tahun dengan kebaikan-Mu, jejak-Mu mengeluarkan lemak."'
    }
  ]

  return holyDaysList.sort((a, b) => new Date(a.date) - new Date(b.date))
}

// Computeds
const holyDaysList = computed(() => getHolyDaysForYear(selectedYear.value))

const holyDaysMap = computed(() => {
  const map = {}
  holyDaysList.value.forEach(item => {
    map[item.date] = item
  })
  return map
})

// --- Daftar Hari Ulang Tahun Jemaat untuk Tahun Kalender Terpilih ---
const jemaatBirthdaysForYear = computed(() => {
  const currentCalYear = selectedYear.value
  const list = []

  jemaatMembers.value.forEach((u) => {
    if (!u.birth_date) return

    // Filter Cabang Gereja jika dipilih spesifik
    if (selectedBranchFilter.value !== 'all') {
      const branchName = (u.church_domisili || '').trim()
      if (branchName !== selectedBranchFilter.value.trim()) {
        return
      }
    }

    const parts = u.birth_date.split('-')
    if (parts.length < 3) return
    const birthYear = parseInt(parts[0], 10)
    const birthMonth = parts[1] // '01' - '12'
    const birthDay = parts[2] // '01' - '31'

    const calDateKey = `${currentCalYear}-${birthMonth}-${birthDay}`
    const ageThisYear = currentCalYear - birthYear

    list.push({
      id: `bday_${u.id}`,
      userId: u.id,
      name: u.full_name,
      username: u.username,
      church_domisili: u.church_domisili || 'Cabang Mandiri',
      church_central: u.church_central || '',
      birth_date: u.birth_date,
      age: ageThisYear > 0 ? ageThisYear : 0,
      gender: u.gender || 'Laki-laki',
      phone: u.phone || '',
      address: u.address || '',
      date: calDateKey,
      category: 'birthday',
      title: `Ulang Tahun: ${u.full_name}`,
      icon: 'bi-cake2-fill',
      colorName: 'Ulang Tahun Jemaat',
      badgeClass: 'bg-pink-950/80 text-pink-300 border-pink-500/50',
      description: `Perayaan Hari Ulang Tahun ke-${ageThisYear} bagi Saudara/i ${u.full_name} di ${u.church_domisili || 'Cabang Gereja'}. Tanggal lahir resmi: ${u.birth_date}.`,
      bibleVerse: 'Mazmur 90:12 — "Ajarlah kami menghitung hari-hari kami sedemikian, hingga kami beroleh hati yang bijaksana."'
    })
  })

  return list.sort((a, b) => new Date(a.date) - new Date(b.date))
})

// Peta Ulang Tahun Jemaat Berdasarkan Kunci Tanggal (YYYY-MM-DD)
const birthdaysMap = computed(() => {
  const map = {}
  jemaatBirthdaysForYear.value.forEach((b) => {
    if (!map[b.date]) {
      map[b.date] = []
    }
    map[b.date].push(b)
  })
  return map
})

// --- Daftar Agenda Kegiatan Gereja dari Database untuk Tahun Terpilih ---
const churchAgendasForYear = computed(() => {
  const currentCalYear = selectedYear.value
  return churchAgendas.value
    .filter((a) => {
      if (!a.start_date) return false
      const parts = a.start_date.split('-')
      if (parts.length < 1) return false
      const year = parseInt(parts[0], 10)
      if (year !== currentCalYear) return false

      if (selectedBranchFilter.value !== 'all') {
        const branchName = (a.church_name || '').trim()
        if (branchName !== 'Semua Cabang' && branchName !== selectedBranchFilter.value.trim()) {
          return false
        }
      }
      return true
    })
    .map((a) => ({
      id: `agenda_${a.id}`,
      agendaId: a.id,
      title: a.title,
      category: 'kegiatan',
      subCategory: a.category || 'Ibadah',
      color: a.color || 'amber',
      colorName: a.category || 'Kegiatan Gereja',
      icon: 'bi-calendar-check-fill',
      badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      date: a.start_date,
      time: a.start_time || '',
      location: a.location || '',
      organizer: a.organizer || 'Majelis Gereja',
      church_name: a.church_name || 'Semua Cabang',
      target_audience: a.target_audience || 'Semua Jemaat',
      status: a.status || 'Akan Datang',
      description: a.description || `Agenda ${a.category} di ${a.church_name || 'Gereja'}. Waktu: ${a.start_time || 'Fleksibel'}. Lokasi: ${a.location || '-'}. Penanggung Jawab: ${a.organizer || 'Majelis Gereja'}.`,
      bibleVerse: ''
    }))
})

const churchAgendasMap = computed(() => {
  const map = {}
  churchAgendasForYear.value.forEach((a) => {
    if (!map[a.date]) map[a.date] = []
    map[a.date].push(a)
  })
  return map
})

// --- Matriks Kalender Otomatis & Presisi Menggunakan date-fns ---
// Menghitung startOfWeek, endOfWeek, eachDayOfInterval secara matematis 100% akurat
const calendarDays = computed(() => {
  const monthDate = new Date(selectedYear.value, selectedMonth.value, 1)
  const monthStart = startOfMonth(monthDate)
  const monthEnd = endOfMonth(monthDate)

  // Hari pertama grid selalu dimulai dari hari Minggu (weekStartsOn: 0)
  const gridStart = startOfWeek(monthStart, { weekStartsOn: 0 })
  const gridEnd = endOfWeek(monthEnd, { weekStartsOn: 0 })

  // Dapatkan seluruh tanggal dalam rentang dengan fungsi date-fns
  const intervalDays = eachDayOfInterval({ start: gridStart, end: gridEnd })

  // Standarisasi grid 42 cell (6 baris x 7 kolom) agar tata letak kalender konsisten dan kokoh
  const days = [...intervalDays]
  while (days.length < 42) {
    days.push(addDays(days[days.length - 1], 1))
  }

  return days.map((d) => {
    const dateKey = format(d, 'yyyy-MM-dd')
    const isCurrent = isSameMonth(d, monthStart)
    const isTodayDate = isToday(d)
    const isSunday = getDay(d) === 0
    const holy = (eventTypeFilter.value !== 'birthday' && eventTypeFilter.value !== 'kegiatan') ? (holyDaysMap.value[dateKey] || null) : null
    const bdays = (eventTypeFilter.value !== 'liturgi' && eventTypeFilter.value !== 'kegiatan') ? (birthdaysMap.value[dateKey] || []) : []
    const ags = (eventTypeFilter.value !== 'liturgi' && eventTypeFilter.value !== 'birthday') ? (churchAgendasMap.value[dateKey] || []) : []

    return {
      dateObj: d,
      dayNumber: getDate(d),
      dateKey,
      isCurrentMonth: isCurrent,
      isToday: isTodayDate,
      isSunday,
      holyDay: holy,
      birthdays: bdays,
      agendas: ags
    }
  })
})

// Selected Holy Day & Birthdays & Agendas Details
const selectedHolyDay = ref(null)
const selectedBirthdays = ref([])
const selectedChurchAgendas = ref([])
const selectedDateKey = ref('')

const handleSelectDate = (cell) => {
  selectedDateKey.value = cell.dateKey
  selectedHolyDay.value = cell.holyDay || null
  selectedBirthdays.value = cell.birthdays || []
  selectedChurchAgendas.value = cell.agendas || []
}

// Navigasi Bulan & Tahun
const prevMonth = () => {
  if (selectedMonth.value === 0) {
    selectedMonth.value = 11
    selectedYear.value--
  } else {
    selectedMonth.value--
  }
  selectedHolyDay.value = null
  selectedBirthdays.value = []
  selectedChurchAgendas.value = []
}

const nextMonth = () => {
  if (selectedMonth.value === 11) {
    selectedMonth.value = 0
    selectedYear.value++
  } else {
    selectedMonth.value++
  }
  selectedHolyDay.value = null
  selectedBirthdays.value = []
  selectedChurchAgendas.value = []
}

const prevYear = () => {
  selectedYear.value--
  selectedHolyDay.value = null
  selectedBirthdays.value = []
  selectedChurchAgendas.value = []
}

const nextYear = () => {
  selectedYear.value++
  selectedHolyDay.value = null
  selectedBirthdays.value = []
  selectedChurchAgendas.value = []
}

const resetToToday = () => {
  const now = new Date()
  selectedYear.value = now.getFullYear()
  selectedMonth.value = now.getMonth()
  const todayKey = format(now, 'yyyy-MM-dd')
  selectedDateKey.value = todayKey
  selectedHolyDay.value = holyDaysMap.value[todayKey] || null
  selectedBirthdays.value = birthdaysMap.value[todayKey] || []
  selectedChurchAgendas.value = churchAgendasMap.value[todayKey] || []
}

// Filtered List untuk Tab Daftar Lengkap
const filteredAgendaList = computed(() => {
  let list = []
  if (eventTypeFilter.value === 'all') {
    list = [...holyDaysList.value, ...churchAgendasForYear.value, ...jemaatBirthdaysForYear.value]
  } else if (eventTypeFilter.value === 'liturgi') {
    list = [...holyDaysList.value]
  } else if (eventTypeFilter.value === 'kegiatan') {
    list = [...churchAgendasForYear.value]
  } else if (eventTypeFilter.value === 'birthday') {
    list = [...jemaatBirthdaysForYear.value]
  }

  // Filter sub-kategori liturgi jika bukan mode birthday/kegiatan
  if (activeFilter.value !== 'all' && eventTypeFilter.value !== 'birthday' && eventTypeFilter.value !== 'kegiatan') {
    list = list.filter(item => item.category === activeFilter.value)
  }

  return list.sort((a, b) => new Date(a.date) - new Date(b.date))
})


// Alias untuk kompatibilitas kode template lama
const filteredHolyDays = filteredAgendaList

// Event Terdekat dari Hari Ini (Liturgi atau Ulang Tahun Jemaat)
const upcomingHolyDay = computed(() => {
  const today = format(new Date(), 'yyyy-MM-dd')
  const combined = [...holyDaysList.value, ...jemaatBirthdaysForYear.value].sort((a, b) => new Date(a.date) - new Date(b.date))
  const upcoming = combined.find(item => item.date >= today)
  if (!upcoming) return combined[0] || holyDaysList.value[0]
  return upcoming
})

// Hitung Mundur Hari dengan date-fns
const getDaysUntil = (dateStr) => {
  try {
    const target = parseISO(dateStr)
    const diffDays = differenceInDays(startOfDay(target), startOfDay(new Date()))
    if (diffDays === 0) return 'Hari Ini!'
    if (diffDays < 0) return `${Math.abs(diffDays)} hari lalu`
    return `${diffDays} hari lagi`
  } catch (e) {
    return ''
  }
}

// Generator URL Ucapan Selamat Ulang Tahun WhatsApp
const getWhatsAppGreetingUrl = (b) => {
  const cleanPhone = (b.phone || '').replace(/[^0-9]/g, '')
  const formattedPhone = cleanPhone.startsWith('0') ? '62' + cleanPhone.slice(1) : cleanPhone
  const message = `Shalom Saudara/i ${b.name},\n\nSelamat Ulang Tahun yang ke-${b.age}! 🎉🎂\n\nKiranya kasih karunia, damai sejahtera, dan sukacita dari Tuhan Yesus Kristus senantiasa melimpah dalam kehidupan dan pelayanan Saudara/i di ${b.church_domisili}.\n\n"Tuhan memberkati engkau dan melindungi engkau; Tuhan menyinari engkau dengan wajah-Nya dan memberi engkau kasih karunia." (Bilangan 6:24-25)\n\nSalam hangat & doa dari seluruh pelayan & jemaat GracePoint.`
  return `https://wa.me/${formattedPhone}?text=${encodeURIComponent(message)}`
}
</script>

<template>
  <CalendarLayout>
    <!-- HERO SECTION (Identik dengan HomeView.vue) -->
    <div class="mainBody" id="home"> 
      <!-- Dark Overlay Layer & Content Wrapper -->
      <div class="hero-overlay"></div>
      <div class="content-wrapper z-10 relative">
        <div class="headerLogo" data-aos="zoom-in">
          <img src="@/assets/images/GracePoint.png" alt="logo_gracepoint" class="imgSize">
        </div>

        <h1 class="headertext">Kalender Hari Besar Gereja {{ selectedYear }}</h1>
        <p class="subtext">Jadwal lengkap perayaan hari-hari besar gerejawi, penanggalan Paskah &amp; Natal masehi, serta penataan warna liturgi gereja.</p>

        <div class="button-container">
          <a 
            href="#kalender"
            class="portal-button bg-amber-500 hover:bg-amber-400 text-[#070c1e] border-amber-300 shadow-lg shadow-amber-500/25 flex items-center justify-center no-underline"
          >
            <span class="no-underline text-[#070c1e] font-bold">Lihat Kalender Liturgi</span>
          </a>
          <a 
            href="#bigday"
            class="portal-button bg-sky-500 hover:bg-sky-400 text-[#070c1e] border-sky-300 shadow-lg shadow-sky-500/25 flex items-center justify-center no-underline"
          >
            <span class="no-underline text-[#070c1e] font-bold">Jadwal Hari Raya</span>
          </a>
        </div>
      </div>
    </div>

    <div class="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8 font-sans relative overflow-hidden">
      
      <!-- Visual Ambient Glow Overlay -->
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none animate-pulse"></div>
      <div class="absolute top-1/3 -right-40 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none animate-pulse" style="animation-delay: 1.5s;"></div>
      <div class="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-25 pointer-events-none"></div>

      <div class="max-w-6xl mx-auto space-y-8 relative z-10">

        <!-- Page Banner Header dengan AOS Animation -->
        <div class="text-center space-y-3" data-aos="fade-down" id="bigday">
          <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-amber-950/80 via-slate-900 to-purple-950/80 border border-amber-500/30 text-amber-300 text-xs font-semibold uppercase tracking-widest shadow-lg animate__animated animate__pulse animate__infinite">
            <i class="bi bi-journal-bookmark-fill text-amber-400"></i>
            <span>Kalender Liturgi & Hari Raya Gereja</span>
          </div>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-400 to-amber-100 tracking-tight font-serif">
            Kalender Hari Besar Kristen {{ selectedYear }}
          </h1>
          <p class="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed" id="bigday">
            Jadwal lengkap perayaan hari-hari besar gerejawi, penanggalan Paskah & Natal masehi, serta penataan warna liturgi gereja.
          </p>
        </div>

        <!-- Upcoming Featured Banner dengan AOS & Animate.css -->
        <div 
          v-if="upcomingHolyDay" 
          data-aos="zoom-in"
          class="bg-gradient-to-r from-amber-950/70 via-slate-900 to-purple-950/70 border border-amber-500/40 rounded-2xl p-5 sm:p-6 backdrop-blur-xl shadow-2xl shadow-amber-950/20 flex flex-col md:flex-row items-center justify-between gap-6 hover:border-amber-400/60 transition-all duration-500"
        >
          <div class="flex items-center space-x-4">
            <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-amber-600 to-amber-400 p-0.5 shadow-lg shadow-amber-500/30 shrink-0">
              <div class="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center text-amber-400">
                <i :class="['bi', upcomingHolyDay.icon || 'bi-calendar-event', 'text-2xl']"></i>
              </div>
            </div>
            <div>
              <span class="text-xs font-semibold text-amber-400 uppercase tracking-widest flex items-center gap-1.5 mb-0.5">
                <i class="bi bi-clock-history"></i> Hari Raya Mendatang
              </span>
              <h2 class="text-xl font-bold text-white font-serif tracking-wide">{{ upcomingHolyDay.title }}</h2>
              <p class="text-xs text-slate-300 mt-1 flex items-center gap-2 flex-wrap">
                <span><i class="bi bi-calendar3 text-amber-400"></i> {{ upcomingHolyDay.date }}</span>
                <span class="text-slate-600">•</span>
                <span>Warna Liturgi: <strong class="text-amber-200 font-semibold">{{ upcomingHolyDay.colorName }}</strong></span>
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-3 shrink-0">
            <div class="px-4 py-2 bg-slate-950/90 border border-amber-500/40 rounded-xl text-center shadow-inner">
              <span class="text-[10px] text-slate-400 block font-mono uppercase">HITUNG MUNDUR</span>
              <span class="text-sm font-bold text-amber-300 font-mono flex items-center justify-center gap-1">
                <i class="bi bi-[#070c1e] bi-hourglass-split"></i> {{ getDaysUntil(upcomingHolyDay.date) }}
              </span>
            </div>
            <button 
              @click="selectedHolyDay = upcomingHolyDay" 
              class="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-bold text-xs rounded-xl transition-all duration-200 shadow-lg shadow-amber-500/25 flex items-center gap-1.5 cursor-pointer"
            >
              <i class="bi bi-book-half"></i>
              <span>Lihat Makna</span>
            </button>
          </div>
        </div>

        <!-- Controls: Tab Switcher & Filters dengan AOS -->
        <div data-aos="fade-up" class="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 bg-slate-900/80 p-3.5 rounded-2xl border border-slate-800 backdrop-blur-md">
          
          <!-- Mode View Switcher (Kalender / Daftar) -->
          <div class="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800/80 shrink-0" id="kalender">
            <button 
              @click="activeTab = 'calendar'"
              :class="activeTab === 'calendar' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-400 hover:text-white'"
              class="px-3.5 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer"
            >
              <i class="bi bi-calendar3"></i>
              <span>Kalender</span>
            </button>
            <button 
              @click="activeTab = 'list'"
              :class="activeTab === 'list' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'text-slate-400 hover:text-white'"
              class="px-3.5 py-1.5 rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer"
            >
              <i class="bi bi-list-ul"></i>
              <span>Daftar Agenda ({{ filteredAgendaList.length }})</span>
            </button>
          </div>

          <!-- Filter Kategori Event: Semua | Liturgi | Kegiatan Gereja | Ultah Jemaat -->
          <div class="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800/80 text-xs shrink-0 overflow-x-auto">
            <button 
              @click="eventTypeFilter = 'all'"
              :class="eventTypeFilter === 'all' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-white'"
              class="px-2.5 py-1 rounded-lg transition cursor-pointer whitespace-nowrap"
            >
              Semua Agenda
            </button>
            <button 
              @click="eventTypeFilter = 'liturgi'"
              :class="eventTypeFilter === 'liturgi' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-white'"
              class="px-2.5 py-1 rounded-lg transition cursor-pointer whitespace-nowrap"
            >
              Liturgi Gereja
            </button>
            <button 
              @click="eventTypeFilter = 'kegiatan'"
              :class="eventTypeFilter === 'kegiatan' ? 'bg-amber-500 text-slate-950 font-bold shadow' : 'text-slate-400 hover:text-white'"
              class="px-2.5 py-1 rounded-lg transition cursor-pointer flex items-center gap-1 whitespace-nowrap"
            >
              <i class="bi bi-calendar2-check-fill text-[11px]"></i>
              <span>Kegiatan Gereja ({{ churchAgendasForYear.length }})</span>
            </button>
            <button 
              @click="eventTypeFilter = 'birthday'"
              :class="eventTypeFilter === 'birthday' ? 'bg-pink-600 text-white font-bold shadow' : 'text-slate-400 hover:text-white'"
              class="px-2.5 py-1 rounded-lg transition cursor-pointer flex items-center gap-1 whitespace-nowrap"
            >
              <span>🎂</span>
              <span>Ultah Jemaat ({{ jemaatBirthdaysForYear.length }})</span>
            </button>
          </div>

          <!-- Filter Cabang Gereja & Pemilih Tahun -->
          <div class="flex flex-wrap items-center gap-2.5 justify-end">
            <!-- Filter Cabang Gereja -->
            <div class="relative">
              <select 
                v-model="selectedBranchFilter"
                class="px-3 py-1.5 pr-8 bg-slate-950 border border-slate-700/80 rounded-xl text-xs text-amber-300 font-semibold focus:outline-none focus:border-amber-400 cursor-pointer appearance-none max-w-[200px] truncate"
              >
                <option value="all">Semua Cabang Gereja</option>
                <option v-for="branch in availableBranches" :key="branch" :value="branch">
                  {{ branch }}
                </option>
              </select>
              <i class="bi bi-geo-alt-fill absolute right-2.5 top-1/2 -translate-y-1/2 text-amber-400 text-[10px] pointer-events-none"></i>
            </div>

            <!-- Tombol Hari Ini & Stepper Tahun Dinamis -->
            <div class="flex items-center gap-2">
              <button 
                @click="resetToToday"
                class="px-3 py-1.5 bg-slate-950 hover:bg-slate-800 text-amber-400 border border-slate-700/80 rounded-xl text-xs font-semibold transition cursor-pointer flex items-center gap-1"
                title="Kembali ke Hari Ini"
              >
                <i class="bi bi-bullseye"></i> Hari Ini
              </button>

              <!-- Quick Stepper Tahun & Dropdown Tahun Dinamis (date-fns) -->
              <div class="flex items-center bg-slate-950 border border-slate-700/90 rounded-xl p-0.5 shadow-sm">
                <button 
                  @click="prevYear" 
                  class="px-2 py-1 text-slate-400 hover:text-amber-300 hover:bg-slate-800 rounded-lg text-xs transition cursor-pointer"
                  title="Tahun Sebelumnya"
                >
                  <i class="bi bi-chevron-double-left"></i>
                </button>
                <div class="relative">
                  <select 
                    v-model.number="selectedYear"
                    class="px-2.5 py-1 pr-6 bg-transparent text-amber-300 font-bold text-xs focus:outline-none cursor-pointer appearance-none"
                  >
                    <option v-for="y in availableYears" :key="y" :value="y" class="bg-slate-900 text-amber-300">
                      Tahun {{ y }}
                    </option>
                  </select>
                  <i class="bi bi-chevron-down absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 text-[9px] pointer-events-none"></i>
                </div>
                <button 
                  @click="nextYear" 
                  class="px-2 py-1 text-slate-400 hover:text-amber-300 hover:bg-slate-800 rounded-lg text-xs transition cursor-pointer"
                  title="Tahun Berikutnya"
                >
                  <i class="bi bi-chevron-double-right"></i>
                </button>
              </div>
            </div>
          </div>

        </div>

        <!-- MAIN VIEW 1: Tampilan Grid Kalender Interaktif -->
        <div v-if="activeTab === 'calendar'" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <!-- Calendar Grid Box (2 Cols) -->
          <div data-aos="fade-right" class="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md space-y-4">
            
            <!-- Month Header Navigation -->
            <div class="flex items-center justify-between px-2 py-1 border-b border-slate-800 pb-3">
              <button 
                @click="prevMonth"
                class="p-2 bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-amber-300 rounded-xl border border-slate-800 transition flex items-center justify-center cursor-pointer"
                title="Bulan Sebelumnya"
              >
                <i class="bi bi-chevron-left"></i>
              </button>

              <div class="text-center">
                <h2 class="text-lg font-bold text-amber-300 font-serif tracking-wide flex items-center justify-center gap-2">
                  <i class="bi bi-calendar3"></i>
                  <span>{{ monthNames[selectedMonth] }} {{ selectedYear }}</span>
                </h2>
                <div class="flex items-center justify-center gap-2 mt-0.5">
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 text-[10px] font-semibold border border-amber-500/20">
                    <i class="bi bi-book-half"></i> {{ liturgicalYearCycle.cycle }} ({{ liturgicalYearCycle.focus }})
                  </span>
                  <span v-if="selectedBranchFilter !== 'all'" class="text-[11px] text-slate-400">
                    • Cabang: <strong class="text-amber-400">{{ selectedBranchFilter }}</strong>
                  </span>
                </div>
              </div>

              <button 
                @click="nextMonth"
                class="p-2 bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-amber-300 rounded-xl border border-slate-800 transition flex items-center justify-center cursor-pointer"
                title="Bulan Berikutnya"
              >
                <i class="bi bi-chevron-right"></i>
              </button>
            </div>

            <!-- Days of Week Header -->
            <div class="grid grid-cols-7 text-center font-bold text-xs text-slate-400 py-1 font-serif">
              <span class="text-amber-400">Minggu</span>
              <span>Senin</span>
              <span>Selasa</span>
              <span>Rabu</span>
              <span>Kamis</span>
              <span>Jumat</span>
              <span>Sabtu</span>
            </div>

            <!-- Date Cells Grid -->
            <div class="grid grid-cols-7 gap-1.5 sm:gap-2">
              <div 
                v-for="(cell, index) in calendarDays" 
                :key="index"
                @click="handleSelectDate(cell)"
                :class="[
                  'min-h-[70px] sm:min-h-[82px] p-1.5 rounded-xl border transition-all duration-300 cursor-pointer flex flex-col justify-between relative group hover:-translate-y-0.5',
                  cell.isCurrentMonth ? 'bg-slate-950/70 border-slate-800/80 hover:border-amber-500/60 shadow-sm' : 'bg-slate-950/20 border-transparent opacity-30',
                  cell.isToday ? 'ring-2 ring-amber-400 ring-offset-2 ring-offset-slate-950' : '',
                  cell.holyDay || (cell.birthdays && cell.birthdays.length > 0) || (cell.agendas && cell.agendas.length > 0) ? 'bg-gradient-to-b from-slate-900 to-slate-950 border-amber-500/40 shadow-lg shadow-amber-950/20' : ''
                ]"
              >
                <!-- Day Number & Indicators -->
                <div class="flex items-center justify-between">
                  <span 
                    :class="[
                      'text-xs font-bold font-mono px-1.5 py-0.5 rounded-md',
                      cell.isToday ? 'bg-amber-400 text-slate-950 shadow-sm' : cell.isCurrentMonth ? (cell.isSunday ? 'text-amber-400' : 'text-slate-200') : 'text-slate-600'
                    ]"
                  >
                    {{ cell.dayNumber }}
                  </span>
                  
                  <div class="flex items-center gap-1">
                    <!-- Icon Agenda Gereja -->
                    <span v-if="cell.agendas && cell.agendas.length > 0" class="w-1.5 h-1.5 rounded-full bg-amber-400" title="Ada agenda kegiatan gereja"></span>
                    <!-- Icon Ulang Tahun Jemaat -->
                    <span v-if="cell.birthdays && cell.birthdays.length > 0" class="text-[11px]" title="Ada jemaat ulang tahun">🎂</span>
                    <!-- Indicator Icon jika Hari Raya -->
                    <span v-if="cell.holyDay" class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
                  </div>
                </div>

                <!-- Event Snippets on date cell -->
                <div class="mt-1 space-y-1">
                  <!-- Holy Day Snippet -->
                  <span 
                    v-if="cell.holyDay"
                    class="text-[9px] sm:text-[10px] font-semibold leading-tight line-clamp-1 px-1 py-0.5 rounded border block font-sans"
                    :class="cell.holyDay.badgeClass"
                  >
                    <i :class="['bi', cell.holyDay.icon || 'bi-bookmark-star', 'me-0.5']"></i>
                    {{ cell.holyDay.title }}
                  </span>

                  <!-- Church Agenda Snippet -->
                  <span 
                    v-if="cell.agendas && cell.agendas.length > 0 && !cell.holyDay"
                    class="text-[9px] sm:text-[10px] font-semibold leading-tight line-clamp-1 px-1 py-0.5 rounded border block font-sans bg-amber-500/20 text-amber-200 border-amber-500/40 hover:bg-amber-500/30 transition"
                  >
                    <i class="bi bi-calendar-event me-0.5 text-[8px]"></i>
                    {{ cell.agendas[0].title }}
                  </span>

                  <!-- Birthday Snippet -->
                  <span 
                    v-if="cell.birthdays && cell.birthdays.length > 0 && !cell.holyDay && (!cell.agendas || cell.agendas.length === 0)"
                    class="text-[9px] sm:text-[10px] font-semibold leading-tight line-clamp-1 px-1 py-0.5 rounded border block font-sans bg-pink-950/80 text-pink-300 border-pink-500/40 hover:bg-pink-900/90 transition"
                  >
                    🎂 {{ cell.birthdays.length === 1 ? `${cell.birthdays[0].name.split(' ')[0]} (ke-${cell.birthdays[0].age})` : `${cell.birthdays.length} Jemaat Ultah` }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Legend Warna Liturgi & Ulang Tahun -->
            <div class="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
              <span class="font-bold text-slate-300 flex items-center gap-1">
                <i class="bi bi-palette text-amber-400"></i> Keterangan Agenda:
              </span>
              <span class="inline-flex items-center gap-1"><span class="text-[11px]">🎂</span> Ulang Tahun Jemaat Cabang</span>
              <span class="inline-flex items-center gap-1"><i class="bi bi-circle-fill text-amber-400 text-[8px]"></i> Putih/Emas (Paskah/Natal)</span>
              <span class="inline-flex items-center gap-1"><i class="bi bi-circle-fill text-purple-500 text-[8px]"></i> Ungu (Adven/Pra-Paskah)</span>
              <span class="inline-flex items-center gap-1"><i class="bi bi-circle-fill text-rose-500 text-[8px]"></i> Merah (Pentakosta)</span>
            </div>

          </div>

          <!-- Detail Card Sidebar (1 Col) dengan AOS -->
          <div data-aos="fade-left" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-2xl backdrop-blur-md flex flex-col justify-between space-y-6">
            
            <!-- Kasus 1: Tanggal yang dipilih memiliki Hari Raya Liturgi ATAU Ulang Tahun Jemaat ATAU Agenda Gereja -->
            <div v-if="selectedHolyDay || (selectedBirthdays && selectedBirthdays.length > 0) || (selectedChurchAgendas && selectedChurchAgendas.length > 0)" class="space-y-5 animate__animated animate__fadeIn">
              
              <!-- Bagian Agenda Kegiatan Gereja (Jika Ada) -->
              <div v-if="selectedChurchAgendas && selectedChurchAgendas.length > 0" class="space-y-3 pb-4 border-b border-slate-800">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold text-amber-400 uppercase tracking-widest font-mono flex items-center gap-1.5">
                    <i class="bi bi-calendar-check-fill"></i> Agenda Kegiatan Gereja
                  </span>
                  <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-950/80 text-amber-300 border border-amber-500/50">
                    {{ selectedChurchAgendas.length }} Kegiatan
                  </span>
                </div>

                <div class="space-y-3">
                  <div 
                    v-for="ag in selectedChurchAgendas" 
                    :key="ag.id"
                    class="p-3.5 rounded-xl bg-gradient-to-br from-[#1c1d24] via-[#141820] to-[#0f141b] border border-amber-500/40 space-y-2 shadow-lg"
                  >
                    <div class="flex items-center justify-between gap-2">
                      <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        {{ ag.subCategory }}
                      </span>
                      <span class="text-[10px] font-semibold text-emerald-400">
                        {{ ag.status }}
                      </span>
                    </div>

                    <h4 class="text-sm font-bold text-white font-serif">{{ ag.title }}</h4>

                    <div class="text-[11px] text-slate-300 space-y-1">
                      <p v-if="ag.time" class="flex items-center gap-1.5 text-amber-200">
                        <i class="bi bi-clock-fill text-amber-400"></i>
                        <span>{{ ag.time }}</span>
                      </p>
                      <p v-if="ag.location" class="flex items-center gap-1.5 text-slate-300">
                        <i class="bi bi-geo-alt-fill text-amber-400"></i>
                        <span>{{ ag.location }}</span>
                      </p>
                      <p class="flex items-center gap-1.5 text-slate-400">
                        <i class="bi bi-buildings-fill text-slate-500"></i>
                        <span>{{ ag.church_name }}</span>
                      </p>
                    </div>

                    <p v-if="ag.description" class="text-[11px] text-slate-400 pt-1 border-t border-slate-800">
                      {{ ag.description }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Bagian Ulang Tahun Jemaat Cabang (Jika Ada) -->
              <div v-if="selectedBirthdays && selectedBirthdays.length > 0" class="space-y-3 pb-4 border-b border-slate-800">
                <div class="flex items-center justify-between">
                  <span class="text-xs font-bold text-pink-400 uppercase tracking-widest font-mono flex items-center gap-1.5">
                    <span>🎂</span> Ulang Tahun Jemaat Cabang
                  </span>
                  <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-pink-950/80 text-pink-300 border border-pink-500/50">
                    {{ selectedBirthdays.length }} Jemaat
                  </span>
                </div>

                <div class="space-y-3">
                  <div 
                    v-for="bday in selectedBirthdays" 
                    :key="bday.id"
                    class="p-3.5 rounded-xl bg-gradient-to-br from-[#1a0f26] via-[#120a1f] to-[#0d0718] border border-pink-500/40 space-y-2 shadow-lg"
                  >
                    <div class="flex items-center justify-between gap-2">
                      <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-full bg-pink-500/20 border border-pink-400/40 text-pink-300 font-bold flex items-center justify-center text-sm font-serif">
                          {{ bday.name ? bday.name.charAt(0) : 'J' }}
                        </div>
                        <div>
                          <h4 class="text-sm font-bold text-white font-serif">{{ bday.name }}</h4>
                          <p class="text-[11px] text-pink-300/90 font-medium">Ulang Tahun ke-{{ bday.age }} Tahun</p>
                        </div>
                      </div>
                      <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-900/80 text-amber-300 font-mono border border-amber-500/30">
                        {{ bday.gender }}
                      </span>
                    </div>

                    <div class="text-[11px] text-slate-300 space-y-0.5">
                      <p class="flex items-center gap-1.5 text-amber-200">
                        <i class="bi bi-geo-alt-fill text-amber-400"></i>
                        <span>{{ bday.church_domisili }}</span>
                      </p>
                      <p class="text-slate-400 flex items-center gap-1.5">
                        <i class="bi bi-calendar-heart text-pink-400"></i>
                        <span>Lahir: {{ bday.birth_date }}</span>
                      </p>
                    </div>

                    <!-- Tombol Kirim Ucapan WhatsApp -->
                    <div class="pt-2 flex items-center justify-between gap-2">
                      <a 
                        v-if="bday.phone"
                        :href="getWhatsAppGreetingUrl(bday)"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="flex-1 px-3 py-1.5 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold text-xs rounded-lg transition flex items-center justify-center gap-1.5 no-underline shadow-md shadow-emerald-600/20"
                      >
                        <i class="bi bi-whatsapp"></i>
                        <span>Kirim Ucapan WA</span>
                      </a>
                      <span v-else class="text-[10px] text-slate-500 italic">Kontak belum tersedia</span>
                    </div>

                    <!-- Ayat Berkat Alkitab -->
                    <div class="p-2.5 rounded-lg bg-pink-950/30 border border-pink-500/20 text-[10px] italic text-pink-200/90 font-serif leading-relaxed">
                      "Karena oleh aku umurmu diperpanjang, dan tahun-tahun hidupmu ditambah." (Amsal 9:11)
                    </div>
                  </div>
                </div>
              </div>

              <!-- Bagian Detail Hari Raya Liturgi (Jika Ada) -->
              <div v-if="selectedHolyDay" class="space-y-4">
                <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span class="text-xs font-bold text-amber-400 uppercase tracking-widest font-mono flex items-center gap-1.5">
                    <i class="bi bi-info-circle"></i> Detail Hari Raya Liturgi
                  </span>
                  <span class="px-2.5 py-0.5 text-[10px] rounded-full font-semibold border" :class="selectedHolyDay.badgeClass">
                    {{ selectedHolyDay.colorName }}
                  </span>
                </div>

                <div>
                  <h3 class="text-xl font-bold text-white font-serif tracking-wide flex items-center gap-2">
                    <i :class="['bi', selectedHolyDay.icon || 'bi-star', 'text-amber-400']"></i>
                    <span>{{ selectedHolyDay.title }}</span>
                  </h3>
                  <p class="text-xs text-amber-300/90 font-mono mt-1 flex items-center gap-1.5">
                    <i class="bi bi-calendar-event"></i>
                    <span>Tanggal: {{ selectedHolyDay.date }}</span>
                  </p>
                </div>

                <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-1.5">
                  <span class="text-[11px] font-semibold text-slate-400 uppercase flex items-center gap-1.5">
                    <i class="bi bi-journal-text text-amber-400"></i> Makna & Tradisi Gereja
                  </span>
                  <p class="text-xs text-slate-200 leading-relaxed">{{ selectedHolyDay.description }}</p>
                </div>

                <div class="bg-amber-950/30 p-3.5 rounded-xl border border-amber-500/30 space-y-1">
                  <span class="text-[11px] font-semibold text-amber-300 uppercase flex items-center gap-1.5">
                    <i class="bi bi-quote text-amber-400 text-sm"></i> Refleksi Alkitab
                  </span>
                  <p class="text-xs italic text-amber-100/90 leading-relaxed font-serif">{{ selectedHolyDay.bibleVerse }}</p>
                </div>
              </div>

            </div>

            <!-- Empty State jika belum pilih tanggal atau tanggal kosong -->
            <div v-else class="h-full flex flex-col items-center justify-center text-center p-6 space-y-3 text-slate-500">
              <div class="w-14 h-14 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-amber-400/70 shadow-inner">
                <i class="bi bi-calendar-heart text-2xl"></i>
              </div>
              <p class="text-xs text-slate-400 leading-relaxed">
                Klik salah satu tanggal pada kalender yang memiliki penanda untuk melihat Hari Raya Gereja atau jadwal Ulang Tahun Jemaat Cabang.
              </p>
            </div>

            <!-- Quick Tip Footer -->
            <div class="pt-4 border-t border-slate-800 text-[11px] text-slate-400 text-center flex items-center justify-center gap-1">
              <i class="bi bi-check-circle-fill text-emerald-400"></i>
              <span>Tanggal lahir jemaat tersinkronisasi otomatis dari basis data gereja.</span>
            </div>
          </div>

        </div>

        <!-- MAIN VIEW 2: Tampilan Daftar Lengkap Kronologis -->
        <div v-else class="space-y-5" data-aos="fade-up">
          
          <!-- Category Filter Bar -->
          <div class="flex items-center space-x-2 text-xs overflow-x-auto pb-2">
            <button 
              @click="activeFilter = 'all'; eventTypeFilter = 'all'"
              :class="activeFilter === 'all' && eventTypeFilter === 'all' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'bg-slate-900 text-slate-300 hover:bg-slate-800'"
              class="px-3.5 py-1.5 rounded-xl border border-slate-800 transition shrink-0 flex items-center gap-1.5 cursor-pointer"
            >
              <i class="bi bi-grid-fill"></i> Semua Agenda
            </button>
            <button 
              @click="eventTypeFilter = 'birthday'"
              :class="eventTypeFilter === 'birthday' ? 'bg-pink-600 text-white font-bold shadow-md' : 'bg-slate-900 text-slate-300 hover:bg-slate-800'"
              class="px-3.5 py-1.5 rounded-xl border border-slate-800 transition shrink-0 flex items-center gap-1.5 cursor-pointer"
            >
              <span>🎂</span> Ulang Tahun Jemaat ({{ jemaatBirthdaysForYear.length }})
            </button>
            <button 
              @click="eventTypeFilter = 'liturgi'; activeFilter = 'paskah'"
              :class="eventTypeFilter === 'liturgi' && activeFilter === 'paskah' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'bg-slate-900 text-slate-300 hover:bg-slate-800'"
              class="px-3.5 py-1.5 rounded-xl border border-slate-800 transition shrink-0 flex items-center gap-1.5 cursor-pointer"
            >
              <i class="bi bi-plus-lg text-amber-400"></i> Siklus Paskah
            </button>
            <button 
              @click="eventTypeFilter = 'liturgi'; activeFilter = 'natal'"
              :class="eventTypeFilter === 'liturgi' && activeFilter === 'natal' ? 'bg-amber-500 text-slate-950 font-bold shadow-md' : 'bg-slate-900 text-slate-300 hover:bg-slate-800'"
              class="px-3.5 py-1.5 rounded-xl border border-slate-800 transition shrink-0 flex items-center gap-1.5 cursor-pointer"
            >
              <i class="bi bi-star-fill text-amber-400"></i> Siklus Natal
            </button>
          </div>

          <!-- Holy Days & Birthdays Cards List -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="(item, idx) in filteredAgendaList" 
              :key="item.id || item.date + idx"
              data-aos="fade-up"
              :data-aos-delay="Math.min(idx * 40, 400)"
              :class="[
                'border rounded-2xl p-5 shadow-xl transition-all duration-300 space-y-3 group hover:-translate-y-1 backdrop-blur-md',
                item.category === 'birthday'
                  ? 'bg-gradient-to-br from-[#180e28] to-[#0c0818] border-pink-500/40 hover:border-pink-400/70'
                  : 'bg-slate-900/80 border-slate-800 hover:border-amber-500/50'
              ]"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <div 
                    :class="[
                      'w-10 h-10 rounded-xl flex items-center justify-center shrink-0 mt-0.5 border transition',
                      item.category === 'birthday'
                        ? 'bg-pink-950/60 border-pink-500/40 text-pink-300'
                        : 'bg-slate-950 border-slate-800 text-amber-400 group-hover:border-amber-500/40'
                    ]"
                  >
                    <i :class="['bi', item.icon || 'bi-bookmark-star', 'text-lg']"></i>
                  </div>
                  <div>
                    <span class="text-xs font-mono text-amber-400 font-semibold flex items-center gap-1">
                      <i class="bi bi-calendar-event"></i> {{ item.date }}
                    </span>
                    <h3 
                      class="text-lg font-bold font-serif mt-0.5 transition"
                      :class="item.category === 'birthday' ? 'text-pink-100 group-hover:text-pink-300' : 'text-white group-hover:text-amber-300'"
                    >
                      {{ item.title }}
                    </h3>
                  </div>
                </div>
                <span class="px-2.5 py-1 text-[11px] font-semibold rounded-lg border shrink-0" :class="item.badgeClass">
                  {{ item.colorName }}
                </span>
              </div>

              <p class="text-xs text-slate-300 leading-relaxed">{{ item.description }}</p>

              <div class="pt-2 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px]">
                <div class="italic text-amber-200/90 font-serif flex items-center gap-1.5">
                  <i class="bi bi-quote text-amber-400 text-sm shrink-0"></i>
                  <span>{{ item.bibleVerse }}</span>
                </div>

                <!-- Tombol WhatsApp untuk Kartu Ultah di List View -->
                <a 
                  v-if="item.category === 'birthday' && item.phone"
                  :href="getWhatsAppGreetingUrl(item)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg text-xs flex items-center gap-1 no-underline transition self-start sm:self-auto shrink-0"
                >
                  <i class="bi bi-whatsapp"></i>
                  <span>Kirim WA</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </CalendarLayout>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Lato:wght@400;500;700&display=swap');

.mainBody {
  background: url(https://media.istockphoto.com/id/1271405992/id/vektor/konsep-ibadah-kekristenan-futuristik-dengan-alkitab-terbuka-poligonal-rendah-bersinar-dan.jpg?s=612x612&w=0&k=20&c=qf1QAy8mlLTSlOg4DrvoCelAOoiApQe2XKUlan6zNj0=);
  min-height: 80vh;
  width: 100%;
  padding: 4rem 1.5rem;
  animation: fadeUp 1s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  box-shadow: inset 0 0 0 1000px rgba(0, 0, 0, 0.7);
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(7, 12, 25, 0.40) 0%, rgba(7, 12, 25, 0.20) 50%, rgba(7, 12, 25, 0.70) 100%);
  backdrop-filter: blur(1px);
  pointer-events: none;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  max-width: 900px;
}

.headerLogo {
  margin-top: -1rem;
  margin-bottom: 1.5rem;
}

.imgSize {
  width: 210px;
  height: 210px;
  animation: fadeUp 1s ease-in-out;
  transition: transform 0.3s ease, filter 0.3s ease;
  cursor: pointer;
}

.imgSize:hover {
  transform: scale(1.05);
  filter: drop-shadow(0 0 18px rgba(251, 191, 36, 0.6)); 
}

.headertext {
  font-family: 'Cinzel', 'Times New Roman', serif;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-align: center;
  margin-top: -1.5rem;
  margin-bottom: 1rem;
  color: #fbbf24;
  text-shadow: 0 4px 18px rgba(245, 158, 11, 0.35);
  animation: slideIn 1s ease-in-out;
  transition: transform 0.3s ease, filter 0.3s ease;
  cursor: pointer;
}

.headertext:hover {
  transform: scale(1.03);
  filter: drop-shadow(0 0 15px rgba(251, 191, 36, 0.5));
}

.subtext {
  font-family: 'Lato', 'Helvetica Neue', sans-serif;
  font-size: 1.25rem;
  line-height: 1.6;
  text-align: center;
  color: #cbd5e1;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.85);
  max-width: 680px;
  margin-top: -0.5rem;
  margin-bottom: 2.5rem;
  font-weight: 500;
  animation: slideIn 1s ease-in-out;
  transition: transform 0.3s ease, filter 0.3s ease;
  cursor: pointer;
}

.subtext:hover {
  transform: scale(1.02);
  filter: drop-shadow(0 0 15px rgba(251, 191, 36, 0.5));
}

.button-container {
  display: flex;
  flex-direction: row;
  gap: 1.25rem;
  animation: fadeUp 1s ease-in-out 0.2s;
  animation-fill-mode: backwards;
  margin-top: 0;
  justify-content: center;
  flex-wrap: wrap;
}

.portal-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.75rem;
  border-width: 1px;
  border-radius: 0.5rem;
  font-family: 'Lato', 'Helvetica Neue', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.825rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  min-width: 240px;
  justify-content: center;
  text-decoration: none !important;
  color: #070c1e !important;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  } 
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Custom Line Clamp */
.line-clamp-2 {
  display: -webkit-box;
  --webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Light Theme Overrides */
:global(html[data-theme="light"]) {
  .mainBody {
    box-shadow: inset 0 0 0 1000px rgba(255, 255, 255, 0.75);
  }
  .hero-overlay {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(240, 249, 255, 0.78) 50%, rgba(224, 242, 254, 0.92) 100%);
  }
  .headertext {
    color: #b45309;
    text-shadow: 0 2px 12px rgba(217, 119, 6, 0.25);
  }
  .subtext {
    color: #1e293b;
    text-shadow: 0 1px 4px rgba(255, 255, 255, 0.8);
  }
}
</style>


