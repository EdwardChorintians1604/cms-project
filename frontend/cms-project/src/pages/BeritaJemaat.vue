<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import BeritaJemaatLayout from '@/layouts/BeritaJemaatLayout.vue'
import AOS from 'aos'

onMounted(() => {
  nextTick(() => {
    try {
      AOS.refresh()
    } catch (e) {
      // Safe fallback
    }
  })
  setTimeout(() => {
    try {
      AOS.refresh()
    } catch (e) {}
  }, 350)
})

// --- Data Berita & Warta Jemaat ---
const newsList = ref([
  {
    id: 1,
    title: 'Pelaksanaan Perjamuan Kudus & Ibadah Syukur Agung Serentak Bulan Ini',
    excerpt: 'Seluruh jemaat diundang hadir dalam Perjamuan Kudus bulan ini. Mari persiapkan hati dan fisik kita dalam persekutuan kasih Kristus.',
    content: `
      <p class="mb-4">Salam sejahtera dalam kasih Tuhan kita Yesus Kristus.</p>
      <p class="mb-4">Majelis dan Tim Pastoral Gracepoint mengundang seluruh jemaat untuk menghadiri <strong>Ibadah Raya & Perjamuan Kudus Serentak</strong> yang akan dilaksanakan pada Minggu Pertama bulan ini. Ibadah ini merupakan momen istimewa bagi jemaat untuk mengingat kembali pengorbanan Kristus di kayu salib dan memperbarui komitmen iman kita.</p>
      <div class="my-4 p-4 bg-slate-950 rounded-2xl border border-amber-500/30 text-amber-300">
        <h5 class="font-serif font-bold text-sm mb-1"><i class="bi bi-clock-history mr-2"></i> Jadwal Ibadah Perjamuan Kudus:</h5>
        <ul class="list-disc list-inside text-xs space-y-1 text-slate-200 font-sans">
          <li>Sesi Pagi I: 07.00 WIB (Main Sanctuary Lt. 2)</li>
          <li>Sesi Pagi II & Kids Church: 10.00 WIB (Main Sanctuary & Kids Hall)</li>
          <li>Sesi Sore (Youth & Worker): 17.00 WIB (Youth Auditorium)</li>
        </ul>
      </div>
      <p class="mb-4">Bagi jemaat lansia atau yang berhalangan hadir secara fisik karena sakit, tim visitas diakonia siap melayani Perjamuan Kudus di rumah. Silakan menghubungi sekretariat gereja terlebih dahulu.</p>
    `,
    category: 'Warta Utama',
    church: 'Gracepoint Central',
    date: '06 Agustus 2026',
    readTime: '4 min baca',
    views: 1240,
    likes: 85,
    isLiked: false,
    isBookmarked: false,
    featured: true,
    image: 'https://images.unsplash.com/photo-1548625361-1854589d8161?auto=format&fit=crop&w=1200&q=80',
    author: {
      name: 'Pdt. Andreas Susanto, M.Th',
      role: 'Gembala Pembina',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80'
    }
  },
  {
    id: 2,
    title: 'Aksi Diakonia Gracepoint Care: Penyaluran 500 Paket Sembako & Pengobatan Gratis',
    excerpt: 'Tim Diakonia dan Layanan Sosial berhasil menyalurkan bantuan sembako dan pelayanan kesehatan bagi warga sekitar perumahan dan perkampungan.',
    content: `
      <p class="mb-4">Sebagai wujud kepedulian nyata gereja terhadap masyarakat sekitar, Tim Diakonia Gracepoint Care kembali menggelar Bakti Sosial dan Pengobatan Gratis pada akhir pekan lalu.</p>
      <p class="mb-4">Dalam kegiatan ini, sebanyak 500 paket sembako disalurkan kepada keluarga pra-sejahtera. Selain itu, tim dokter dan perawat dari jemaat juga memberikan layanan pemeriksaan kesehatan umum, cek gula darah, dan pemberian obat-obatan gratis kepada lebih dari 300 warga.</p>
      <p class="mb-4">Terima kasih atas partisipasi dan persembahan kasih seluruh jemaat yang telah mendukung keberlangsungan program ini. Soli Deo Gloria!</p>
    `,
    category: 'Diakonia & Sosial',
    church: 'Gracepoint Care',
    date: '04 Agustus 2026',
    readTime: '3 min baca',
    views: 890,
    likes: 64,
    isLiked: false,
    isBookmarked: false,
    featured: false,
    image: 'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&w=800&q=80',
    author: {
      name: 'Tim Diakonia & Sosial',
      role: 'Pelayanan Masyarakat',
      avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=200&q=80'
    }
  },
  {
    id: 3,
    title: 'Youth Revival Camp 2026: "Arise & Shine" Pendaftaran Resmi Dibuka!',
    excerpt: 'Panggilan bagi seluruh pemuda & mahasiswa! Mari bergabung dalam retreat tahunan pemuda dengan pembicara inspiratif dan worship malam pembaharuan.',
    content: `
      <p class="mb-4">Halo Youth & Campus Impact! Pendaftaran <strong>Youth Revival Camp 2026</strong> bertema <em>"Arise & Shine" (Yesaya 60:1)</em> resmi dibuka mulai hari ini.</p>
      <p class="mb-4">Retreat ini dirancang khusus untuk membakar kembali semangat pelayanan generasi muda, memberikan pembekalan karakter Kristen di era digital, serta mempererat persaudaraan antar mahasiswa dan pekerja muda.</p>
      <div class="my-4 p-4 bg-slate-950 rounded-2xl border border-amber-500/30 text-amber-300">
        <h5 class="font-serif font-bold text-sm mb-1"><i class="bi bi-geo-alt mr-2"></i> Lokasi & Tempat:</h5>
        <p class="text-xs text-slate-200">Wisma Pines Resort, Tretes - Pasuruan | 24 - 26 Agustus 2026</p>
      </div>
      <p class="mb-4">Kuota terbatas untuk 150 peserta pertama. Dapatkan diskon Early Bird hingga tanggal 15 Agustus. Kontak panitia Youth untuk pendaftaran langsung.</p>
    `,
    category: 'Kegiatan Pemuda',
    church: 'Gracepoint Youth',
    date: '02 Agustus 2026',
    readTime: '5 min baca',
    views: 1560,
    likes: 112,
    isLiked: false,
    isBookmarked: false,
    featured: false,
    image: 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?auto=format&fit=crop&w=800&q=80',
    author: {
      name: 'Pdt. Kevin Hartanto',
      role: 'Pastor Pemuda',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80'
    }
  },
  {
    id: 4,
    title: 'Pembinaan Kelas Katekisasi Baptisan & Keanggotaan Jemaat Gelombang II',
    excerpt: 'Bagi jemaat yang rindu menerima Sakramen Baptisan Kudus atau bergabung menjadi anggota resmi gereja, kelas pembinaan akan dimulai minggu depan.',
    content: `
      <p class="mb-4">Sekretariat Gereja membuka pendaftaran <strong>Kelas Katekisasi Gelombang II Tahun 2026</strong>. Kelas ini ditujukan bagi jemaat yang hendak mempersiapkan diri menerima Sakramen Baptisan Air maupun penerimaan anggota jemaat resmi.</p>
      <p class="mb-4">Pembinaan akan berlangsung selama 8 sesi tatap muka setiap hari Sabtu sore pkl 15.30 WIB di Ruang Konseling Lt. 3.</p>
    `,
    category: 'Pengumuman Ibadah',
    church: 'GKI Diponegoro',
    date: '30 Juli 2026',
    readTime: '3 min baca',
    views: 620,
    likes: 38,
    isLiked: false,
    isBookmarked: false,
    featured: false,
    image: 'https://images.unsplash.com/photo-1438032005730-c779502df39b?auto=format&fit=crop&w=800&q=80',
    author: {
      name: 'Pdt. Johanes Rahardjo',
      role: 'Sekretariat Pastoral',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=200&q=80'
    }
  },
  {
    id: 5,
    title: 'Renungan Mingguan: Menjaga Ketenangan Hati di Tengah Ketidakpastian Hidup',
    excerpt: 'Bagaimana firman Tuhan menuntun kita tetap memiliki damai sejahtera yang melampaui segala akal saat menghadapi tantangan hidup perkotaan.',
    content: `
      <p class="mb-4"><em>"Damai sejahtera Kutinggalkan bagimu. Damai sejahtera-Ku Kuberikan kepadamu..." (Yohanes 14:27)</em></p>
      <p class="mb-4">Di tengah riuk pikuk kehidupan modern yang menuntut kecepatan dan efisiensi, seringkali hati kita tergerus oleh rasa cemas dan ketakutan akan masa depan. Namun Firman Tuhan mengingatkan kita bahwa kedamaian sejati tidak ditentukan oleh situasi luar, melainkan oleh kehadiran Kristus di dalam hidup kita.</p>
      <p class="mb-4">Mari luangkan waktu sejenak di awal hari untuk berdoa, berserah, dan meyakini janji penyertaan-Nya yang tidak pernah gagal.</p>
    `,
    category: 'Renungan Harian',
    church: 'Gracepoint Central',
    date: '28 Juli 2026',
    readTime: '4 min baca',
    views: 2100,
    likes: 195,
    isLiked: false,
    isBookmarked: false,
    featured: false,
    image: 'https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=800&q=80',
    author: {
      name: 'Tim Penulis Renungan',
      role: 'Departemen Pengajaran',
      avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80'
    }
  },
  {
    id: 6,
    title: 'Seminar Keuangan Keluarga Kristen: "Mengelola Berkat dengan Akuntabel & Alkitabiah"',
    excerpt: 'Pelatihan praktis pengelolaan anggaran rumah tangga, perencanaan investasi rohani, dan literasi keuangan keluarga berbasis prinsip Firman.',
    content: `
      <p class="mb-4">Departemen Pelayanan Keluarga mengadakan <strong>Seminar & Workshop Keuangan Keluarga Kristen</strong> pada Sabtu mendatang.</p>
      <p class="mb-4">Seminar ini menghadirkan perencana keuangan profesional dan konselor pernikahan untuk membantu pasangan suami istri mengelola keuangan rumah tangga secara bijak, bebas dari utang yang menjerat, dan berdampak bagi pekerjaan Tuhan.</p>
    `,
    category: 'Seminar & Pelatihan',
    church: 'HKBP Surabaya Kota',
    date: '25 Juli 2026',
    readTime: '3 min baca',
    views: 740,
    likes: 52,
    isLiked: false,
    isBookmarked: false,
    featured: false,
    image: 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=800&q=80',
    author: {
      name: 'Tim Pelayanan Keluarga',
      role: 'Family Ministry',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80'
    }
  }
])

