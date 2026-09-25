<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChurchHistoryLayout from '@/layouts/ChurchHistoryLayout.vue'
import AOS from 'aos'
import 'aos/dist/aos.css'

// --- State Mesin Pencari ---
const searchQuery = ref('')
const selectedDenomination = ref('all')
const selectedRegion = ref('all')
const selectedEra = ref('all')
const sortBy = ref('origin-asc') // 'year-asc' | 'year-desc' | 'name-asc' | 'name-desc'
const viewMode = ref('grid') // 'grid' | 'timeline'
const onlyBookmarks = ref(false)

const searchInputRef = ref(null)
const selectedChurch = ref(null) // Modal Detail Gereja
const isDetailModalOpen = ref(false)
const selectedCorridor = ref(null) // Modal Detail Jalur Misi
const isCorridorModalOpen = ref(false)
const selectedCorridorCategory = ref('all') // 'all' | 'kuno_voc' | 'zending_19' | 'sulawesi_pedalaman' | 'gerakan_modern'
const toastMessage = ref('')
const isToastVisible = ref(false)

// --- LocalStorage Bookmarks ---
const bookmarkedIds = ref([])

const loadBookmarks = () => {
  try {
    const saved = localStorage.getItem('gracepoint_church_history_bookmarks')
    if (saved) {
      bookmarkedIds.value = JSON.parse(saved)
    }
  } catch (e) {
    console.warn('Gagal membaca bookmark dari localStorage:', e)
  }
}

const toggleBookmark = (id) => {
  if (bookmarkedIds.value.includes(id)) {
    bookmarkedIds.value = bookmarkedIds.value.filter(item => item !== id)
    showToast('Dihapus dari daftar yang disimpan')
  } else {
    bookmarkedIds.value.push(id)
    showToast('Ditambahkan ke daftar yang disimpan')
  }
  try {
    localStorage.setItem('gracepoint_church_history_bookmarks', JSON.stringify(bookmarkedIds.value))
  } catch (e) {}
}

const showToast = (msg) => {
  toastMessage.value = msg
  isToastVisible.value = true
  setTimeout(() => {
    isToastVisible.value = false
  }, 2600)
}

