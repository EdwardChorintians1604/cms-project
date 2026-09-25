<script setup>
import { RouterLink } from 'vue-router'
import Main_Admin_Navbar from '@/components/Main_Administrator/Main_Admin_Navbar.vue'
import Main_Admin_Sidebar from '@/components/Main_Administrator/Main_Admin_Sidebar.vue'
</script>

<template>
  <div class="min-h-screen bg-[var(--theme-bg-primary)] text-[var(--theme-text-primary)] flex flex-col font-sans selection:bg-amber-500/30 selection:text-amber-200 transition-colors duration-300">
    <Main_Admin_Navbar />
    
    <!-- Sidebar Superadmin: Posisi di atas navbar (z-[60]) menjangkau dari paling atas layar (top-0) -->
    <Main_Admin_Sidebar />

    <div class="flex flex-1 relative items-start min-w-0">
      <!-- Area Konten Utama -->
      <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full transition-all duration-300 min-w-0">
        <slot />
      </main>
    </div>

    <!-- Footer di Dasar Halaman (Kompatibel & Selaras dengan HomeView / HomeLayout) -->
    <footer class="myfooter">
      <div class="footer-container">
        <!-- Main Footer Grid -->
        <div class="footer-grid">
          <!-- Col 1: Brand & Motto -->
          <div class="footer-col footer-col-brand">
            <div class="footer-brand flex items-center gap-3 mb-1">
              <div class="footer-logo">
                <img src="@/assets/images/GracePoint.png" alt="GracePoint Logo" class="w-full h-full object-cover">
              </div>
              <div class="flex flex-col">
                <span class="footer-brand-title">GRACEPOINT</span>
                <span class="footer-brand-sub">Platform Pelayanan Gereja</span>
              </div>
            </div>
            <p class="footer-description">
              Sistem informasi terpadu untuk pengurusan administrasi, pendataan jemaat, dan koordinasi pelayanan gereja yang transparan, modern, dan akuntabel.
            </p>
            <div class="footer-motto">
              <span>✝ Soli Deo Gloria</span> — Melayani dengan Kasih &amp; Kesetiaan
            </div>
          </div>

          <!-- Col 2: Navigasi Cepat Superadmin -->
          <div class="footer-col">
            <h4 class="footer-heading">Navigasi Utama</h4>
            <ul class="footer-links">
              <li><RouterLink to="/dashboard" class="footer-link">Console System Admin</RouterLink></li>
              <li><RouterLink to="/main_admin_calendar" class="footer-link">Kalender &amp; Agenda</RouterLink></li>
              <li><RouterLink to="/data-gereja" class="footer-link">Manajemen Data Gereja</RouterLink></li>
              <li><RouterLink to="/cabang-gereja" class="footer-link">Daftar Cabang Gereja</RouterLink></li>
              <li><RouterLink to="/data-pengguna" class="footer-link">Biodata Jemaat</RouterLink></li>
            </ul>
          </div>

          <!-- Col 3: Portal & Keamanan -->
          <div class="footer-col">
            <h4 class="footer-heading">Infrastruktur &amp; Sistem</h4>
            <ul class="footer-links">
              <li><RouterLink to="/server-postgresql" class="footer-link">Server PostgreSQL</RouterLink></li>
              <li><RouterLink to="/audit-it" class="footer-link">Audit IT &amp; Aktivitas</RouterLink></li>
              <li><RouterLink to="/backup-database" class="footer-link">Backup &amp; Restore</RouterLink></li>
              <li><RouterLink to="/hari-besar" class="footer-link">Kalender Liturgi Publik</RouterLink></li>
              <li><RouterLink to="/" class="footer-link">Halaman Beranda</RouterLink></li>
            </ul>
          </div>

          <!-- Col 4: Status Infrastruktur & Dukungan Kontak -->
          <div class="footer-col">
            <h4 class="footer-heading">Status &amp; Kontak</h4>
            <div class="footer-contact-info">
              <div class="contact-item">
                <span class="contact-icon">⚡</span>
                <div>
                  <div class="contact-label">PostgreSQL Engine</div>
                  <div class="contact-val">Port 5432 • Cloud Active</div>
                </div>
              </div>
              <div class="contact-item">
                <span class="contact-icon">🛡️</span>
                <div>
                  <div class="contact-label">Hak Akses Sistem</div>
                  <div class="contact-val">Superadmin Infrastructure</div>
                </div>
              </div>
              <div class="contact-item">
                <span class="contact-icon">💬</span>
                <div>
                  <div class="contact-label">Helpdesk Dukungan IT</div>
                  <div class="contact-val">support@gracepoint.org</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Elegant Divider -->
        <div class="footer-divider"></div>

        <!-- Bottom Copyright Bar -->
        <div class="mycard">
          <p class="copyright-text">
            &copy; 2026 <strong>GracePoint</strong> — Sistem Informasi Gereja &amp; Pelayanan Jemaat.
          </p>
          <div class="footer-status-badge">
            <span class="status-dot"></span>
            <span>GracePoint Infrastructure Console v1.0 • System Online</span>
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
  padding: 3rem 1.5rem 1.5rem 1.5rem;
  color: #e2e8f0;
  font-family: Inter, system-ui, -apple-system, sans-serif;
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

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
</style>