// --- UI State ---
const searchQuery = ref('')
const selectedCategory = ref('Semua')
const selectedChurchFilter = ref('Semua')
const sortBy = ref('terbaru') // 'terbaru' | 'populer' | 'disukai'
const selectedNewsDetail = ref(null)
const isSearchFocused = ref(false)

const categoriesList = [
  'Semua',
  'Warta Utama',
  'Pengumuman Ibadah',
  'Diakonia & Sosial',
  'Kegiatan Pemuda',
  'Renungan Harian',
  'Seminar & Pelatihan'
]

const churchFilterList = [
  'Semua',
  'Gracepoint Central',
  'GKI Diponegoro',
  'HKBP Surabaya',
  'Gracepoint Care',
  'Gracepoint Youth'
]

// Computed Featured News Item
const featuredNews = computed(() => {
  return newsList.value.find(n => n.featured) || newsList.value[0]
})

// Filtered & Sorted News List
const filteredNews = computed(() => {
  let list = newsList.value.filter(n => !n.featured)

  // Search filter
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    list = list.filter(n => 
      n.title.toLowerCase().includes(q) ||
      n.excerpt.toLowerCase().includes(q) ||
      n.category.toLowerCase().includes(q) ||
      n.church.toLowerCase().includes(q)
    )
  }

  // Category filter
  if (selectedCategory.value !== 'Semua') {
    list = list.filter(n => n.category === selectedCategory.value)
  }

  // Church filter
  if (selectedChurchFilter.value !== 'Semua') {
    list = list.filter(n => n.church.toLowerCase().includes(selectedChurchFilter.value.toLowerCase()))
  }

  // Sort logic
  if (sortBy.value === 'populer') {
    list.sort((a, b) => b.views - a.views)
  } else if (sortBy.value === 'disukai') {
    list.sort((a, b) => b.likes - a.likes)
  }

  return list
})