// Focus Search Input
const focusSearch = () => {
  viewMode.value = 'grid'
  nextTick(() => {
    if (searchInputRef.value) {
      searchInputRef.value.focus()
      searchInputRef.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

// Quick Search Chips dengan Pembedaan Misi vs Sinode
const quickQueries = [
  { label: 'GMIT (Misi 1614 / Sinode 1947)', query: 'GMIT' },
  { label: 'GKI (THKTKH 1920 / Fusi 1988)', query: 'GKI' },
  { label: 'GBI (Akar 1921 / Sinode 1970)', query: 'GBI Senduk' },
  { label: 'GPM (VOC 1605 / Sinode 1935)', query: 'GPM' },
  { label: 'Katolik (Xaverius 1546 / KWI 1961)', query: 'Katolik' },
  { label: 'Mentawai GKPM (1901 / 1968)', query: 'Mentawai' },
  { label: 'Methodist (GMI 1905)', query: 'Methodist' },
  { label: 'Gereja Riau & Minyak', query: 'Riau' },
  { label: 'Bengkulu Marlborough', query: 'Bengkulu' },
  { label: 'GKPS Simalungun (1903)', query: 'Simalungun' },
  { label: 'GKPA Angkola (1861)', query: 'Angkola' },
  { label: 'GKPI Pembaruan 1964', query: 'GKPI' },
  { label: 'HKI Pantoan 1927', query: 'HKI' },
  { label: 'Bali Blimbingsari 1931', query: 'Bali' },
  { label: 'GKST Danau Poso 1892', query: 'GKST' },
  { label: 'GMIST Sangihe 1857', query: 'Sangihe' },
  { label: 'GMIH Halmahera 1866', query: 'Halmahera' },
  { label: 'GKMI Muria Kudus 1920', query: 'GKMI' },
  { label: 'GKPPD Pakpak Dairi', query: 'Pakpak' },
  { label: 'HKBP Nommensen 1861', query: 'Nommensen' },
  { label: 'Mansinam Papua 1855', query: 'Mansinam' },
  { label: 'Kyai Sadrach Karangjoso', query: 'Sadrach' },
  { label: 'Pentakosta Cepu 1921', query: 'Cepu' }
]

const setQuickQuery = (q) => {
  searchQuery.value = q
  focusSearch()
}

const clearSearch = () => {
  searchQuery.value = ''
  selectedDenomination.value = 'all'
  selectedRegion.value = 'all'
  selectedEra.value = 'all'
  onlyBookmarks.value = false
}

// --- Ensiklopedia Basis Data Sejarah Cikal Bakal Gereja-Gereja di Indonesia ---
const churchData = ref([
  {
    id: 'hkbp',
    name: 'HKBP (Huria Kristen Batak Protestan)',
    shortName: 'HKBP',
    fullName: 'Huria Kristen Batak Protestan',
    originYear: 1861,
    originEvent: 'Pekabaran Injil RMG Barmen Resmi Dimulai di Silindung (7 Oktober 1861)',
    synodYear: 1930,
    synodEvent: 'Pengesahan Anggaran Dasar & Kemandirian Sinode Mandiri HKBP di Pearaja (1 Mei 1930)',
    era: 'zending_19',
    eraLabel: 'Abad 19 (Misi Zending)',
    region: 'Sumatera',
    subRegion: 'Pearaja Tarutung, Tapanuli Utara, Sumatera Utara',
    denomination: 'Protestan',
    tradition: 'Lutheran / Reformed',
    oikoumene: ['PGI', 'LWF (Lutheran World Federation)', 'WCC'],
    founder: 'Dr. Ingwer Ludwig Nommensen ("Apostel Batak"), Pdt. Johannes Warneck, Pdt. P.H. Betz',
    missionAgency: 'Rheinische Missionsgesellschaft (RMG) Barmen, Jerman',
    currentHeadquarters: 'Pearaja, Tarutung, Tapanuli Utara, Sumatera Utara',
    summary: 'Sinode gereja Protestan terbesar di Asia Tenggara yang berakar dari pekabaran Injil RMG Barmen di Lembah Silindung, mentransformasi tatanan adat Batak dengan Injil, pendidikan, dan kesehatan.',
    fullStory: `
      Pekabaran Injil di Tanah Batak diawali dengan pengorbanan para pekabar Injil pendahulu seperti Munson dan Lyman dari Boston (1834). Tonggak kebangunan besar terjadi ketika Dr. Ingwer Ludwig Nommensen, misionaris berkebangsaan Jerman yang diutus oleh RMG (Rheinische Missionsgesellschaft) Barmen, tiba di Barus pada 1861 dan berani melangkah masuk ke Lembah Silindung (Tarutung) pada Mei 1864.
      
      Dengan pendekatan kontekstual yang bijak dan penuh kasih, Nommensen tidak menghancurkan adat Batak melainkan memperbaruinya dalam terang Kristus. Beliau mendirikan Huta Dame (Kampung Damai) sebagai suaka perlindungan rohani dan sosial. Pada 1878, Nommensen berhasil merampungkan penerjemahan Perjanjian Baru ke dalam bahasa Batak Toba, disusul seluruh Alkitab pada 1893.
      
      HKBP terus berkembang pesat ke Danau Toba, Samosir, Toba Holbung, hingga ke Angkola dan Dairi. Pada 1 Mei 1930, sinode mandiri pertama digelar, dan pada 1940 HKBP resmi mandiri dengan terpilihnya Ephorus pribumi pertama, Pdt. Kasimin Sirait. Kini HKBP menaungi jutaan jemaat dengan ratusan distrik di Indonesia dan mancanegara.
    `,
    milestones: [
      { year: '1861', title: 'Kedatangan Penginjil RMG', desc: 'RMG Jerman resmi memulai pekabaran Injil di Tanah Batak pada 7 Oktober 1861.' },
      { year: '1864', title: 'Nommensen di Lembah Silindung', desc: 'Dr. I.L. Nommensen menetap di Silindung dan mendirikan perkampungan Kristen pertama "Huta Dame".' },
      { year: '1878', title: 'Alkitab Bahasa Batak Toba', desc: 'Penerjemahan Kitab Perjanjian Baru ke Bahasa Batak selesai dicetak dan disebarkan.' },
      { year: '1930', title: 'Kelahiran Sinode HKBP', desc: 'Pengesahan Anggaran Dasar pertama HKBP dan pembentukan struktur kemandirian.' },
      { year: '1940', title: 'Ephorus Pribumi Pertama', desc: 'Pdt. K. Sirait ditahbiskan sebagai Ephorus Batak pertama menggantikan pimpinan zending Jerman.' }
    ],
    heritage: 'Melahirkan dan mempererat rumpun gereja Batak: GKPS (Simalungun), GKPA (Angkola), GBKP (Karo), HKI, dan GKPI. Mengelola Universitas HKBP Nommensen dan RS Balige.',
    trivia: 'Pemerintah Kolonial Belanda menganugerahkan gelar kehormatan Doctor Honoris Causa kepada Nommensen dari Universitas Bonn atas jasanya merintis peradaban modern di Tanah Batak.',
    icon: 'bi-cross',
    crestBg: 'from-amber-600 to-amber-800',
    tags: ['Batak', 'Nommensen', 'Tarutung', 'Silindung', 'RMG', 'Lutheran', 'Pearaja', 'Sumatera']
  },
  {
    id: 'indische-kerk',
    name: 'Gereja Protestan di Indonesia (GPI / Indische Kerk)',
    shortName: 'GPI (Indische Kerk)',
    fullName: 'De Protestantse Kerk in Nederlandsch-Indië / Gereja Protestan di Indonesia',
    originYear: 1605,
    originEvent: 'Ibadah Protestan Perdana di Benteng Ambon oleh Sieckentrooster Armada VOC (Februari 1605)',
    synodYear: 1815,
    synodEvent: 'Dekret Raja Willem I Menyatukan Jemaat dalam De Protestantse Kerk in Nederlandsch-Indië (1815)',
    era: 'voc_early',
    eraLabel: 'Abad 16-18 (Era VOC & Indische Kerk 1815)',
    region: 'Jawa & Maluku',
    subRegion: 'Ambon (Maluku) & Batavia (Jakarta)',
    denomination: 'Protestan',
    tradition: 'Presbiterial-Sinodal / Calvinis',
    oikoumene: ['PGI', 'WCRC (World Communion of Reformed Churches)', 'WCC'],
    founder: 'Sieckentrooster & Rohaniwan VOC (1605), Ds. Casparus Wiltens (1615), Sebastianus Danckaerts, Joseph Kam ("Rasul Maluku")',
    missionAgency: 'Keluarga Gereja Negara Hindia Belanda (Indische Kerk) / Lembaga Zending Batavia',
    currentHeadquarters: 'Gedung Pertemuan GPI, Menteng, Jakarta Pusat',
    summary: 'Ibu cikal bakal sinode-sinode Protestan bersejarah di Indonesia. Berakar dari perebutan Benteng Ambon oleh VOC (1605) di mana ibadah pertama dipimpin sieckentrooster (penghibur orang sakit), kedatangan Ds. Casparus Wiltens (1615), hingga pelembagaan resmi gereja negara oleh Raja Willem I pada 1815.',
    fullStory: `
      Ketika armada VOC pimpinan Laksamana Steven van der Hagen merebut benteng Portugis di Ambon pada Februari 1605, kebaktian Protestan pertama kali di bumi Nusantara dipimpin oleh seorang sieckentrooster (petugas penghibur orang sakit) dan pendeta armada kapal VOC.
      
      Pendeta jemaat definitif pertama, Ds. Casparus Wiltens, baru tiba di Hindia Timur/Ambon sekitar tahun 1614–1615. Bersama Sebastianus Danckaerts, Ds. Casparus Wiltens mempelajari bahasa lokal dan menyusun kamus cetak Melayu-Belanda pertama yang terbit pada tahun 1623. Di Batavia, jemaat didirikan pada 1619 dan Gereja Sion (Portugeesche Buitenkerk) dibangun pada 1695, yang kini menjadi gedung gereja tertua yang masih aktif berdiri di Jakarta.
      
      Pada masa pemerintahan Raja Willem I dari Belanda (1815), seluruh jemaat Protestan di Hindia Belanda disatukan di bawah satu badan gereja negara bernama De Protestantse Kerk in Nederlandsch-Indië (Indische Kerk). Tokoh legendaris Joseph Kam diutus ke Ambon pada 1814–1815 dan dijuluki "Rasul Maluku" karena dedikasinya menghidupkan kembali ratusan jemaat di kepulauan terpencil.
      
      Mulai dekade 1930-an, Indische Kerk memandirikan jemaat-jemaat di berbagai daerah menjadi gereja otonom, melahirkan 12 Gereja Bagian Mandiri (GBM) yang menjadi pilar oikoumene di tanah air.
    `,
    milestones: [
      { year: '1605', title: 'Ibadah Protestan Perdana di Ambon', desc: 'Armada VOC merebut Benteng Ambon; ibadah Protestan pertama dipimpin sieckentrooster armada kapal.' },
      { year: '1615', title: 'Kedatangan Ds. Casparus Wiltens', desc: 'Ds. Casparus Wiltens tiba di Ambon dan merintis penyusunan kamus Melayu-Belanda pertama (1623).' },
      { year: '1619', title: 'Jemaat Kota Batavia', desc: 'Pendirian jemaat Protestan resmi di Batavia dan peletakan dasar gereja kota.' },
      { year: '1733', title: 'Alkitab Melayu Melchior Leijdecker', desc: 'Alkitab terjemahan bahasa Melayu klasik pertama di Asia dirampungkan di Batavia.' },
      { year: '1815', title: 'Struktur Indische Kerk Willem I', desc: 'Dekret Raja Willem I menyatukan seluruh jemaat Protestan Hindia Belanda.' },
      { year: '1934-1948', title: 'Pemekaran Gereja Bagian Mandiri', desc: 'Kemandirian GMIM (1934), GPM (1935), GMIT (1947), dan GPIB (1948).' }
    ],
    heritage: 'Menjadi "Ibu Asal" dari 12 gereja mandiri di Indonesia: GMIM, GPM, GMIT, GPIB, GPIBT (Toli-toli), GKST (Tentena), GKPB (Bali), GPID (Donggala), dll.',
    trivia: 'Alkitab terjemahan Dr. Melchior Leijdecker (1733) menjadi salah satu rujukan kosakata bahasa Melayu tinggi yang kelak memperkaya pembentukan Bahasa Indonesia baku.',
    icon: 'bi-bank',
    crestBg: 'from-blue-700 to-indigo-900',
    tags: ['Indische Kerk', 'VOC', 'Batavia', 'Ambon', 'Joseph Kam', 'GPIB', 'GMIM', 'GPM', 'GMIT']
  },
  {
    id: 'gmim',
    name: 'GMIM (Gereja Masehi Injili di Minahasa)',
    shortName: 'GMIM',
    fullName: 'Gereja Masehi Injili di Minahasa',
    originYear: 1831,
    originEvent: 'Pendaratan Misionaris Riedel & Schwarz di Minahasa (12 Juni 1831)',
    synodYear: 1934,
    synodEvent: 'Deklarasi Kemandirian Sinode GMIM Otonom di Tomohon (30 September 1934)',
    era: 'zending_19',
    eraLabel: 'Abad 19 (Misi Zending)',
    region: 'Sulawesi',
    subRegion: 'Tomohon, Manado & Tondano, Sulawesi Utara',
    denomination: 'Protestan',
    tradition: 'Calvinis / Reformed',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Johann Friedrich Riedel & Johann Gottlieb Schwarz (Pekabar Injil NZG)',
    missionAgency: 'Nederlandsch Zendeling Genootschap (NZG) Rotterdam',
    currentHeadquarters: 'Kantor Sinode GMIM, Tomohon, Sulawesi Utara',
    summary: 'Gereja pembaru tanah Toar Lumimuut Minahasa yang dirintis oleh misionaris Riedel dan Schwarz pada 1831, berkembang menjadi salah satu pilar pendidikan dan iman terbesar di Indonesia Timur.',
    fullStory: `
      Pada 12 Juni 1831, dua misionaris muda asal Jerman yang diutus oleh badan zending Belanda NZG, Johann Friedrich Riedel dan Johann Gottlieb Schwarz, menginjakkan kaki di tanah Minahasa. Riedel memilih melayani di Tondano, sedangkan Schwarz melayani di Langowan.
      
      Pekerjaan mereka mengubah lanskap masyarakat Minahasa secara dramatis. Mereka mendirikan gereja, sekolah-sekolah rakyat Kristen, dan fasilitas pengobatan. Tanggal 12 Juni hingga kini diperingati sebagai Hari Pekabaran Injil dan Pendidikan Kristen di Minahasa.
      
      Setelah satu abad bernaung di bawah Indische Kerk, pada 30 September 1934 GMIM memproklamirkan kemandiriannya sebagai gereja otonom pertama dari rahim Indische Kerk. Tokoh pendidik terkemuka Ds. A.Z.R. Wenas kemudian memimpin GMIM melewati masa pendudukan Jepang dan pergolakan Permesta.
    `,
    milestones: [
      { year: '1831', title: 'Pendaratan Riedel & Schwarz', desc: 'Tiba di Minahasa pada 12 Juni 1831 dan membuka pos pekabaran Injil di Tondano & Langowan.' },
      { year: '1851', title: 'Sekolah Guru Kuranga Tomohon', desc: 'Pembangunan sekolah guru dan penginjil pribumi pertama di Minahasa.' },
      { year: '1934', title: 'Deklarasi Kemandirian GMIM', desc: 'Pada 30 September 1934 GMIM resmi berdiri mandiri dengan Ketua Sinode pertama Dr. E.A.A. de Vreede.' },
      { year: '1942', title: 'Pimpinan Pribumi Pdt. A.Z.R. Wenas', desc: 'Ds. Albertus Zacharias Runturambi Wenas menjadi Ketua Sinode Minahasa legendaris.' }
    ],
    heritage: 'Menaungi Universitas Kristen Indonesia Tomohon (UKIT), Rumah Sakit Bethesda Tomohon, dan ribuan jemaat di Sulawesi Utara.',
    trivia: 'Pdt. A.Z.R. Wenas dikenal sangat disegani bahkan oleh pimpinan tentara pendudukan Jepang karena wibawa moral dan keberaniannya melindungi jemaat.',
    icon: 'bi-flower1',
    crestBg: 'from-sky-600 to-blue-800',
    tags: ['Minahasa', 'Riedel', 'Schwarz', 'Tomohon', 'Tondano', 'Langowan', 'Manado', 'Sulawesi']
  },
  {
    id: 'gki-papua',
    name: 'GKI di Tanah Papua',
    shortName: 'GKI di Tanah Papua',
    fullName: 'Gereja Kristen Injili di Tanah Papua',
    originYear: 1855,
    originEvent: 'Pendaratan C.W. Ottow & J.G. Geissler di Pulau Mansinam Teluk Doreri (5 Februari 1855)',
    synodYear: 1956,
    synodEvent: 'Peresmian Sinode Mandiri GKI di Tanah Papua di Serui (26 Oktober 1956)',
    era: 'zending_19',
    eraLabel: 'Abad 19 (Misi Zending)',
    region: 'Papua',
    subRegion: 'Pulau Mansinam, Teluk Doreri, Manokwari, Papua Barat',
    denomination: 'Protestan',
    tradition: 'Reformed / Calvinis',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Carl Wilhelm Ottow & Johann Gottlob Geissler',
    missionAgency: 'Zendings-Werkman Heldenbergen (Jerman) & Utrechtsche Zendingsvereeniging (UZV)',
    currentHeadquarters: 'Argapura, Kota Jayapura, Papua',
    summary: 'Gerbang peradaban modern di Tanah Papua yang dimulai dari doa sulung Ottow dan Geissler di Pulau Mansinam pada 5 Februari 1855: "Dengan Nama Tuhan Kami Menginjakkan Kaki di Tanah Ini."',
    fullStory: `
      Pada pagi hari 5 Februari 1855, dua misionaris tukang asal Jerman, Carl Wilhelm Ottow dan Johann Gottlob Geissler, mendarat di Pulau Mansinam, Teluk Doreri, Manokwari. Begitu turun dari sekunar Ternate, mereka berlutut di pantai pasir putih dan berdoa: "Dalam nama Tuhan, kami menginjakkan kaki di tanah ini." Doa ini menandai fajar baru bagi peradaban masyarakat Papua.
      
      Di tengah kondisi malaria tropis dan isolasi geografis, Ottow dan Geissler mulai belajar bahasa Numfor, membuka sekolah baca-tulis, mengajar pertukangan, serta menyembuhkan penyakit warga. Keduanya wafat di tanah Papua sebagai martir kasih bagi suku-suku Papua.
      
      Pekerjaan zending dilanjutkan oleh UZV dengan tokoh seperti F.J.F. van Hasselt dan bapak pendidikan Izaak Samuel Kijne yang mendirikan sekolah di Miei, Teluk Wondama. Pada 26 Oktober 1956, Sinode GKI di Tanah Papua resmi mandiri di Serui, mengayomi keberagaman suku dari pesisir hingga pedalaman.
    `,
    milestones: [
      { year: '1855', title: 'Pendaratan Bersejarah di Mansinam', desc: '5 Februari 1855 menjadi hari kelahiran zending dan peringatan HUT Pekabaran Injil se-Tanah Papua.' },
      { year: '1925', title: 'Pendidikan Terpadu Miei Wondama', desc: 'I.S. Kijne mendirikan sekolah guru Miei dan menggubah lagu spiritual Papua legendaris.' },
      { year: '1956', title: 'Kemandirian Sinode di Serui', desc: 'Pada 26 Oktober 1956, GKI di Tanah Papua diresmikan sebagai sinode mandiri.' },
      { year: '2000-an', title: 'Situs Religi Mansinam', desc: 'Monumen Kristus Raja dan situs pendaratan Mansinam dijadikan pusat cagar budaya rohani Papua.' }
    ],
    heritage: 'Gereja terbesar dan pemersatu di seluruh Tanah Papua, menaungi Universitas Kristen Ottow Geissler Jayapura dan ratusan sekolah YPK.',
    trivia: 'Pemerintah menetapkan tanggal 5 Februari sebagai hari libur resmi keagamaan di seluruh provinsi Tanah Papua untuk mengenang pendaratan Ottow & Geissler.',
    icon: 'bi-sun',
    crestBg: 'from-amber-500 to-orange-700',
    tags: ['Papua', 'Mansinam', 'Ottow', 'Geissler', 'Manokwari', 'Kijne', 'Serui', 'Jayapura']
  },
  {
    id: 'gkj',
    name: 'GKJ (Gereja Kristen Jawa)',
    shortName: 'GKJ',
    fullName: 'Sinode Gereja-Gereja Kristen Jawa',
    originYear: 1860,
    originEvent: 'Perintisan Jemaat Kristen Jawa oleh Kyai Sadrach & Kiai Tunggul Wulung (1860-an)',
    synodYear: 1931,
    synodEvent: 'Sidang Sinode Pertama Gereja Kristen Jawa di Kebumen (17-18 Februari 1931)',
    era: 'zending_19',
    eraLabel: 'Abad 19 (Misi Pribumi & Zending)',
    region: 'Jawa',
    subRegion: 'Karangjoso (Purworejo), Kebumen & Salatiga, Jawa Tengah',
    denomination: 'Protestan',
    tradition: 'Reformed Kontekstual Budaya Jawa',
    oikoumene: ['PGI', 'WCRC'],
    founder: 'Kyai Sadrach (Radin Abas), Kiai Ibrahim Tunggul Wulung, Ny. Van Oostrom Philips',
    missionAgency: 'Gerakan Penginjil Pribumi & Zending Gereformeerd Belanda (GKN)',
    currentHeadquarters: 'Jl. dr. Sumardi No. 8-10, Salatiga, Jawa Tengah',
    summary: 'Gereja bercorak budaya Jawa yang lahir dari pergerakan penginjil pribumi karismatik Kyai Sadrach di Karangjoso dan Kiai Tunggul Wulung, memadukan tembang gamelan dengan teologi Reformed.',
    fullStory: `
      Berbeda dengan wilayah luar Jawa yang banyak diprakarsai misionaris asing, benih awal Kekristenan di Jawa Tengah ditabur kuat oleh tokoh-tokoh pribumi. Kiai Ibrahim Tunggul Wulung, seorang pertapa dan mantan lurah di lereng Gunung Muria, bertobat menjadi Kristen dan mengabarkan Injil dengan metode mistisisme kejawen yang ditransformasikan kepada Yesus Kristus.
      
      Muridnya yang paling tersohor adalah Radin Abas yang kemudian bergelar Kyai Sadrach Surapranata. Di desa Karangjoso (Purworejo), Kyai Sadrach mendirikan padepokan Kristen yang mandiri, di mana orang Jawa belajar iman Kristen tanpa harus meniru cara hidup orang Belanda. Beliau mendidik para "guru injil" keliling dan memimpin lebih dari 7.000 pengikut.
      
      Ketika zending Gereformeerd (GKN) tiba, terjadi dialektika teologis yang menghasilkan berdirinya gereja-gereja lokal Jawa yang solid. Pada 17-18 Februari 1931 di Kebumen, sinode perdana GKJ resmi dibentuk.
    `,
    milestones: [
      { year: '1855', title: 'Kiprah Kiai Tunggul Wulung', desc: 'Membuka desa-desa Kristen mandiri di lereng Gunung Muria (Bondo, Banyutowo).' },
      { year: '1870-an', title: 'Padepokan Karangjoso Kyai Sadrach', desc: 'Kyai Sadrach membangun pusat pengajaran Kristen Jawa dengan kepemimpinan pribumi total.' },
      { year: '1900', title: 'Zending GKN Masuk', desc: 'Pendirian RS Kristen Purwokerto dan Zending di Klaten serta Surakarta.' },
      { year: '1931', title: 'Sinode Pertama GKJ di Kebumen', desc: 'Penggabungan klasis-klasis Jawa Tengah menjadi satu sinode am Gereja Kristen Jawa.' }
    ],
    heritage: 'Melahirkan Universitas Kristen Satya Wacana (UKSW) Salatiga dan RS Bethesda Yogyakarta. Liturgi kaya tembang Macapat dan Gamelan Jawa.',
    trivia: 'Kyai Sadrach menolak pakaian jas Eropa dan tetap memakai blangkon serta surjan khas Jawa saat memimpin kebaktian dan sakramen baptisan.',
    icon: 'bi-gem',
    crestBg: 'from-emerald-700 to-teal-900',
    tags: ['Jawa', 'GKJ', 'Sadrach', 'Tunggul Wulung', 'Karangjoso', 'Purworejo', 'Salatiga', 'Gamelan']
  },
  {
    id: 'katolik-indonesia',
    name: 'Gereja Katolik di Indonesia (KWI)',
    shortName: 'Gereja Katolik',
    fullName: 'Gereja Katolik Indonesia (Konferensi Waligereja Indonesia)',
    originYear: 1546,
    originEvent: 'Pendaratan & Pelayanan Misi Santo Fransiskus Xaverius di Maluku (1546)',
    synodYear: 1961,
    synodEvent: 'Konstitusi Apostolik Paus Yohanes XXIII: Penetapan Hierarki Episkopal Mandiri Indonesia / KWI (3 Januari 1961)',
    era: 'voc_early',
    eraLabel: 'Abad 16 (Misi Portugis) & KWI 1961',
    region: 'Nasional',
    subRegion: 'Maluku, Flores (NTT), dan Batavia (Jakarta)',
    denomination: 'Katolik',
    tradition: 'Katolik Roma',
    oikoumene: ['KWI (Konferensi Waligereja Indonesia)', 'Tahta Suci Vatikan'],
    founder: 'Santo Fransiskus Xaverius, Pastor Jacobus Nellissen, Mgr. Albertus Soegijapranata SJ',
    missionAgency: 'Serikat Yesus (SJ), Serikat Sabda Allah (SVD), Fransiskan (OFM)',
    currentHeadquarters: 'Kantor Konferensi Waligereja Indonesia (KWI), Jl. Cut Meutia, Menteng, Jakarta Pusat',
    summary: 'Kehadiran Katolik berakar dari misi Santo Fransiskus Xaverius di Maluku (1546). Sempat dilarang keras di era VOC, hierarki dipulihkan pada 1808 (Prefektur Apostolik Batavia oleh Pastor Jacobus Nellissen), dan memuncak dalam komitmen kebangsaan legendaris Mgr. Albertus Soegijapranata pada era revolusi kemerdekaan 1940-an: "100% Katolik, 100% Indonesia".',
    fullStory: `
      Jejak umat Katolik tertua di Nusantara tercatat sejak kedatangan bangsa Portugis di Maluku. Pada 1546–1547, salah seorang pendiri Serikat Yesus (SJ), Santo Fransiskus Xaverius, berkunjung ke Ambon, Ternate, dan Halmahera (Morotai) untuk melayani serta membaptis ribuan jemaat perdana.
      
      Ketika VOC menguasai Hindia Timur pada abad ke-17 hingga ke-18, kegiatan imam Katolik dilarang keras dan pastor-pastor diusir. Angin segar pemulihan baru berhembus pada 1807 ketika Raja Louis Bonaparte di Belanda memulihkan kebebasan beragama. Pada tahun 1808, Pastor Jacobus Nellissen dan Pastor Lambertus Prinsen tiba di Batavia, menandai berdirinya Prefektur Apostolik Batavia sebagai pemulihan hierarki gereja Katolik di Hindia Belanda. Gereja Katedral Jakarta kemudian diresmikan pada 1901 dalam arsitektur Neo-Gotik megah.
      
      Pada masa revolusi kemerdekaan (1940-an), Mgr. Albertus Soegijapranata SJ, Uskup pribumi pertama, mencetuskan semboyan patriotik legendaris dalam Kongres Umat Katolik Seluruh Indonesia (KUKSI): "100% Katolik, 100% Indonesia", serta memindahkan kediaman keuskupannya ke Yogyakarta untuk mendukung penuh kedaulatan Republik Indonesia. Pada 3 Januari 1961, Paus Yohanes XXIII menetapkan Konstitusi Apostolik "Quod Christus Adorandus" yang meresmikan hierarki episkopal mandiri Gereja Katolik di Indonesia dengan Konferensi Waligereja Indonesia (KWI/MAWI).
    `,
    milestones: [
      { year: '1546', title: 'Misi Santo Fransiskus Xaverius', desc: 'Melayani dan membaptis ribuan jemaat di Kepulauan Maluku Utara dan Ambon.' },
      { year: '1808', title: 'Prefektur Apostolik Batavia', desc: 'Pemulihan hierarki gereja Katolik dengan kedatangan Pastor Jacobus Nellissen di era Louis Bonaparte.' },
      { year: '1901', title: 'Peresmian Katedral Jakarta', desc: 'Gereja Katedral Santa Maria Diangkat ke Surga diresmikan di Lapangan Banteng.' },
      { year: '1940', title: 'Semboyan Patriotik Mgr. Soegijapranata', desc: 'Mgr. Albertus Soegijapranata SJ mencetuskan "100% Katolik, 100% Indonesia" pada era revolusi kemerdekaan.' },
      { year: '1961', title: 'Hierarki Episkopal Mandiri KWI', desc: 'Paus Yohanes XXIII menetapkan Konstitusi Apostolik pembentukan hierarki gereja mandiri Indonesia.' },
      { year: '1989 / 2024', title: 'Kunjungan Apostolik Paus', desc: 'Paus Yohanes Paulus II (1989) dan Paus Fransiskus (2024) berkunjung ke Indonesia.' }
    ],
    heritage: 'Memiliki 37 keuskupan di seluruh Nusantara, ribuan sekolah unggulan (Kanisius, Gonzaga, Santa Ursula), rumah sakit St. Carolus, dan universitas ternama.',
    trivia: 'Mgr. Soegijapranata SJ menyumbang peran penting dalam diplomasi internasional meyakinkan Tahta Suci Vatikan sebagai negara Eropa pertama yang mengakui kemerdekaan RI.',
    icon: 'bi-shield-shaded',
    crestBg: 'from-red-700 to-rose-950',
    tags: ['Katolik', 'KWI', 'Fransiskus Xaverius', 'Soegijapranata', 'Katedral', 'Batavia', 'Flores', 'Vatikan']
  },
  {
    id: 'gpdi',
    name: 'GPdI (Gereja Pantekosta di Indonesia)',
    shortName: 'GPdI',
    fullName: 'Gereja Pantekosta di Indonesia',
    originYear: 1921,
    originEvent: 'Pendaratan Misionaris Groesbeek & Van Klaveren di Cepu (Maret 1921)',
    synodYear: 1923,
    synodEvent: 'Pengesahan Badan Hukum De Pinkstergemeente in Nederlandsch-Indië (4 Juni 1923)',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Kemandirian Awal)',
    region: 'Jawa & Seluruh Nusantara',
    subRegion: 'Cepu (Blora, Jawa Tengah) & Surabaya (Jawa Timur)',
    denomination: 'Pentakosta',
    tradition: 'Pentakosta Klasik (Baptisan Roh Kudus & Karunia)',
    oikoumene: ['PGPI (Persekutuan Gereja-Gereja Pentakosta Indonesia)', 'PWF (Pentecostal World Fellowship)'],
    founder: 'Cornelius E. Groesbeek, Richard D. Van Klaveren, Pdt. F.G. Van Gessel, Pdt. H.N. Runkat',
    missionAgency: 'Bethel Temple Seattle, Washington, USA',
    currentHeadquarters: 'Majelis Pusat GPdI, Jl. Kramat Raya No. 136, Jakarta Pusat',
    summary: 'Pelopor kegerakan Pentakosta di Indonesia yang lahir dari kedatangan misionaris Groesbeek & Van Klaveren di Cepu tahun 1921, berkembang menjadi sinode pentakosta tertua dan terbesar di tanah air.',
    fullStory: `
      Gerakan Pentakosta masuk ke Indonesia berkat kerinduan dua keluarga misionaris berkebangsaan Amerika keturunan Belanda dari Bethel Temple Seattle: Cornelius E. Groesbeek dan Richard D. Van Klaveren. Mereka mendarat di Batavia pada 4 Januari 1921, lalu bergerak ke Bali dan akhirnya berlabuh di kota minyak Cepu, Jawa Tengah.
      
      Di kota Cepu, pada bulan Maret 1921, kebaktian doa pertama diadakan di rumah keluarga Weenink. Di sinilah terjadi pencurahan Roh Kudus perdana dengan tanda berbahasa roh (bahasa lidah) di Indonesia. Dari Cepu, kobaran api rohani merembet cepat ke Surabaya, Bandung, dan Manado.
      
      Pada 19 Maret 1923, pemerintah Hindia Belanda mengesahkan badan hukum "De Pinkstergemeente in Nederlandsch-Indie", yang setelah kemerdekaan berubah nama menjadi Gereja Pantekosta di Indonesia (GPdI). Sinode ini menjadi rahim bagi banyak sinode pentakosta modern berikutnya.
    `,
    milestones: [
      { year: '1921', title: 'Pendaratan Misi di Cepu', desc: 'Cornelius Groesbeek dan Richard Van Klaveren memulai pelayanan dan terjadi baptisan Roh Kudus.' },
      { year: '1923', title: 'Badan Hukum Pinkstergemeente', desc: 'Pengakuan hukum resmi pemerintah Hindia Belanda pada 19 Maret 1923.' },
      { year: '1935', title: 'Sekolah Alkitab Surabaya', desc: 'Pdt. F.G. Van Gessel mendirikan Sekolah Alkitab pertama untuk mencetak pendeta pribumi.' },
      { year: '1942', title: 'Kemandirian Nasional', desc: 'Pdt. H.N. Runkat memimpin GPdI saat semua warga asing diinternir oleh tentara Jepang.' }
    ],
    heritage: 'Memiliki lebih dari 5.000 sidang jemaat di seluruh Indonesia dan luar negeri, puluhan Sekolah Alkitab (SAATB, SAP), dan menjadi pendiri utama PGPI.',
    trivia: 'Pdt. F.G. Van Gessel awalnya adalah seorang perwira perusahaan perminyakan Belanda (BPM) di Cepu yang bertobat dan menyerahkan seluruh hidupnya demi ladang pelayanan.',
    icon: 'bi-fire',
    crestBg: 'from-amber-500 to-red-600',
    tags: ['Pentakosta', 'GPdI', 'Cepu', 'Groesbeek', 'Surabaya', 'Roh Kudus', 'Van Gessel', 'PGPI']
  },
  {
    id: 'gbi',
    name: 'GBI (Gereja Bethel Indonesia)',
    shortName: 'GBI',
    fullName: 'Sinode Gereja Bethel Indonesia',
    originYear: 1921,
    originEvent: 'Akar Hulu Gerakan Pentakosta di Cepu (1921) & Gereja Bethel Injil Sepenuh / GBIS (1952)',
    synodYear: 1970,
    synodEvent: 'Deklarasi Pembentukan Sinode Mandiri GBI di Sukabumi oleh Pdt. Dr. H.L. Senduk (6 Oktober 1970)',
    era: 'pasca_kemerdekaan',
    eraLabel: 'Akar Misi 1921 & Sinode Mandiri 1970',
    region: 'Nasional & Global',
    subRegion: 'Sukabumi, Jawa Barat',
    denomination: 'Pentakosta - Kharismatik',
    tradition: 'Pentakosta / Kharismatik Modern',
    oikoumene: ['PGI', 'PGPI', 'Church of God (Cleveland, TN)', 'PWF'],
    founder: 'Pdt. Dr. Ho Liong Seng (Pdt. H.L. Senduk), Pdt. The Tjiauw Hin, Pdt. A.I. Palealu',
    missionAgency: 'Gerakan Penginjilan & Pemuridan Mandiri bermitra dengan Church of God',
    currentHeadquarters: 'Graha Bethel, Jl. Ahmad Yani No. 65, Cempaka Putih, Jakarta Pusat',
    summary: 'Sinode Pentakosta-Kharismatik terbesar di Indonesia. Secara teologis berakar dari hulu kegerakan Pentakosta di Cepu (1921) dan GBIS (1952), Sinode Mandiri GBI resmi dideklarasikan oleh Pdt. Dr. H.L. Senduk di Sukabumi pada 6 Oktober 1970, dikenal dengan motto "Maju Terus Pantang Mundur" dan merambah ribuan jemaat dari kota besar hingga perintisan di pelosok Nusantara.',
    fullStory: `
      Gereja Bethel Indonesia (GBI) berakar secara teologis dan historis dari hulu kegerakan Pentakosta di Indonesia yang dimulai di Cepu pada Maret 1921. Tokoh pendiri utamanya, Pdt. Dr. Ho Liong Seng (Pdt. H.L. Senduk), awalnya berkiprah sebagai gembala dan pimpinan dalam tubuh GPdI, sebelum kemudian turut membentuk Gereja Bethel Injil Sepenuh (GBIS) pada 1952 di Gang Holland (Jakarta).
      
      Merasakan panggilan visi kepemimpinan yang lebih dinamis, misioner, mandiri, serta tata kelola sinodal yang teratur dan transparan, Pdt. Dr. H.L. Senduk bersama rekan-rekannya mengambil langkah bersejarah. Pada 6 Oktober 1970 di Sukabumi, Jawa Barat, dideklarasikanlah pembentukan Sinode Mandiri Gereja Bethel Indonesia (GBI). Dalam deklarasi ini dicanangkan tekad untuk memberitakan Injil Sepenuh (Full Gospel) ke seluruh penjuru dengan motto legendaris: "Maju Terus Pantang Mundur".
      
      GBI bermitra secara oikoumenis dengan Church of God yang berpusat di Cleveland, Tennessee. Pada era 1980-an hingga 2000-an, GBI memicu gelombang pujian dan penyembahan (praise and worship) kontemporer serta merintis gereja-gereja lokal berskala besar (seperti GBI Gatot Subroto, GBI Rock, GBI CK7).
      
      Di samping gereja-gereja metropolitan, Departemen Pekabaran Injil GBI secara masif merintis pos-pos pelayanan ke daerah pedalaman dan perkebunan: sawit di Riau (Duri, Dumai, Pekanbaru), pesisir Bengkulu, pedalaman Dayak Kalimantan, hingga lembah-lembah pegunungan Papua, mendirikan ribuan gereja lokal mandiri.
    `,
    milestones: [
      { year: '1921', title: 'Hulu Aliran Pentakosta di Indonesia', desc: 'Misionaris Groesbeek & Van Klaveren membawa gerakan Pentakosta perdana di Cepu.' },
      { year: '1952', title: 'Pelayanan Bethel Gang Holland & GBIS', desc: 'Pdt. H.L. Senduk menggembalakan jemaat Bethel di Batavia/Jakarta.' },
      { year: '1970', title: 'Deklarasi Sinode Mandiri GBI Sukabumi', desc: '6 Oktober 1970: Deklarasi berdirinya Sinode Mandiri Gereja Bethel Indonesia oleh Pdt. Dr. H.L. Senduk.' },
      { year: '1972', title: 'Penerimaan Badan Hukum', desc: 'GBI diakui secara resmi oleh Departemen Agama Republik Indonesia.' },
      { year: '1988', title: 'Kebangunan Pujian & Penyembahan', desc: 'Ledakan rohani praise & worship kontemporer merambah kota-kota metropolitan.' },
      { year: '1990-2000', title: 'Misi Perintisan ke Pelosok Nusantara', desc: 'Ekspansi ribuan pos jemaat ke kawasan Riau, Bengkulu, Sumatera, Kalimantan, dan Papua.' },
      { year: '2020', title: 'Jubileum Emas 50 Tahun GBI', desc: 'GBI merayakan 50 tahun pelayanan dengan ribuan cabang di lebih dari 30 negara.' }
    ],
    heritage: 'Menjadi salah satu sinode dengan jumlah jemaat terbesar di Indonesia (jutaan anggota), pengelola STT Bethel Indonesia (STTBI) Petamburan, dan pelopor musik rohani Nusantara.',
    trivia: 'Pdt. H.L. Senduk juga berprofesi sebagai dokter medis terdidik yang mendedikasikan kliniknya bagi masyarakat kurang mampu di samping tugas kepenggembalaannya.',
    icon: 'bi-stars',
    crestBg: 'from-yellow-600 to-amber-700',
    tags: ['GBI', 'Senduk', 'Bethel', 'Sukabumi', 'Kharismatik', 'Praise and Worship', 'Mega Church', 'PGPI', 'Riau', 'Bengkulu', 'Misi Pedalaman']
  },
  {
    id: 'gki',
    name: 'GKI (Gereja Kristen Indonesia)',
    shortName: 'GKI',
    fullName: 'Sinode Gereja Kristen Indonesia',
    originYear: 1920,
    originEvent: 'Cikal Bakal Persekutuan Jemaat Tionghoa THKTKH di Tiga Wilayah Jawa (1920-an)',
    synodYear: 1988,
    synodEvent: 'Penyatuan Historis Tiga Sinode Menjadi Satu Sinode Am GKI di Cipanas (26 Agustus 1988)',
    era: 'kemandirian_early',
    eraLabel: 'Cikal Bakal 1920 & Fusi Sinode Am 1988',
    region: 'Jawa & Seluruh Indonesia',
    subRegion: 'Jawa Barat, Jawa Tengah, dan Jawa Timur',
    denomination: 'Protestan',
    tradition: 'Presbiterial-Sinodal / Reformed',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Ds. Kho Tek Bie, Pdt. Basuki Probowinoto, Pdt. Tan King Hien',
    missionAgency: 'Perhimpunan Tiong Hoa Kie Tok Kauw Hwee (THKTKH) & Zending Belanda',
    currentHeadquarters: 'Kantor Sinode GKI, Jl. Tanjung Duren Barat I No. 1, Jakarta Barat',
    summary: 'Sinode Protestan modern berwawasan oikoumenis dan kebangsaan. Cikal bakalnya berakar dari jemaat Tionghoa (THKTKH) awal dekade 1920-an di Jawa, yang melewati proses rekonsiliasi kebangsaan puluhan tahun hingga fusi ketiga sinode otonom resmi diikrarkan menjadi satu Sinode Am GKI pada 26 Agustus 1988 di Cipanas.',
    fullStory: `
      Sejarah GKI bermula dari kerinduan warga Tionghoa perantauan di Pulau Jawa untuk beribadah dalam iman Kristen. Pada awal dekade 1920-an, didirikan persekutuan Tiong Hoa Kie Tok Kauw Hwee (THKTKH) di tiga wilayah otonom: Jawa Barat, Jawa Tengah, dan Jawa Timur.
      
      Seiring lahirnya kemerdekaan Republik Indonesia, ketiga sinode ini menyadari panggilan persatuan kebangsaan. Nama THKTKH ditanggalkan dan diganti menjadi Gereja Kristen Indonesia (GKI Jabar, GKI Jateng, GKI Jatim). Mereka membuka pintu selebar-lebarnya bagi semua suku bangsa tanpa sekat primordial dan aktif dalam gerakan nasional oikoumene (DGI/PGI).
      
      Proses penyatuan ketiga sinode memakan waktu puluhan tahun demi merajut keselarasan tata gereja, konfesi, dan liturgi. Akhirnya, pada 26 Agustus 1988 di Cipanas, Jawa Barat, ikrar Penyatuan Sinode Am GKI resmi diproklamasikan.
    `,
    milestones: [
      { year: '1920-an', title: 'Pendirian THKTKH di Tiga Wilayah Jawa', desc: 'Jemaat Kristen perantauan Tionghoa membentuk persekutuan di Bandung, Semarang, dan Surabaya.' },
      { year: '1956', title: 'Pergantian Nama Menjadi GKI', desc: 'Penanggalan identitas eksklusif etnis menuju gereja yang inklusif berwawasan Indonesia.' },
      { year: '1962', title: 'Pembentukan Sinode Am Rancangan', desc: 'Musyawarah bersama di Magelang untuk merintis penyatuan tata gereja.' },
      { year: '1988', title: 'Deklarasi Penyatuan Sinode Am Cipanas', desc: '26 Agustus 1988: Tiga sinode mandiri resmi melebur menjadi satu Sinode Am GKI.' }
    ],
    heritage: 'Mendirikan dan mengayomi Yayasan BPK Penabur (pendidikan terkemuka di Indonesia), Universitas Kristen Krida Waskita (UKRIDA), dan penerbitan buku teologi bermutu.',
    trivia: 'Penyatuan GKI menjadi salah satu contoh langka di dunia di mana tiga sinode gereja yang mandiri bersedia membubarkan diri demi melebur dalam kesatuan tanpa perpecahan.',
    icon: 'bi-building-check',
    crestBg: 'from-blue-600 to-cyan-800',
    tags: ['GKI', 'THKTKH', 'Cipanas', 'Penabur', 'Reformed', 'PGI', 'Jawa Barat', 'Jawa Tengah', 'Jawa Timur']
  },
  {
    id: 'gkii',
    name: 'GKII (Gereja Kemah Injil Indonesia)',
    shortName: 'GKII',
    fullName: 'Sinode Gereja Kemah Injil Indonesia',
    originYear: 1928,
    originEvent: 'Kedatangan Dr. Robert A. Jaffray di Makassar & Pembukaan Misi CMA (1928)',
    synodYear: 1983,
    synodEvent: 'Konsolidasi Nasional dan Penetapan Nama Resmi Gereja Kemah Injil Indonesia (1983)',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Misi Pedalaman)',
    region: 'Kalimantan, Sulawesi, Papua & Bali',
    subRegion: 'Makassar (Sulawesi Selatan) & Pedalaman Mahakam Kalimantan',
    denomination: 'Injili',
    tradition: 'Evangelikal / Aliansi CMA (Christian and Missionary Alliance)',
    oikoumene: ['PGLII (Persekutuan Gereja dan Lembaga Injili Indonesia)', 'Alliance World Fellowship'],
    founder: 'Dr. Robert Alexander Jaffray (Misionaris Kanada), Pdt. C.G. Brill, Pdt. Walter M. Post',
    missionAgency: 'The Christian and Missionary Alliance (CMA) Amerika/Kanada',
    currentHeadquarters: 'Graha Kemah Injil, Jl. Kramat V No. 17, Senen, Jakarta Pusat',
    summary: 'Gereja bervisi misi perintis yang dirintis oleh Dr. Robert A. Jaffray di Makassar sejak 1928, menerobos rimba raya Kalimantan Timur dan Lembah Baliem Papua dengan pesawat misi dan kapal zending.',
    fullStory: `
      Dr. Robert Alexander Jaffray, seorang pemuda bangsawan Kanada yang memilih hidup bagi misi, meninggalkan kemewahan keluarganya di Toronto untuk mengabarkan Injil. Setelah melayani di Tiongkok, hati Jaffray terpanggil kuat ke kepulauan Hindia Belanda. Pada 1928, ia tiba di Makassar dan mendirikan basis misi CMA.
      
      Di Makassar, Jaffray mendirikan Sekolah Alkitab Makassar pada 1932 (kini STT Jaffray) serta Percetakan Kalam Hidup untuk menerbitkan literatur rohani. Dari Makassar, Jaffray mengirim misionaris dan perahu penginjilan ke pedalaman Sungai Mahakam di Kalimantan, Pulau Bali, Lombok, serta membuka isolasi suku Dani di Pegunungan Tengah Papua.
      
      Ketika Perang Pasifik meletus, Jaffray menolak dievakuasi pulang ke Kanada. Beliau memilih tinggal bersama jemaatnya dan wafat sebagai martir di kamp interniran Jepang di Wehoru, Makassar pada 29 Juli 1945.
    `,
    milestones: [
      { year: '1928', title: 'Kedatangan Dr. Jaffray di Makassar', desc: 'Membuka pos pelayanan CMA pertama di Indonesia Timur.' },
      { year: '1932', title: 'Sekolah Alkitab & Kalam Hidup', desc: 'Pendirian STT Jaffray dan penerbitan buku serta majalah rohani berbahasa Melayu.' },
      { year: '1938', title: 'Penerobosan Rimba Kalimantan & Papua', desc: 'Pekabaran Injil ke pedalaman suku Dayak Kenyah/Kayan dan suku Dani Lembah Baliem.' },
      { year: '1945', title: 'Kemartiran Dr. Robert Jaffray', desc: 'Jaffray wafat di kamp tawanan Jepang, meninggalkan ribuan jemaat yang berakar kuat.' },
      { year: '1983', title: 'Penetapan Nama Resmi GKII', desc: 'Konsolidasi nasional dan pemakaian nama Gereja Kemah Injil Indonesia.' }
    ],
    heritage: 'Pilar utama PGLII di Indonesia, pelopor penerbitan Kalam Hidup, pengelola STT Jaffray Makassar dan Jakarta, serta misi penerbangan MAF (Mission Aviation Fellowship).',
    trivia: 'Penerbitan "Kalam Hidup" yang didirikan Jaffray pada 1932 merupakan salah satu penerbit literatur Kristen tertua yang masih aktif beroperasi di Indonesia hingga hari ini.',
    icon: 'bi-compass',
    crestBg: 'from-teal-600 to-emerald-900',
    tags: ['GKII', 'Jaffray', 'Makassar', 'Dayak', 'Papua', 'Kalam Hidup', 'CMA', 'PGLII', 'Injili']
  },
  {
    id: 'gpib',
    name: 'GPIB (Gereja Protestan di Indonesia bagian Barat)',
    shortName: 'GPIB',
    fullName: 'Gereja Protestan di Indonesia bagian Barat',
    originYear: 1948,
    originEvent: 'Pemekaran Gereja Bagian Mandiri (GBM) Barat dari Indische Kerk',
    synodYear: 1948,
    synodEvent: 'Diresmikan sebagai Sinode Mandiri GPIB di Gereja Immanuel Jakarta (31 Oktober 1948)',
    era: 'pasca_kemerdekaan',
    eraLabel: '1945-Sekarang (Pasca Kemerdekaan)',
    region: 'Jawa, Sumatera & Kalimantan Barat',
    subRegion: 'Gereja Immanuel Pejambon, Jakarta Pusat',
    denomination: 'Protestan',
    tradition: 'Calvinis / Presbiterial-Sinodal',
    oikoumene: ['PGI', 'GPI', 'WCRC', 'WCC'],
    founder: 'Ds. J.P. de Ridder, Ds. A.E.B. Engel, Ds. I.J. Soplanit',
    missionAgency: 'Pemekaran Gereja Bagian Mandiri (GBM) dari Indische Kerk / GPI',
    currentHeadquarters: 'Majelis Sinode GPIB, Jl. Medan Merdeka Timur No. 10, Gambir, Jakarta Pusat',
    summary: 'Sinode pemekaran Indische Kerk untuk wilayah barat Indonesia yang diresmikan pada 31 Oktober 1948 di Gereja Immanuel Jakarta, mengelola warisan gedung cagar budaya bersejarah bangsa.',
    fullStory: `
      Menyusul kemandirian GMIM di Minahasa (1934), GPM di Maluku (1935), dan GMIT di Timor (1947), wilayah Indonesia bagian barat yang meliputi Jawa, Sumatera, Bangka Belitung, Riau, hingga Kalimantan Barat masih berada di bawah pimpinan langsung Indische Kerk.
      
      Pada tanggal 31 Oktober 1948, bertepatan dengan peringatan Hari Reformasi Gereja sedunia, bertempat di gedung Gereja Immanuel Pejambon Jakarta, GPIB diresmikan sebagai Gereja Bagian Mandiri ke-4 dari tubuh GPI.
      
      GPIB memiliki karakteristik unik karena memelihara puluhan gedung gereja tua peninggalan era VOC dan Hindia Belanda yang kini berstatus cagar budaya nasional, seperti Gereja Sion (1695), Gereja Immanuel Gambir (1839), Gereja Blenduk Semarang (1753), dan Gereja Koinonia Jatinegara.
    `,
    milestones: [
      { year: '1948', title: 'Peresmian di Gereja Immanuel', desc: '31 Oktober 1948: GPIB resmi mandiri dengan Ketua Sinode pertama Ds. J.P. de Ridder.' },
      { year: '1958', title: 'Nasionalisasi Kepemimpinan Penuh', desc: 'Seluruh tenaga pelayan dan majelis jemaat beralih penuh kepada putra-putri bangsa Indonesia.' },
      { year: '2023', title: 'Peringatan 75 Tahun GPIB', desc: 'Perayaan Yubileum 75 tahun GPIB melayani dalam damai dan keragaman nusantara.' }
    ],
    heritage: 'Merawat situs cagar budaya arsitektur gereja bersejarah (Gereja Sion, Gereja Immanuel, Gereja Blenduk) serta yayasan pendidikan Kristen di kota-kota pelabuhan tua.',
    trivia: 'Gereja Sion Jakarta yang dirawat GPIB memiliki orgel pipa antik buatan tahun 1750-an yang hingga kini masih terawat dan dapat dibunyikan.',
    icon: 'bi-bell',
    crestBg: 'from-indigo-600 to-slate-900',
    tags: ['GPIB', 'Immanuel', 'Pejambon', 'Gereja Sion', 'Blenduk', 'Jakarta', 'PGI', 'Indische Kerk']
  },
  {
    id: 'gpm',
    name: 'GPM (Gereja Protestan Maluku)',
    shortName: 'GPM',
    fullName: 'Gereja Protestan Maluku',
    originYear: 1605,
    originEvent: 'Benteng Victoria Ambon & Ibadah Protestan Perdana oleh Sieckentrooster VOC (Februari 1605)',
    synodYear: 1935,
    synodEvent: 'Kemandirian Penuh Sinode GPM di Gedung Gereja Maranatha Ambon (6 September 1935)',
    era: 'voc_early',
    eraLabel: 'Abad 17 (VOC & Kam) & Sinode Mandiri 1935',
    region: 'Maluku',
    subRegion: 'Ambon, Lease, Seram, Banda, Kepulauan Maluku',
    denomination: 'Protestan',
    tradition: 'Calvinis / Presbiterial',
    oikoumene: ['PGI', 'GPI', 'WCRC', 'WCC'],
    founder: 'Sieckentrooster VOC (1605), Ds. Casparus Wiltens (1615), Joseph Kam ("Rasul Maluku"), Ds. C.H. Boger',
    missionAgency: 'Indische Kerk & Lembaga Pekabaran Zending Ambon',
    currentHeadquarters: 'Jl. Mayjen D.I. Panjaitan No. 1, Ambon, Maluku',
    summary: 'Sinode bersejarah di Kepulauan Rempah Maluku. Berakar dari ibadah Protestan pertama di Benteng Ambon oleh sieckentrooster VOC (1605), kedatangan Ds. Casparus Wiltens (1615), kebangunan rohani Joseph Kam (1815), hingga deklarasi Sinode Mandiri pada 6 September 1935, menjadi pelopor perdamaian sejati "Pela Gandong".',
    fullStory: `
      Sejarah GPM identik dengan babak paling awal Protestanisme di Nusantara. Setelah Benteng Victoria direbut dari Portugis pada Februari 1605, ibadah Protestan pertama dipimpin oleh sieckentrooster (penghibur orang sakit) armada VOC. Pendeta jemaat definitif pertama seperti Ds. Casparus Wiltens baru melayani di Ambon pada kurun 1614–1615, merintis pengajaran firman dalam bahasa Melayu dan penyusunan kamus Melayu-Belanda.
      
      Namun titik balik rohani dan pastoral sejati terjadi ketika Joseph Kam tiba di Ambon pada Maret 1815. Selama 19 tahun hingga wafatnya pada 1833, Joseph Kam berlayar menggunakan perahu kora-kora tradisional menerjang ombak ganas Laut Banda demi menggembalakan jemaat-jemaat di pelosok kepulauan Maluku yang terlantar puluhan tahun tanpa pendeta. Karena pengorbanannya, beliau dihormati abadi sebagai "Rasul Maluku".
      
      Setelah berabad-abad bernaung di bawah gereja negara (Indische Kerk), pada 6 September 1935 GPM memproklamasikan kemandiriannya sebagai sinode mandiri di Gedung Gereja Maranatha Ambon. GPM menjadi teladan ketahanan iman dan pelopor rekonsiliasi persaudaraan lintas agama melalui kearifan lokal "Pela Gandong".
    `,
    milestones: [
      { year: '1605', title: 'Benteng Victoria Ambon', desc: 'Pengambilalihan benteng dari Portugis dan ibadah Protestan perdana oleh sieckentrooster armada VOC.' },
      { year: '1615', title: 'Pelayanan Ds. Casparus Wiltens', desc: 'Pelayanan jemaat definitif perdana dan perintisan literatur Melayu-Ambon.' },
      { year: '1815', title: 'Pelayanan Joseph Kam', desc: 'Joseph Kam tiba di Ambon dan membangkitkan kehidupan rohani ratusan jemaat kepulauan.' },
      { year: '1935', title: 'Kemandirian Sinode GPM', desc: '6 September 1935: Sinode GPM berdiri mandiri terpisah dari administrasi kolonial.' },
      { year: '2000-an', title: 'Pelopor Perdamaian Maluku', desc: 'GPM bersama para tokoh Muslim memulihkan persaudaraan sejati pasca konflik Ambon.' }
    ],
    heritage: 'Pilar identitas kultural dan spiritual masyarakat Maluku, menaungi Universitas Kristen Indonesia Maluku (UKIM) di Ambon.',
    trivia: 'Makam Joseph Kam hingga kini masih terawat di pekarangan belakang Gereja Bethfage di Mangga Dua, Ambon.',
    icon: 'bi-water',
    crestBg: 'from-blue-700 to-sky-900',
    tags: ['Maluku', 'GPM', 'Ambon', 'Joseph Kam', 'Pela Gandong', 'Maranatha', 'PGI']
  },
  {
    id: 'gmit',
    name: 'GMIT (Gereja Masehi Injili di Timor)',
    shortName: 'GMIT',
    fullName: 'Gereja Masehi Injili di Timor',
    originYear: 1614,
    originEvent: 'Pelayanan Pendeta VOC Pertama Ds. Mattheus van den Broeck di Rote & Kupang (1614)',
    synodYear: 1947,
    synodEvent: 'Peresmian Sinode Mandiri GMIT di Kupang (31 Oktober 1947)',
    era: 'voc_early',
    eraLabel: 'Sentuhan VOC 1614 & Sinode Mandiri 1947',
    region: 'Nusa Tenggara',
    subRegion: 'Kupang, Pulau Timor, Rote, Sabu, Alor, Nusa Tenggara Timur',
    denomination: 'Protestan',
    tradition: 'Reformed / Presbiterial',
    oikoumene: ['PGI', 'GPI', 'WCRC', 'WCC'],
    founder: 'Ds. Mattheus van den Broeck (Rohaniwan VOC 1614), Ds. Ernst Durkstra (Ketua Sinode 1947), Ds. Th. Basoeki',
    missionAgency: 'Indische Kerk & Zending di Kepulauan Sunda Kecil',
    currentHeadquarters: 'Kantor Sinode GMIT, Jl. S.K. Lerik No. 1, Kupang, NTT',
    summary: 'Gereja terbesar kedua di Indonesia Timur yang melayani kepulauan Timor, Rote, Sabu, dan Alor. Cikal bakalnya berakar dari pelayanan pendeta VOC Mattheus van den Broeck di Rote & Kupang (1614), tradisi melek huruf sekolah desa Rote abad ke-18, hingga resmi dideklarasikan mandiri sebagai Sinode GMIT pada 31 Oktober 1947.',
    fullStory: `
      Akar Kekristenan di bumi Timor dan Rote telah bersemi sejak kunjungan pendeta VOC pertama, Ds. Mattheus van den Broeck, pada tahun 1614. Pulau Rote kemudian menjadi salah satu wilayah paling awal di Nusantara yang memiliki tradisi literasi aksara Melayu dan sekolah desa Kristen sejak paruh awal abad ke-18. Para raja di Rote mengirim anak-anak mereka belajar membaca Alkitab ke Batavia.
      
      Pada abad ke-19 dan awal abad ke-20, pekabaran Injil menjangkau pedalaman Timor Barat (Amanuban, Mollo, Miomaffo) dan Pulau Alor. Setelah berabad-abad dilayani sebagai bagian dari Indische Kerk, pada tanggal 31 Oktober 1947 bertempat di Kupang, jemaat-jemaat ini bersepakat memandirikan diri secara otonom dengan nama Gereja Masehi Injili di Timor (GMIT).
      
      GMIT memegang peranan luar biasa dalam pemberantasan buta huruf, pelayanan air bersih, kesehatan pedesaan, serta advokasi lingkungan hidup di provinsi Nusa Tenggara Timur.
    `,
    milestones: [
      { year: '1614', title: 'Pelayanan VOC Pertama di Kupang & Rote', desc: 'Ds. Mattheus van den Broeck mengunjungi jemaat awal di Kupang dan Pulau Rote.' },
      { year: '1729', title: 'Sekolah Desa Aksara Melayu Rote', desc: 'Pendirian sekolah berbahasa Melayu di Pulau Rote, salah satu yang tertua di Nusantara.' },
      { year: '1947', title: 'Peresmian Sinode Mandiri GMIT', desc: 'Diresmikan pada 31 Oktober 1947 di Kupang dengan Ketua Sinode pertama Ds. Ernst Durkstra.' },
      { year: '1965', title: 'Kegerakan Rohani Soe Timor', desc: 'Terjadi fenomena kebangunan rohani besar di kota Soe yang dicatat sejarah misi dunia.' }
    ],
    heritage: 'Menaungi ribuan sekolah YPKGMIT, Universitas Kristen Artha Wacana (UKAW) Kupang, dan jaringan rumah sakit di NTT.',
    trivia: 'Orang Rote dikenal sebagai pelopor guru-guru sekolah di berbagai pelosok Nusantara pada zaman kolonial karena tingginya tingkat melek huruf sejak dini.',
    icon: 'bi-brightness-high',
    crestBg: 'from-amber-600 to-yellow-800',
    tags: ['GMIT', 'Timor', 'Kupang', 'Rote', 'Sabu', 'Alor', 'NTT', 'PGI']
  },
  {
    id: 'gke',
    name: 'GKE (Gereja Kalimantan Evangelis)',
    shortName: 'GKE',
    fullName: 'Gereja Kalimantan Evangelis',
    originYear: 1836,
    originEvent: 'Pendaratan Misionaris RMG Barnstein di Banjarmasin (26 Juni 1836)',
    synodYear: 1935,
    synodEvent: 'Sinode Mandiri Gereja Dayak Evangelis di Banjarmasin (4 April 1935)',
    era: 'zending_19',
    eraLabel: 'Abad 19 (Misi Zending Dayak)',
    region: 'Kalimantan',
    subRegion: 'Banjarmasin, Kuala Kapuas, Palangka Raya, Kalimantan Tengah & Selatan',
    denomination: 'Protestan',
    tradition: 'Lutheran - Reformed (Uniert)',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Barnstein, Heyer, Becker (Pekabar RMG & Basel Mission), Pdt. H. Dingang Patianom',
    missionAgency: 'RMG Barmen Jerman & Basler Missionsgesellschaft (Misi Basel Swiss)',
    currentHeadquarters: 'Jl. Jenderal Sudirman No. 4, Banjarmasin, Kalimantan Selatan',
    summary: 'Gereja suku Dayak tertua di Pulau Borneo yang dirintis sejak 1836 oleh RMG dan Misi Basel, mentransformasi adat Kaharingan pedalaman dan menerjemahkan Alkitab bahasa Dayak Ngaju.',
    fullStory: `
      Pada 26 Juni 1836, tiga misionaris RMG Barmen Jerman tiba di Banjarmasin. Mereka mulai menjalin hubungan dengan suku Dayak Ngaju di sepanjang aliran Sungai Kahayan dan Kapuas. Pembaptisan pertama orang Dayak berlangsung di Betlehem (sekarang Kuala Kapuas) pada tahun 1839.
      
      Pekerjaan zending sempat tergoncang hebat oleh pecahnya Perang Banjar pada 1859 di mana beberapa misionaris gugur. Namun tongkat estafet diambil alih dengan gigih oleh Basel Mission dari Swiss. Misi Basel mengembangkan sistem perkebunan rakyat, sekolah tukang, dan rumah sakit kusta.
      
      Misionaris August Hardeland merampungkan kamus bahasa Dayak Ngaju dan menerjemahkan Alkitab lengkap. Pada 4 April 1935 di Banjarmasin, sinode ini berdiri mandiri dengan nama awal "Gereja Dayak Evangelis" (GDE), sebelum akhirnya berganti nama menjadi GKE untuk merangkul semua suku bangsa di Kalimantan.
    `,
    milestones: [
      { year: '1836', title: 'Pendaratan Misi RMG di Banjarmasin', desc: 'Membuka perintisan zending di kalangan masyarakat Dayak.' },
      { year: '1858', title: 'Alkitab Bahasa Dayak Ngaju', desc: 'Penerjemahan Alkitab lengkap oleh August Hardeland, menjadi dasar literasi suku Dayak.' },
      { year: '1935', title: 'Sinode Mandiri GDE', desc: '4 April 1935: Kemandirian penuh Gereja Dayak Evangelis dipimpin pimpinan lokal.' },
      { year: '1950', title: 'Transformasi Nama Menjadi GKE', desc: 'Perubahan nama menjadi Gereja Kalimantan Evangelis untuk menjangkau seluruh Kalimantan.' }
    ],
    heritage: 'Mendirikan STT GKE Banjarmasin, Universitas Kristen Palangka Raya (UNKRIP), dan jaringan asrama pelajar pedalaman Kalimantan.',
    trivia: 'Penerjemahan Alkitab ke dalam bahasa Dayak Ngaju oleh Hardeland pada 1858 menjadi tonggak pertama kalinya bahasa lisan Dayak dikodifikasikan dalam bentuk tulisan cetak modern.',
    icon: 'bi-tree',
    crestBg: 'from-emerald-800 to-green-950',
    tags: ['GKE', 'Kalimantan', 'Dayak', 'Kapuas', 'Banjarmasin', 'Palangka Raya', 'RMG', 'Misi Basel']
  },
  {
    id: 'gereja-toraja',
    name: 'Gereja Toraja (GT)',
    shortName: 'Gereja Toraja',
    fullName: 'Sinode Gereja Toraja',
    originYear: 1913,
    originEvent: 'Kedatangan Antonie Aris van de Loosdrecht di Rantepao Toraja (November 1913)',
    synodYear: 1947,
    synodEvent: 'Sidang Sinode Am I Gereja Toraja di Rantepao (25-28 Maret 1947)',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Zending & Kemandirian)',
    region: 'Sulawesi',
    subRegion: 'Rantepao & Makale, Tana Toraja & Toraja Utara, Sulawesi Selatan',
    denomination: 'Protestan',
    tradition: 'Calvinis / Reformed',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Antonie Aris van de Loosdrecht, Pdt. J. Belksma, Pdt. J. Kobong',
    missionAgency: 'Gereformeerde Zendingsbond (GZB) Belanda',
    currentHeadquarters: 'Tongkonan Sangullele, Jl. Ahmad Yani No. 45, Rantepao, Toraja Utara',
    summary: 'Gereja berakar kuat di lembah Tongkonan Tana Toraja yang diawali martir A.A. van de Loosdrecht tahun 1913, menyatukan masyarakat Toraja dalam naungan kasih Kristus dan pendidikan modern.',
    fullStory: `
      GZB (Gereformeerde Zendingsbond) mengutus Antonie Aris van de Loosdrecht dan istrinya tiba di Rantepao pada November 1913. Loosdrecht segera membuka sekolah-sekolah rakyat desa bagi anak-anak petani Toraja. Namun situasi politik dan ketegangan dengan bangsawan lokal memuncak, dan pada 26 Juli 1917 Loosdrecht wafat ditombak di Bori, menjadi martir pertama di Toraja.
      
      Kematian Loosdrecht justru menumbuhkan simpati dan ketertarikan mendalam masyarakat Toraja terhadap Injil. Rekan-rekannya seperti Pdt. J. Belksma meneruskan perjuangan dengan mendirikan Sekolah Guru Normaalschool di Barana.
      
      Pada tanggal 25 Maret 1947 di Rantepao, sinode mandiri Gereja Toraja resmi didirikan. Gereja Toraja memadukan arsitektur rumah adat Tongkonan yang luhur dengan salib Kristus sebagai lambang perteduhan sejati keluarga Allah.
    `,
    milestones: [
      { year: '1913', title: 'Kedatangan A.A. van de Loosdrecht', desc: 'Membuka pelayanan di Rantepao dan mendirikan sekolah rakyat Toraja.' },
      { year: '1917', title: 'Kemartiran van de Loosdrecht', desc: 'Wafatnya Loosdrecht menjadi benih kebangkitan gereja di Tana Toraja.' },
      { year: '1947', title: 'Sinode Pertama Gereja Toraja', desc: '25 Maret 1947: Sidang Sinode Am I di Rantepao memilih pimpinan putra daerah.' },
      { year: '2013', title: 'Satu Abad Pekabaran Injil Toraja', desc: 'Peringatan 100 tahun masuknya Injil di Toraja dihadiri ratusan ribu jemaat.' }
    ],
    heritage: 'Mendirikan Universitas Kristen Indonesia Toraja (UKI Toraja), RS Elim Rantepao, dan menaungi jemaat diaspora Toraja di seluruh dunia.',
    trivia: 'Gedung kantor Sinode Gereja Toraja dibangun berbentuk Tongkonan raksasa bernama "Tongkonan Sangullele" yang berarti rumah musyawarah bersama.',
    icon: 'bi-house',
    crestBg: 'from-amber-700 to-rose-900',
    tags: ['Toraja', 'Gereja Toraja', 'Rantepao', 'Makale', 'Tongkonan', 'Loosdrecht', 'GZB', 'Sulawesi']
  },
  {
    id: 'bala-keselamatan',
    name: 'Bala Keselamatan (The Salvation Army Indonesia)',
    shortName: 'Bala Keselamatan',
    fullName: 'Bala Keselamatan Teritori Indonesia',
    originYear: 1894,
    synodYear: 1894,
    era: 'zending_19',
    eraLabel: 'Abad 19 (Misi Kemanusiaan)',
    region: 'Jawa & Sulawesi Tengah',
    subRegion: 'Purworejo, Semarang, Palu & Kulawi (Sulawesi Tengah)',
    denomination: 'Bala Keselamatan',
    tradition: 'Evangelikal / Gerakan Kekudusan (Holiness Movement)',
    oikoumene: ['PGI', 'The Salvation Army International London'],
    founder: 'Staf Kapten Jacob Gerrit Brouwer & Letnan Adolf van Emmerik',
    missionAgency: 'The Salvation Army International (Dirintis William Booth di London)',
    currentHeadquarters: 'Kantor Teritori Bala Keselamatan, Jl. Jawa No. 20, Bandung, Jawa Barat',
    summary: 'Gerakan kekudusan dengan disiplin spiritual dan kepangkatan rohani yang tiba di Batavia pada 1894, terkenal di seantero nusantara atas dedikasi pelayanan kusta, rumah sakit, dan panti asuhan.',
    fullStory: `
      Gerakan Bala Keselamatan yang didirikan William Booth di London menjangkau Indonesia pada 24 November 1894 ketika Staf Kapten Jacob Gerrit Brouwer dan Letnan Adolf van Emmerik tiba di Batavia. Mereka segera merintis pos pelayanan di Purworejo dan Semarang.
      
      Kekuatan utama Bala Keselamatan adalah aksi sosial tanpa membedakan suku dan agama: merawat penderita kusta (lepra) di Pelantungan Jawa Tengah, membuka dapur umum, mendirikan panti yatim piatu, dan mendirikan RS William Booth di Semarang dan Surabaya.
      
      Pada tahun 1913, perwira Bala Keselamatan bergerak ke pedalaman Sulawesi Tengah (Palu, Kulawi, Lembah Palolo). Di sana, Bala Keselamatan diterima dengan sukacita dan menjadi gereja mayoritas yang memajukan kehidupan sosial masyarakat suku Kaili dan Kulawi.
    `,
    milestones: [
      { year: '1894', title: 'Pendaratan di Batavia & Semarang', desc: 'Jacob Brouwer dan Adolf van Emmerik memulai aksi pelayanan kasih.' },
      { year: '1909', title: 'Klinik Kusta Pelantungan', desc: 'Membuka pelayanan lepra terkemuka yang menjadi rujukan penanganan kusta Hindia Belanda.' },
      { year: '1913', title: 'Misi ke Lembah Palu & Kulawi', desc: 'Ekspansi besar ke pedalaman Sulawesi Tengah dan pengangkatan perwira lokal.' },
      { year: '1915', title: 'RS William Booth Surabaya & Semarang', desc: 'Pendirian rumah sakit umum melayani kaum miskin dan buruh pabrik.' }
    ],
    heritage: 'Mengelola Rumah Sakit William Booth (Surabaya, Semarang, Palu), panti jompo, panti asuhan, dan korps pelayanan di pelosok Nusantara.',
    trivia: 'Para pendeta Bala Keselamatan memakai sebutan pangkat terstruktur (Kapten, Mayor, Kolonel, Komisioner) dan seragam khusus yang melambangkan kesiapan berperang melawan dosa dan kemiskinan.',
    icon: 'bi-heart-pulse',
    crestBg: 'from-rose-700 to-red-900',
    tags: ['Bala Keselamatan', 'Salvation Army', 'William Booth', 'Semarang', 'Palu', 'Kulawi', 'PGI']
  },
  {
    id: 'gbkp',
    name: 'GBKP (Gereja Batak Karo Protestan)',
    shortName: 'GBKP',
    fullName: 'Gereja Batak Karo Protestan',
    originYear: 1890,
    originEvent: 'Pdt. H.C. Kruyt Mendirikan Pos Zending Buluh Awar Tanah Karo (18 April 1890)',
    synodYear: 1941,
    synodEvent: 'Sidang Sinode Pertama GBKP di Sibolangit (23 Juli 1941)',
    era: 'zending_19',
    eraLabel: 'Abad 19 & Kemandirian 1941',
    region: 'Sumatera',
    subRegion: 'Buluh Awar & Kabanjahe, Tanah Karo, Sumatera Utara',
    denomination: 'Protestan',
    tradition: 'Calvinis / Reformed',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Pdt. H.C. Kruyt, Pdt. J.K. Wijngaarden, Guru Pekabar Injil Guillaume',
    missionAgency: 'Nederlandsch Zendeling Genootschap (NZG) Rotterdam',
    currentHeadquarters: 'Kantor Moderamen GBKP, Jl. Kapten Pala Bangun No. 66, Kabanjahe, Tanah Karo',
    summary: 'Pilar spiritual suku Karo yang bermula dari desa bersejarah Buluh Awar pada 1890, mandiri sejak 1941 dan menghadirkan transformasi pendidikan serta pertanian di dataran tinggi Karo.',
    fullStory: `
      NZG mengutus Pdt. H.C. Kruyt tiba di pesisir Deli pada 1890, lalu naik ke perbukitan dan mendirikan pos zending pertama di desa Buluh Awar (Deli Serdang) pada 18 April 1890. Desa Buluh Awar ini hingga kini dikenang oleh orang Karo sebagai "Desa Titik Nol" penyebaran Injil.
      
      Pekerjaan zending dilanjutkan oleh Pdt. J.K. Wijngaarden dan penginjil pribumi asal Minahasa bernama Benjamin Willem. Pembaptisan perdana orang Karo berlangsung pada 20 Agustus 1893, di antaranya Sampe, Ngurupi, Mbelin, dan Nuan.
      
      Misi berkembang mendirikan rumah sakit di Kabanjahe (RS Kabanjahe) dan pusat pertanian. Pada 23 Juli 1941, digelar Sinode Pertama di Sibolangit yang memproklamasikan kemandirian penuh Gereja Batak Karo Protestan (GBKP).
    `,
    milestones: [
      { year: '1890', title: 'Pos Misi Buluh Awar', desc: '18 April 1890: H.C. Kruyt mendirikan pos zending pertama di Tanah Karo.' },
      { year: '1893', title: 'Baptisan Perdana Orang Karo', desc: 'Empat pemuda Karo dibaptis di Buluh Awar menandai awal jemaat Kristen Karo.' },
      { year: '1941', title: 'Sinode Pertama di Sibolangit', desc: '23 Juli 1941: GBKP berdiri mandiri dengan Moderamen pribumi.' },
      { year: '2010-an', title: 'Pelayanan Bencana Gunung Sinabung', desc: 'GBKP menjadi garda terdepan posko kemanusiaan bagi ribuan pengungsi Sinabung.' }
    ],
    heritage: 'Memiliki ratusan Runggun (jemaat) di Sumatera Utara dan kota-kota diaspora, RS Kabanjahe, dan asrama panti asuhan Alpha Omega.',
    trivia: 'Masyarakat Karo sangat menghormati desa Buluh Awar dan mendirikan monumen salib peringatan tempat berkumpulnya peziarah rohani.',
    icon: 'bi-shield-check',
    crestBg: 'from-amber-600 to-stone-800',
    tags: ['GBKP', 'Karo', 'Buluh Awar', 'Kabanjahe', 'NZG', 'Sumatera Utara', 'PGI']
  },
  {
    id: 'gmahk',
    name: 'GMAHK (Gereja Masehi Advent Hari Ketujuh)',
    shortName: 'GMAHK',
    fullName: 'Gereja Masehi Advent Hari Ketujuh Uni Indonesia',
    originYear: 1900,
    originEvent: 'Pdt. Ralph W. Munson Memulai Misi Advent di Padang (1900) & Pembaptisan Tay Hong Siang',
    synodYear: 1929,
    synodEvent: 'Pembentukan Uni Indonesia Gereja Masehi Advent Hari Ketujuh (1929)',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Awal Abad 20)',
    region: 'Nasional',
    subRegion: 'Padang (Sumatera Barat) & Sukabumi/Bandung (Jawa Barat)',
    denomination: 'Advent',
    tradition: 'Adventis Hari Ketujuh (Sabat & Pengharapan Kedatangan)',
    oikoumene: ['General Conference of Seventh-day Adventists, Silver Spring, MD, USA'],
    founder: 'Pendeta Ralph W. Munson & Ny. Munson, Abram La Rue',
    missionAgency: 'Seventh-day Adventist World Mission',
    currentHeadquarters: 'Kantor Uni Indonesia Kawasan Barat, Gedung Pertemuan Advent, Jl. MT Haryono, Jakarta Selatan',
    summary: 'Gereja pemelihara hari Sabat yang dirintis di Padang pada tahun 1900 oleh Ralph W. Munson, pelopor pola hidup sehat vegetarian, pendidikan asrama, dan rumah sakit modern.',
    fullStory: `
      Benih Adventisme di Indonesia bermula dari penginjil literatur mandiri Abram La Rue di Hong Kong yang mengirimkan buku-buku rohani ke pelabuhan-pelabuhan Nusantara. Pada tahun 1900, Pendeta Ralph W. Munson bersama istrinya tiba di Padang, Sumatera Barat.
      
      Di Padang, Munson mulai mengabarkan kabar Injil dan pola hidup sehat. Orang Indonesia pertama yang dibaptis menjadi pemeluk Advent adalah Tay Hong Siang pada awal 1900-an. Dari Padang, keluarga Munson pindah ke Sukabumi dan Batavia, membuka jemaat di Jawa Barat dan Minahasa.
      
      Advent berkembang pesat melalui misi pengobatan dan gaya hidup sehat preventif. Pada dekade 1930-an didirikan Sanatorium Advent di Bandung (kini RS Advent Bandung) dan perguruan tinggi berasrama di Parongpong Bandung (Universitas Advent Indonesia - UNAI).
    `,
    milestones: [
      { year: '1900', title: 'Kedatangan Ralph Munson di Padang', desc: 'Membuka perintisan jemaat Advent pertama di Kepulauan Nusantara.' },
      { year: '1910-an', title: 'Perluasan ke Jawa & Minahasa', desc: 'Pembentukan jemaat di Sukabumi, Jakarta, dan Manado.' },
      { year: '1949', title: 'Pendirian UNAI Parongpong Bandung', desc: 'Pusat pendidikan teologi, keperawatan, dan bisnis terkemuka Advent di Indonesia.' },
      { year: '1950', title: 'RS Advent Bandung', desc: 'Pelopor pelayanan kesehatan holistik dan edukasi diet nabati sehat.' }
    ],
    heritage: 'Mengelola jaringan Rumah Sakit Advent (Bandung, Manado, Medan), UNAI Parongpong, dan ADRA (Adventist Development and Relief Agency).',
    trivia: 'Penganut Advent di Indonesia dikenal mempraktikkan diet vegetarian sehat dan pantang merokok serta alkohol, menghasilkan angka harapan hidup yang tinggi.',
    icon: 'bi-heart',
    crestBg: 'from-blue-600 to-sky-800',
    tags: ['Advent', 'GMAHK', 'Sabat', 'Padang', 'Bandung', 'UNAI', 'RS Advent', 'Munson']
  },
  {
    id: 'gkp',
    name: 'GKP (Gereja Kristen Pasundan)',
    shortName: 'GKP',
    fullName: 'Sinode Gereja Kristen Pasundan',
    originYear: 1863,
    originEvent: 'Mr. F.L. Anthing Merintis Jemaat Kristen Pribumi Sunda di Batavia & Priangan (1863)',
    synodYear: 1934,
    synodEvent: 'Kemandirian Sinode Gereja Kristen Pasundan di Bandung (14 November 1934)',
    era: 'zending_19',
    eraLabel: 'Abad 19 (Misi Tanah Sunda)',
    region: 'Jawa',
    subRegion: 'Cirebon, Cianjur, Bandung, Jawa Barat',
    denomination: 'Protestan',
    tradition: 'Calvinis / Kontekstual Basa Sunda',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Mr. Frederik Lodewijk Anthing, Pdt. C. Albers, Pdt. Titus',
    missionAgency: 'Perhimpunan Penginjil Mandiri Anthing & NZV (Nederlandsche Zendingsvereeniging)',
    currentHeadquarters: 'Jl. Sudirman No. 638, Bandung, Jawa Barat',
    summary: 'Gereja bersahaja penutur Basa Sunda yang lahir dari pekabaran Injil mandiri Mr. F.L. Anthing dan NZV di bumi Priangan, mandiri sejak 14 November 1934.',
    fullStory: `
      Pekabaran Injil di Tanah Pasundan memiliki keunikan tersendiri karena diawali oleh seorang pejabat hukum Belanda yang sangat mencintai masyarakat pribumi, yaitu Mr. Frederik Lodewijk Anthing (seorang hakim di Batavia). Pada 1863, Anthing mendanai sendiri pemuda-pemuda Kristen lokal untuk belajar Injil dan mengutus mereka ke desa-desa di sekitar Cianjur, Meester Cornelis, dan Karawang.
      
      Gerakan Anthing kemudian disokong oleh badan zending NZV (Nederlandsche Zendingsvereeniging) dengan misionaris seperti C. Albers di Cianjur dan Pdt. D.J. van der Linden. Mereka mendirikan perkampungan Kristen mandiri di Pangharepan dan Palalangon.
      
      Pada 14 November 1934 di Bandung, jemaat-jemaat Pasundan mendeklarasikan kemandirian sinode mereka dengan nama Gereja Kristen Pasundan (GKP). GKP terus konsisten menyuarakan kasih Kristus dalam kehangatan budaya Sunda yang santun dan terbuka.
    `,
    milestones: [
      { year: '1863', title: 'Misi Mandiri Mr. F.L. Anthing', desc: 'Anthing mendidik pemuda penginjil lokal untuk menjangkau Tatar Pasundan.' },
      { year: '1902', title: 'Desa Kristen Palalangon Cianjur', desc: 'Pembukaan pemukiman tani Kristen di Palalangon dan Pangharepan.' },
      { year: '1934', title: 'Kemandirian Sinode GKP', desc: '14 November 1934: Sinode resmi berdiri di Bandung dengan kebaktian berbahasa Sunda.' }
    ],
    heritage: 'Merawat khazanah pujian kidung "Pangrehe Suci" dalam Basa Sunda halus, RS Immanuel Bandung, dan sekolah YPK Pasundan.',
    trivia: 'Di Gereja Palalangon Cianjur, arsitektur gereja dirancang memadukan atap Julang Ngapak khas Sunda dengan salib menara yang asri.',
    icon: 'bi-feather',
    crestBg: 'from-emerald-700 to-green-900',
    tags: ['GKP', 'Pasundan', 'Sunda', 'Anthing', 'Bandung', 'Cianjur', 'PGI', 'Jawa Barat']
  },
  {
    id: 'bnkp',
    name: 'BNKP (Banua Niha Keriso Protestan)',
    shortName: 'BNKP',
    fullName: 'Banua Niha Keriso Protestan',
    originYear: 1865,
    originEvent: 'Pendaratan Misionaris Ludwig Ernst Denninger di Gunungsitoli Nias (27 September 1865)',
    synodYear: 1936,
    synodEvent: 'Sidang Sinode Mandiri BNKP Pertama di Gunungsitoli (1936)',
    era: 'zending_19',
    eraLabel: 'Abad 19 (Misi Pulau Nias)',
    region: 'Sumatera',
    subRegion: 'Gunungsitoli, Pulau Nias, Sumatera Utara',
    denomination: 'Protestan',
    tradition: 'Lutheran',
    oikoumene: ['PGI', 'LWF (Lutheran World Federation)', 'WCC'],
    founder: 'Ernst Ludwig Denninger, Johann Adam Kramer, Pdt. Thomas Sigurö',
    missionAgency: 'Rheinische Missionsgesellschaft (RMG) Barmen, Jerman',
    currentHeadquarters: 'Jl. Soekarno No. 22, Gunungsitoli, Pulau Nias, Sumatera Utara',
    summary: 'Sinode pemersatu suku Nias ("Ono Niha") yang berawal dari kedatangan E.L. Denninger tahun 1865, mengalami kebangunan rohani besar Fangesa Dödö (Pembaruan Hati) tahun 1916.',
    fullStory: `
      Misionaris RMG Ernst Ludwig Denninger mendarat di Gunungsitoli, Pulau Nias pada 27 September 1865 setelah istrinya pulih dari sakit di Batavia. Beliau mulai mempelajari bahasa Nias (Li Niha) dan membuka sekolah pertama. Pada Paskah 1874, Denninger membaptis 25 orang Nias pertama.
      
      Puncak kebangkitan rohani Pulau Nias terjadi pada tahun 1916 yang dikenal sebagai "Fangesa Dödö" (Gerakan Pembaruan Hati dan Pertobatan Massal). Gerakan ini dimulai di Helefanikha dan meluas bagai api ke seluruh penjuru pulau, di mana warga secara sukarela menyerahkan jimat-jimat kuno dan berdamai dengan sesama.
      
      Pada tahun 1936, sinode BNKP resmi berdiri mandiri dengan pengesahan Sinode Pertama di Gunungsitoli. Kini BNKP menaungi lebih dari 80 persen populasi Kepulauan Nias dan ribuan diaspora Nias di kota-kota besar Indonesia.
    `,
    milestones: [
      { year: '1865', title: 'Pendaratan E.L. Denninger', desc: '27 September 1865 menjadi hari Pekabaran Injil bagi masyarakat Pulau Nias.' },
      { year: '1916-1930', title: 'Kebangunan Rohani Fangesa Dödö', desc: 'Gerakan pertobatan akbar yang melahirkan kidung rohani Nias (Buku Zinunö).' },
      { year: '1936', title: 'Sinode Mandiri BNKP', desc: 'Pengesahan Anggaran Dasar dan kepemimpinan sinode mandiri di Gunungsitoli.' }
    ],
    heritage: 'Pilar utama pemersatu masyarakat kepulauan Nias, pengelola STT BNKP Sundermann Gunungsitoli dan museum budaya Nias.',
    trivia: 'Kidung pujian Nias dalam "Buku Zinunö" memiliki melodi vokal polifonik tradisional yang sangat merdu dan khas, diakui para antropolog musik dunia.',
    icon: 'bi-gem',
    crestBg: 'from-amber-600 to-yellow-900',
    tags: ['BNKP', 'Nias', 'Gunungsitoli', 'Denninger', 'Fangesa Dodo', 'Lutheran', 'PGI']
  },
  {
    id: 'gia',
    name: 'Gereja Isa Almasih (GIA)',
    shortName: 'GIA',
    fullName: 'Sinode Gereja Isa Almasih',
    originYear: 1946,
    originEvent: 'Persekutuan Doa Kebangunan Rohani Pringgading Semarang oleh Pdt. Dr. Tan Hok Tjoan (1946)',
    synodYear: 1950,
    synodEvent: 'Pengesahan Badan Hukum Resmi Sinode Gereja Isa Almasih (1950)',
    era: 'pasca_kemerdekaan',
    eraLabel: '1945-Sekarang (Pasca Kemerdekaan)',
    region: 'Jawa & Seluruh Indonesia',
    subRegion: 'Pringgading, Semarang, Jawa Tengah',
    denomination: 'Pentakosta - Injili',
    tradition: 'Pentakosta / Karismatik Klasik',
    oikoumene: ['PGI', 'PGPI'],
    founder: 'Pdt. Dr. Tan Hok Tjoan',
    missionAgency: 'Persekutuan Doa & Kebangunan Rohani Mandiri di Semarang',
    currentHeadquarters: 'Jl. Pringgading No. 13, Semarang, Jawa Tengah',
    summary: 'Sinode unik berakar dari persekutuan doa pasca kemerdekaan tahun 1946 di Pringgading Semarang oleh Pdt. Dr. Tan Hok Tjoan, berpegang teguh pada nama luhur "Isa Almasih".',
    fullStory: `
      Pasca proklamasi kemerdekaan Republik Indonesia, suasana di kota Semarang penuh dengan ketidakpastian. Di tengah situasi genting tersebut, Pdt. Dr. Tan Hok Tjoan bersama sekelompok orang percaya mulai mengadakan persekutuan doa dan penelaahan Alkitab secara intensif di rumahnya di kawasan Pringgading, Semarang pada tahun 1946.
      
      Persekutuan doa ini disertai tanda-tanda mujizat kesembuhan dan jamahan Roh Kudus yang memikat banyak orang. Jemaat bertumbuh sangat pesat sehingga pada awal dekade 1950-an mereka memutuskan melembagakan diri dengan nama resmi "Gereja Isa Almasih".
      
      Penggunaan nama "Isa Almasih" mencerminkan identitas penghormatan atas nama Juruselamat yang telah dikenal luas dalam khazanah bahasa Indonesia dan Timur. GIA terus berkembang membuka cabang di berbagai kota di Jawa, Bali, dan Sumatera.
    `,
    milestones: [
      { year: '1946', title: 'Persekutuan Pringgading', desc: 'Pdt. Dr. Tan Hok Tjoan memulai kebaktian doa di Semarang.' },
      { year: '1950-an', title: 'Badan Hukum Resmi GIA', desc: 'Pengesahan nama dan badan gereja mandiri di Kementerian Agama RI.' },
      { year: '2000-an', title: 'Pemekaran Jemaat Nasional', desc: 'Membuka jemaat-jemaat berkembang di Jakarta, Yogyakarta, dan Surabaya.' }
    ],
    heritage: 'Pusat pembinaan teologi dan pelayanan misi di Semarang, mengelola STT Isa Almasih (STTIA).',
    trivia: 'Gereja Isa Almasih merupakan salah satu sinode pelopor yang secara berani menggunakan nama berbahasa Indonesia/Melayu asli "Isa Almasih" sejak awal kelahirannya.',
    icon: 'bi-lightning-charge',
    crestBg: 'from-amber-600 to-orange-800',
    tags: ['GIA', 'Isa Almasih', 'Semarang', 'Pringgading', 'Tan Hok Tjoan', 'Pentakosta', 'PGI']
  },
  {
    id: 'ortodoks-indonesia',
    name: 'Gereja Ortodoks di Indonesia (GOI)',
    shortName: 'Gereja Ortodoks',
    fullName: 'Gereja Ortodoks Indonesia (Gereja Timur Purba)',
    originYear: 1988,
    originEvent: 'Kepulangan Romo Dr. Daniel Bambang Dwi Byantoro & Pelayanan Liturgi Pertama di Solo (1988)',
    synodYear: 1996,
    synodEvent: 'Pengakuan Hukum Resmi Bimas Kristen Kementerian Agama RI (1996)',
    era: 'pasca_kemerdekaan',
    eraLabel: 'Abad 7 Kuno & 1988 Modern',
    region: 'Jawa & Sumatera',
    subRegion: 'Solo (Surakarta) & Barus (Sumatera Utara)',
    denomination: 'Ortodoks',
    tradition: 'Ortodoks Timur (Patristik Bizantium & Siria)',
    oikoumene: ['Patriarkat Ekumenis Konstantinopel / Gereja Ortodoks Rusia (ROCOR)'],
    founder: 'Arkimandrit Romo Dr. Daniel Bambang Dwi Byantoro',
    missionAgency: 'Pekabaran Teologi Patristik Purba Mandiri',
    currentHeadquarters: 'Paroki Tritunggal Mahakudus, Surakarta & Jakarta',
    summary: 'Mengenalkan tradisi spiritual tertua gereja perdana (bapa-bapa rasuli) ke Indonesia, diprakarsai oleh Romo Daniel Byantoro dengan liturgi puitis bernuansa budaya nusantara.',
    fullStory: `
      Catatan sejarah mencatat bahwa jejak kekristenan paling awal di Nusantara adalah umat Kristen Nestorian / Gereja Timur Asiria yang berlabuh di pelabuhan Barus (Fansur), Sumatera Utara pada abad ke-7.
      
      Kebangunan Gereja Ortodoks modern di Indonesia bermula ketika seorang pemuda muslim asal Solo, Bambang Dwi Byantoro, mengalami perjumpaan pribadi dengan Kristus. Ia menempuh studi teologi di Amerika Serikat, Korea, dan Yunani, hingga ditahbiskan menjadi imam dan menyandang gelar Arkimandrit Daniel Byantoro.
      
      Pada tahun 1988, Romo Daniel kembali ke tanah air dan mendirikan Gereja Ortodoks Indonesia. Beliau menerjemahkan Liturgi Suci Santo Yohanes Krisostomus ke dalam bahasa Indonesia dan memadukan tembang gamelan Jawa dalam kidung pujian dupa liturgis yang agung.
    `,
    milestones: [
      { year: 'Abad ke-7', title: 'Jejak Awal di Barus Fansur', desc: 'Kehadiran saudagar Kristen Timur di pelabuhan kapur barus Sumatera Utara.' },
      { year: '1988', title: 'Kepulangan Romo Daniel Byantoro', desc: 'Memulai kebaktian liturgi Ortodoks pertama di Solo, Jawa Tengah.' },
      { year: '1996', title: 'Pengakuan Hukum Depag RI', desc: 'Gereja Ortodoks diakui secara sah dalam rumpun Bimas Kristen Departemen Agama.' }
    ],
    heritage: 'Pusat studi spiritualitas mistik patristik bapa-bapa gereja purba, penulisan ikonografi kudus di Indonesia.',
    trivia: 'Doa-doa Mazmur dan Liturgi Suci diterjemahkan oleh Romo Daniel ke dalam langgam tembang Macapat Dhandhanggula dan Sinom Jawa.',
    icon: 'bi-incognito',
    crestBg: 'from-amber-700 to-yellow-900',
    tags: ['Ortodoks', 'Daniel Byantoro', 'Solo', 'Barus', 'Bizantium', 'Liturgi', 'Konstantinopel']
  },
  {
    id: 'kharismatik-modern',
    name: 'Gerakan Kharismatik Metropolitan Modern (JPCC, Tiberias, NDC, dll)',
    shortName: 'Kharismatik Modern',
    fullName: 'Gerakan Gereja Kharismatik Kontemporer Perkotaan Indonesia',
    originYear: 1990,
    originEvent: 'Gelombang Kebangunan Rohani & Pelayanan Pemuda Perkotaan Era 1990-an',
    synodYear: 1999,
    synodEvent: 'Pendirian Jemaat Mandiri JPCC & Revolusi Pelayanan Gereja Kontemporer (1999)',
    era: 'pasca_kemerdekaan',
    eraLabel: '1990-an - Abad 21 (Kontemporer)',
    region: 'Kota-Kota Metropolitan (Jakarta, Surabaya, Medan, dll)',
    subRegion: 'Jakarta (Senayan, Kokas, Kelapa Gading, Central Park)',
    denomination: 'Pentakosta - Kharismatik',
    tradition: 'Kharismatik Kontemporer & Discipleship',
    oikoumene: ['PGPI', 'PGI', 'Jaringan Oikoumene Global'],
    founder: 'Pdt. Jeffrey Rachmat (JPCC), Pdt. Pariadji (Tiberias), Pdt. Niko Njotorahardjo, Pdt. Josia Abdisaputera (NDC)',
    missionAgency: 'Gerakan Pembaharuan Kaum Muda & Profesional Kota',
    currentHeadquarters: 'Gedung-gedung Ibadah Kota Jakarta, Surabaya, Bandung, & Medan',
    summary: 'Fenomena pertumbuhan gereja perkotaan dengan aransemen musik modern berkelas dunia, multimedia canggih, dan pemuridan relevan bagi generasi muda profesional Indonesia.',
    fullStory: `
      Memasuki dekade 1990-an dan era Reformasi, kota-kota besar di Indonesia mengalami fenomena kebangunan rohani kontemporer yang sangat masif. Berdirinya komunitas seperti JPCC (Jakarta Praise Community Church) pada 1999 oleh Pdt. Jeffrey Rachmat dan Pdt. Jose Carol mengedepankan pendekatan pemuridan praktis, relevansi iman di tempat kerja, serta komposisi lagu penyembahan melalui True Worshippers yang mendunia.
      
      Di sisi lain, Gereja Tiberias Indonesia yang dirintis oleh Pdt. Dr. Yesaya Pariadji menekankan perjamuan kudus dan minyak urapan dengan kebaktian di gedung-gedung besar seperti Gelora Bung Karno yang dihadiri ratusan ribu jemaat. Sementara itu NDC (Nafiri Discipleship Church) dan GBI Rock memelopori gerakan gereja sel yang dinamis.
      
      Gereja-gereja ini merevolusi standar pelayanan multimedia, pencahayaan panggung, aransemen orkestrasi pujian, serta kepedulian sosial terhadap anak-anak jalanan dan bantuan bencana nasional.
    `,
    milestones: [
      { year: '1990-an', title: 'Kelahiran Tiberias & Pelayanan Minyak Urapan', desc: 'Kebaktian kebangunan rohani berskala stadion di Jakarta.' },
      { year: '1999', title: 'Pendirian JPCC & True Worshippers', desc: 'Gerakan pemuridan kaum muda profesional dan revolusi musik rohani kontemporer.' },
      { year: '2010-an', title: 'Pusat Penyembahan Digital & Global', desc: 'Lagu-lagu pujian karya musisi Kristen Indonesia dinyanyikan oleh gereja di berbagai belahan dunia.' }
    ],
    heritage: 'Penciptaan ribuan album lagu pujian rohani (True Worshippers, Symphony Music, Tiberias Singers), gerakan sosial pemuda dan profesional.',
    trivia: 'Lagu-lagu gubahan pemuda gereja Jakarta telah diterjemahkan ke dalam bahasa Inggris, Mandarin, Korea, dan Spanyol, dinyanyikan di gereja-gereja internasional.',
    icon: 'bi-broadcast-pin',
    crestBg: 'from-purple-700 to-indigo-950',
    tags: ['JPCC', 'Tiberias', 'NDC', 'Kharismatik', 'Jeffrey Rachmat', 'True Worshippers', 'Jakarta', 'Mega Church']
  },
  {
    id: 'gkpm-mentawai',
    name: 'GKPM (Gereja Kristen Protestan di Mentawai)',
    shortName: 'GKPM Mentawai',
    fullName: 'Gereja Kristen Protestan di Mentawai',
    originYear: 1901,
    originEvent: 'Misionaris August Lett Mendarat di Sikakap Mentawai (1901) & Baptisan Perdana 9 Juli 1916',
    synodYear: 1968,
    synodEvent: 'Sinode Mandiri GKPM diresmikan di Nemnemleleu Sikakap Mentawai (11 Juli 1968)',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Misi Kepulauan Mentawai)',
    region: 'Sumatera',
    subRegion: 'Nemnemleleu, Sikakap, Kepulauan Mentawai, Sumatera Barat',
    denomination: 'Protestan',
    tradition: 'Lutheran / Reformed',
    oikoumene: ['PGI', 'LWF (Lutheran World Federation)', 'WCC'],
    founder: 'Pdt. August Lett (Misionaris Martir RMG Jerman), Pdt. F. Boerger, Guru Penginjil Pribumi',
    missionAgency: 'Rheinische Missionsgesellschaft (RMG) Barmen, Jerman',
    currentHeadquarters: 'Kantor Sinode GKPM, Nemnemleleu, Sikakap, Kepulauan Mentawai, Sumatera Barat',
    summary: 'Gereja suku kepulauan Mentawai yang dirintis misionaris August Lett tahun 1901 di Sikakap, melewati pengorbanan martir perdamaian hingga pembaptisan perdana 9 Juli 1916 dan berakar kuat di Siberut, Sipora, serta Pagai.',
    fullStory: `
      Kepulauan Mentawai yang terdiri dari gugusan pulau Siberut, Sipora, Pagai Utara, dan Pagai Selatan memiliki tradisi kepercayaan asli Arat Sabulungan. Pada tahun 1901, RMG Barmen Jerman mengutus misionaris muda Pdt. August Lett bersama istrinya tiba di Nemnemleleu, Sikakap, Pagai Utara.
      
      Perintisan berlangsung penuh tantangan iklim tropis, gelombang Samudra Hindia, dan penyakit malaria. Tragedi besar terjadi pada 20 Agustus 1909: ketika terjadi ketegangan antara tentara patroli kolonial Belanda dengan sekelompok warga lokal di Taikako, August Lett melangkah tanpa senjata untuk melerai dan menjadi penengah damai. Namun dalam kekacauan, sebuah panah beracun mengenai dirinya, dan beliau wafat sebagai martir perdamaian demi membela rakyat Mentawai.
      
      Kemartiran Lett meluluhkan prasangka suku Mentawai. Pekerjaan misi dilanjutkan oleh Pdt. F. Boerger yang menerjemahkan Injil dan kidung ke dalam bahasa Mentawai (Basa Mentawai). Buah iman pertama dituai pada 9 Juli 1916, ketika sembilan pemuda Mentawai pertama dibaptis di Sikakap. Tanggal 9 Juli diperingati sebagai Hari Kebangunan Rohani & Pekabaran Injil Mentawai. Pada tahun 1968 di Nemnemleleu, sinode berdiri mandiri penuh dengan nama Gereja Kristen Protestan di Mentawai (GKPM).
    `,
    milestones: [
      { year: '1901', title: 'Kedatangan Misi August Lett di Sikakap', desc: 'Pdt. August Lett mendirikan pos zending pertama di Nemnemleleu, Pagai Utara.' },
      { year: '1909', title: 'Kemartiran August Lett di Taikako', desc: 'August Lett gugur saat berusaha mendamaikan perselisihan berdarah di Taikako.' },
      { year: '1916', title: 'Baptisan Perdana 9 Juli', desc: 'Sembilan orang Mentawai pertama dibaptis, menjadi tonggak hari kelahiran jemaat Mentawai.' },
      { year: '1930-an', title: 'Penerjemahan Alkitab Bahasa Mentawai', desc: 'Pdt. F. Boerger menerjemahkan kitab Perjanjian Baru dan Buku Kidung Rohani Mentawai.' },
      { year: '1968', title: 'Sinode Mandiri GKPM', desc: 'Kemandirian penuh sinode GKPM berpusat di Nemnemleleu melayani seluruh kepulauan Mentawai.' }
    ],
    heritage: 'Pilar utama pemersatu sosial, pendidikan, dan kesehatan suku Mentawai, mengelola asrama pelajar, kapal misi kepulauan, dan pelestarian kearifan lokal.',
    trivia: 'Makam Pdt. August Lett di Nemnemleleu Sikakap dihormati oleh warga Mentawai sebagai lambang kasih sejati seorang hamba Tuhan yang rela menumpahkan darah demi perdamaian Mentawai.',
    icon: 'bi-compass',
    crestBg: 'from-teal-700 to-slate-900',
    tags: ['GKPM', 'Mentawai', 'August Lett', 'Sikakap', 'Sipora', 'Siberut', 'Pagai', 'Arat Sabulungan', 'Sumatera Barat', 'PGI', 'LWF']
  },
  {
    id: 'gmi-methodist',
    name: 'Gereja Methodist Indonesia (GMI)',
    shortName: 'GMI Methodist',
    fullName: 'Sinode Gereja Methodist Indonesia',
    originYear: 1905,
    originEvent: 'Bishop W.F. Oldham & Solomon Pakianathan Memulai Misi Methodist di Medan (1905)',
    synodYear: 1964,
    synodEvent: 'Kemandirian Provisional Annual Conference GMI di Medan (10 Agustus 1964)',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Awal Abad 20)',
    region: 'Sumatera & Jawa',
    subRegion: 'Medan (Sumut), Palembang (Sumsel), Riau & Jawa',
    denomination: 'Protestan',
    tradition: 'Methodist (Ajaran John Wesley / Kesucian Hidup & Aksi Sosial)',
    oikoumene: ['PGI', 'World Methodist Council (WMC)', 'WCC'],
    founder: 'Bishop William F. Oldham, Pdt. G.F. Pykett, Solomon Pakianathan, Pdt. W.T. Cherry',
    missionAgency: 'Methodist Episcopal Church (Misi Methodist Amerika & Malaysia/Singapura)',
    currentHeadquarters: 'Kantor Sinode GMI, Jl. Hang Tuah No. 8, Medan, Sumatera Utara',
    summary: 'Sinode beraliran Methodist pengikut John Wesley yang dirintis di Medan dan Palembang sejak 1905, terkenal di seluruh Sumatera atas sekolah-sekolah unggulan Perguruan Methodist dan pelayanan medis Susanna Wesley.',
    fullStory: `
      Gereja Methodist berakar dari gerakan rohani kebangunan John Wesley di Inggris abad ke-18. Masuknya misi Methodist ke Indonesia diprakarsai oleh Bishop William F. Oldham dari Dewan Misi Methodist Episcopal Church yang berpusat di Singapura. Pada tahun 1905, diutuslah Solomon Pakianathan ke Medan untuk melayani perantau Kristen Tionghoa dan Tamil di perkebunan Sumatera Timur.
      
      Di saat yang hampir bersamaan, pos pelayanan dibuka di Palembang oleh Pdt. W.T. Cherry. Di Medan, perintisan berkembang sangat pesat dengan dibukanya Anglo-Chinese School (kini Perguruan Methodist Medan) yang menjadi pelopor sekolah modern dwibahasa bermutu tinggi. Misi kemudian merambah ke Riau (Bengkalis, Selatpanjang, Siak) dan kota-kota pelabuhan Sumatera.
      
      Pada tanggal 9 Agustus 1964 di Medan, Gereja Methodist Indonesia (GMI) diresmikan sebagai gereja mandiri otonom dari United Methodist Church. GMI kini terbagi ke dalam dua wilayah yurisdiksi besar: Wilayah I (meliputi Sumatera Utara dan Aceh) serta Wilayah II (meliputi Riau, Kepri, Jambi, Sumsel, Bengkulu, Lampung, hingga Jawa dan Bali).
    `,
    milestones: [
      { year: '1905', title: 'Perintisan Misi di Medan & Palembang', desc: 'Solomon Pakianathan dan utusan Bishop Oldham memulai pelayanan di Medan dan Palembang.' },
      { year: '1910-an', title: 'Pendirian Perguruan Methodist', desc: 'Pembukaan jaringan sekolah Methodist yang mendidik ratusan ribu pemimpin bangsa di Sumatera.' },
      { year: '1964', title: 'Kemandirian Sinode Otonom GMI', desc: '9 Agustus 1964: Deklarasi kemandirian Gereja Methodist Indonesia terpisah dari misi Amerika.' },
      { year: '2000-an', title: 'Pemekaran Dua Wilayah Episkopal', desc: 'Struktur kepemimpinan dipimpin dua Bishop: Konferensi Tahunan Wilayah I dan Wilayah II.' }
    ],
    heritage: 'Jaringan sekolah bergengsi Perguruan Methodist (Methodist 1, 2, 3 di Medan, Palembang, Pekanbaru), Universitas Methodist Indonesia (UMI) Medan, dan RS Susanna Wesley.',
    trivia: 'Tradisi Methodist di Sumatera sangat kuat memadukan penginjilan pribadi dengan disiplin kelas pemuridan kecil (class meeting) warisan John Wesley.',
    icon: 'bi-mortarboard',
    crestBg: 'from-red-800 to-rose-950',
    tags: ['Methodist', 'GMI', 'John Wesley', 'Oldham', 'Medan', 'Palembang', 'Riau', 'Bengkalis', 'PGI', 'Sumatera']
  },
  {
    id: 'gereja-riau',
    name: 'Cikal Bakal Gereja di Riau & Kepulauan Riau',
    shortName: 'Gereja Riau & Kepri',
    fullName: 'Jejak Pekabaran Injil & Pertumbuhan Gereja di Bumi Lancang Kuning Riau',
    originYear: 1910,
    originEvent: 'Pos Pekabaran Injil Selatpanjang (1910) & Gelombang Pekerja Minyak Caltex Minas-Duri (1950)',
    synodYear: 1958,
    synodEvent: 'Pemekaran Distrik Mandiri XXII Riau HKBP & Ekosistem Jaringan Sinode Oikoumenis Riau',
    era: 'kemandirian_early',
    eraLabel: 'Awal Abad 20 & Era Minyak 1950',
    region: 'Sumatera',
    subRegion: 'Pekanbaru, Rumbai, Minas, Duri, Dumai, Selatpanjang & Bengkalis (Riau)',
    denomination: 'Oikoumenis / Lintas Denominasi',
    tradition: 'Reformed, Methodist, Pentakosta & Karismatik',
    oikoumene: ['PGIW Riau', 'PGPI Riau', 'PGLII Riau'],
    founder: 'Guru J. Simorangkir, Misi Methodist Selatpanjang, Komunitas Karyawan Minyak Caltex',
    missionAgency: 'Misi Methodist Melayu, Zending Batak & Jemaat Diaspora Mandiri',
    currentHeadquarters: 'Pusat Oikoumene PGI Wilayah Riau, Pekanbaru',
    summary: 'Kisah unik pertumbuhan gereja di tanah Melayu Riau, berakar dari pos zending pelabuhan Selatpanjang-Bengkalis (1910) dan ledakan migrasi insinyur serta pekerja ladang minyak Caltex di Minas, Rumbai, dan Duri sejak era 1950-an.',
    fullStory: `
      Kehadiran gereja di wilayah Riau memiliki latar sejarah yang unik di bumi Nusantara. Babak pertama dimulai pada awal abad ke-20 di kota-kota pelabuhan pesisir seperti Selatpanjang, Bagansiapiapi, dan Bengkalis melalui perintisan misi Methodist dan Tiong Hoa Kie Tok Kauw Hwee (THKTKH) yang melayani masyarakat pedagang.
      
      Babak kebangkitan kedua terjadi secara dramatis pada awal 1950-an saat perusahaan eksplorasi minyak bumi Caltex Pacific Indonesia (kini Pertamina Hulu Rokan) menemukan cadangan minyak terbesar di Minas, Duri, dan Rumbai. Ribuan tenaga ahli, insinyur perminyakan, dokter, dan buruh terdidik dari berbagai daerah Kristen di Nusantara (Batak, Minahasa, Ambon, Jawa, dan Flores) datang dan bermukim di Camp Rumbai dan Minas.
      
      Di perkemahan minyak tersebut, mereka bersama-sama mendirikan gereja-gereja oikoumenis pertama di pedalaman Riau, seperti jemaat GPIB Pniel Pekanbaru, HKBP Rumbai, GKPI Duri, serta pos-pos pekabaran Injil Methodist dan Katolik. Kini Riau menjadi salah satu wilayah dengan dinamika gereja paling bersemangat dan rukun berdampingan secara harmonis dengan adat budaya Melayu.
    `,
    milestones: [
      { year: '1910-an', title: 'Pos Misi Pesisir Selatpanjang & Bengkalis', desc: 'Membuka sekolah dan pos kebaktian bagi warga Tionghoa dan perantau Selat Malaka.' },
      { year: '1952', title: 'Perintisan Jemaat Minyak Rumbai & Minas', desc: 'Komunitas karyawan Kristen Caltex menggelar kebaktian bersama di Camp Rumbai.' },
      { year: '1958', title: 'Pendirian HKBP & GPIB Pekanbaru', desc: 'Gedung gereja permanen pertama berdiri di pusat ibukota Provinsi Riau.' },
      { year: '1970-an', title: 'Ledakan Pertumbuhan Jemaat Perkebunan', desc: 'Pembukaan kebun sawit dan transmigrasi melipatgandakan ratusan jemaat di pelosok Riau.' }
    ],
    heritage: 'Melahirkan jemaat-jemaat terkemuka seperti HKBP Hang Tuah Pekanbaru, GPIB Pniel, GMI Wesley Pekanbaru, GBI Bethel Riau, dan sekolah-sekolah Kristen di Pekanbaru dan Duri.',
    trivia: 'Gedung pertemuan gereja pertama di Rumbai Caltex awalnya dibangun berdampingan di dalam kompleks perumahan karyawan perusahaan minyak dengan fasilitas audio dan pendingin ruangan modern pertama di Riau.',
    icon: 'bi-fuel-pump',
    crestBg: 'from-amber-700 to-slate-900',
    tags: ['Riau', 'Pekanbaru', 'Rumbai', 'Minas', 'Duri', 'Dumai', 'Selatpanjang', 'Bengkalis', 'Caltex', 'Minyak', 'PGIW Riau']
  },
  {
    id: 'gereja-bengkulu',
    name: 'Cikal Bakal Gereja di Bengkulu (Era Benteng Marlborough & Rejang)',
    shortName: 'Gereja Bengkulu',
    fullName: 'Jejak Sejarah Kekristenan di Bumi Rafflesia Bengkulu',
    originYear: 1818,
    synodYear: 1960,
    era: 'voc_early',
    eraLabel: 'Abad 19 (Misi Raffles & Zending)',
    region: 'Sumatera',
    subRegion: 'Fort Marlborough (Kota Bengkulu), Curup, Rejang Lebong, Bengkulu',
    denomination: 'Oikoumenis / Protestan & Methodist',
    tradition: 'Anglikan, Baptis, Methodist, dan Presbiterial',
    oikoumene: ['PGIW Bengkulu', 'Komite Antar Gereja Bengkulu'],
    founder: 'Sir Thomas Stamford Raffles, William Robinson (Misionaris Baptis Inggris), Pdt. Misi Curup',
    missionAgency: 'Baptist Missionary Society (BMS) Inggris & Misi Methodist Sumatera',
    currentHeadquarters: 'Gereja-Gereja Wilayah Bengkulu, Jl. Veteran / Pintu Batu, Kota Bengkulu',
    summary: 'Sejarah pekabaran Injil di pesisir barat Sumatera sejak era kekuasaan Inggris di Benteng Fort Marlborough (1818) yang didukung Gubernur Jenderal Stamford Raffles, dilanjutkan perkembangan jemaat di Curup dan pegunungan Rejang Lebong.',
    fullStory: `
      Bengkulu memiliki status sejarah yang sangat istimewa di Indonesia karena pernah berada di bawah kekuasaan Imperium Britania Raya (EIC) selama hampir 140 tahun (1685–1824) dengan pusatnya di Benteng Fort Marlborough. Pada masa kepemimpinan Letnan Gubernur Sir Thomas Stamford Raffles (1818–1824), Raffles secara pribadi mendukung pekabaran Injil dan pendidikan literasi di Bengkulu.
      
      Raffles mengundang para misionaris dari Baptist Missionary Society (BMS) London, di antaranya Pendeta William Robinson dan Thomas Trowt, untuk mendirikan sekolah gratis bagi anak-anak pribumi di Bengkulu, mencetak literatur bahasa Melayu, dan menerjemahkan Injil. Meskipun Inggris kemudian menyerahkan Bengkulu kepada Belanda lewat Traktat London 1824, benih pengajaran kebajikan Kristen tidak pernah padam.
      
      Pada dekade 1920-an hingga pasca kemerdekaan, pelayanan dihidupkan kembali melalui kedatangan guru-guru Methodist di Curup (Rejang Lebong) dan dibukanya jemaat GPIB, HKBP, GKI, serta Gereja Kristen Rejang. Komunitas Kristen di Bengkulu hidup rukun dan menjunjung tinggi falsafah kearifan lokal "Seia Sekata" bumi Rafflesia.
    `,
    milestones: [
      { year: '1818', title: 'Misi William Robinson di Era Raffles', desc: 'Pendirian sekolah rakyat dan penerjemahan literatur rohani di Fort Marlborough.' },
      { year: '1824', title: 'Traktat London', desc: 'Bengkulu diserahkan ke Belanda, jemaat dibina secara oikoumenis oleh Indische Kerk.' },
      { year: '1930-an', title: 'Pekabaran Injil ke Dataran Tinggi Curup', desc: 'Misi menjangkau kawasan sejuk Rejang Lebong dan perkebunan teh kepahiang.' },
      { year: '1960-an', title: 'Konsolidasi PGI Wilayah Bengkulu', desc: 'Pembentukan wadah oikoumene antar gereja melayani seluruh kabupaten di Provinsi Bengkulu.' }
    ],
    heritage: 'Situs cagar budaya makam para pekabar Injil di kompleks Fort Marlborough, Gereja GPIB Immanuel Bengkulu, GMI Curup, dan sekolah Methodist Curup.',
    trivia: 'Di dalam Benteng Marlborough Bengkulu masih terdapat prasasti nisan kuno peninggalan pejabat dan pekabar Injil abad ke-18 dan awal abad ke-19.',
    icon: 'bi-shield-shaded',
    crestBg: 'from-amber-600 to-stone-900',
    tags: ['Bengkulu', 'Marlborough', 'Raffles', 'Curup', 'Rejang', 'William Robinson', 'Sumatera', 'PGI']
  },
  {
    id: 'gkps',
    name: 'GKPS (Gereja Kristen Protestan Simalungun)',
    shortName: 'GKPS Simalungun',
    fullName: 'Gereja Kristen Protestan Simalungun',
    originYear: 1903,
    originEvent: 'Pdt. August Theis Menginjakkan Kaki di Pematang Raya Simalungun (2 September 1903)',
    synodYear: 1963,
    synodEvent: 'Kemandirian Penuh Sinode GKPS Mandiri Terpisah dari HKBP (1 September 1963)',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Misi Tanah Simalungun)',
    region: 'Sumatera',
    subRegion: 'Pematang Siantar & Pematang Raya, Simalungun, Sumatera Utara',
    denomination: 'Protestan',
    tradition: 'Lutheran / Reformed',
    oikoumene: ['PGI', 'LWF (Lutheran World Federation)', 'WCC'],
    founder: 'Pdt. August Theis (Misionaris RMG), Guru Jason Saragih, Tuan Rondahaim Saragih',
    missionAgency: 'Rheinische Missionsgesellschaft (RMG) Barmen Jerman',
    currentHeadquarters: 'Kantor Pusat Sinode GKPS, Jl. Pdt. J. Wismar Saragih No. 23, Pematang Siantar',
    summary: 'Gereja suku Simalungun berakar dari kedatangan Pdt. August Theis pada 2 September 1903 di Pematang Siantar, terkenal dengan perjuangan literasi Alkitab dan kidung Haleluya dalam bahasa Simalungun oleh Guru J. Wismar Saragih.',
    fullStory: `
      Pekabaran Injil di Tano Habonaron Do Bona (Simalungun) diawali saat misionaris RMG Pdt. August Theis tiba di Pematang Siantar pada tanggal 2 September 1903. Di tengah kecurigaan para raja-raja Simalungun, Theis perlahan mendapatkan kepercayaan Raja Pamatang Raya, Tuan Rondahaim Saragih dan penerusnya.
      
      Pembaptisan pertama orang Simalungun terjadi pada 1907. Namun tantangan besar timbul karena gereja saat itu diadministrasikan di bawah distrik HKBP dengan liturgi berbahasa Batak Toba yang kurang dipahami orang Simalungun. Seorang putra Simalungun terdidik yang cerdas dan gigih, Guru J. Wismar Saragih (kelak menjadi pendeta Simalungun pertama), memperjuangkan agar firman Tuhan diterjemahkan ke dalam bahasa ibu Simalungun.
      
      Wismar Saragih menerjemahkan Perjanjian Baru ke Bahasa Simalungun dan menyusun buku nyanyian "Haleluya". Pada 1 September 1963 di Pematang Raya, sinode GKPS resmi berdiri mandiri secara otonom dari HKBP dan menjadi pengayom kebudayaan luhur Simalungun.
    `,
    milestones: [
      { year: '1903', title: 'Pendaratan Pdt. August Theis', desc: '2 September 1903: Masuknya zending RMG di Pematang Siantar diperingati sebagai HUT PI Simalungun.' },
      { year: '1928', title: 'Komite Na Sa-Ria Simalungun', desc: 'Gerakan pemuda Simalungun menuntut penggunaan bahasa daerah dalam kebaktian gereja.' },
      { year: '1953', title: 'Alkitab Bahasa Simalungun', desc: 'Pdt. J. Wismar Saragih merampungkan penerjemahan seluruh Alkitab ke Bahasa Simalungun.' },
      { year: '1963', title: 'Kemandirian Penuh Sinode GKPS', desc: '1 September 1963: GKPS resmi menjadi sinode mandiri di Pematang Raya.' }
    ],
    heritage: 'Universitas Simalungun (USI), Pusat Asrama Pelajar GKPS, Percetakan Salbe, dan Rumah Sakit GKPS di Saribudolok.',
    trivia: 'Pdt. J. Wismar Saragih dinobatkan sebagai pelopor literasi modern Simalungun karena menulis kamus pertama bahasa Simalungun-Belanda dan puluhan buku adat.',
    icon: 'bi-gem',
    crestBg: 'from-amber-600 to-yellow-800',
    tags: ['GKPS', 'Simalungun', 'August Theis', 'Wismar Saragih', 'Pematang Siantar', 'Raya', 'Haleluya', 'PGI', 'LWF']
  },
  {
    id: 'gkpa',
    name: 'GKPA (Gereja Kristen Protestan Angkola)',
    shortName: 'GKPA Angkola',
    fullName: 'Gereja Kristen Protestan Angkola',
    originYear: 1861,
    originEvent: 'Penginjil Gerrit van Asselt Menetap di Parausorat Sipirok Angkola (1861)',
    synodYear: 1975,
    synodEvent: 'Sinode Mandiri GKPA Diresmikan di Padangsidimpuan (19 Oktober 1975)',
    era: 'zending_19',
    eraLabel: 'Abad 19 & Kemandirian 1975',
    region: 'Sumatera',
    subRegion: 'Sipirok & Padangsidimpuan, Tapanuli Selatan, Sumatera Utara',
    denomination: 'Protestan',
    tradition: 'Lutheran / Kontekstual Adat Dalihan Na Tolu Angkola',
    oikoumene: ['PGI', 'LWF', 'WCC'],
    founder: 'Pdt. Gerrit van Asselt (Misi Ermelo Belanda), Pdt. W. Klammer, Pdt. W. Heine (RMG)',
    missionAgency: 'Zending Ermelo Belanda & RMG Barmen Jerman',
    currentHeadquarters: 'Kantor Pusat Sinode GKPA, Jl. Teuku Umar No. 102, Padangsidimpuan',
    summary: 'Sinode berakar dari titik awal zending tertua di Tapanuli Selatan (Sipirok 1861) oleh Gerrit van Asselt, menghadirkan kesaksian damai di tengah masyarakat Angkola yang kental dengan falsafah Dalihan Na Tolu.',
    fullStory: `
      Jejak zending di Tanah Batak bagian selatan sesungguhnya mendahului kedatangan Nommensen di Silindung. Pada awal tahun 1861, seorang pekabar Injil mandiri asal Ermelo Belanda, Gerrit van Asselt, mulai melayani di Parausorat (Sipirok). Van Asselt membaptis dua orang Batak pertama, Simon Siregar dan Jakobus Sipahutar, pada 31 Maret 1861.
      
      Pekerjaan zending Ermelo kemudian diserahkan kepada RMG Barmen dengan misionaris Klammer dan Heine yang mendirikan pos gereja permanen di Baringin, Sipirok, dan Padangsidimpuan. Wilayah Angkola memiliki kekhasan karena penduduknya hidup berdampingan erat dalam tali kekerabatan marga Dalihan Na Tolu bersama warga Muslim.
      
      Gereja di Angkola sempat berada di bawah naungan HKBP Distrik 1 Angkola. Namun demi efektivitas pelayanan dan penguatan budaya tutur bahasa Angkola, pada 26 Oktober 1975 jemaat-jemaat Angkola bersepakat mendirikan sinode mandiri bernama GKPA.
    `,
    milestones: [
      { year: '1861', title: 'Misi Gerrit van Asselt di Sipirok', desc: '31 Maret 1861: Pembaptisan dua orang pertama di Parausorat Sipirok.' },
      { year: '1870-an', title: 'Pembangunan Gereja Baringin Sipirok', desc: 'Mendirikan gedung gereja cagar budaya tertua di Tapanuli Selatan.' },
      { year: '1975', title: 'Deklarasi Sinode Mandiri GKPA', desc: '26 Oktober 1975: GKPA diresmikan di Padangsidimpuan dengan Ephorus pertama Pdt. C.T. Siregar.' }
    ],
    heritage: 'Merawat gedung gereja bersejarah Sipirok Baringin (1870-an) dan mengayomi sekolah-sekolah di Tapanuli Selatan.',
    trivia: 'Masyarakat Angkola Kristen dan Muslim dikenal memiliki tingkat toleransi yang sangat tinggi di mana dalam acara adat perkawinan dan pesta marga selalu disediakan dapur terpisah yang saling menghormati.',
    icon: 'bi-feather',
    crestBg: 'from-emerald-700 to-slate-900',
    tags: ['GKPA', 'Angkola', 'Sipirok', 'Padangsidimpuan', 'Van Asselt', 'Dalihan Na Tolu', 'Tapanuli Selatan', 'PGI']
  },
  {
    id: 'gkpi',
    name: 'GKPI (Gereja Kristen Protestan Indonesia)',
    shortName: 'GKPI',
    fullName: 'Gereja Kristen Protestan Indonesia',
    originYear: 1964,
    originEvent: 'Gerakan Pembaruan Rohani & Tata Gereja di Pematangsiantar (30 Agustus 1964)',
    synodYear: 1964,
    synodEvent: 'Sinode Mandiri GKPI Diresmikan di Pematangsiantar (30 Agustus 1964)',
    era: 'pasca_kemerdekaan',
    eraLabel: '1945-Sekarang (Pembaruan Sinodal)',
    region: 'Sumatera & Seluruh Indonesia',
    subRegion: 'Pematang Siantar, Toba, Medan & Kota-Kota Diaspora',
    denomination: 'Protestan',
    tradition: 'Lutheran / Presbiterial-Sinodal Terbuka',
    oikoumene: ['PGI', 'LWF', 'WCC'],
    founder: 'Pdt. Dr. Andar M. Lumbantobing, Ds. P. Sihombing, Guru-guru Teologi Pribumi',
    missionAgency: 'Gerakan Pembaruan Tata Gereja & Kepemimpinan Sinodal Mandiri',
    currentHeadquarters: 'Kantor Sinode GKPI, Jl. Sriwijaya No. 9-11, Pematang Siantar, Sumatera Utara',
    summary: 'Lahir dari gerakan pembaruan teologi dan desentralisasi kepemimpinan gereja yang dipelopori teolog Pdt. Dr. Andar Lumbantobing pada 30 Agustus 1964 di Pematang Siantar, mengedepankan peranan aktif kaum awam.',
    fullStory: `
      Pada awal dekade 1960-an, di dalam tubuh gereja-gereja Protestan di Sumatera Utara timbul kerinduan mendalam dari kalangan cendekiawan dan pemuda untuk melihat pembaruan tata gereja yang lebih demokratis, transparan, serta memberikan ruang seluas-luasnya bagi peranan warga jemaat biasa (kaum awam).
      
      Gerakan pembaruan ini dipelopori oleh Pdt. Dr. Andar Martinus Lumbantobing, seorang doktor teologi lulusan Jerman yang juga menjabat sebagai Rektor Universitas HKBP Nommensen yang pertama, bersama tokoh senior Ds. P. Sihombing. Pada tanggal 30 Agustus 1964 di Gedung Kesenian Pematang Siantar, dideklarasikanlah pendirian Gereja Kristen Protestan Indonesia (GKPI).
      
      GKPI mengadopsi struktur kepemimpinan yang kolegial, pastoral, dan modern. Belakangan GKPI diterima penuh sebagai anggota Persekutuan Gereja-Gereja di Indonesia (PGI) dan Federasi Lutheran Sedunia (LWF), melayani di berbagai pelosok nusantara.
    `,
    milestones: [
      { year: '1964', title: 'Deklarasi Pendirian GKPI', desc: '30 Agustus 1964: Deklarasi akbar di Pematang Siantar dipimpin Pdt. Dr. Andar Lumbantobing.' },
      { year: '1970-an', title: 'Pusat Pelatihan Diakonia & Pertanian', desc: 'Mendirikan pusat pembinaan pertanian dan sosial bagi masyarakat desa di Toba.' },
      { year: '1984', title: 'Penerimaan Anggota PGI & LWF', desc: 'GKPI secara resmi diakui penuh dalam keluarga oikoumene nasional dan dunia.' }
    ],
    heritage: 'Pusat Pelatihan Diakonia GKPI di Pematang Siantar, Yayasan Pendidikan GKPI, dan kontribusi karya penulisan teologi kontekstual Indonesia.',
    trivia: 'Pdt. Dr. Andar Lumbantobing adalah salah satu teolog Indonesia pertama yang menulis disertasi ilmiah mendalam tentang konsep "Sahala" (daya kharisma kepemimpinan Batak) di Universitas Tübingen Jerman.',
    icon: 'bi-lightbulb',
    crestBg: 'from-blue-700 to-indigo-900',
    tags: ['GKPI', 'Andar Lumbantobing', 'Pematang Siantar', 'Pembaruan', 'Lutheran', 'PGI', 'Sumatera']
  },
  {
    id: 'hki',
    name: 'HKI (Huria Kristen Indonesia)',
    shortName: 'HKI',
    fullName: 'Huria Kristen Indonesia',
    originYear: 1927,
    originEvent: 'Kemandirian Jemaat Batak Pantoan oleh Pdt. M.D. Panggabean (1 Mei 1927)',
    synodYear: 1927,
    synodEvent: 'Sinode Huria Kristen Indonesia (HKI) Diresmikan di Pematangsiantar',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Kemandirian Pribumi)',
    region: 'Sumatera & Diaspora Nasional',
    subRegion: 'Pantoan, Pematang Siantar, Tapanuli & Riau',
    denomination: 'Protestan',
    tradition: 'Lutheran',
    oikoumene: ['PGI', 'LWF', 'WCC'],
    founder: 'Guru P. Sitompul, Guru H. Simorangkir, St. K. Silalahi',
    missionAgency: 'Gerakan Kemandirian Jemaat Pribumi Nusantara',
    currentHeadquarters: 'Kantor Pusat HKI, Jl. Gereja No. 49, Pematang Siantar, Sumatera Utara',
    summary: 'Pelopor kemandirian gereja pribumi Batak yang didirikan pada 1 Mei 1927 di Pantoan Siantar dengan nama awal "Huria Kristen Batak", bertekad membiayai dan memimpin gereja sendiri tanpa subsidi kolonial.',
    fullStory: `
      Pada dekade 1920-an, semangat kebangkitan nasional Indonesia (Budi Utomo, Sumpah Pemuda) merasuk kuat ke sanubari para guru jemaat pribumi di Sumatera Utara. Mereka mendambakan sebuah gereja yang mandiri seutuhnya, dipimpin oleh putra daerah, dan tidak terus-menerus bergantung kepada dana maupun restu zending bangsa Eropa.
      
      Pada tanggal 1 Mei 1927 di Pantoan, Pematang Siantar, sekelompok guru dan sintua memproklamirkan berdirinya "Huria Kristen Batak" (HKB). Peristiwa ini mendahului kemandirian HKBP (1930/1940) sehingga para perintis HKB sempat menghadapi tekanan berat dari otoritas kolonial Belanda.
      
      Pada tahun 1946, sinode memperluas visinya dengan menanggalkan sekat kesukuan dan mengubah namanya menjadi "Huria Kristen Indonesia" (HKI). HKI membuktikan bahwa gereja dapat tumbuh subur murni atas pengorbanan dan persembahan tulus umatnya sendiri.
    `,
    milestones: [
      { year: '1927', title: 'Deklarasi 1 Mei di Pantoan Siantar', desc: 'Kelahiran sinode mandiri pertama yang diprakarsai penuh oleh sintua dan guru pribumi.' },
      { year: '1933', title: 'Pengesahan Badan Hukum Hindia Belanda', desc: 'Mendapatkan pengakuan hukum resmi setelah perjuangan hukum yang gigih.' },
      { year: '1946', title: 'Pergantian Nama Menjadi HKI', desc: 'Menegaskan komitmen kebangsaan berwawasan kesatuan Republik Indonesia.' }
    ],
    heritage: 'Mengayomi ratusan resort dan ribuan jemaat di Sumatera Utara, Riau, Kepri, Jambi, Jakarta, dan Jawa.',
    trivia: 'Pendiri HKI mengusung prinsip "Gereja Berdiri di Atas Kaki Sendiri" (Berdikari) puluhan tahun sebelum istilah tersebut dipopulerkan Presiden Soekarno.',
    icon: 'bi-flag',
    crestBg: 'from-amber-600 to-red-800',
    tags: ['HKI', 'Pantoan', 'Pematang Siantar', 'Berdikari', 'Pribumi', 'Lutheran', 'PGI', 'Sumatera']
  },
  {
    id: 'gkpb-bali',
    name: 'GKPB (Gereja Kristen Protestan di Bali)',
    shortName: 'GKPB Bali',
    fullName: 'Sinode Gereja Kristen Protestan di Bali',
    originYear: 1931,
    synodYear: 1949,
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Misi Tanah Dewata)',
    region: 'Bali & Nusa Tenggara',
    subRegion: 'Untal-untal (Badung) & Desa Blimbingsari (Jembrana), Bali',
    denomination: 'Protestan',
    tradition: 'Reformed / Kontekstual Seni Arsitektur Budaya Bali',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Tsang Kam Foek (Misionaris Tionghoa), I Made Tengkeg, Pdt. Dirk de Vroom, Pdt. I Wayan Mastra',
    missionAgency: 'The Christian and Missionary Alliance (CMA) & Zending Belanda',
    currentHeadquarters: 'Kantor Sinode GKPB, Gedung Bintang Timur, Jl. Raya Kapal No. 20, Mengwi, Badung, Bali',
    summary: 'Sinode unik di Pulau Dewata yang lahir dari baptisan perdana 11 November 1931 di Untal-untal, mendirikan Desa Kristen Blimbingsari dengan arsitektur gereja bermahkota pura wantilan Bali bertatahkan Salib Kristus.',
    fullStory: `
      Pemerintah Hindia Belanda pada awalnya melarang pekabaran Injil di Pulau Bali demi menjaga kelestarian adat budaya dan agama Hindu Bali. Namun pada akhir 1920-an, seorang penginjil Tionghoa beraliran CMA, Tsang Kam Foek, mulai membagikan buku-buku Injil secara santun kepada masyarakat di Mengwi dan Badung.
      
      Pada tanggal 11 November 1931, di sebuah sungai kecil di Untal-untal, dilangsungkanlah pembaptisan terhadap 12 orang Bali pertama, di antaranya I Made Tengkeg dan I Wayan Dibjo. Ketika warga Kristen baru ini menghadapi pengucilan sosial dari banjar asal mereka, pemerintah kolonial mengizinkan mereka membuka hutan belantara di Jembrana barat.
      
      Di bawah pimpinan I Wayan Deker dan rekan-rekannya, lahirlah Desa Kristen Blimbingsari pada tahun 1939. Di desa ini, iman Kristen menyatu indah dengan budaya Bali: lonceng gereja digantikan kulkul kayu berukir, gedung gereja dibangun menggunakan arsitektur pura wantilan Bali beratapkan ijuk, dan jemaat memakai kebaya serta udeng dalam kebaktian sakral.
    `,
    milestones: [
      { year: '1931', title: 'Baptisan 12 Orang Bali di Untal-untal', desc: '11 November 1931 diperingati sebagai hari kelahiran Kekristenan di Pulau Bali.' },
      { year: '1939', title: 'Pembukaan Hutan Desa Blimbingsari', desc: 'Warga Kristen Bali membangun pemukiman mandiri berbasis persawahan subak di Jembrana.' },
      { year: '1949', title: 'Kemandirian Sinode GKPB', desc: 'Pengesahan sinode otonom dipimpin pendeta pribumi pertama Bali.' },
      { year: '1970-an', title: 'Kontekstualisasi Teologi Pdt. Dr. I Wayan Mastra', desc: 'Membangun Pusat Kebudayaan Dhyana Pura dan arsitektur gereja bergaya candi Bali.' }
    ],
    heritage: 'Desa Wisata Spiritual Blimbingsari, Universitas Dhyana Pura (UNDHIRA) Bali, Rumah Sakit Kristen Puri Raharja Denpasar.',
    trivia: 'Gereja Pniel Blimbingsari tidak menggunakan lonceng besi barat melainkan menara kulkul kayu khas banjar Bali yang dipukul dengan irama sakral penanda waktu ibadah.',
    icon: 'bi-flower3',
    crestBg: 'from-amber-600 to-orange-900',
    tags: ['GKPB', 'Bali', 'Blimbingsari', 'Untal-untal', 'Wayan Mastra', 'Jembrana', 'Badung', 'PGI', 'Reformed']
  },
  {
    id: 'gkst',
    name: 'GKST (Gereja Kristen Sulawesi Tengah)',
    shortName: 'GKST Tentena',
    fullName: 'Sinode Gereja Kristen Sulawesi Tengah',
    originYear: 1892,
    synodYear: 1947,
    era: 'zending_19',
    eraLabel: 'Abad 19 & Kemandirian 1947',
    region: 'Sulawesi',
    subRegion: 'Tentena, Danau Poso, Lembah Bada, Morowali, Sulawesi Tengah',
    denomination: 'Protestan',
    tradition: 'Calvinis / Reformed',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Dr. Albertus Christiaan Kruyt (Bapak Misi Poso) & Dr. Nicolaus Adriani (Pakar Bahasa Bare\'e)',
    missionAgency: 'Nederlandsch Zendeling Genootschap (NZG) Rotterdam',
    currentHeadquarters: 'Kantor Sinode GKST, Jl. Diponegoro No. 20, Tentena, Poso, Sulawesi Tengah',
    summary: 'Pilar persaudaraan masyarakat Danau Poso yang dirintis Dr. A.C. Kruyt dan pakar bahasa Dr. N. Adriani sejak 1892, mentransformasi tradisi suku Pamona-Bare\'e dengan pendekatan kasih, literasi aksara, dan kemandirian.',
    fullStory: `
      Sulawesi Tengah pedalaman pada abad ke-19 merupakan daerah yang terisolasi dengan tradisi perang antar-suku. Badan zending NZG mengutus Dr. Albertus Christiaan Kruyt tiba di Poso pada tahun 1892. Bersama sahabat karibnya, Dr. Nicolaus Adriani (seorang pakar linguistik Alkitab asal Belanda), mereka memutuskan tinggal berbaur di tengah masyarakat suku Pamona di pesisir Danau Poso.
      
      Kruyt menerapkan metode misi antropologis yang sangat terkenal di dunia: ia mempelajari adat istiadat, kepercayaan lamoa, serta merawat orang sakit tanpa memaksakan konversi tergesa-gesa. Pembaptisan pertama terjadi di Kasiguncu pada hari Natal 1909 terhadap Papa i Wunte dan keluarganya.
      
      Pada tanggal 18 Oktober 1947 di Tentena, sinode Gereja Kristen Sulawesi Tengah (GKST) resmi berdiri mandiri. GKST menjadi tiang utama perdamaian, pendidikan, dan pemulihan rekonsiliasi pasca-konflik Poso melalui ikrar perdamaian Deklarasi Malino.
    `,
    milestones: [
      { year: '1892', title: 'Kedatangan Dr. A.C. Kruyt di Poso', desc: 'Membuka pos zending di pesisir Danau Poso dan mempelajari kebudayaan lokal Pamona.' },
      { year: '1909', title: 'Baptisan Pertama di Kasiguncu', desc: 'Natal 1909: Pembaptisan kepala suku Papa i Wunte menandai awal jemaat Kristen Poso.' },
      { year: '1947', title: 'Sinode Mandiri GKST di Tentena', desc: '18 Oktober 1947: Diresmikan sebagai sinode mandiri dengan Ketua Sinode Pdt. K. Stefens.' },
      { year: '2001', title: 'Deklarasi Damai Malino', desc: 'GKST berperan sentral memulihkan persaudaraan sejati masyarakat Poso pasca pertikaian.' }
    ],
    heritage: 'Universitas Kristen Tentena (UNKRIT), Rumah Sakit Sinar Kasih Tentena, dan Sekolah Teologi Tentena.',
    trivia: 'Buku-buku karya Dr. A.C. Kruyt tentang etnografi suku Bare\'e di Poso hingga kini menjadi rujukan utama ilmu antropologi budaya dunia di Universitas Leiden Belanda.',
    icon: 'bi-water',
    crestBg: 'from-blue-700 to-teal-900',
    tags: ['GKST', 'Tentena', 'Poso', 'Danau Poso', 'Kruyt', 'Adriani', 'Pamona', 'Sulawesi Tengah', 'PGI']
  },
  {
    id: 'gmist',
    name: 'GMIST (Gereja Masehi Injili di Sangihe Talaud)',
    shortName: 'GMIST Sangihe',
    fullName: 'Gereja Masehi Injili di Sangihe Talaud',
    originYear: 1857,
    synodYear: 1947,
    era: 'zending_19',
    eraLabel: 'Abad 19 & Kemandirian 1947',
    region: 'Sulawesi',
    subRegion: 'Tahuna, Kepulauan Sangihe, Siau, Tagulandang, Talaud, Sulawesi Utara',
    denomination: 'Protestan',
    tradition: 'Calvinis / Reformed Bahari',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Carl W. Groenhart, Ernst T. Steller (Misionaris Tukang Heldenbergen), Pdt. F. Kelling',
    missionAgency: 'Zendings-Werkman Heldenbergen Jerman & Komite Zending Sangihe-Talaud',
    currentHeadquarters: 'Kantor Sinode GMIST, Jl. Tatehe, Kel. Manganitu, Tahuna, Kepulauan Sangihe',
    summary: 'Sinode bahari kepulauan terluar di perbatasan utara Indonesia-Filipina yang dirintis misionaris-tukang E.T. Steller sejak 1857, membentengi kedaulatan rohani dan budaya masyarakat Nusa Utara.',
    fullStory: `
      Kepulauan Sangihe dan Talaud membentang di ujung utara nusantara hingga Pulau Miangas di perbatasan Filipina. Pada tahun 1857, datanglah empat orang "misionaris tukang" (zendingswerkman) yang diutus dari perkumpulan Heldenbergen Jerman, dipimpin oleh Ernst T. Steller dan Carl W. Groenhart.
      
      Mereka tidak hanya mengabarkan Injil, tetapi melatih warga kepulauan keahlian pertukangan kayu, pelayaran bahari, penanaman pohon kelapa/kopra, dan pendirian sekolah desa. Pdt. F. Kelling yang melayani di Pulau Tagulandang menerjemahkan Perjanjian Baru ke bahasa Sangir pada 1883.
      
      Pada 25 Mei 1947 di Manganitu (Tahuna), jemaat-jemaat kepulauan bersepakat memandirikan diri dari Indische Kerk dengan nama GMIST. GMIST mendidik generasi bahari yang tangguh, setia menjaga kedaulatan teritorial dan spiritual kepulauan terdepan Indonesia.
    `,
    milestones: [
      { year: '1857', title: 'Pendaratan 4 Misionaris Tukang', desc: 'E.T. Steller dan Groenhart mendarat di Kepulauan Sangihe memulai aksi peradaban.' },
      { year: '1883', title: 'Alkitab Bahasa Sangir', desc: 'Pdt. F. Kelling menerbitkan terjemahan Kitab Suci berbahasa Sangir.' },
      { year: '1947', title: 'Sinode Mandiri GMIST di Manganitu', desc: '25 Mei 1947: Diresmikan kemandirian sinode dengan kepemimpinan putra daerah.' }
    ],
    heritage: 'Pilar persatuan masyarakat Nusa Utara, Institut Agama Kristen Sangihe, dan jaringan asrama pelajar pulau terluar.',
    trivia: 'Paduan suara dan ansambel musik bambu tiup khas Sangihe yang dibina oleh GMIST diakui sebagai salah satu karya warisan budaya musik tradisional terindah di Indonesia.',
    icon: 'bi-compass',
    crestBg: 'from-sky-700 to-blue-950',
    tags: ['GMIST', 'Sangihe', 'Talaud', 'Tahuna', 'Steller', 'Manganitu', 'Nusa Utara', 'PGI', 'Sulawesi']
  },
  {
    id: 'gmih',
    name: 'GMIH (Gereja Masehi Injili di Halmahera)',
    shortName: 'GMIH Halmahera',
    fullName: 'Gereja Masehi Injili di Halmahera',
    originYear: 1866,
    synodYear: 1949,
    era: 'zending_19',
    eraLabel: 'Abad 19 & Kemandirian 1949',
    region: 'Maluku',
    subRegion: 'Tobelo, Galela, Kau, Morotai, Halmahera Utara, Maluku Utara',
    denomination: 'Protestan',
    tradition: 'Calvinis / Reformed',
    oikoumene: ['PGI', 'WCRC', 'WCC'],
    founder: 'Pdt. Hendrik van Dijken, Pdt. Anton Hueting (Rasul Tobelo)',
    missionAgency: 'Utrechtsche Zendingsvereeniging (UZV) Belanda',
    currentHeadquarters: 'Kantor Sinode GMIH, Jl. Kemakmuran No. 1, Tobelo, Halmahera Utara',
    summary: 'Sinode bersejarah di bumi Moloku Kie Raha yang dirintis di Galela dan Tobelo sejak 1866 oleh Hendrik van Dijken dan Anton Hueting, mengubah daerah konflik suku menjadi pusat pertanian dan pendidikan damai.',
    fullStory: `
      Pekabaran Injil modern di Pulau Halmahera dimulai ketika UZV mengutus Hendrik van Dijken pada tahun 1866. Beliau membuka ladang pertanian percontohan di Duma, Danau Galela. Namun gerakan penginjilan yang mengguncang tanah Halmahera dipelopori oleh Pdt. Anton Hueting yang tiba di Tobelo pada tahun 1898.
      
      Hueting hidup berbaur dengan masyarakat suku Tugutil dan Tobelo yang saat itu ditakuti karena tradisi perompakan laut. Melalui keteladanan kasih dan pengobatan, pada bulan April 1919 terjadi baptisan massal ribuan orang di pesisir Tobelo.
      
      Pada tanggal 19 April 1949, bertempat di Tobelo, dibentuklah Sinode Gereja Masehi Injili di Halmahera (GMIH) yang mandiri. GMIH mengayomi kerukunan suku dan menaungi universitas serta rumah sakit di Maluku Utara.
    `,
    milestones: [
      { year: '1866', title: 'Perintisan Hendrik van Dijken di Duma Galela', desc: 'Pembukaan pos zending pertanian di pedalaman Halmahera Utara.' },
      { year: '1898', title: 'Kiprah Pdt. Anton Hueting di Tobelo', desc: 'Memulai transformasi sosial dan pengobatan bagi suku pesisir dan pedalaman Halmahera.' },
      { year: '1949', title: 'Sinode Mandiri GMIH di Tobelo', desc: '19 April 1949: Diresmikan sebagai sinode mandiri di Halmahera Utara.' }
    ],
    heritage: 'Universitas Halmahera (UNIERA) di Tobelo, RS Bethesda Tobelo, dan monumen sejarah Duma Galela.',
    trivia: 'Anton Hueting juga dikenal sebagai seorang etnolog ulung yang mendokumentasikan tata bahasa dan kamus bahasa Tobelo pertama yang sangat rinci.',
    icon: 'bi-tree-fill',
    crestBg: 'from-emerald-700 to-teal-950',
    tags: ['GMIH', 'Halmahera', 'Tobelo', 'Galela', 'Anton Hueting', 'Duma', 'Maluku Utara', 'PGI']
  },
  {
    id: 'gkmi',
    name: 'GKMI (Gereja Kristen Muria Indonesia)',
    shortName: 'GKMI Muria',
    fullName: 'Sinode Gereja Kristen Muria Indonesia',
    originYear: 1920,
    originEvent: 'Tee Siem Tat Merintis Persekutuan Jemaat Anabaptis-Menonit di Kudus (1920)',
    synodYear: 1957,
    synodEvent: 'Kemandirian Sinode Gereja Kristen Muria Indonesia (1957)',
    era: 'kemandirian_early',
    eraLabel: '1900-1945 (Tradisi Anabaptis Muria)',
    region: 'Jawa & Seluruh Indonesia',
    subRegion: 'Kudus, Jepara, Pati, Semarang, Jawa Tengah',
    denomination: 'Protestan',
    tradition: 'Anabaptis / Mennonite (Ajaran Perdamaian & Hidup Sederhana)',
    oikoumene: ['PGI', 'Mennonite World Conference (MWC)'],
    founder: 'Pdt. Tee Siem Tat & Ny. Sie Djoen Nio',
    missionAgency: 'Gerakan Kebangunan Rohani Pribumi Tionghoa-Jawa & Misi Doopsgezinde (Mennonite Belanda)',
    currentHeadquarters: 'Kantor Sinode GKMI, Jl. Senopati No. 4, Semarang, Jawa Tengah',
    summary: 'Sinode berakar tradisi Anabaptis-Mennonite yang lahir di lereng Gunung Muria (Kudus) pada 1920 oleh Tee Siem Tat, menjunjung tinggi nilai-nilai perdamaian, kesederhanaan, dan baptisan selam atas pengakuan iman sadar.',
    fullStory: `
      GKMI lahir dari pengalaman kesembuhan ilahi yang dialami oleh Tee Siem Tat, seorang pedagang batik keturunan Tionghoa di Kudus pada tahun 1917. Setelah pulih secara ajaib, Tee Siem Tat dan istrinya, Sie Djoen Nio, mendedikasikan rumah mereka di Kudus sebagai pos doa dan penelaahan Alkitab.
      
      Gerakan ini berkembang pesat di kalangan masyarakat Tionghoa dan Jawa di sekitar lereng Gunung Muria (Kudus, Jepara, Welahan, Pati). Mereka berinteraksi dengan misionaris Mennonite Belanda (Doopsgezinde Zendingsvereeniging) yang mengajarkan prinsip-prinsip Anabaptis: cinta damai, anti-kekerasan, pemuridan radikal, dan penolakan baptisan bayi (menekankan baptisan orang percaya/dewasa).
      
      Pada tanggal 6 Desember 1920, kebaktian resmi pertama jemaat Kudus diadakan. Sinode GKMI mandiri resmi dibentuk pada 1957. Pada tahun 2022, Indonesia dipercaya menjadi tuan rumah Sidang Raya Sedunia Gereja-Gereja Mennonite (Mennonite World Conference) yang berpusat di Salatiga berkat warisan GKMI dan GITJ.
    `,
    milestones: [
      { year: '1920', title: 'Perintisan Tee Siem Tat di Kudus', desc: '6 Desember 1920: Persekutuan iman Kudus resmi menggelar kebaktian perdana.' },
      { year: '1957', title: 'Pembentukan Sinode Mandiri GKMI', desc: 'Konsolidasi jemaat-jemaat Muria menjadi satu tubuh sinode nasional.' },
      { year: '2022', title: 'Tuan Rumah Sidang Raya Mennonite Sedunia', desc: 'Mennonite World Conference ke-17 digelar di Jawa Tengah dihadiri delegasi 60 negara.' }
    ],
    heritage: 'Mennonite Diaconal Services (MDS), Sekolah Menengah Masehi Kudus & Semarang, serta yayasan pelayanan perdamaian lintas iman.',
    trivia: 'GKMI merupakan salah satu dari hanya sedikit gereja di Asia yang beraliran Anabaptis Mennonite dengan komitmen teologis yang sangat kuat terhadap perdamaian (peace theology).',
    icon: 'bi-peace',
    crestBg: 'from-amber-700 to-green-950',
    tags: ['GKMI', 'Muria', 'Kudus', 'Jepara', 'Tee Siem Tat', 'Mennonite', 'Anabaptis', 'Jawa Tengah', 'PGI']
  },
  {
    id: 'gkppd',
    name: 'GKPPD (Gereja Kristen Protestan Pakpak Dairi)',
    shortName: 'GKPPD Pakpak',
    fullName: 'Gereja Kristen Protestan Pakpak Dairi',
    originYear: 1966,
    synodYear: 1991,
    era: 'pasca_kemerdekaan',
    eraLabel: '1945-Sekarang (Suku Pakpak)',
    region: 'Sumatera',
    subRegion: 'Salak (Pakpak Bharat), Sidikalang (Dairi), Sumatera Utara & Singkil (Aceh)',
    denomination: 'Protestan',
    tradition: 'Lutheran / Kontekstual Adat Pakpak Silima Suak',
    oikoumene: ['PGI', 'LWF (Lutheran World Federation)'],
    founder: 'Tokoh-tokoh Rohaniwan Suku Pakpak, Pdt. G. Solin, Sintua Pakpak',
    missionAgency: 'Pemekaran Jemaat Etnis Pakpak dari HKBP',
    currentHeadquarters: 'Kantor Pusat Sinode GKPPD, Jl. Barisan Nauli No. 5, Salak, Pakpak Bharat, Sumatera Utara',
    summary: 'Sinode pengayom masyarakat suku Pakpak (Silima Suak) di dataran tinggi Dairi dan Pakpak Bharat, melestarikan liturgi dan kidung ibadah dalam bahasa daerah Pakpak Dairi.',
    fullStory: `
      Masyarakat etnis Pakpak yang mendiami wilayah Dairi, Pakpak Bharat, Humbang, dan perbatasan Aceh Singkil terbagi dalam lima suak budaya (Silima Suak: Suak Simsim, Keppas, Pegagan, Boang, dan Kelasen). Sejak awal abad ke-20 mereka menerima Injil melalui zending RMG dan terhimpun dalam jemaat HKBP.
      
      Namun kerinduan mendalam untuk menyembah Tuhan dalam bahasa ibu Pakpak dan mengembangkan teologi kontekstual yang berakar pada adat Pakpak mendorong para penatua dan pendeta suku Pakpak membentuk persekutuan mandiri. Pada 25 Agustus 1991, di Salak, sinode GKPPD diresmikan sebagai gereja mandiri terpisah dari HKBP.
      
      GKPPD secara gigih memperjuangkan pelestarian bahasa Pakpak melalui penerjemahan Alkitab (Bibel Bahasa Pakpak) dan buku nyanyian "Buku Ende Pakpak", serta merawat harmoni persaudaraan di wilayah perbatasan Sumatera Utara dan Aceh.
    `,
    milestones: [
      { year: '1966', title: 'Rintisan Jemaat Khusus Pakpak', desc: 'Membuka kebaktian pertama berbahasa daerah Pakpak di Salak dan Sidikalang.' },
      { year: '1991', title: 'Kemandirian Sinode GKPPD', desc: '25 Agustus 1991: Diresmikan sebagai sinode mandiri di Salak, Pakpak Bharat.' },
      { year: '2000-an', title: 'Penerbitan Alkitab Lengkap Bahasa Pakpak', desc: 'Peresmian Kitab Suci Alkitab lengkap terjemahan Lembaga Alkitab Indonesia (LAI) dalam Basa Pakpak.' }
    ],
    heritage: 'Pusat kebudayaan rohani suku Pakpak di Salak, asrama pembinaan pemuda desa, dan pelestarian seni vokal Odong-odong Pakpak bernuansa rohani.',
    trivia: 'GKPPD menggunakan alat musik tradisional genderang sisibah Pakpak dalam prosesi ibadah-ibadah perayaan gerejawi agung.',
    icon: 'bi-gem',
    crestBg: 'from-emerald-800 to-amber-950',
    tags: ['GKPPD', 'Pakpak', 'Dairi', 'Salak', 'Sidikalang', 'Singkil', 'Silima Suak', 'PGI', 'LWF', 'Sumatera']
  }
])

