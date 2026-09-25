<script setup>
import { onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import PetaBerandaNavbar from '@/components/PetaBerandaNavbar.vue'
import Home_Sidebar from '@/components/Home_Sidebar.vue'
import { useSidebar } from '@/composables/useSidebar'
import AOS from 'aos'

const props = defineProps({
  totalChurches: {
    type: Number,
    default: 0
  },
  isGpsActive: {
    type: Boolean,
    default: false
  },
  isDetectingLocation: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'detect-location',
  'reset-map',
  'open-report-modal',
  'open-floorplan-modal',
  'focus-search'
])

const { isSidebarOpen, toggleSidebar } = useSidebar()

onMounted(() => {
  nextTick(() => {
    try {
      AOS.refresh()
    } catch (e) {
      // safe fallback
    }
  })
})
</script>

<template>
  <div class="peta-layout min-h-screen bg-[var(--theme-bg-primary)] text-[var(--theme-text-primary)] flex flex-col relative transition-colors duration-300">
    
    <!-- Navbar Khusus Peta & Denah Gereja -->
    <PetaBerandaNavbar 
      :total-churches="totalChurches"
      :is-gps-active="isGpsActive"
      :is-detecting-location="isDetectingLocation"
      @detect-location="emit('detect-location')"
      @reset-map="emit('reset-map')"
      @open-report-modal="emit('open-report-modal')"
      @open-floorplan-modal="emit('open-floorplan-modal')"
      @focus-search="emit('focus-search')"
    />

    <div class="flex flex-1 relative min-w-0">
      <!-- Backdrop Gelap di Semua Ukuran Layar -->
      <Transition name="fade">
        <div 
          v-if="isSidebarOpen" 
          @click="toggleSidebar"
          class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 transition-opacity duration-300 cursor-pointer"
        ></div>
      </Transition>

      <!-- Floating Slide-over Drawer Sidebar (Fixed Overlay di Semua Ukuran Layar) -->
      <Transition name="slide">
        <div 
          v-if="isSidebarOpen" 
          class="fixed inset-y-0 left-0 z-50 h-full w-72 sm:w-80 shadow-2xl"
        >
          <Home_Sidebar />
        </div>
      </Transition>

      <!-- Area Konten Utama Halaman Peta -->
      <main class="flex-1 min-w-0 transition-all duration-300">
        <slot />
      </main>
    </div>

    <!-- Footer Tematik Khusus Peta & Geolokasi Gereja -->
    <footer class="myfooter">
      <div class="footer-container">
        <!-- Main Footer Grid -->
        <div class="footer-grid">
          
          <!-- Col 1: Brand & Sistem GIS -->
          <div class="footer-col footer-col-brand">
            <div class="footer-brand flex items-center gap-3 mb-1">
              <div class="footer-logo">
                <img src="@/assets/images/GracePoint.png" alt="GracePoint Logo" class="w-full h-full object-cover">
              </div>
              <div class="flex flex-col">
                <span class="footer-brand-title">GRACEPOINT GIS</span>
                <span class="footer-brand-sub">Pemetaan &amp; Denah Gereja Indonesia</span>
              </div>
            </div>
            <p class="footer-description">
              Sistem geolokasi presisi yang menghubungkan jemaat dengan gereja induk, pos pelayanan, serta cabang sinode secara real-time melalui integrasi DBMS PostgreSQL dan Google Maps.
            </p>
            <div class="footer-motto">
              <span>✝ Soli Deo Gloria</span> — Menuntun Langkah Menuju Rumah Tuhan
            </div>
          </div>

          <!-- Col 2: Fitur Pemetaan & Rute -->
          <div class="footer-col">
            <h4 class="footer-heading">Navigasi Peta</h4>
            <ul class="footer-links">
              <li><a href="#peta-gereja" class="footer-link"><i class="bi bi-geo-alt text-amber-400"></i> Peta Koordinat Terdaftar</a></li>
              <li><a href="#daftar-rute" class="footer-link"><i class="bi bi-compass text-amber-400"></i> Rute &amp; Navigasi Google Maps</a></li>
              <li><a href="#" @click.prevent="emit('detect-location')" class="footer-link"><i class="bi bi-crosshair text-emerald-400"></i> Deteksi Posisi Pengguna (GPS)</a></li>
              <li><a href="#" @click.prevent="emit('open-floorplan-modal')" class="footer-link"><i class="bi bi-diagram-3 text-cyan-400"></i> Denah &amp; Tata Ruang Gedung</a></li>
            </ul>
          </div>

          <!-- Col 3: Partisipasi & Pelaporan -->
          <div class="footer-col">
            <h4 class="footer-heading">Partisipasi &amp; Koreksi</h4>
            <ul class="footer-links">
              <li>
                <a href="#" @click.prevent="emit('open-report-modal')" class="footer-link text-amber-300 font-semibold">
                  <i class="bi bi-pencil-square text-amber-400"></i> Lapor Pembaruan Koordinat
                </a>
              </li>
              <li><RouterLink to="/church-register" class="footer-link">Registrasi Gereja Baru</RouterLink></li>
              <li><RouterLink to="/verification-login" class="footer-link">Masuk Portal Admin Gereja</RouterLink></li>
              <li><RouterLink to="/hari-besar" class="footer-link">Kalender &amp; Hari Besar Gereja</RouterLink></li>
            </ul>
          </div>

          <!-- Col 4: Status Database & Kontak Layanan -->
          <div class="footer-col">
            <h4 class="footer-heading">Layanan &amp; Dukungan</h4>
            <div class="footer-contact-info">
              <div class="contact-item">
                <span class="contact-icon">📍</span>
                <div>
                  <div class="contact-label">Status Geolocation</div>
                  <div class="contact-val text-emerald-400 font-mono">{{ totalChurches }} Titik Koordinat Aktif</div>
                </div>
              </div>
              <div class="contact-item">
                <span class="contact-icon">🏛️</span>
                <div>
                  <div class="contact-label">Pembaruan Denah</div>
                  <div class="contact-val">Admin Gereja &amp; Verifikasi Sinode</div>
                </div>
              </div>
              <div class="contact-item">
                <span class="contact-icon">💬</span>
                <div>
                  <div class="contact-label">Bantuan Teknis DBMS</div>
                  <div class="contact-val">(021) 555-0199 / WA 0812-3456-7890</div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Divider -->
        <div class="footer-divider"></div>

        <!-- Bottom Copyright Bar -->
        <div class="mycard">
          <p class="copyright-text">
            &copy; 2026 <strong>GracePoint</strong> — Sistem Pemetaan &amp; Denah Gereja Indonesia.
          </p>
          <div class="footer-status-badge">
            <span class="status-dot"></span>
            <span>GracePoint Map GIS Engine v1.0</span>
          </div>
        </div>
      </div>
    </footer>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&display=swap');

.myfooter {
  width: 100%;
  background-color: #070c1e;
  border-top: 1px solid rgba(245, 158, 11, 0.25);
  position: relative;
  z-index: 10;
  padding: 2rem 0.75rem 1.25rem 0.75rem;
  color: #e2e8f0;
  font-family: Inter, system-ui, -apple-system, sans-serif;
}

@media (min-width: 360px) {
  .myfooter {
    padding: 2.5rem 1rem 1.5rem 1rem;
  }
}

@media (min-width: 640px) {
  .myfooter {
    padding: 3rem 1.5rem 1.5rem 1.5rem;
  }
}

.footer-container {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 2rem;
}

@media (min-width: 640px) {
  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .footer-grid {
    grid-template-columns: 1.8fr 1fr 1.1fr 1.3fr;
  }
}

.footer-col-brand {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-logo {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid rgba(245, 158, 11, 0.5);
  background: linear-gradient(180deg, #0f172a 0%, #020617 100%);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px rgba(245, 158, 11, 0.15);
}

.footer-brand-title {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #fcd34d;
}

.footer-brand-sub {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.65rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #ffffff;
}

.footer-description {
  font-size: 0.85rem;
  line-height: 1.5;
  color: #ad982e;
  margin: 0;
}

.footer-motto {
  display: inline-block;
  font-size: 0.75rem;
  color: #b89830;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.25);
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-weight: 500;
  width: fit-content;
}

.footer-heading {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #fcd34d;
  margin-bottom: 1rem;
  position: relative;
  padding-bottom: 0.4rem;
}

.footer-heading::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 30px;
  height: 2px;
  background-color: #f59e0b;
  border-radius: 2px;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.footer-link {
  color: #ffffff;
  text-decoration: none;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.footer-link:hover {
  color: #fcd34d;
  transform: translateX(4px);
}

.footer-contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(245, 158, 11, 0.2);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
}

.contact-icon {
  font-size: 1rem;
}

.contact-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #cbd5e1;
}

.contact-val {
  font-size: 0.8rem;
  font-weight: 600;
  color: #ffffff;
}

.footer-divider {
  height: 1px;
  width: 100%;
  background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.35), transparent);
  margin-top: 0.5rem;
}

.mycard {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #cbd5e1;
}

@media (min-width: 640px) {
  .mycard {
    flex-direction: row;
  }
}

.copyright-text {
  margin: 0;
  color: #ffffff;
}

.copyright-text strong {
  color: #fcd34d;
}

.footer-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fcd34d;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(245, 158, 11, 0.25);
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #10b981;
  box-shadow: 0 0 6px #10b981;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