watch([selectedCategory, selectedChurchFilter, searchQuery, sortBy], () => {
  nextTick(() => {
    setTimeout(() => {
      try {
        AOS.refresh()
      } catch (e) {}
    }, 150)
  })
})

// Interaction Handlers
function toggleLike(newsItem) {
  newsItem.isLiked = !newsItem.isLiked
  if (newsItem.isLiked) newsItem.likes++
  else newsItem.likes--
}

function toggleBookmark(newsItem) {
  newsItem.isBookmarked = !newsItem.isBookmarked
}

function openNewsModal(newsItem) {
  selectedNewsDetail.value = newsItem
}

function closeNewsModal() {
  selectedNewsDetail.value = null
}
</script>

<template>
  <BeritaJemaatLayout>
    <div class="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-10 font-sans text-slate-100">

      <!-- ================= HERO HEADER BANNER ================= -->
      <section class="relative text-center py-12 px-6 rounded-3xl bg-slate-900 border border-amber-500/30 shadow-2xl overflow-hidden" data-aos="fade-up">
        <div class="absolute -top-28 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 max-w-3xl mx-auto space-y-4">
          <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold uppercase font-serif tracking-wider">
            <i class="bi bi-newspaper text-amber-400"></i>
            Warta & Portal Berita Jemaat Terintegrasi
          </div>

          <h1 class="font-serif text-3xl sm:text-5xl font-extrabold tracking-wide text-amber-300 leading-tight">
            Berita, Warta & Informasi Pelayanan Jemaat
          </h1>

          <p class="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Dapatkan informasi warta mingguan, pengumuman ibadah raya, laporan diakonia sosial, dan artikel spiritual terpercaya dalam satu portal terpadu.
          </p>

          <!-- SEARCH BAR -->
          <div id="search" class="relative mt-8 max-w-2xl mx-auto text-left scroll-mt-28">
            <div 
              class="flex items-center bg-slate-950 border transition-all duration-300 rounded-full px-5 py-3.5 shadow-2xl relative z-20"
              :class="isSearchFocused ? 'border-amber-400 ring-4 ring-amber-500/20' : 'border-amber-500/30 hover:border-amber-500/60'"
            >
              <i class="bi bi-search text-xl text-amber-400 mr-3"></i>

              <input 
                v-model="searchQuery"
                @focus="isSearchFocused = true"
                @blur="isSearchFocused = false"
                type="text" 
                placeholder="Cari berita (contoh: Perjamuan Kudus, Diakonia, Youth Camp, Renungan)..."
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
                <i class="bi bi-newspaper"></i>
                <span>Cari Warta</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= SPOTLIGHT / FEATURED NEWS HERO ================= -->
      <section id="spotlight" v-if="featuredNews" data-aos="fade-up" data-aos-delay="100" class="scroll-mt-28">
        <div class="group bg-slate-900 border border-amber-500/30 rounded-3xl overflow-hidden shadow-2xl hover:border-amber-400/80 transition-all duration-300 grid grid-cols-1 lg:grid-cols-12">
          
          <!-- Image Banner Side -->
          <div class="lg:col-span-7 relative h-72 lg:h-auto overflow-hidden bg-slate-950">
            <img 
              :src="featuredNews.image" 
              :alt="featuredNews.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 opacity-90 group-hover:opacity-100" 
            />
            <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/30 to-transparent lg:bg-gradient-to-r lg:from-transparent lg:to-slate-900"></div>

            <div class="absolute top-4 left-4 flex gap-2">
              <span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500 text-slate-950 shadow-lg font-serif">
                <i class="bi bi-star-fill mr-1"></i> Warta Utama Minggu Ini
              </span>
              <span class="px-3 py-1 rounded-full text-xs font-semibold bg-slate-950/80 text-amber-300 border border-amber-500/30 backdrop-blur-md">
                {{ featuredNews.category }}
              </span>
            </div>
          </div>

          <!-- Content Details Side -->
          <div class="lg:col-span-5 p-6 lg:p-8 flex flex-col justify-between space-y-6">
            <div class="space-y-4">
              <div class="flex items-center justify-between text-xs text-slate-400">
                <span class="flex items-center gap-1.5 text-amber-300 font-semibold font-serif">
                  <i class="bi bi-building"></i> {{ featuredNews.church }}
                </span>
                <span class="flex items-center gap-1.5">
                  <i class="bi bi-calendar-event"></i> {{ featuredNews.date }}
                </span>
              </div>

              <h2 class="font-serif text-xl sm:text-2xl font-extrabold text-white group-hover:text-amber-300 transition-colors leading-snug">
                {{ featuredNews.title }}
              </h2>

              <p class="text-xs sm:text-sm text-slate-300 leading-relaxed line-clamp-3">
                {{ featuredNews.excerpt }}
              </p>
            </div>

            <!-- Author & Action Footer -->
            <div class="pt-4 border-t border-amber-500/20 flex items-center justify-between gap-4">
              <div class="flex items-center gap-3">
                <img :src="featuredNews.author.avatar" class="w-10 h-10 rounded-full object-cover border border-amber-400" />
                <div>
                  <h4 class="text-xs font-bold text-white font-serif">{{ featuredNews.author.name }}</h4>
                  <p class="text-[10px] text-amber-300">{{ featuredNews.author.role }}</p>
                </div>
              </div>

              <button 
                @click="openNewsModal(featuredNews)"
                class="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-xl text-xs shadow-md transition-all flex items-center gap-1.5 shrink-0 cursor-pointer"
              >
                <span>Baca Warta</span>
                <i class="bi bi-arrow-right-short text-base"></i>
              </button>
            </div>
          </div>

        </div>
      </section>

      <!-- ================= CONTROLS & FILTER BAR ================= -->
      <section data-aos="fade-up" data-aos-delay="150" class="bg-slate-900 border border-amber-500/30 rounded-2xl p-4 sm:p-5 flex flex-col md:flex-row justify-between items-center gap-4 shadow-xl">
        
        <!-- Category Quick Chips -->
        <div class="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 scrollbar-none">
          <button 
            v-for="cat in categoriesList" 
            :key="cat"
            @click="selectedCategory = cat"
            :class="[
              'px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 cursor-pointer',
              selectedCategory === cat 
                ? 'bg-amber-500 text-slate-950 font-bold shadow-md scale-105' 
                : 'bg-slate-800 text-slate-300 border border-amber-500/20 hover:border-amber-400 hover:text-amber-300'
            ]"
          >
            <span>{{ cat }}</span>
          </button>
        </div>

        <!-- Filters & Sorting Selects -->
        <div class="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end shrink-0">
          
          <!-- Church Filter -->
          <div class="flex items-center gap-1 text-xs text-slate-300">
            <i class="bi bi-church text-amber-400"></i>
            <select 
              v-model="selectedChurchFilter"
              class="bg-slate-800 border border-amber-500/30 text-slate-200 rounded-xl px-3 py-1.5 focus:outline-none text-xs"
            >
              <option value="Semua">Semua Gereja</option>
              <option v-for="ch in churchFilterList.filter(x => x !== 'Semua')" :key="ch" :value="ch">{{ ch }}</option>
            </select>
          </div>

          <!-- Sort Select -->
          <div class="flex items-center gap-1 text-xs text-slate-300">
            <i class="bi bi-sort-down text-amber-400"></i>
            <select 
              v-model="sortBy"
              class="bg-slate-800 border border-amber-500/30 text-slate-200 rounded-xl px-3 py-1.5 focus:outline-none text-xs"
            >
              <option value="terbaru">Terbaru</option>
              <option value="populer">Paling Banyak Dibaca</option>
              <option value="disukai">Paling Banyak Disukai</option>
            </select>
          </div>

        </div>
      </section>

      <!-- ================= NEWS CARDS GRID ================= -->
      <section class="space-y-6">
        
        <!-- Empty State -->
        <div v-if="filteredNews.length === 0" data-aos="zoom-in" class="text-center py-16 bg-slate-900 rounded-3xl border border-amber-500/30 space-y-4">
          <div class="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-amber-400 text-2xl border border-amber-500/30">
            <i class="bi bi-newspaper"></i>
          </div>
          <h3 class="font-serif text-lg font-bold text-amber-300">Tidak Ada Warta Ditemukan</h3>
          <p class="text-xs text-slate-400 max-w-md mx-auto">
            Coba sesuaikan kata kunci pencarian Anda atau reset filter kategori yang sedang aktif.
          </p>
          <button 
            @click="searchQuery = ''; selectedCategory = 'Semua'; selectedChurchFilter = 'Semua';"
            class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-xl text-xs font-semibold border border-amber-500/30 transition-all cursor-pointer"
          >
            Reset Filter Pencarian
          </button>
        </div>

        <!-- News Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          <div 
            v-for="(news, idx) in filteredNews" 
            :key="news.id"
            data-aos="fade-up"
            :data-aos-delay="((idx % 3) + 1) * 100"
            class="group bg-slate-900 border border-amber-500/30 rounded-3xl overflow-hidden hover:border-amber-400/80 hover:shadow-2xl hover:shadow-amber-950/30 transition-all duration-300 flex flex-col justify-between"
          >
            <!-- Card Image Header -->
            <div class="relative h-48 overflow-hidden bg-slate-950 cursor-pointer" @click="openNewsModal(news)">
              <img 
                :src="news.image" 
                :alt="news.title"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-85 group-hover:opacity-100" 
              />
              <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/20 to-transparent"></div>

              <!-- Top Badges -->
              <div class="absolute top-3 left-3 flex items-center gap-1.5 z-10">
                <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-950/90 text-amber-300 border border-amber-500/40 backdrop-blur-md">
                  {{ news.category }}
                </span>
              </div>

              <!-- Bookmark Trigger Button -->
              <button 
                @click.stop="toggleBookmark(news)"
                :class="[
                  'absolute top-3 right-3 w-8 h-8 rounded-full border flex items-center justify-center transition-all z-10 backdrop-blur-md cursor-pointer',
                  news.isBookmarked 
                    ? 'bg-amber-500 border-amber-400 text-slate-950 shadow-lg' 
                    : 'bg-slate-950/80 border-amber-500/30 text-amber-300 hover:text-white'
                ]"
                title="Simpan Berita"
              >
                <i :class="['bi', news.isBookmarked ? 'bi-bookmark-fill' : 'bi-bookmark']"></i>
              </button>
            </div>

            <!-- Card Body Content -->
            <div class="p-5 flex-1 space-y-4 flex flex-col justify-between">
              
              <div class="space-y-2">
                <div class="flex items-center justify-between text-[11px] text-slate-400 font-sans">
                  <span class="text-amber-400 font-semibold font-serif flex items-center gap-1">
                    <i class="bi bi-building"></i> {{ news.church }}
                  </span>
                  <span><i class="bi bi-clock mr-1"></i> {{ news.readTime }}</span>
                </div>

                <h3 
                  @click="openNewsModal(news)"
                  class="font-serif text-base font-bold text-white group-hover:text-amber-300 transition-colors leading-snug cursor-pointer line-clamp-2"
                >
                  {{ news.title }}
                </h3>

                <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {{ news.excerpt }}
                </p>
              </div>

              <!-- Card Footer Actions -->
              <div class="pt-3 border-t border-amber-500/20 flex items-center justify-between text-xs">
                
                <div class="flex items-center gap-3 text-slate-400">
                  <button 
                    @click="toggleLike(news)" 
                    :class="['flex items-center gap-1 transition-colors cursor-pointer', news.isLiked ? 'text-red-400 font-bold' : 'hover:text-red-300']"
                  >
                    <i :class="['bi', news.isLiked ? 'bi-heart-fill text-red-500' : 'bi-heart']"></i>
                    <span>{{ news.likes }}</span>
                  </button>

                  <span class="flex items-center gap-1 text-slate-400">
                    <i class="bi bi-eye"></i> {{ news.views }}
                  </span>
                </div>

                <button 
                  @click="openNewsModal(news)"
                  class="text-amber-400 hover:text-amber-300 font-bold text-xs flex items-center gap-1 cursor-pointer"
                >
                  <span>Selengkapnya</span>
                  <i class="bi bi-chevron-right text-xs"></i>
                </button>

              </div>

            </div>

          </div>

        </div>

      </section>

      <!-- ================= NEWSLETTER & DIGITAL WARTA DOWNLOAD SECTION ================= -->
      <section data-aos="fade-up" class="bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border border-amber-500/30 rounded-3xl p-6 sm:p-10 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="space-y-2 max-w-xl text-center md:text-left">
          <span class="px-3 py-1 rounded-full text-xs font-serif font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
            <i class="bi bi-file-earmark-pdf mr-1"></i> Warta Mingguan Digital (PDF)
          </span>
          <h3 class="font-serif text-xl sm:text-2xl font-bold text-white">Unduh Warta Jemaat Format PDF Sesuai Minggu Ini</h3>
          <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Dapatkan salinan warta fisik mingguan lengkap dengan rincian anggaran diakonia, warta duka/sukacita, dan jadwal pembina jemaat.
          </p>
        </div>

        <div class="flex flex-col sm:flex-row gap-3 w-full md:w-auto shrink-0">
          <button 
            class="px-5 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold rounded-2xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
          >
            <i class="bi bi-download text-base"></i>
            <span>Unduh Warta PDF (1.4 MB)</span>
          </button>
        </div>
      </section>

      <!-- ================= MODAL DETAIL BERITA / WARTA ================= -->
      <Transition name="fade">
        <div 
          v-if="selectedNewsDetail"
          class="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto"
          @click.self="closeNewsModal"
        >
          <div class="bg-slate-900 border border-amber-500/40 w-full max-w-3xl rounded-3xl shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col">
            
            <!-- Modal Banner Header -->
            <div class="relative h-56 sm:h-72 bg-slate-950 shrink-0">
              <img :src="selectedNewsDetail.image" class="w-full h-full object-cover opacity-85" />
              <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/40 to-transparent"></div>

              <button 
                @click="closeNewsModal"
                class="absolute top-4 right-4 w-9 h-9 rounded-full bg-slate-950/80 text-slate-300 hover:text-white border border-amber-500/30 flex items-center justify-center transition-all z-10 cursor-pointer"
              >
                <i class="bi bi-x-lg"></i>
              </button>

              <div class="absolute bottom-4 left-6 right-6 space-y-1">
                <div class="flex items-center gap-2 text-xs text-amber-300 font-serif font-bold">
                  <span class="px-2.5 py-0.5 rounded bg-slate-950/80 border border-amber-500/30">{{ selectedNewsDetail.category }}</span>
                  <span>•</span>
                  <span>{{ selectedNewsDetail.church }}</span>
                </div>
                <h2 class="font-serif text-lg sm:text-2xl font-extrabold text-white leading-tight">
                  {{ selectedNewsDetail.title }}
                </h2>
              </div>
            </div>

            <!-- Modal Content Body -->
            <div class="p-6 overflow-y-auto space-y-6 text-sm text-slate-300 flex-1">
              
              <!-- Meta Stats Bar -->
              <div class="flex items-center justify-between text-xs text-slate-400 pb-4 border-b border-amber-500/20">
                <div class="flex items-center gap-3">
                  <img :src="selectedNewsDetail.author.avatar" class="w-9 h-9 rounded-full object-cover border border-amber-400" />
                  <div>
                    <h5 class="font-bold text-white font-serif">{{ selectedNewsDetail.author.name }}</h5>
                    <p class="text-[10px] text-amber-300">{{ selectedNewsDetail.author.role }}</p>
                  </div>
                </div>

                <div class="flex items-center gap-4 text-xs">
                  <span><i class="bi bi-calendar-event mr-1 text-amber-400"></i> {{ selectedNewsDetail.date }}</span>
                  <span><i class="bi bi-clock mr-1 text-amber-400"></i> {{ selectedNewsDetail.readTime }}</span>
                </div>
              </div>

              <!-- Main Formatted Article HTML -->
              <div class="leading-relaxed space-y-4 text-slate-200 text-sm" v-html="selectedNewsDetail.content"></div>

            </div>

            <!-- Modal Footer Bar -->
            <div class="p-4 bg-slate-950 border-t border-amber-500/30 flex items-center justify-between shrink-0">
              <div class="flex items-center gap-3 text-xs">
                <button 
                  @click="toggleLike(selectedNewsDetail)"
                  :class="['px-3 py-1.5 rounded-xl border flex items-center gap-1.5 transition-all cursor-pointer', selectedNewsDetail.isLiked ? 'bg-red-500/20 border-red-500 text-red-400 font-bold' : 'bg-slate-800 border-amber-500/30 text-slate-300']"
                >
                  <i :class="['bi', selectedNewsDetail.isLiked ? 'bi-heart-fill text-red-500' : 'bi-heart']"></i>
                  <span>{{ selectedNewsDetail.likes }} Menyukai</span>
                </button>
              </div>

              <button 
                @click="closeNewsModal" 
                class="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 text-xs font-bold border border-amber-500/30 transition-colors cursor-pointer"
              >
                Tutup Warta
              </button>
            </div>

          </div>
        </div>
      </Transition>

    </div>
  </BeritaJemaatLayout>
</template>

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