// --- Data 10 Koridor & Jalur Misi Bersejarah Nusantara (Historiografi Komprehensif) ---
const missionCorridors = [
  {
    id: 'barus-kuno',
    category: 'kuno_voc',
    categoryLabel: 'Era Kuno & Bahari',
    corridor: '1. Jalur Bahari Kuno Barus & Sriwijaya',
    period: 'Abad VII - XIV Masehi',
    badge: 'Misi Timur Purba',
    geography: 'Pelabuhan Fansur (Barus), Pantai Barat Sumatera Utara, Selat Malaka',
    routeStations: ['Teluk Persia & Siria', 'Pelabuhan Fansur (Barus)', 'Selat Malaka & Sriwijaya'],
    missionAgencies: 'Gereja Asiria dari Timur (Gereja Nestorian / Tradisi Siria Purba)',
    pioneers: 'Saudagar Kristen Siria-Persia; dicatat musafir Abu Salih al-Armani (abad ke-12) & Chronicle of Seert',
    description: 'Jauh sebelum tibanya bangsa-bangsa Barat, saudagar Kristen Nestorian dari Timur Tengah telah singgah dan bermukim di pelabuhan kapur barus Fansur (Barus) di pesisir barat Sumatera. Catatan naskah kuno Timur Tengah membuktikan keberadaan gereja dan komunitas umat beriman yang dilayani seorang presbiter di Sumatera Utara.',
    keyImpact: 'Bukti tertua kehadiran monoteisme Kristiani di kepulauan Nusantara berabad-abad sebelum era kolonialisme Eropa.',
    resultingChurches: ['Ortodoks', 'Kekristenan Purba Barus'],
    accentBg: 'from-amber-700/20 to-yellow-900/30',
    icon: 'bi-compass',
    stationsDetail: [
      { name: 'Jalur Sutra Maritim', note: 'Pelayaran pedagang rempah dan kapur barus dari Teluk Persia ke Samudra Hindia.' },
      { name: 'Pelabuhan Fansur / Barus', note: 'Pendirian koloni niaga dan jemaat gereja dengan liturgi bahasa Siria.' },
      { name: 'Pesisir Selat Malaka', note: 'Jejak kontak pertukaran budaya dan komoditas dengan kerajaan-kerajaan maritim kuno.' }
    ]
  },
  {
    id: 'rempah-yesuit',
    category: 'kuno_voc',
    categoryLabel: 'Era Portugis',
    corridor: '2. Koridor Kepulauan Rempah & Misi Yesuit Portugis',
    period: '1534 - 1605 Masehi',
    badge: 'Padroado Portugis',
    geography: 'Malaka ➔ Ternate ➔ Tidore ➔ Moro (Halmahera) ➔ Ambon ➔ Solor & Larantuka (Flores)',
    routeStations: ['Malaka Portugis (1511)', 'Benteng Ternate & Tidore (1522)', 'Moro / Morotai (1534)', 'Pulau Ambon (1546)', 'Kepulauan Solor & Larantuka (1556)'],
    missionAgencies: 'Padroado Portugis, Serikat Yesus (SJ / Yesuit) & Ordo Dominikan (OP)',
    pioneers: 'Santo Fransiskus Xaverius (1546-1547), Pastor Simon Vaz (martir perdana 1535), Pastor Antonio Taveira',
    description: 'Menyusuri rute armada niaga cengkih Portugis, Santo Fransiskus Xaverius tiba di Ambon dan Halmahera pada 1546. Beliau menerjemahkan katekismus sederhana, melayani orang kusta, dan membaptis ribuan warga. Di Nusa Tenggara Timur, ordo Dominikan meletakkan dasar tradisi iman Katolik yang bertahan turun-temurun di Flores Timur.',
    keyImpact: 'Peletakan tonggak iman Katolik perdana di Indonesia Timur, melahirkan tradisi keagamaan Flores (Larantuka) dan pemulihan hierarki nasional.',
    resultingChurches: ['Gereja Katolik', 'Keuskupan Amboina', 'Keuskupan Larantuka'],
    accentBg: 'from-rose-700/20 to-red-900/30',
    icon: 'bi-shield-shaded',
    stationsDetail: [
      { name: 'Ternate & Halmahera Utara', note: 'Simon Vaz memulai pembaptisan di Moro; disusul misi Xaverius 1546.' },
      { name: 'Jazirah Leitimor Ambon', note: 'Pendirian stasi pelayanan Katolik pertama di kawasan Teluk Ambon.' },
      { name: 'Solor & Flores Timur', note: 'Pembangunan benteng misi Dominikan dan komunitas Semana Santa Larantuka.' }
    ]
  },
  {
    id: 'voc-indische',
    category: 'kuno_voc',
    categoryLabel: 'Era VOC & Indische Kerk',
    corridor: '3. Koridor Benteng Kompeni & De Protestantse Kerk',
    period: '1605 - 1815 Masehi',
    badge: 'VOC & Indische Kerk',
    geography: 'Benteng Victoria (Ambon), Banda Neira, Batavia (Jakarta), Semarang, Surabaya, Makassar',
    routeStations: ['Benteng Victoria Ambon (1605)', 'Kota Batavia & Portugeesche Kerk (1619)', 'Kepulauan Banda', 'Semarang & Surabaya'],
    missionAgencies: 'Vereenigde Oostindische Compagnie (VOC) & De Protestantse Kerk in Nederlandsch-Indië (Indische Kerk 1815)',
    pioneers: 'Sieckentrooster VOC (1605), Ds. Casparus Wiltens (1615), Sebastianus Danckaerts, Dr. Melchior Leijdecker (1733), Joseph Kam ("Rasul Maluku" 1815)',
    description: 'Setelah merebut benteng Ambon pada Februari 1605, ibadah Protestan pertama dipimpin sieckentrooster armada VOC. Ds. Casparus Wiltens tiba 1614-1615 merintis kamus Melayu-Belanda pertama (1623). Pada 1815, Raja Willem I menyatukan seluruh jemaat menjadi Indische Kerk. Joseph Kam berlayar menembus badai Laut Banda dengan kora-kora untuk menghidupkan jemaat kepulauan.',
    keyImpact: 'Ibu asali yang melahirkan 12 Gereja Bagian Mandiri (GBM) di seluruh pelosok Indonesia dan Alkitab terjemahan Leijdecker 1733.',
    resultingChurches: ['GPI (Indische Kerk)', 'GPM', 'GMIM', 'GMIT', 'GPIB'],
    accentBg: 'from-blue-700/20 to-indigo-950/30',
    icon: 'bi-bank',
    stationsDetail: [
      { name: 'Benteng Victoria Ambon (1605)', note: 'Ibadah Protestan perdana VOC; disusul kedatangan Ds. Casparus Wiltens 1615.' },
      { name: 'Batavia (1619-1695)', note: 'Pendirian Gereja Sion (Portugeesche Buitenkerk) dan penerjemahan Alkitab Leijdecker.' },
      { name: 'Kepulauan Maluku (1815)', note: 'Pelayaran epik Joseph Kam membangkitkan kembali gereja-gereja kepulauan.' }
    ]
  },
  {
    id: 'timor-rote',
    category: 'kuno_voc',
    categoryLabel: 'Era VOC & Sunda Kecil',
    corridor: '4. Koridor Sunda Kecil & Tradisi Literasi Melayu NTT',
    period: '1614 - 1947 Masehi',
    badge: 'Misi Bahari NTT',
    geography: 'Pulau Rote (Thie, Baa, Bilba) ➔ Kupang (Timor Barat) ➔ Sabu ➔ Alor ➔ Pedalaman Soe',
    routeStations: ['Teluk Kupang (1614)', 'Pulau Rote (Sekolah Melayu 1729)', 'Pulau Sabu & Alor', 'Dataran Tinggi Soe Timor'],
    missionAgencies: 'VOC, Lembaga Zending Batavia & Indische Kerk Hindia Belanda',
    pioneers: 'Ds. Mattheus van den Broeck (1614), Para Raja Rote (Manek), Guru-Guru Melayu Rote, Ds. Ernst Durkstra (1947)',
    description: 'Kunjungan rohaniwan VOC Ds. Mattheus van den Broeck pada 1614 mengawali hubungan mendalam suku kepulauan NTT dengan Injil. Pulau Rote menjadi pelopor pendidikan dengan didirikannya sekolah desa Melayu sejak 1729. Para raja Rote mengirim anak-anak mereka belajar Alkitab ke Batavia, mencetak angkatan guru pribumi yang mengajar hingga pelosok Nusantara.',
    keyImpact: 'Pemberantasan buta huruf kepulauan karang NTT, melahirkan Sinode GMIT mandiri pada 31 Oktober 1947 dan UKAW Kupang.',
    resultingChurches: ['GMIT', 'Gereja Timor'],
    accentBg: 'from-yellow-700/20 to-amber-900/30',
    icon: 'bi-brightness-high',
    stationsDetail: [
      { name: 'Kupang & Rote (1614)', note: 'Kunjungan pelayanan VOC Mattheus van den Broeck di pos bandar Kupang.' },
      { name: 'Sekolah Desa Rote (1729)', note: 'Sekolah aksara Melayu tertua yang mencetak ratusan guru penginjil perintis.' },
      { name: 'Sinode Mandiri Kupang (1947)', note: '31 Oktober 1947: Kemandirian penuh GMIT melayani seluruh kepulauan NTT.' }
    ]
  },
  {
    id: 'papua-mansinam',
    category: 'zending_19',
    categoryLabel: 'Era Zending Abad 19',
    corridor: '5. Koridor Lembah Mansinam & Fajar Peradaban Papua',
    period: '1855 - 1956 Masehi',
    badge: 'Gerbang Peradaban Papua',
    geography: 'Pulau Mansinam (Teluk Doreri) ➔ Pulau Roon ➔ Miei (Teluk Wondama) ➔ Serui (Yapen) ➔ Biak ➔ Jayapura',
    routeStations: ['Pantai Pasir Putih Mansinam (5 Feb 1855)', 'Pulau Roon & Teluk Wondama', 'Sekolah Guru Miei (1925)', 'Sinode Mandiri Serui (1956)'],
    missionAgencies: 'Zendings-Werkman Heldenbergen (Jerman) & Utrechtsche Zendingsvereeniging (UZV Belanda)',
    pioneers: 'Carl Wilhelm Ottow & Johann Gottlob Geissler, F.J.F. van Hasselt, Izaak Samuel Kijne ("Bapak Peradaban Papua")',
    description: 'Dimulai dari pendaratan sekunar Ternate di pantai pasir putih Mansinam pada 5 Februari 1855 oleh Ottow dan Geissler dengan doa sulung: "Dengan nama Tuhan kami menginjakkan kaki di tanah ini". Misi mentransformasi Papua lewat sekolah tukang, pemberantasan malaria, penerjemahan Alkitab bahasa Numfor, hingga berdirinya Sekolah Guru Miei oleh I.S. Kijne.',
    keyImpact: 'Fondasi peradaban modern Tanah Papua, penetapan hari libur resmi 5 Februari se-Papua, dan kemandirian Sinode GKI di Serui 1956.',
    resultingChurches: ['GKI di Tanah Papua'],
    accentBg: 'from-amber-600/20 to-orange-900/30',
    icon: 'bi-sun',
    stationsDetail: [
      { name: 'Pulau Mansinam (1855)', note: 'Doa sulung Ottow & Geissler menandai fajar terang kabar baik di Tanah Papua.' },
      { name: 'Miei Wondama (1925)', note: 'I.S. Kijne membangun pusat pendidikan guru dan menggubah lagu rohani peradaban.' },
      { name: 'Serui Yapen (1956)', note: 'Peresmian Sinode Mandiri GKI di Tanah Papua menyatukan ratusan suku bangsa.' }
    ]
  },
  {
    id: 'silindung-nias',
    category: 'zending_19',
    categoryLabel: 'Era Zending Abad 19',
    corridor: '6. Koridor Silindung, Pegunungan Toba & Pulau Nias',
    period: '1861 - 1941 Masehi',
    badge: 'Misi RMG Barmen',
    geography: 'Barus ➔ Lembah Silindung (Tarutung) ➔ Toba Samosir ➔ Gunungsitoli (Nias) ➔ Raya (Simalungun) ➔ Sipirok (Angkola)',
    routeStations: ['Pelabuhan Barus (1861)', 'Lembah Silindung Tarutung (1864)', 'Gunungsitoli Pulau Nias (1865)', 'Pematang Raya Simalungun (1903)', 'Parausorat Sipirok (1861)'],
    missionAgencies: 'Rheinische Missionsgesellschaft (RMG) Barmen Jerman',
    pioneers: 'Dr. I.L. Nommensen ("Apostel Batak"), Ludwig Ernst Denninger (Nias), August Theis (Simalungun), Gerrit van Asselt (Angkola)',
    description: 'Menerobos pedalaman dataran tinggi Sumatera Utara dan pulau terluar Nias. Nommensen mendirikan Huta Dame (Kampung Damai) di Silindung, menerjemahkan Alkitab Perjanjian Baru Batak (1878), dan menyelaraskan hukum adat Batak dalam terang kasih Kristus. Di Nias, Denninger memulai misi yang meledak menjadi kebangunan rohani akbar Fangesa Dödö (1916).',
    keyImpact: 'Melahirkan rumpun gereja Protestan terbesar di Asia Tenggara: HKBP (1861/1930), BNKP Nias (1865/1936), GKPS (1903/1963), GKPA (1861/1975).',
    resultingChurches: ['HKBP', 'BNKP', 'GKPS Simalungun', 'GKPA Angkola'],
    accentBg: 'from-amber-700/20 to-stone-900/30',
    icon: 'bi-cross',
    stationsDetail: [
      { name: 'Huta Dame Silindung (1864)', note: 'Nommensen mendirikan perkampungan suaka damai pertama di Tanah Batak.' },
      { name: 'Gunungsitoli Nias (1865)', note: 'Denninger mendarat dan memicu kebangunan rohani pertobatan Fangesa Dodo 1916.' },
      { name: 'Pematang Raya (1903)', note: 'August Theis menembus pedalaman Simalungun dan membaptis warga lokal perdana.' }
    ]
  },
  {
    id: 'dayak-borneo',
    category: 'zending_19',
    categoryLabel: 'Era Zending Abad 19',
    corridor: '7. Koridor Riam Sungai & Hutan Belantara Dayak Borneo',
    period: '1836 - 1935 Masehi',
    badge: 'Misi Rimba Kalimantan',
    geography: 'Banjarmasin ➔ Kuala Kapuas (Betlehem) ➔ Aliran Sungai Kahayan, Barito, Kapuas & Katingan',
    routeStations: ['Muara Banjarmasin (1836)', 'Kuala Kapuas / Betlehem (1839)', 'Hulu Sungai Kahayan & Barito', 'Palangka Raya & Kalsel'],
    missionAgencies: 'RMG Barmen Jerman (1836) dilanjutkan Basler Missionsgesellschaft / Misi Basel Swiss (1920-an)',
    pioneers: 'Misionaris Barnstein, August Hardeland (penerjemah Alkitab Dayak Ngaju 1858), Pdt. H. Dingang Patianom',
    description: 'Menyusuri riam dan jeram sungai raksasa Kalimantan dengan perahu dayung untuk menjangkau masyarakat suku Dayak Ngaju, Ot Danum, dan Maanyan di Rumah Betang. Hardeland berhasil menyusun tata bahasa, kamus, dan Alkitab bahasa Dayak Ngaju pertama. Misi Basel mendirikan pusat kerajinan rotan, pertukangan kayu, dan perkebunan karet rakyat.',
    keyImpact: 'Literasi cetak aksara Dayak perdana di dunia dan kemandirian Gereja Dayak Evangelis (GDE/GKE) pada 4 April 1935.',
    resultingChurches: ['GKE', 'Gereja Dayak Kalimantan'],
    accentBg: 'from-emerald-700/20 to-green-950/30',
    icon: 'bi-tree',
    stationsDetail: [
      { name: 'Banjarmasin & Kapuas (1836)', note: 'Pendaratan Barnstein dan pembaptisan perdana orang Dayak pada 1839.' },
      { name: 'Kamus & Alkitab Ngaju (1858)', note: 'August Hardeland mengkodifikasikan bahasa Dayak ke dalam literatur cetak Alkitab.' },
      { name: 'Sinode Mandiri GDE (1935)', note: '4 April 1935: Sinode mandiri gereja Dayak resmi dipimpin pimpinan lokal.' }
    ]
  },
  {
    id: 'pasundan-jawa',
    category: 'zending_19',
    categoryLabel: 'Misi Pribumi & Jawa',
    corridor: '8. Koridor Penginjil Pribumi & Kontekstualisasi Sunda-Jawa',
    period: '1860 - 1934 Masehi',
    badge: 'Inisiatif Tokoh Pribumi',
    geography: 'Karangjoso (Purworejo), Lereng Muria (Kudus/Pati), Salatiga, Cianjur (Palalangon), Meester Cornelis, Bandung',
    routeStations: ['Gunung Muria (1855)', 'Padepokan Karangjoso (1870)', 'Desa Kristen Palalangon Cianjur (1902)', 'Kebumen & Bandung (1931-1934)'],
    missionAgencies: 'Inisiatif Penginjil Pribumi Mandiri, NZV (Nederlandsche Zendingsvereeniging) & Zending GKN',
    pioneers: 'Kiai Ibrahim Tunggul Wulung, Radin Abas Kyai Sadrach Surapranata, Mr. Frederik Lodewijk Anthing (1863), Tee Siem Tat (1920)',
    description: 'Gerakan pekabaran Injil unik yang digerakkan oleh kearifan tokoh-tokoh pribumi. Kyai Sadrach mendirikan padepokan Kristen Jawa Karangjoso dan memimpin ribuan pengikut dengan melestarikan surjan, blangkon, dan gamelan. Di tanah Pasundan, Mr. F.L. Anthing mendidik pemuda lokal mendirikan desa mandiri Palalangon berarsitektur Sunda Julang Ngapak.',
    keyImpact: 'Pelopor inkulturasi tembang Macapat & gamelan dalam liturgi gereja, melahirkan Sinode GKJ (1931), GKP Pasundan (1934), dan GKMI Muria (1957).',
    resultingChurches: ['GKJ', 'GKP', 'GKMI Muria'],
    accentBg: 'from-emerald-800/20 to-teal-950/30',
    icon: 'bi-flower2',
    stationsDetail: [
      { name: 'Padepokan Karangjoso (1870)', note: 'Kyai Sadrach memimpin ribuan jemaat Kristen Jawa dengan kemandirian pribumi penuh.' },
      { name: 'Palalangon Cianjur (1902)', note: 'Pemukiman tani Kristen Pasundan mandiri dengan perpaduan budaya Basa Sunda halus.' },
      { name: 'Sinode Kebumen & Bandung (1931/1934)', note: 'Pengesahan sinode mandiri GKJ Jawa Tengah dan GKP Jawa Barat.' }
    ]
  },
  {
    id: 'utara-toraja',
    category: 'sulawesi_pedalaman',
    categoryLabel: 'Sulawesi & Kepulauan Utara',
    corridor: '9. Koridor Minahasa, Sangihe-Halmahera & Lembah Toraja-Poso',
    period: '1831 - 1947 Masehi',
    badge: 'Sulawesi & Kepulauan Rempah Utara',
    geography: 'Tondano & Langowan (Minahasa) ➔ Manganitu (Sangihe) ➔ Galela & Tobelo (Halmahera) ➔ Tentena (Poso) ➔ Rantepao (Tana Toraja)',
    routeStations: ['Danau Tondano & Langowan (1831)', 'Manganitu Sangihe (1857)', 'Duma Galela Halmahera (1866)', 'Danau Poso & Tentena (1892)', 'Lembah Tongkonan Rantepao (1913)'],
    missionAgencies: 'NZG Rotterdam, Zendeling-Tukang Heldenbergen, UZV Halmahera & GZB Belanda',
    pioneers: 'J.F. Riedel & J.G. Schwarz, E.T. Steller (Sangihe), Hendrik van Dijken (Halmahera), Dr. A.C. Kruyt & N. Adriani (Poso), A.A. van de Loosdrecht (martir Toraja 1913/1917)',
    description: 'Membentang dari jazirah Minahasa hingga lembah Tongkonan Toraja. Riedel dan Schwarz mengubah Minahasa menjadi lumbung guru penginjil Nusantara. Dr. A.C. Kruyt memelopori pendekatan etnografi kultural di Danau Poso. Di Tana Toraja, darah martir Loosdrecht melahirkan gereja berakar kuat yang menaungi masyarakat Toraja di bawah salib Kristus.',
    keyImpact: 'Melahirkan pilar-pilar sinode terkuat di Indonesia Timur: GMIM (1934), GMIST (1947), GMIH (1949), GKST Tentena (1947), dan Gereja Toraja (1947).',
    resultingChurches: ['GMIM', 'Gereja Toraja', 'GKST', 'GMIST', 'GMIH'],
    accentBg: 'from-sky-700/20 to-blue-950/30',
    icon: 'bi-water',
    stationsDetail: [
      { name: 'Minahasa (1831)', note: 'Riedel & Schwarz memulai kebangunan rohani pendidikan dan gereja rakyat.' },
      { name: 'Tentena Poso (1892)', note: 'Dr. Kruyt dan Nicolaus Adriani merintis pekabaran Injil berbasis budaya Pamona.' },
      { name: 'Rantepao Toraja (1913/1947)', note: 'Misi GZB Loosdrecht melahirkan Sinode Gereja Toraja berarsitektur Tongkonan.' }
    ]
  },
  {
    id: 'pentakosta-cma',
    category: 'gerakan_modern',
    categoryLabel: 'Kegerakan Abad 20 & Modern',
    corridor: '10. Koridor Api Roh Kudus, Misi Pedalaman CMA & Diaspora',
    period: '1905 - 1970 Masehi',
    badge: 'Gerakan Abad 20 & Global',
    geography: 'Cepu (Blora) ➔ Surabaya ➔ Makassar ➔ Medan & Riau ➔ Pedalaman Mahakam & Papua ➔ Sukabumi & Jakarta',
    routeStations: ['Medan & Palembang (Methodist 1905)', 'Kota Minyak Cepu (Pentakosta 1921)', 'Makassar & STT Jaffray (CMA 1928)', 'Sukabumi & Nasional (GBI 1970)', 'Fusi Sinode Am Cipanas (GKI 1988)'],
    missionAgencies: 'Bethel Temple Seattle (Pentakosta), The Christian and Missionary Alliance / CMA (Injili), Methodist Episcopal Church, Perhimpunan THKTKH',
    pioneers: 'C.E. Groesbeek & Richard van Klaveren (Cepu 1921), Dr. Robert Alexander Jaffray (Makassar 1928), Bishop W.F. Oldham (Medan 1905), Pdt. Dr. H.L. Senduk (GBI 1970)',
    description: 'Gerakan abad ke-20 yang memadukan kuasa Roh Kudus, penerobosan rimba terisolasi, dan penginjilan perkotaan. Pendaratan Groesbeek di Cepu (1921) menyulut api Pentakosta. Dr. Jaffray di Makassar memelopori penerbangan misi MAF dan penerbitan Kalam Hidup menerobos pedalaman Dayak Mahakam dan Papua. Di perkotaan, misi Methodist dan jemaat THKTKH melahirkan sekolah unggulan dan berfusi menjadi Sinode Am GKI.',
    keyImpact: 'Melahirkan sinode-sinode pentakosta dan injili terbesar di tanah air: GPdI (1921/1923), GBI (1970), GKII (1928/1983), GMI Methodist (1905/1964), dan GKI (1920/1988).',
    resultingChurches: ['GPdI', 'GBI', 'GKII', 'GMI Methodist', 'GKI'],
    accentBg: 'from-amber-500/20 to-red-950/30',
    icon: 'bi-fire',
    stationsDetail: [
      { name: 'Cepu & Surabaya (1921)', note: 'Pencurahan Roh Kudus perdana di Cepu Jawa Tengah melahirkan pergerakan GPdI.' },
      { name: 'Makassar & Kalam Hidup (1928)', note: 'Dr. Robert Jaffray mendirikan STT Jaffray dan menerobos rimba Kalimantan-Papua.' },
      { name: 'Sukabumi & Cipanas (1970/1988)', note: 'Deklarasi Sinode Mandiri GBI (1970) dan Fusi Penyatuan Sinode Am GKI (1988).' }
    ]
  }
]

