<script setup>
import { onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import User_Navbar from '@/components/User/User_Navbar.vue'
import User_Sidebar from '@/components/User/User_Sidebar.vue'
import AOS from 'aos'

onMounted(() => {
  nextTick(() => {
    try { AOS.refresh() } catch (e) {}
  })
})
</script>

<template>
  <div class="min-h-screen bg-[var(--theme-bg-primary)] text-[var(--theme-text-primary)] flex flex-col font-sans selection:bg-amber-500/30 selection:text-amber-200 transition-colors duration-300">
    <!-- Navbar Sticky -->
    <User_Navbar />

    <!-- Sidebar: Self-contained, fixed overlay dari top-0 (z-[60]), mencakup navbar -->
    <User_Sidebar />

    <div class="flex flex-1 relative items-start min-w-0">
      <!-- Area Konten Utama -->
      <main class="flex-1 min-w-0 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full transition-all duration-300">
        <slot />
      </main>
    </div>

    <!-- Footer Premium -->
    <footer class="myfooter">
      <div class="footer-container">
        <div class="footer-grid">

          <!-- Col 1: Brand & Motto -->
          <div class="footer-col footer-col-brand">
            <div class="footer-brand">
              <div class="footer-logo">
                <img src="@/assets/images/GracePoint.png" alt="GracePoint Logo" class="w-full h-full object-cover">
              </div>
              <div class="flex flex-col">
                <span class="footer-brand-title">GRACEPOINT</span>
                <span class="footer-brand-sub">Platform Pelayanan Gereja</span>
              </div>
            </div>
            <p class="footer-description">
              Portal jemaat GracePoint untuk mengakses warta gereja, jadwal ibadah, informasi pelayanan, dan komunitas yang hidup dalam kasih Kristus.
            </p>
            <div class="footer-motto">
              <span>✝ Soli Deo Gloria</span> — Hadir, Bertumbuh &amp; Melayani
            </div>
          </div>

          <!-- Col 2: Navigasi Jemaat -->
          <div class="footer-col">
            <h4 class="footer-heading">Navigasi Portal</h4>
            <ul class="footer-links">
              <li><RouterLink to="/dashboard-user" class="footer-link">Beranda Jemaat</RouterLink></li>
              <li><RouterLink to="/berita-jemaat" class="footer-link">Warta &amp; Berita Jemaat</RouterLink></li>
              <li><RouterLink to="/informasi-pelayanan" class="footer-link">Informasi Pelayanan</RouterLink></li>
              <li><RouterLink to="/hari-besar" class="footer-link">Kalender Hari Besar</RouterLink></li>
              <li><RouterLink to="/dashboard-user#agenda" class="footer-link">Jadwal Ibadah</RouterLink></li>
            </ul>
          </div>

          <!-- Col 3: Layanan Gereja -->
          <div class="footer-col">
            <h4 class="footer-heading">Layanan Gereja</h4>
            <ul class="footer-links">
              <li><RouterLink to="/dashboard-user#profil" class="footer-link">Profil &amp; Keanggotaan</RouterLink></li>
              <li><RouterLink to="/dashboard-user#doa" class="footer-link">Pokok Doa &amp; Konseling</RouterLink></li>
              <li><RouterLink to="/sejarah-gereja" class="footer-link">Sejarah Gereja</RouterLink></li>
              <li><RouterLink to="/" class="footer-link">Halaman Beranda Publik</RouterLink></li>
            </ul>
          </div>

          <!-- Col 4: Info Kontak & Ibadah -->
          <div class="footer-col">
            <h4 class="footer-heading">Jadwal &amp; Kontak</h4>
            <div class="footer-contact-info">
              <div class="contact-item">
                <span class="contact-icon">⛪</span>
                <div>
                  <div class="contact-label">Ibadah Raya Minggu</div>
                  <div class="contact-val">Sesi I: 08:00 | Sesi II: 17:00</div>
                </div>
              </div>
              <div class="contact-item">
                <span class="contact-icon">🕊️</span>
                <div>
                  <div class="contact-label">Doa Jemaat</div>
                  <div class="contact-val">Rabu 19:00 · Ruang Doa</div>
                </div>
              </div>
              <div class="contact-item">
                <span class="contact-icon">📞</span>
                <div>
                  <div class="contact-label">Sekretariat Gereja</div>
                  <div class="contact-val">(021) 555-0199</div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Divider -->
        <div class="footer-divider"></div>

        <!-- Bottom Copyright -->
        <div class="mycard">
          <p class="copyright-text">
            &copy; 2026 <strong>GracePoint</strong> — Sistem Informasi Gereja &amp; Pelayanan Jemaat.
          </p>
          <div class="footer-status-badge">
            <span class="status-dot"></span>
            <span>GracePoint Church Portal v1.0 • Portal Aktif</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&display=swap');

html {
  scroll-behavior: smooth;
}

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
    grid-template-columns: 1.8fr 1fr 1fr 1.3fr;
  }
}

.footer-col-brand {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
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
  flex-shrink: 0;
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
  color: #965d08;
  margin: 0;
}

.footer-motto {
  display: inline-block;
  font-size: 0.75rem;
  color: #a98409;
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
</style>