const filteredMissionCorridors = computed(() => {
  if (selectedCorridorCategory.value === 'all') return missionCorridors
  return missionCorridors.filter(c => c.category === selectedCorridorCategory.value)
})

// --- Filtered and Sorted Church List ---
const filteredChurches = computed(() => {
  let result = churchData.value

  // Search Query filter
  const query = searchQuery.value.trim().toLowerCase()
  if (query) {
    result = result.filter(church => {
      const matchName = church.name.toLowerCase().includes(query)
      const matchFull = church.fullName.toLowerCase().includes(query)
      const matchFounder = church.founder.toLowerCase().includes(query)
      const matchRegion = church.region.toLowerCase().includes(query) || church.subRegion.toLowerCase().includes(query)
      const matchDenom = church.denomination.toLowerCase().includes(query)
      const matchTradition = church.tradition.toLowerCase().includes(query)
      const matchSummary = church.summary.toLowerCase().includes(query)
      const matchYear = church.originYear.toString().includes(query) || (church.synodYear && church.synodYear.toString().includes(query))
      const matchEvents = (church.originEvent || '').toLowerCase().includes(query) || (church.synodEvent || '').toLowerCase().includes(query)
      const matchTags = church.tags.some(t => t.toLowerCase().includes(query))
      return matchName || matchFull || matchFounder || matchRegion || matchDenom || matchTradition || matchSummary || matchYear || matchEvents || matchTags
    })
  }

  // Denomination Filter
  if (selectedDenomination.value !== 'all') {
    result = result.filter(c => c.denomination.toLowerCase().includes(selectedDenomination.value.toLowerCase()))
  }

  // Region Filter
  if (selectedRegion.value !== 'all') {
    const sel = selectedRegion.value.toLowerCase()
    result = result.filter(c => {
      const reg = (c.region || '').toLowerCase()
      const subReg = (c.subRegion || '').toLowerCase()
      const tags = (c.tags || []).map(t => t.toLowerCase())
      return reg.includes(sel) || subReg.includes(sel) || tags.some(t => t.includes(sel))
    })
  }

  // Era Filter
  if (selectedEra.value !== 'all') {
    result = result.filter(c => c.era === selectedEra.value)
  }

  // Only Bookmarks Filter
  if (onlyBookmarks.value) {
    result = result.filter(c => bookmarkedIds.value.includes(c.id))
  }

  // Sorting (Misi Awal vs Sinode Mandiri vs Nama)
  const sorted = [...result]
  if (sortBy.value === 'origin-asc' || sortBy.value === 'year-asc') {
    sorted.sort((a, b) => a.originYear - b.originYear)
  } else if (sortBy.value === 'origin-desc' || sortBy.value === 'year-desc') {
    sorted.sort((a, b) => b.originYear - a.originYear)
  } else if (sortBy.value === 'synod-asc') {
    sorted.sort((a, b) => (a.synodYear || a.originYear) - (b.synodYear || b.originYear))
  } else if (sortBy.value === 'synod-desc') {
    sorted.sort((a, b) => (b.synodYear || b.originYear) - (a.synodYear || a.originYear))
  } else if (sortBy.value === 'name-asc') {
    sorted.sort((a, b) => a.shortName.localeCompare(b.shortName))
  } else if (sortBy.value === 'name-desc') {
    sorted.sort((a, b) => b.shortName.localeCompare(a.shortName))
  }

  return sorted
})

// Timeline View Sorted Chronologically
const timelineChurches = computed(() => {
  return [...filteredChurches.value].sort((a, b) => a.originYear - b.originYear)
})

// Counts
const totalCount = computed(() => churchData.value.length)
const filteredCount = computed(() => filteredChurches.value.length)

// Modal Handlers
const openChurchDetail = (church) => {
  selectedChurch.value = church
  isDetailModalOpen.value = true
}

const closeChurchDetail = () => {
  isDetailModalOpen.value = false
  selectedChurch.value = null
}

const openCorridorDetail = (corridor) => {
  selectedCorridor.value = corridor
  isCorridorModalOpen.value = true
}

const closeCorridorDetail = () => {
  isCorridorModalOpen.value = false
  selectedCorridor.value = null
}

const filterByCorridorChurch = (churchKeyword) => {
  searchQuery.value = churchKeyword
  viewMode.value = 'grid'
  showToast(`Menampilkan arsip gereja terkait: ${churchKeyword}`)
  nextTick(() => {
    const el = document.getElementById('search-engine')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
}

// Copy Summary Citation to Clipboard
const copyCitation = (church) => {
  const text = `[Arsip Historiografi Gereja Indonesia: ${church.fullName}]\n- Tahun Misi / Cikal Bakal: ${church.originYear} (${church.originEvent || 'Awal Pekabaran Injil'})\n- Tahun Sinode Mandiri: ${church.synodYear} (${church.synodEvent || 'Kemandirian Penuh Sinode'})\n- Lokasi Asal: ${church.subRegion}\n- Tokoh Kunci / Misionaris: ${church.founder}\n- Badan Misi / Induk: ${church.missionAgency}\n- Ringkasan Sejarah: ${church.summary}\n\nSumber: GracePoint Historia Search Engine (https://gracepoint.id/sejarah-gereja)`
  
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast('Kutipan sejarah berhasil disalin ke clipboard!')
    }).catch(() => {
      showToast('Gagal menyalin otomatis, silakan pilih manual.')
    })
  } else {
    showToast('Teks kutipan siap disalin.')
  }
}

// Keyboard shortcuts (e.g. '/' for search, 'Esc' for modal)
const handleKeydown = (e) => {
  if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
    e.preventDefault()
    focusSearch()
  }
  if (e.key === 'Escape') {
    if (isDetailModalOpen.value) {
      closeChurchDetail()
    }
  }
}

onMounted(() => {
  loadBookmarks()
  window.addEventListener('keydown', handleKeydown)
  nextTick(() => {
    try {
      AOS.init({
        duration: 700,
        easing: 'ease-out-cubic',
        once: true,
        offset: 40
      })
      AOS.refresh()
    } catch (e) {}
  })
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <ChurchHistoryLayout 
    :bookmark-count="bookmarkedIds.length"
    :current-view="viewMode"
    @focus-search="focusSearch"
    @toggle-timeline="(mode) => viewMode = mode"
    @toggle-bookmarks="onlyBookmarks = !onlyBookmarks"
  >
    <!-- Notification Toast -->
    <Transition name="fade-slide">
      <div 
        v-if="isToastVisible" 
        class="fixed bottom-6 right-6 z-50 bg-slate-950/95 border border-amber-500/50 text-amber-300 px-4 py-3 rounded-xl shadow-2xl backdrop-blur-md flex items-center gap-3 text-xs font-semibold max-w-sm"
      >
        <i class="bi bi-info-circle-fill text-amber-400 text-base"></i>
        <span>{{ toastMessage }}</span>
      </div>
    </Transition>

    <!-- HERO SECTION & SEARCH ENGINE INTERFACE -->
    <section class="history-hero relative bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 pt-10 sm:pt-16 pb-14 px-4 sm:px-6 lg:px-8 border-b border-amber-500/20 overflow-hidden">
      <!-- Background Ambient Glows -->
      <div class="absolute -top-24 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute top-1/2 left-10 w-[300px] h-[300px] bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 right-10 w-[300px] h-[300px] bg-amber-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="max-w-5xl mx-auto text-center relative z-10">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-semibold mb-5 shadow-sm">
          <i class="bi bi-compass text-amber-400"></i>
          <span>Mesin Pencari &amp; Arsip Cikal Bakal Gereja Indonesia</span>
        </div>

        <!-- Headline -->
        <h1 class="text-3xl sm:text-5xl lg:text-6xl font-serif font-black text-white tracking-tight leading-tight mb-4">
          Kenal Lebih Dekat <span class="bg-gradient-to-r from-amber-300 via-amber-400 to-amber-500 bg-clip-text text-transparent">Cikal Bakal Gereja</span> di Indonesia
        </h1>

        <!-- Subheading -->
        <p class="text-slate-300 text-sm sm:text-base max-w-3xl mx-auto leading-relaxed mb-8 font-sans">
          Jelajahi garis waktu sejarah, kisah tokoh misionaris &amp; penginjil pribumi, serta akar perintisan sinode-sinode Kristen dan Katolik dari Sabang sampai Merauke sejak abad ke-16.
        </p>

        <!-- MAIN SEARCH BAR (Search Engine Input) -->
        <div class="max-w-3xl mx-auto mb-6">
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-4 sm:pl-5 flex items-center pointer-events-none text-amber-400">
              <i class="bi bi-search text-lg sm:text-xl"></i>
            </div>
            <input 
              ref="searchInputRef"
              v-model="searchQuery"
              type="text" 
              placeholder="Cari sinode (HKBP, Indische Kerk, GMIM), tokoh (Nommensen, Sadrach, Jaffray), kota (Cepu, Mansinam)..." 
              class="w-full pl-12 sm:pl-14 pr-24 sm:pr-28 py-4 sm:py-5 rounded-2xl bg-slate-950/80 hover:bg-slate-950 border-2 border-amber-500/40 focus:border-amber-400 text-white placeholder-slate-400 text-sm sm:text-base shadow-2xl focus:outline-none focus:ring-4 focus:ring-amber-500/20 backdrop-blur-xl transition-all"
            />
            <div class="absolute inset-y-0 right-0 pr-3 sm:pr-4 flex items-center gap-1.5">
              <button 
                v-if="searchQuery" 
                type="button" 
                @click="clearSearch"
                class="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
                title="Hapus Pencarian"
              >
                <i class="bi bi-x-circle-fill text-base sm:text-lg"></i>
              </button>
              <kbd class="hidden sm:inline-block px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-[11px] font-mono text-amber-300/80">
                /
              </kbd>
            </div>
          </div>

          <!-- Quick Query Suggestions Bar -->
          <div class="mt-3.5 flex items-center justify-center flex-wrap gap-1.5 text-xs text-slate-400">
            <span class="text-slate-400 text-[11px] flex items-center gap-1">
              <i class="bi bi-lightbulb text-amber-400"></i> Rekomendasi Pencarian:
            </span>
            <button 
              v-for="chip in quickQueries" 
              :key="chip.query"
              type="button"
              @click="setQuickQuery(chip.query)"
              class="px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-amber-500/20 text-slate-300 hover:text-amber-300 border border-slate-700 hover:border-amber-500/40 text-[11px] transition-all cursor-pointer"
            >
              {{ chip.label }}
            </button>
          </div>
        </div>

        <!-- STATS COUNTERS -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto pt-6 border-t border-slate-800/80 text-left">
          <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div class="font-serif font-black text-xl sm:text-2xl text-amber-400">{{ totalCount }}</div>
            <div class="text-[11px] text-slate-400 font-medium">Sinode &amp; Gerakan Terindeks</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div class="font-serif font-black text-xl sm:text-2xl text-amber-400">5 Abad</div>
            <div class="text-[11px] text-slate-400 font-medium">Rentang Garis Waktu (1546-2026)</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div class="font-serif font-black text-xl sm:text-2xl text-amber-400">8 Kepulauan</div>
            <div class="text-[11px] text-slate-400 font-medium">Sumatera hingga Papua</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div class="font-serif font-black text-xl sm:text-2xl text-emerald-400">100%</div>
            <div class="text-[11px] text-slate-400 font-medium">Arsip Dokumen Terverifikasi</div>
          </div>
        </div>

      </div>
    </section>

    <!-- MAIN SEARCH ENGINE DASHBOARD & FILTERS -->
    <section class="history-dashboard max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
      <!-- Filter Controls Bar -->
      <div class="bg-slate-950/90 border border-amber-500/30 rounded-2xl p-4 sm:p-5 shadow-xl mb-8 space-y-4">
        
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <!-- Left: Filter Indicators -->
          <div class="flex items-center gap-2">
            <i class="bi bi-funnel text-amber-400 text-lg"></i>
            <h2 class="font-serif font-bold text-white text-base">Filter Cikal Bakal</h2>
            <span class="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-xs font-semibold">
              {{ filteredCount }} dari {{ totalCount }} Sinode
            </span>
          </div>

          <!-- Right: View Mode Toggle & Clear Filter -->
          <div class="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
            <!-- View Mode (Grid vs Timeline) -->
            <div class="inline-flex rounded-xl bg-slate-900 p-1 border border-slate-700">
              <button 
                type="button" 
                @click="viewMode = 'grid'"
                :class="[
                  'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer',
                  viewMode === 'grid' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
                ]"
              >
                <i class="bi bi-grid-fill"></i>
                <span>Kartu Katalog</span>
              </button>
              <button 
                type="button" 
                @click="viewMode = 'timeline'"
                :class="[
                  'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer',
                  viewMode === 'timeline' ? 'bg-amber-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
                ]"
              >
                <i class="bi bi-clock-history"></i>
                <span>Garis Waktu</span>
              </button>
            </div>

            <!-- Toggle Only Bookmarked -->
            <button 
              type="button" 
              @click="onlyBookmarks = !onlyBookmarks"
              :class="[
                'px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer',
                onlyBookmarks ? 'bg-amber-500/20 text-amber-300 border-amber-500' : 'bg-slate-900 text-slate-300 border-slate-700 hover:border-slate-600'
              ]"
            >
              <i :class="onlyBookmarks ? 'bi bi-bookmark-star-fill text-amber-400' : 'bi bi-bookmark text-slate-400'"></i>
              <span>Tersimpan ({{ bookmarkedIds.length }})</span>
            </button>

            <!-- Reset Filters -->
            <button 
              v-if="searchQuery || selectedDenomination !== 'all' || selectedRegion !== 'all' || selectedEra !== 'all' || onlyBookmarks"
              type="button" 
              @click="clearSearch"
              class="px-2.5 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold transition-all cursor-pointer flex items-center gap-1"
              title="Reset Semua Filter"
            >
              <i class="bi bi-arrow-counterclockwise"></i>
              <span class="hidden sm:inline">Reset</span>
            </button>
          </div>
        </div>

        <!-- Filter Dropdowns Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <!-- Filter Denominasi -->
          <div>
            <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Denominasi / Aliran</label>
            <select 
              v-model="selectedDenomination" 
              class="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 hover:border-amber-500/50 text-white text-xs focus:outline-none focus:ring-2 focus:ring-amber-500/30 cursor-pointer"
            >
              <option value="all">Semua Denominasi &amp; Tradisi</option>
              <option value="protestan">Protestan (PGI / Reformed / Lutheran)</option>
              <option value="pentakosta">Pentakosta &amp; Kharismatik (PGPI)</option>
              <option value="injili">Injili / Evangelical (PGLII)</option>
              <option value="katolik">Katolik Roma (KWI)</option>
              <option value="advent">Adventis (GMAHK)</option>
              <option value="bala keselamatan">Bala Keselamatan</option>
              <option value="ortodoks">Gereja Ortodoks Timur</option>
            </select>
          </div>

          <!-- Filter Wilayah Asal -->
          <div>
            <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Wilayah Asal Mula</label>
            <select 
              v-model="selectedRegion" 
              class="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 hover:border-amber-500/50 text-white text-xs focus:outline-none focus:ring-2 focus:ring-amber-500/30 cursor-pointer"
            >
              <option value="all">Seluruh Wilayah Indonesia</option>
              <option value="sumatera">Seluruh Sumatera</option>
              <option value="mentawai">Kepulauan Mentawai (GKPM)</option>
              <option value="riau">Riau &amp; Kepulauan Riau</option>
              <option value="bengkulu">Bengkulu (Marlborough &amp; Rejang)</option>
              <option value="simalungun">Simalungun (GKPS)</option>
              <option value="angkola">Angkola &amp; Sipirok (GKPA)</option>
              <option value="nias">Pulau Nias (BNKP)</option>
              <option value="jawa">Jawa &amp; Sunda (GKJ, GKI, GKP, GKMI)</option>
              <option value="bali">Bali (Blimbingsari &amp; Untal-untal)</option>
              <option value="maluku">Kepulauan Maluku &amp; Halmahera</option>
              <option value="sulawesi">Sulawesi (Minahasa, Toraja, Poso, Sangihe)</option>
              <option value="papua">Tanah Papua (Mansinam &amp; Pedalaman)</option>
              <option value="nusa tenggara">Nusa Tenggara (Timor &amp; Rote)</option>
              <option value="kalimantan">Kalimantan (Dayak GKE &amp; GKII)</option>
            </select>
          </div>

          <!-- Filter Era Sejarah -->
          <div>
            <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Periode / Era Sejarah</label>
            <select 
              v-model="selectedEra" 
              class="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 hover:border-amber-500/50 text-white text-xs focus:outline-none focus:ring-2 focus:ring-amber-500/30 cursor-pointer"
            >
              <option value="all">Semua Periode Sejarah</option>
              <option value="voc_early">Abad 16 - 18 (Era Portugis &amp; VOC)</option>
              <option value="zending_19">Abad 19 (Misi Zending &amp; Tokoh Pribumi)</option>
              <option value="kemandirian_early">1900 - 1945 (Kemandirian Sinode Awal)</option>
              <option value="pasca_kemerdekaan">1945 - Sekarang (Pasca Kemerdekaan &amp; Modern)</option>
            </select>
          </div>

          <!-- Urutan / Sorting -->
          <div>
            <label class="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Urutan Tampilan</label>
            <select 
              v-model="sortBy" 
              class="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 hover:border-amber-500/50 text-white text-xs focus:outline-none focus:ring-2 focus:ring-amber-500/30 cursor-pointer"
            >
              <option value="origin-asc">Tahun Misi Awal: Tertua ke Termuda</option>
              <option value="origin-desc">Tahun Misi Awal: Termuda ke Tertua</option>
              <option value="synod-asc">Tahun Sinode Mandiri: Tertua ke Termuda</option>
              <option value="synod-desc">Tahun Sinode Mandiri: Termuda ke Tertua</option>
              <option value="name-asc">Nama Sinode: Alfabet (A - Z)</option>
              <option value="name-desc">Nama Sinode: Alfabet (Z - A)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- ACTIVE SEARCH NOTIFICATION BAR -->
      <div v-if="searchQuery" class="mb-6 flex items-center justify-between bg-amber-500/10 border border-amber-500/30 rounded-xl px-4 py-2.5 text-xs text-amber-300">
        <div class="flex items-center gap-2">
          <i class="bi bi-search text-amber-400"></i>
          <span>Menampilkan <strong>{{ filteredCount }}</strong> hasil pencarian untuk kata kunci "<strong>{{ searchQuery }}</strong>"</span>
        </div>
        <button 
          type="button" 
          @click="searchQuery = ''"
          class="text-amber-400 hover:text-white underline cursor-pointer font-medium"
        >
          Bersihkan
        </button>
      </div>

      <!-- EMPTY SEARCH RESULT STATE -->
      <div 
        v-if="filteredChurches.length === 0" 
        class="text-center py-16 px-4 bg-slate-950/50 border border-slate-800 rounded-3xl space-y-4 max-w-xl mx-auto my-12"
      >
        <div class="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center text-3xl mx-auto">
          <i class="bi bi-journal-x"></i>
        </div>
        <h3 class="font-serif font-bold text-lg text-white">Tidak Ada Hasil yang Cocok</h3>
        <p class="text-xs text-slate-400 leading-relaxed">
          Pencarian untuk "{{ searchQuery }}" tidak ditemukan dalam arsip dengan filter aktif saat ini. Coba gunakan kata kunci lain seperti nama pulau, misionaris, atau reset filter Anda.
        </p>
        <button 
          type="button" 
          @click="clearSearch"
          class="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-xs transition-colors cursor-pointer"
        >
          Reset Semua Pencarian
        </button>
      </div>

      <!-- VIEW MODE 1: GRID CARDS (Search Engine Catalog) -->
      <div 
        v-if="viewMode === 'grid' && filteredChurches.length > 0" 
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        <article 
          v-for="church in filteredChurches" 
          :key="church.id"
          class="bg-slate-950/80 hover:bg-slate-900 border border-slate-800 hover:border-amber-500/50 rounded-2xl p-5 sm:p-6 transition-all duration-300 shadow-xl hover:shadow-amber-500/10 flex flex-col justify-between group relative"
        >
          <!-- Bookmark Ribbon Pin -->
          <button 
            type="button" 
            @click.stop="toggleBookmark(church.id)"
            class="absolute top-4 right-4 p-2 rounded-lg bg-slate-900/90 hover:bg-slate-800 text-slate-400 hover:text-amber-400 border border-slate-700/80 transition-all cursor-pointer z-10"
            :title="bookmarkedIds.includes(church.id) ? 'Hapus dari Tersimpan' : 'Simpan ke Favorit'"
          >
            <i :class="bookmarkedIds.includes(church.id) ? 'bi bi-bookmark-star-fill text-amber-400' : 'bi bi-bookmark text-slate-400'"></i>
          </button>

          <!-- Top Metadata & Header -->
          <div>
            <!-- Era, Dual Chronology Badges and Denomination -->
            <div class="flex items-center gap-1.5 flex-wrap mb-3 pr-10">
              <!-- Misi Awal Badge -->
              <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1" title="Tahun Permulaan Misi / Pekabaran Injil / Cikal Bakal">
                <i class="bi bi-compass text-amber-400"></i>
                <span>Misi: {{ church.originYear }}</span>
              </span>
              <!-- Sinode Mandiri Badge -->
              <span 
                v-if="church.synodYear && church.synodYear !== church.originYear"
                class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1"
                title="Tahun Peresmian Kemandirian Sinode Otonom"
              >
                <i class="bi bi-check2-circle text-emerald-400"></i>
                <span>Sinode Mandiri: {{ church.synodYear }}</span>
              </span>
              <span 
                v-else-if="church.synodYear"
                class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 flex items-center gap-1"
                title="Tahun Berdiri & Mandiri"
              >
                <i class="bi bi-award text-blue-400"></i>
                <span>Mandiri: {{ church.synodYear }}</span>
              </span>
              <!-- Denomination -->
              <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {{ church.denomination }}
              </span>
              <!-- Region -->
              <span class="text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-900 text-slate-400 border border-slate-800">
                {{ church.region }}
              </span>
            </div>

            <!-- Church Title -->
            <h3 class="font-serif font-black text-lg sm:text-xl text-white group-hover:text-amber-300 transition-colors leading-snug mb-1">
              {{ church.shortName }}
            </h3>
            <div class="text-xs text-amber-400/90 font-medium mb-3 line-clamp-1">
              {{ church.fullName }}
            </div>

            <!-- Quick Specs Matrix with Explicit Chronology -->
            <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-800 space-y-1.5 mb-4 text-xs font-sans">
              <div class="flex items-start gap-2 text-slate-300">
                <i class="bi bi-calendar2-range text-amber-400 shrink-0 mt-0.5"></i>
                <div class="text-[11px] leading-snug">
                  <span class="text-slate-400">Kronologi:</span>
                  <span class="text-amber-300 font-semibold ml-1">Misi {{ church.originYear }}</span>
                  <span class="text-slate-500 mx-1">→</span>
                  <span class="text-emerald-300 font-semibold">Sinode Mandiri {{ church.synodYear }}</span>
                </div>
              </div>
              <div class="flex items-start gap-2 text-slate-300">
                <i class="bi bi-geo-alt text-amber-400 shrink-0 mt-0.5"></i>
                <span class="text-[11px] text-slate-300 line-clamp-1">
                  <strong>Lokasi Asal:</strong> {{ church.subRegion }}
                </span>
              </div>
              <div class="flex items-start gap-2 text-slate-300">
                <i class="bi bi-person-badge text-amber-400 shrink-0 mt-0.5"></i>
                <span class="text-[11px] text-slate-300 line-clamp-1">
                  <strong>Tokoh Kunci:</strong> {{ church.founder }}
                </span>
              </div>
              <div class="flex items-start gap-2 text-slate-300">
                <i class="bi bi-diagram-3 text-amber-400 shrink-0 mt-0.5"></i>
                <span class="text-[11px] text-slate-300 line-clamp-1">
                  <strong>Tradisi:</strong> {{ church.tradition }}
                </span>
              </div>
            </div>

            <!-- Summary Text -->
            <p class="text-xs text-slate-300 leading-relaxed line-clamp-3 mb-4 font-sans">
              {{ church.summary }}
            </p>
          </div>

          <!-- Bottom Actions -->
          <div class="pt-4 border-t border-slate-800/80 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <!-- Affiliations Tags -->
            <div class="flex min-w-0 items-center gap-2 text-[10px] font-medium tracking-wide">
              <span class="shrink-0" style="color:gold;">Afiliasi:</span>
              <div class="flex min-w-0 flex-wrap items-center gap-1.5">
                <span
                  v-for="(aff, index) in church.oikoumene.slice(0, 2)"
                  :key="aff"
                  class="inline-flex max-w-[120px] truncate rounded-full border border-amber-500/30 px-1.5 py-0.5"
                  style="color:gold;"
                  :title="aff"
                >
                  {{ aff }}
                </span>
                <span
                  v-if="church.oikoumene.length > 2"
                  class="inline-flex items-center text-[10px]"
                  style="color:gold;"
                >+{{ church.oikoumene.length - 2 }}</span>
              </div>
            </div>

            <!-- Detail Action Button -->
            <button 
              type="button" 
              @click="openChurchDetail(church)"
              class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-amber-500/20 to-amber-600/20 hover:from-amber-500 hover:to-amber-600 text-amber-300 hover:text-slate-950 border border-amber-500/40 font-semibold text-xs transition-all flex items-center gap-1.5 cursor-pointer shrink-0"
            >
              <span>Pelajari Sejarah</span>
              <i class="bi bi-arrow-right text-xs"></i>
            </button>
          </div>
        </article>
      </div>

      <!-- VIEW MODE 2: INTERACTIVE CHRONOLOGICAL TIMELINE -->
      <div 
        v-if="viewMode === 'timeline' && timelineChurches.length > 0" 
        class="max-w-4xl mx-auto py-8 relative"
      >
        <!-- Central Line -->
        <div class="absolute left-4 sm:left-1/2 top-4 bottom-4 w-0.5 bg-gradient-to-b from-amber-500 via-amber-400/40 to-amber-600 -translate-x-1/2 hidden sm:block"></div>

        <div class="space-y-8 relative">
          <div 
            v-for="(church, idx) in timelineChurches" 
            :key="church.id"
            class="relative flex flex-col sm:flex-row items-center gap-6"
            :class="idx % 2 === 0 ? 'sm:flex-row-reverse' : ''"
          >
            <!-- Timeline Center Marker -->
            <div class="hidden sm:flex absolute left-1/2 -translate-x-1/2 w-9 h-9 rounded-full bg-slate-950 border-2 border-amber-400 items-center justify-center text-amber-400 z-10 shadow-lg shadow-amber-500/20">
              <span class="text-[10px] font-bold">{{ idx + 1 }}</span>
            </div>

            <!-- Content Card (50% Width) -->
            <div class="w-full sm:w-[calc(50%-2rem)]">
              <div class="bg-slate-950/90 border border-slate-800 hover:border-amber-500/50 rounded-2xl p-5 shadow-xl transition-all hover:scale-[1.01] group">
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <span class="font-serif font-black text-amber-400 text-lg sm:text-xl" title="Tahun Misi Awal">
                      Misi {{ church.originYear }}
                    </span>
                    <span v-if="church.synodYear && church.synodYear !== church.originYear" class="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" title="Tahun Kemandirian Sinode">
                      Sinode Mandiri {{ church.synodYear }}
                    </span>
                  </div>
                  <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {{ church.region }}
                  </span>
                </div>

                <h3 class="font-serif font-bold text-base text-white group-hover:text-amber-300 transition-colors mb-1">
                  {{ church.name }}
                </h3>

                <!-- Dual Event Chronology Pill -->
                <div class="my-2.5 p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1 text-[11px]">
                  <div class="flex items-start gap-1.5 text-amber-300/90">
                    <i class="bi bi-compass shrink-0 mt-0.5 text-[10px] text-amber-400"></i>
                    <span class="line-clamp-1"><strong>Misi ({{ church.originYear }}):</strong> {{ church.originEvent }}</span>
                  </div>
                  <div v-if="church.synodYear" class="flex items-start gap-1.5 text-emerald-300/90">
                    <i class="bi bi-award shrink-0 mt-0.5 text-[10px] text-emerald-400"></i>
                    <span class="line-clamp-1"><strong>Sinode ({{ church.synodYear }}):</strong> {{ church.synodEvent }}</span>
                  </div>
                </div>

                <p class="text-xs text-slate-300 leading-relaxed mb-3 line-clamp-3">
                  {{ church.summary }}
                </p>

                <div class="flex items-center justify-between pt-2 border-t border-slate-800">
                  <span class="text-[11px] text-amber-300/80 font-medium">
                    Tokoh: {{ church.founder.split(',')[0] }}
                  </span>
                  <button 
                    type="button" 
                    @click="openChurchDetail(church)"
                    class="text-xs text-amber-400 hover:text-white font-semibold flex items-center gap-1 cursor-pointer"
                  >
                    <span>Buka Arsip</span>
                    <i class="bi bi-chevron-right text-xs"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- Empty balance space on opposite side for desktop -->
            <div class="hidden sm:block sm:w-[calc(50%-2rem)]"></div>
          </div>
        </div>
      </div>

    </section>

    <!-- SECTION 10 KORIDOR & JALUR MISI BERSEJARAH NUSANTARA -->
    <section id="jalur-misi" class="history-corridors bg-slate-950/80 border-t border-b border-amber-500/20 py-16 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      <!-- Background Ambient Glow -->
      <div class="absolute top-1/2 left-1/4 -translate-y-1/2 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 right-10 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div class="max-w-7xl mx-auto relative z-10">
        <div class="text-center max-w-3xl mx-auto mb-10">
          <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 text-amber-300 text-xs font-semibold mb-3 border border-amber-500/30 shadow-sm">
            <i class="bi bi-signpost-split-fill text-amber-400"></i>
            <span>Historiografi Topografi & Geografis Pekabaran Injil</span>
          </div>
          <h2 class="font-serif font-black text-2xl sm:text-4xl text-white tracking-tight leading-tight">
            10 Koridor &amp; Jalur Misi Bersejarah Nusantara
          </h2>
          <p class="text-xs sm:text-sm text-slate-400 mt-2.5 leading-relaxed font-sans max-w-2xl mx-auto">
            Pelacakan akurat jalur pelayaran samudra, pos zending pedalaman rimba, padepokan kultural pribumi, hingga gelombang kebangunan rohani abad ke-20 yang melahirkan sinode-sinode di tanah air.
          </p>

          <!-- Category Filter Tabs -->
          <div class="flex items-center justify-center gap-1.5 sm:gap-2 flex-wrap mt-6">
            <button 
              type="button" 
              @click="selectedCorridorCategory = 'all'"
              :class="[
                'px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer border',
                selectedCorridorCategory === 'all' ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-500/20' : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
              ]"
            >
              Semua (10 Jalur Misi)
            </button>
            <button 
              type="button" 
              @click="selectedCorridorCategory = 'kuno_voc'"
              :class="[
                'px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer border',
                selectedCorridorCategory === 'kuno_voc' ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-500/20' : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
              ]"
            >
              Era Kuno &amp; VOC (Abad 7 - 18)
            </button>
            <button 
              type="button" 
              @click="selectedCorridorCategory = 'zending_19'"
              :class="[
                'px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer border',
                selectedCorridorCategory === 'zending_19' ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-500/20' : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
              ]"
            >
              Era Zending Mandiri (Abad 19)
            </button>
            <button 
              type="button" 
              @click="selectedCorridorCategory = 'sulawesi_pedalaman'"
              :class="[
                'px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer border',
                selectedCorridorCategory === 'sulawesi_pedalaman' ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-500/20' : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
              ]"
            >
              Sulawesi, Sangihe &amp; Toraja
            </button>
            <button 
              type="button" 
              @click="selectedCorridorCategory = 'gerakan_modern'"
              :class="[
                'px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer border',
                selectedCorridorCategory === 'gerakan_modern' ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-500/20' : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
              ]"
            >
              Kegerakan Abad 20 &amp; Pentakosta
            </button>
          </div>
        </div>

        <!-- Corridors Cards Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <article 
            v-for="corridor in filteredMissionCorridors" 
            :key="corridor.id"
            class="p-6 rounded-2xl bg-slate-900/85 border border-slate-800 hover:border-amber-500/50 transition-all duration-300 shadow-xl hover:shadow-amber-500/10 flex flex-col justify-between group relative overflow-hidden"
          >
            <!-- Top Badges & Icon -->
            <div>
              <div class="flex items-center justify-between gap-2 mb-3">
                <span class="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {{ corridor.period }}
                </span>
                <div class="w-8 h-8 rounded-xl bg-slate-800/90 border border-slate-700 flex items-center justify-center text-amber-400 group-hover:scale-110 transition-transform">
                  <i :class="[corridor.icon, 'text-sm']"></i>
                </div>
              </div>

              <!-- Title -->
              <h3 class="font-serif font-black text-white group-hover:text-amber-300 transition-colors text-lg leading-snug mb-2">
                {{ corridor.corridor }}
              </h3>

              <!-- Route Stations Flow -->
              <div class="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800/90 mb-3 text-[11px] font-sans">
                <div class="text-[10px] text-amber-400 font-bold uppercase tracking-wider mb-1 flex items-center gap-1">
                  <i class="bi bi-geo-alt-fill"></i>
                  <span>Alur Stasi &amp; Pos Misi:</span>
                </div>
                <div class="text-slate-300 leading-snug flex items-center gap-1.5 flex-wrap">
                  <template v-for="(station, sIdx) in corridor.routeStations" :key="station">
                    <span class="font-medium text-white">{{ station }}</span>
                    <i v-if="sIdx < corridor.routeStations.length - 1" class="bi bi-arrow-right text-[10px] text-amber-500"></i>
                  </template>
                </div>
              </div>

              <!-- Organization and Pioneers -->
              <div class="space-y-1 text-xs mb-3 text-slate-300 font-sans">
                <p class="text-[11px] text-slate-400">
                  <strong class="text-slate-300">Badan Misi:</strong> {{ corridor.missionAgencies }}
                </p>
                <p class="text-[11px] text-slate-400 line-clamp-1">
                  <strong class="text-slate-300">Tokoh Kunci:</strong> {{ corridor.pioneers }}
                </p>
              </div>

              <!-- Narrative Summary -->
              <p class="text-xs text-slate-300 leading-relaxed font-sans line-clamp-3 mb-4">
                {{ corridor.description }}
              </p>

              <!-- Key Impact Callout Box -->
              <div style="font-size: 10px;" class="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 font-sans">
                <strong>Signifikansi:</strong> {{ corridor.keyImpact }}
              </div>
            </div>

            <!-- Bottom: Resulting Churches & Explore Button -->
            <div class="pt-3.5 border-t border-slate-800/90 flex flex-col gap-3">
              <div>
                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">Sinode / Buah Misi Terkait:</span>
                <div class="flex items-center gap-1.5 flex-wrap">
                  <button
                    v-for="ch in corridor.resultingChurches"
                    :key="ch"
                    type="button"
                    @click="filterByCorridorChurch(ch)"
                    class="text-[10px] font-semibold px-2 py-0.5 rounded-lg bg-slate-800 hover:bg-amber-500/20 text-slate-200 hover:text-amber-300 border border-slate-700 hover:border-amber-500/40 transition-all cursor-pointer flex items-center gap-1"
                    :title="'Klik untuk memfilter katalog: ' + ch"
                  >
                    <span>{{ ch }}</span>
                    <i class="bi bi-arrow-up-right text-[8px] text-amber-400"></i>
                  </button>
                </div>
              </div>

              <button 
                type="button" 
                @click="openCorridorDetail(corridor)"
                class="w-full py-2 rounded-xl bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-amber-300 text-xs font-semibold transition-all flex items-center justify-center gap-1.5 cursor-pointer border border-slate-700 hover:border-amber-400"
              >
                <span>Buka Detail Ekspedisi Jalur Ini</span>
                <i class="bi bi-chevron-right text-xs"></i>
              </button>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- MODAL DETAIL JALUR MISI (Corridor Deep Dive Modal) -->
    <Transition name="fade">
      <div 
        v-if="isCorridorModalOpen && selectedCorridor" 
        @click.self="closeCorridorDetail"
        class="history-modal-backdrop fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto"
      >
        <div 
          class="history-modal bg-slate-900 border border-amber-500/40 rounded-3xl max-w-3xl w-full shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col animate__animated animate__zoomIn animate__faster"
        >
          <!-- Top Header -->
          <div class="history-modal-header relative bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 p-6 sm:p-7 border-b border-amber-500/30 shrink-0">
            <button 
              type="button" 
              @click="closeCorridorDetail"
              class="absolute top-5 right-5 p-2 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700 transition-colors cursor-pointer"
              title="Tutup Jendela"
            >
              <i class="bi bi-x-lg text-lg"></i>
            </button>

            <div class="flex items-center gap-2 flex-wrap mb-2 pr-12">
              <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-500 text-slate-950 flex items-center gap-1">
                <i class="bi bi-signpost-split-fill"></i>
                <span>{{ selectedCorridor.period }}</span>
              </span>
              <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-200 border border-slate-700">
                {{ selectedCorridor.badge }}
              </span>
            </div>

            <h2 class="font-serif font-black text-xl sm:text-2xl text-white mb-1">
              {{ selectedCorridor.corridor }}
            </h2>
            <div class="text-xs sm:text-sm text-amber-300 font-medium">
              Wilayah: {{ selectedCorridor.geography }}
            </div>
          </div>

          <!-- Body -->
          <div class="p-6 sm:p-8 overflow-y-auto space-y-6 text-slate-200 font-sans custom-scrollbar">
            
            <!-- Pos Perjalanan Ekspedisi -->
            <div>
              <h4 class="font-serif font-bold text-sm text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <i class="bi bi-geo-alt"></i>
                <span>Jejak Pos &amp; Titik Singgah Ekspedisi</span>
              </h4>
              <div class="space-y-2.5">
                <div 
                  v-for="(st, idx) in selectedCorridor.stationsDetail" 
                  :key="st.name"
                  class="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start gap-3"
                >
                  <div class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center justify-center text-xs font-bold shrink-0">
                    {{ idx + 1 }}
                  </div>
                  <div>
                    <h5 class="text-xs font-bold text-white mb-0.5">{{ st.name }}</h5>
                    <p class="text-xs text-slate-300 leading-snug">{{ st.note }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Lembaga & Tokoh -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">Badan Misi / Ordo Asal</span>
                <span class="text-xs font-semibold text-white block">{{ selectedCorridor.missionAgencies }}</span>
              </div>
              <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">Tokoh Misionaris &amp; Saksi Sejarah</span>
                <span class="text-xs font-semibold text-white block">{{ selectedCorridor.pioneers }}</span>
              </div>
            </div>

            <!-- Full Narrative Story -->
            <div>
              <h4 class="font-serif font-bold text-sm text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                <i class="bi bi-book"></i>
                <span>Dinamika Sejarah &amp; Kontekstualisasi Iman</span>
              </h4>
              <p class="text-xs sm:text-sm text-slate-300 leading-relaxed bg-slate-950/70 p-4 rounded-2xl border border-slate-800 whitespace-pre-line">
                {{ selectedCorridor.description }}
              </p>
            </div>

            <!-- Signifikansi Kebudayaan -->
            <div class="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-1">
              <h5 class="font-serif font-bold text-xs text-amber-300 flex items-center gap-1.5">
                <i class="bi bi-trophy"></i>
                <span>Signifikansi &amp; Warisan Peradaban:</span>
              </h5>
              <p class="text-xs text-slate-200 leading-relaxed">
                {{ selectedCorridor.keyImpact }}
              </p>
            </div>

            <!-- Gereja Terkait -->
            <div>
              <h4 class="font-serif font-bold text-xs text-amber-400 uppercase tracking-wider mb-2">
                Sinode yang Mekar dari Jalur Misi Ini:
              </h4>
              <div class="flex items-center gap-2 flex-wrap">
                <button
                  v-for="ch in selectedCorridor.resultingChurches"
                  :key="ch"
                  type="button"
                  @click="closeCorridorDetail(); filterByCorridorChurch(ch)"
                  class="px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500 text-amber-300 hover:text-slate-950 border border-amber-500/40 text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
                >
                  <i class="bi bi-search text-xs"></i>
                  <span>Lihat Profil {{ ch }}</span>
                </button>
              </div>
            </div>

          </div>

          <!-- Footer -->
          <div class="p-4 bg-slate-950 border-t border-slate-800 shrink-0 flex items-center justify-end">
            <button 
              type="button" 
              @click="closeCorridorDetail"
              class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors cursor-pointer"
            >
              Tutup Jendela
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- INTERACTIVE DETAIL MODAL (Deep Historical Dive) -->
    <Transition name="fade">
      <div 
        v-if="isDetailModalOpen && selectedChurch" 
        @click.self="closeChurchDetail"
        class="history-modal-backdrop fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto"
      >
        <div 
          class="history-modal bg-slate-900 border border-amber-500/40 rounded-3xl max-w-4xl w-full shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col animate__animated animate__zoomIn animate__faster"
        >
          <!-- Modal Top Header Banner -->
          <div class="history-modal-header relative bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 p-6 sm:p-8 border-b border-amber-500/30 shrink-0">
            <button 
              type="button" 
              @click="closeChurchDetail"
              class="absolute top-5 right-5 p-2 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700 transition-colors cursor-pointer"
              title="Tutup Jendela"
            >
              <i class="bi bi-x-lg text-lg"></i>
            </button>

            <div class="flex items-center gap-2 flex-wrap mb-2 pr-12">
              <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-500 text-slate-950 flex items-center gap-1">
                <i class="bi bi-compass-fill"></i>
                <span>Cikal Bakal / Misi: {{ selectedChurch.originYear }}</span>
              </span>
              <span v-if="selectedChurch.synodYear" class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500 text-slate-950 flex items-center gap-1">
                <i class="bi bi-award-fill"></i>
                <span>Sinode Mandiri: {{ selectedChurch.synodYear }}</span>
              </span>
              <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-200 border border-slate-700">
                {{ selectedChurch.denomination }}
              </span>
              <span class="text-xs font-medium px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {{ selectedChurch.region }}
              </span>
            </div>

            <h2 class="font-serif font-black text-2xl sm:text-3xl text-white mb-1">
              {{ selectedChurch.fullName }}
            </h2>
            <div class="text-xs sm:text-sm text-amber-300 font-medium">
              {{ selectedChurch.name }}
            </div>
          </div>

          <!-- Modal Scrollable Body -->
          <div class="p-6 sm:p-8 overflow-y-auto space-y-6 text-slate-200 font-sans custom-scrollbar">
            
            <!-- Quick Info Cards Grid (Chronology & Governance Distinction) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <div class="p-3.5 rounded-xl bg-slate-950 border border-amber-500/30 space-y-1">
                <div class="flex items-center gap-1.5 text-amber-400">
                  <i class="bi bi-compass text-xs"></i>
                  <span class="text-[10px] font-bold uppercase tracking-wider">Permulaan Misi / Pekabaran Injil</span>
                </div>
                <div class="text-sm font-bold text-amber-300">Tahun {{ selectedChurch.originYear }}</div>
                <div class="text-[11px] text-slate-300 leading-snug">{{ selectedChurch.originEvent || 'Perintisan awal karya pekabaran Injil.' }}</div>
              </div>

              <div class="p-3.5 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-1">
                <div class="flex items-center gap-1.5 text-emerald-400">
                  <i class="bi bi-award text-xs"></i>
                  <span class="text-[10px] font-bold uppercase tracking-wider">Kemandirian Sinode Mandiri</span>
                </div>
                <div class="text-sm font-bold text-emerald-300">Tahun {{ selectedChurch.synodYear }}</div>
                <div class="text-[11px] text-slate-300 leading-snug">{{ selectedChurch.synodEvent || 'Penetapan tata gereja dan kemandirian kepemimpinan sinode.' }}</div>
              </div>

              <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">Tokoh Kunci / Misionaris</span>
                <span class="text-xs font-semibold text-white block">{{ selectedChurch.founder }}</span>
              </div>
              <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">Badan Misi / Gereja Asal</span>
                <span class="text-xs font-semibold text-white block">{{ selectedChurch.missionAgency }}</span>
              </div>
              <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">Kantor Pusat Saat Ini</span>
                <span class="text-xs font-semibold text-white block">{{ selectedChurch.currentHeadquarters }}</span>
              </div>
              <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span class="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">Afiliasi Ekumenis</span>
                <span class="text-xs font-semibold text-white block">{{ selectedChurch.oikoumene.join(', ') }}</span>
              </div>
            </div>

            <!-- Full Narrative Story -->
            <div>
              <h3 class="font-serif font-bold text-lg text-white mb-2 flex items-center gap-2 text-amber-400">
                <i class="bi bi-book"></i>
                <span>Kisah Sejarah &amp; Perintisan Cikal Bakal</span>
              </h3>
              <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-3 bg-slate-950/60 p-5 rounded-2xl border border-slate-800 whitespace-pre-line">
                {{ selectedChurch.fullStory.trim() }}
              </div>
            </div>

            <!-- Historical Milestones (Tonggak Bersejarah) -->
            <div>
              <h3 class="font-serif font-bold text-lg text-white mb-3 flex items-center gap-2 text-amber-400">
                <i class="bi bi-clock-history"></i>
                <span>Tonggak-Tonggak Bersejarah</span>
              </h3>
              <div class="space-y-2.5">
                <div 
                  v-for="mile in selectedChurch.milestones" 
                  :key="mile.year"
                  class="history-milestone p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start gap-3"
                >
                  <div class="history-milestone-year font-serif font-bold text-sm text-amber-400 px-2 py-1 rounded bg-amber-500/10 border border-amber-500/30 shrink-0">
                    {{ mile.year }}
                  </div>
                  <div>
                    <h5 class="history-milestone-title text-xs font-bold text-white mb-0.5">{{ mile.title }}</h5>
                    <p class="history-milestone-description text-xs text-slate-300 leading-snug">{{ mile.desc }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Warisan & Hubungan Rumpun Gereja -->
            <div class="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-1.5">
              <h4 class="font-serif font-bold text-sm text-amber-300 flex items-center gap-2">
                <i class="bi bi-diagram-2"></i>
                <span>Warisan Pelayanan &amp; Rumpun Terkait:</span>
              </h4>
              <p class="text-xs text-slate-200 leading-relaxed">
                {{ selectedChurch.heritage }}
              </p>
            </div>

            <!-- Fakta Menarik / Trivia -->
            <div class="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-1">
              <h4 class="font-serif font-bold text-xs text-amber-400 flex items-center gap-2">
                <i class="bi bi-lightbulb"></i>
                <span>Fakta Unik Sejarah:</span>
              </h4>
              <p class="text-xs text-slate-300 leading-relaxed italic">
                "{{ selectedChurch.trivia }}"
              </p>
            </div>

          </div>

          <!-- Modal Footer Actions -->
          <div class="p-4 sm:p-5 bg-slate-950 border-t border-slate-800 shrink-0 flex items-center justify-between gap-3">
            <button 
              type="button" 
              @click="toggleBookmark(selectedChurch.id)"
              class="px-4 py-2 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
              :class="bookmarkedIds.includes(selectedChurch.id) ? 'bg-amber-500/20 text-amber-300 border-amber-500' : 'bg-slate-900 text-slate-300 border-slate-700 hover:border-slate-600'"
            >
              <i :class="bookmarkedIds.includes(selectedChurch.id) ? 'bi bi-bookmark-star-fill text-amber-400' : 'bi bi-bookmark'"></i>
              <span>{{ bookmarkedIds.includes(selectedChurch.id) ? 'Telah Disimpan' : 'Simpan ke Favorit' }}</span>
            </button>

            <div class="flex items-center gap-2">
              <button 
                type="button" 
                @click="copyCitation(selectedChurch)"
                class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Salin Kutipan Sejarah ke Clipboard"
              >
                <i class="bi bi-clipboard-check text-amber-400"></i>
                <span>Salin Ringkasan</span>
              </button>

              <button 
                type="button" 
                @click="closeChurchDetail"
                class="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold transition-colors cursor-pointer"
              >
                Tutup
              </button>
            </div>
          </div>

        </div>
      </div>
    </Transition>

  </ChurchHistoryLayout>
</template>

<style scoped>
:global(html[data-theme="light"]) .history-hero,
:global(html.theme-light) .history-hero {
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 58%, #f0f9ff 100%) !important;
  color: #0f172a;
}

:global(html[data-theme="light"]) .history-dashboard,
:global(html.theme-light) .history-dashboard {
  background-color: #ffffff;
}

:global(html[data-theme="light"]) .history-dashboard [class~="bg-slate-950/90"],
:global(html[data-theme="light"]) .history-dashboard [class~="bg-slate-950/80"],
:global(html[data-theme="light"]) .history-dashboard [class~="bg-slate-950/60"],
:global(html[data-theme="light"]) .history-dashboard [class~="bg-slate-950/50"],
:global(html[data-theme="light"]) .history-dashboard [class~="bg-slate-900/90"],
:global(html[data-theme="light"]) .history-dashboard [class~="bg-slate-900/80"],
:global(html[data-theme="light"]) .history-dashboard [class~="bg-slate-900/50"],
:global(html.theme-light) .history-dashboard [class~="bg-slate-950/90"],
:global(html.theme-light) .history-dashboard [class~="bg-slate-950/80"],
:global(html.theme-light) .history-dashboard [class~="bg-slate-950/60"],
:global(html.theme-light) .history-dashboard [class~="bg-slate-950/50"],
:global(html.theme-light) .history-dashboard [class~="bg-slate-900/90"],
:global(html.theme-light) .history-dashboard [class~="bg-slate-900/80"],
:global(html.theme-light) .history-dashboard [class~="bg-slate-900/50"] {
  background-color: #ffffff !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .history-hero [class~="bg-slate-950/80"],
:global(html[data-theme="light"]) .history-hero [class~="bg-slate-950/60"],
:global(html[data-theme="light"]) .history-hero [class~="bg-slate-800/80"],
:global(html.theme-light) .history-hero [class~="bg-slate-950/80"],
:global(html.theme-light) .history-hero [class~="bg-slate-950/60"],
:global(html.theme-light) .history-hero [class~="bg-slate-800/80"] {
  background-color: rgba(255, 255, 255, 0.86) !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .history-corridors,
:global(html.theme-light) .history-corridors {
  background-color: #f0f9ff !important;
}

:global(html[data-theme="light"]) .history-hero .bg-slate-950,
:global(html[data-theme="light"]) .history-hero .bg-slate-900,
:global(html[data-theme="light"]) .history-hero .bg-slate-800,
:global(html.theme-light) .history-hero .bg-slate-950,
:global(html.theme-light) .history-hero .bg-slate-900,
:global(html.theme-light) .history-hero .bg-slate-800 {
  background-color: rgba(255, 255, 255, 0.86) !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .history-dashboard .bg-slate-950,
:global(html[data-theme="light"]) .history-dashboard .bg-slate-900,
:global(html[data-theme="light"]) .history-dashboard .bg-slate-800,
:global(html.theme-light) .history-dashboard .bg-slate-950,
:global(html.theme-light) .history-dashboard .bg-slate-900,
:global(html.theme-light) .history-dashboard .bg-slate-800 {
  background-color: #ffffff !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .history-corridors .bg-slate-950,
:global(html[data-theme="light"]) .history-corridors .bg-slate-900,
:global(html[data-theme="light"]) .history-corridors .bg-slate-800,
:global(html.theme-light) .history-corridors .bg-slate-950,
:global(html.theme-light) .history-corridors .bg-slate-900,
:global(html.theme-light) .history-corridors .bg-slate-800 {
  background-color: #ffffff !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .history-corridors article,
:global(html.theme-light) .history-corridors article {
  background-color: #ffffff !important;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08) !important;
}

:global(html[data-theme="light"]) .history-modal-backdrop,
:global(html.theme-light) .history-modal-backdrop {
  background-color: rgba(15, 23, 42, 0.48) !important;
}

:global(html[data-theme="light"]) .history-modal,
:global(html.theme-light) .history-modal {
  background-color: #ffffff !important;
  color: #0f172a;
  box-shadow: 0 24px 64px rgba(15, 23, 42, 0.2) !important;
}

:global(html[data-theme="light"]) .history-modal-header,
:global(html.theme-light) .history-modal-header {
  background: linear-gradient(135deg, #f8fafc, #e0f2fe) !important;
}

:global(html[data-theme="light"]) .history-modal .bg-slate-950,
:global(html[data-theme="light"]) .history-modal .bg-slate-900,
:global(html[data-theme="light"]) .history-modal .bg-slate-800,
:global(html.theme-light) .history-modal .bg-slate-950,
:global(html.theme-light) .history-modal .bg-slate-900,
:global(html.theme-light) .history-modal .bg-slate-800 {
  background-color: #f8fafc !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .history-modal .bg-gradient-to-r,
:global(html.theme-light) .history-modal .bg-gradient-to-r {
  background-image: linear-gradient(135deg, #f8fafc, #e0f2fe) !important;
}

:global(html[data-theme="light"]) .history-modal [class~="bg-slate-950/70"],
:global(html[data-theme="light"]) .history-modal [class~="bg-slate-950/60"],
:global(html.theme-light) .history-modal [class~="bg-slate-950/70"],
:global(html.theme-light) .history-modal [class~="bg-slate-950/60"] {
  background-color: #f8fafc !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .history-layout .text-white,
:global(html[data-theme="light"]) .history-layout .text-slate-100,
:global(html[data-theme="light"]) .history-layout .text-slate-200,
:global(html[data-theme="light"]) .history-layout .text-slate-300,
:global(html[data-theme="light"]) .history-layout .text-slate-400,
:global(html.theme-light) .history-layout .text-white,
:global(html.theme-light) .history-layout .text-slate-100,
:global(html.theme-light) .history-layout .text-slate-200,
:global(html.theme-light) .history-layout .text-slate-300,
:global(html.theme-light) .history-layout .text-slate-400 {
  color: var(--theme-text-primary) !important;
}

:global(html[data-theme="light"]) .history-layout .text-slate-200,
:global(html[data-theme="light"]) .history-layout .text-slate-300,
:global(html.theme-light) .history-layout .text-slate-200,
:global(html.theme-light) .history-layout .text-slate-300 {
  color: #334155 !important;
}

:global(html[data-theme="light"]) .history-layout .text-slate-400,
:global(html.theme-light) .history-layout .text-slate-400 {
  color: #64748b !important;
}

:global(html[data-theme="light"]) .history-layout input,
:global(html[data-theme="light"]) .history-layout select,
:global(html.theme-light) .history-layout input,
:global(html.theme-light) .history-layout select {
  background-color: #ffffff !important;
  color: #0f172a !important;
  border-color: #cbd5e1 !important;
}

.history-milestone-year {
  color: var(--theme-gold-light) !important;
}

.history-milestone-title {
  color: var(--theme-text-primary) !important;
}

.history-milestone-description {
  color: var(--theme-text-secondary) !important;
}

:global(html[data-theme="light"]) .history-milestone,
:global(html.theme-light) .history-milestone {
  background-color: #f8fafc !important;
  border-color: #cbd5e1 !important;
}

:global(html[data-theme="light"]) .history-milestone-year,
:global(html.theme-light) .history-milestone-year {
  color: #b45309 !important;
  background-color: rgba(217, 119, 6, 0.1) !important;
  border-color: rgba(217, 119, 6, 0.35) !important;
}

:global(html[data-theme="light"]) .history-milestone-title,
:global(html.theme-light) .history-milestone-title {
  color: #0f172a !important;
}

:global(html[data-theme="light"]) .history-milestone-description,
:global(html.theme-light) .history-milestone-description {
  color: #334155 !important;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.4);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(245, 158, 11, 0.7);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
