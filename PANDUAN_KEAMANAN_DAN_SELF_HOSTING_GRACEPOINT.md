# PANDUAN LENGKAP KEAMANAN DAN SELF-HOSTING MANDIRI GRACEPOINT
**Dokumentasi Teknis Infrastruktur, Proteksi Siber, dan Hosting Mandiri Berbasis WSL / Linux**

---

## DAFTAR ISI
1. [Ringkasan Arsitektur Sistem](#1-ringkasan-arsitektur-sistem)
2. [Bagian I: Alur Penerapan Keamanan Sistem](#bagian-i-alur-penerapan-keamanan-sistem)
   - [Langkah 1: Pasang Nginx Reverse Proxy & SSL HTTPS](#langkah-1-pasang-nginx-reverse-proxy--ssl-https)
   - [Langkah 2: Aktifkan Fail2ban (Anti-Brute Force Protection)](#langkah-2-aktifkan-fail2ban-anti-brute-force-protection)
   - [Langkah 3: Konfigurasi UFW Firewall (Isolasi Database 5432)](#langkah-3-konfigurasi-ufw-firewall-isolasi-database-5432)
3. [Bagian II: Panduan Hosting Mandiri (Self-Hosting di Komputer / WSL)](#bagian-ii-panduan-hosting-mandiri-self-hosting-di-komputer--wsl)
   - [Skenario 1: Hosting Publik Mandiri via Cloudflare Tunnel (Paling Direkomendasikan)](#skenario-1-hosting-publik-mandiri-via-cloudflare-tunnel)
   - [Skenario 2: Jalur Tradisional Router Port Forwarding & Dynamic DNS](#skenario-2-jalur-tradisional-router-port-forwarding--dynamic-dns)
   - [Skenario 3: Intranet Mandiri Gedung Gereja (Tanpa Internet / DNS & SSL Lokal)](#skenario-3-intranet-mandiri-gedung-gereja)
4. [Tabel Komparasi & Rekomendasi Skenario](#4-tabel-komparasi--rekomendasi-skenario)
5. [Daftar Perintah Pemeliharaan Rutin (Cheat Sheet)](#5-daftar-perintah-pemeliharaan-rutin-cheat-sheet)

---

## 1. RINGKASAN ARSITEKTUR SISTEM

Sistem aplikasi **GracePoint** terdiri atas tiga komponen inti:
* **Frontend:** Vue 3 + Tailwind CSS (`http://127.0.0.1:5173`)
* **Backend:** FastAPI Python (`http://127.0.0.1:8000`)
* **Database:** PostgreSQL (`127.0.0.1:5432`)

### Diagram Alur Keamanan & Lalu Lintas Data:
```
                [ Pengguna / Browser Jemaat & Admin ]
                                  │
                                  │ (HTTPS Port 443 / SSL Terenkripsi)
                                  ▼
           ┌──────────────────────────────────────────────┐
           │           UFW FIREWALL (Lapisan 1)           │
           │  • Port 80 & 443: ALLOW                      │
           │  • Port 5432 (PostgreSQL): DENY DARI LUAR    │
           │  • Port 8000 (FastAPI): ISOLASI INTERNAL     │
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │        NGINX REVERSE PROXY (Lapisan 2)       │
           │  • SSL Termination (HTTP -> HTTPS Redirect)  │
           │  • Rate Limiting (Anti-Spam / Anti-DDoS)     │
           │  • Security Headers (Anti-XSS, Anti-Clickjack│
           └──────────────┬───────────────────┬───────────┘
                          │                   │
           Log Akses & Gagal Login       Meneruskan Request
                          │                   │
                          ▼                   │
           ┌───────────────────────────┐      │
           │    FAIL2BAN (Lapisan 3)   │      │
           │ Otomatis blokir IP liar   │      │
           │ jika gagal login > 5 kali │      │
           └───────────────────────────┘      │
                                              │
                    ┌─────────────────────────┴────────────────────────┐
                    ▼                                                  ▼
     [ Frontend Vue Application ]                       [ Backend API FastAPI ]
       (Port 5173 / Static Files)                            (Port 8000)
                                                                  │
                                                        Koneksi Internal (Localhost)
                                                                  │
                                                                  ▼
                                                      [ Database PostgreSQL ]
                                                            (Port 5432)
```

---

## BAGIAN I: ALUR PENERAPAN KEAMANAN SISTEM

### LANGKAH 1: Pasang Nginx Reverse Proxy & SSL HTTPS

Nginx bertindak sebagai gerbang terdepan yang memisahkan akses internet publik dari server backend Anda. Nginx bertugas mengenkripsi komunikasi data, membatasi laju request (*Rate Limiter*), serta menyaring header HTTP berbahaya.

#### 1.1. Instalasi Nginx di Linux / WSL
Buka terminal Linux Anda dan jalankan:
```bash
sudo apt update
sudo apt install nginx -y
```

#### 1.2. Pembuatan Sertifikat SSL (HTTPS)
* **Untuk Pengujian Mandiri / Lokal (Self-Signed SSL):**
  ```bash
  sudo mkdir -p /etc/nginx/ssl
  sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/gracepoint.key \
    -out /etc/nginx/ssl/gracepoint.crt \
    -subj "/C=ID/ST=Sumatera/L=Padang/O=GracePoint/CN=localhost"
  ```
* **Untuk Domain Publik (Let's Encrypt Otomatis):**
  ```bash
  sudo apt install certbot python3-certbot-nginx -y
  sudo certbot --nginx -d namadomain.com
  ```

#### 1.3. Membuat File Konfigurasi Nginx GracePoint
Buka editor teks nano di terminal:
```bash
sudo nano /etc/nginx/sites-available/gracepoint
```

Salin dan tempel konfigurasi berikut:
```nginx
# 1. Definisi Pembatas Laju Request (Rate Limiting) Anti-Spam / Anti-DDoS
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=15r/s;

# 2. Redirect Otomatis HTTP (Port 80) ke HTTPS (Port 443)
server {
    listen 80;
    server_name localhost;
    return 301 https://$host$request_uri;
}

# 3. Server Utama Berbasis HTTPS (Port 443)
server {
    listen 443 ssl http2;
    server_name localhost;

    # Berkas Sertifikat SSL
    ssl_certificate /etc/nginx/ssl/gracepoint.crt;
    ssl_certificate_key /etc/nginx/ssl/gracepoint.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Header Proteksi Keamanan Siber
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Pencatatan Berkas Log Akses untuk Fail2ban
    access_log /var/log/nginx/gracepoint_access.log;
    error_log /var/log/nginx/gracepoint_error.log;

    # Forwarding Endpoint Backend API (FastAPI Port 8000)
    location /api/ {
        limit_req zone=api_limit burst=25 nodelay;
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Forwarding Aplikasi Frontend (Vue Port 5173)
    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```
*Simpan file dengan menekan `Ctrl + O` lalu `Enter`, kemudian keluar dengan `Ctrl + X`.*

#### 1.4. Mengaktifkan dan Menguji Nginx
```bash
# Buat symlink ke sites-enabled
sudo ln -sf /etc/nginx/sites-available/gracepoint /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Periksa apakah sintaks benar
sudo nginx -t

# Muat ulang service Nginx
sudo systemctl restart nginx
```

---

### LANGKAH 2: Aktifkan Fail2ban (Anti-Brute Force Protection)

Fail2ban membaca berkas log akses Nginx. Apabila ada alamat IP penyerang yang mencoba login berulang kali dan menghasilkan status HTTP `401 Unauthorized` lebih dari 5 kali, Fail2ban akan langsung memblokir alamat IP tersebut melalui firewall kernel Linux.

#### 2.1. Instalasi Fail2ban
```bash
sudo apt install fail2ban -y
```

#### 2.2. Membuat Filter Regex Deteksi Gagal Login
Buat file filter baru:
```bash
sudo nano /etc/fail2ban/filter.d/gracepoint-auth.conf
```
Isi filenya:
```ini
[Definition]
# Deteksi status 401 pada percobaan endpoint auth login
failregex = ^<HOST> - .* "(POST|GET) /api/v1/auth/.* HTTP/.*" 401
ignoreregex =
```
*Simpan file (`Ctrl + O`, `Enter`, `Ctrl + X`).*

#### 2.3. Menyiapkan Konfigurasi Jail
Buat file jail baru:
```bash
sudo nano /etc/fail2ban/jail.d/gracepoint.conf
```
Isi filenya:
```ini
[gracepoint-auth]
enabled = true
port = http,https
filter = gracepoint-auth
logpath = /var/log/nginx/gracepoint_access.log
maxretry = 5
findtime = 600
bantime = 3600
```
> **Aturan Jail di atas:** Apabila terjadi 5 kali kegagalan login (`maxretry = 5`) dalam rentang 10 menit (`findtime = 600`), IP penyerang akan dicekal selama 1 jam (`bantime = 3600`).

#### 2.4. Menjalankan dan Memverifikasi Fail2ban
```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Periksa status perlindungan dan daftar IP yang dicekal:
sudo fail2ban-client status gracepoint-auth
```

---

### LANGKAH 3: Konfigurasi UFW Firewall (Isolasi Database 5432)

Database PostgreSQL menyimpan data sensitif jemaat dan keuangan gereja. Port database `5432` **wajib diisolasi** dari internet publik dan hanya diizinkan berkomunikasi dengan backend internal.

#### 3.1. Instalasi UFW
```bash
sudo apt install ufw -y
```

#### 3.2. Menerapkan Aturan Port yang Ketat
```bash
# 1. Kebijakan default: Tolak semua koneksi luar yang masuk
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 2. Izinkan akses SSH dan Web resmi
sudo ufw allow 22/tcp    # Akses SSH Administrasi
sudo ufw allow 80/tcp    # HTTP Nginx
sudo ufw allow 443/tcp   # HTTPS Nginx

# 3. Kunci rapat port Database PostgreSQL
sudo ufw deny 5432
```

#### 3.3. Mengaktifkan Firewall
```bash
sudo ufw enable
```
*(Tekan `y` saat muncul permintaan konfirmasi).*

#### 3.4. Memeriksa Status Firewall
```bash
sudo ufw status verbose
```
Hasil konfigurasi yang benar akan menunjukkan:
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
5432                       DENY IN     Anywhere
```

---

## BAGIAN II: PANDUAN HOSTING MANDIRI (SELF-HOSTING DI KOMPUTER / WSL)

Anda memiliki komputer sendiri dengan terminal Linux (WSL). Anda **tidak wajib menyewa VPS atau hosting pihak ketiga**. Berikut adalah tiga skenario yang bisa Anda pilih untuk meng-hosting GracePoint secara mandiri:

---

### SKENARIO 1: Hosting Publik Mandiri via Cloudflare Tunnel
*(Sangat Direkomendasikan: 100% Gratis, Tanpa Sewa Server, Tembus CGNAT & Otomatis SSL/DNS Global)*

Kebanyakan koneksi Wi-Fi rumahan (IndiHome, Biznet, FirstMedia, MyRepublic, dll.) menggunakan **CGNAT** di mana IP publik tidak bisa diakses dari luar dan port 80/443 diblokir oleh provider internet. 

Solusi standar industri adalah menggunakan **Cloudflare Tunnel (`cloudflared`)** yang dipasang langsung di terminal Linux/WSL Anda.

#### Keuntungan:
* Aplikasi & Database tetap 100% berada di komputer/WSL Anda sendiri.
* Mendapatkan nama domain publik dengan **HTTPS resmi** gratis sedunia.
* Kebal dari serangan DDoS dan tidak perlu membongkar konfigurasi router Wi-Fi.

#### Langkah Pengerjaan di Terminal Linux (WSL):
1. **Instalasi `cloudflared`:**
   ```bash
   curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
   echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared jammy main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
   sudo apt update && sudo apt install cloudflared -y
   ```

2. **Login Otentikasi Domain:**
   ```bash
   cloudflared tunnel login
   ```
   *(Terminal akan memunculkan URL. Buka URL tersebut di browser untuk mengotorisasi domain Anda).*

3. **Membuat Tunnel Baru:**
   ```bash
   cloudflared tunnel create gracepoint-tunnel
   ```
   *Perintah ini akan menghasilkan file kredensial JSON (misal: `uuid-tunnel.json`).*

4. **Membuat File Konfigurasi Tunnel:**
   ```bash
   nano ~/.cloudflared/config.yml
   ```
   Isi filenya:
   ```yaml
   tunnel: gracepoint-tunnel
   credentials-file: /home/mas_amba/.cloudflared/<UUID-TUNNEL-ANDA>.json

   ingress:
     # Teruskan ke Nginx lokal di komputer Anda
     - hostname: app.domainanda.com
       service: http://localhost:80
     - service: http_status:404
   ```

5. **Mendaftarkan DNS Routing:**
   ```bash
   cloudflared tunnel route dns gracepoint-tunnel app.domainanda.com
   ```

6. **Menjalankan Tunnel:**
   ```bash
   cloudflared tunnel run gracepoint-tunnel
   ```
   *Selesai! Website GracePoint langsung bisa dibuka dari seluruh dunia dengan alamat `https://app.domainanda.com`.*

---

### SKENARIO 2: Jalur Tradisional Router Port Forwarding & Dynamic DNS
*(Murni Memakai IP Modem Rumah)*

Skenario ini digunakan jika provider internet Anda memberikan IP Publik Dinamis (*non-CGNAT*):

#### 1. Meneruskan Port Windows ke WSL2 (Port Proxy)
Karena WSL2 memiliki kartu jaringan virtual tersendiri, buka **PowerShell (Run as Administrator)** di Windows dan jalankan:
```powershell
# Ambil IP WSL Anda terlebih dahulu
wsl hostname -I

# Teruskan Port 80 dan 443 dari Windows ke WSL (Ganti <IP_WSL> dengan IP hasil perintah di atas)
netsh interface portproxy add v4tov4 listenport=80 listenaddress=0.0.0.0 connectport=80 connectaddress=<IP_WSL>
netsh interface portproxy add v4tov4 listenport=443 listenaddress=0.0.0.0 connectport=443 connectaddress=<IP_WSL>
```

#### 2. Konfigurasi Port Forwarding di Modem / Router Wi-Fi
1. Buka browser dan ketik alamat IP router Anda (biasanya `http://192.168.1.1`).
2. Masuk ke menu **Forwarding / Virtual Server / Port Mapping**.
3. Tambahkan aturan baru:
   * **Port Eksternal:** `80` dan `443`
   * **Port Internal:** `80` dan `443`
   * **IP Tujuan:** IP Komputer Windows Anda di jaringan Wi-Fi (misal `192.168.1.15`).

#### 3. Instalasi Dynamic DNS Client (DDNS) di Terminal Linux
Gunakan **ddclient** agar domain selalu diperbarui saat IP modem rumah Anda berganti:
```bash
sudo apt install ddclient -y
sudo nano /etc/ddclient.conf
```
*(Sesuaikan dengan penyedia DDNS seperti DuckDNS, No-IP, atau Cloudflare).*

#### 4. Terbitkan Sertifikat SSL Publik (Certbot)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d domainanda.com
```

---

### SKENARIO 3: Intranet Mandiri Gedung Gereja
*(Khusus Jaringan Wi-Fi Gereja — Tanpa Butuh Internet)*

Skenario ini sangat ideal jika GracePoint ingin dijalankan sebagai sistem internal gereja yang cepat, privat, dan tidak bergantung pada kuota internet publik. Seluruh jemaat atau majelis gereja yang terhubung ke Wi-Fi gedung gereja dapat membuka sistem ini.

#### 1. Menjadikan Linux / WSL sebagai Server DNS Lokal (`dnsmasq`)
```bash
sudo apt install dnsmasq -y
sudo nano /etc/dnsmasq.conf
```
Tambahkan di baris paling bawah:
```ini
# Arahkan domain lokal ke IP komputer server Anda di Wi-Fi gereja
address=/gracepoint.gereja/192.168.1.50
listen-address=127.0.0.1,192.168.1.50
```
Restart service DNS:
```bash
sudo systemctl restart dnsmasq
```

#### 2. Membuat Otoritas Sertifikat SSL Lokal Mandiri (`mkcert`)
Agar browser di HP atau laptop jemaat tidak menampilkan peringatan *"Koneksi Tidak Aman / Not Secure"*, gunakan `mkcert`:
```bash
sudo apt install libnss3-tools -y
curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
chmod +x mkcert-v*-linux-amd64
sudo mv mkcert-v*-linux-amd64 /usr/local/bin/mkcert

# Install Certificate Authority lokal
mkcert -install

# Terbitkan SSL untuk domain intranet gereja
mkcert gracepoint.gereja localhost 127.0.0.1 192.168.1.50
```
Gunakan sertifikat yang dihasilkan (`gracepoint.gereja.pem` dan `gracepoint.gereja-key.pem`) di dalam file konfigurasi Nginx.

*Hasilnya:* Setiap orang di gedung gereja yang mengakses `https://gracepoint.gereja` akan mendapatkan koneksi HTTPS berkecepatan tinggi tanpa kuota internet.

---

## 4. TABEL KOMPARASI & REKOMENDASI SKENARIO

| Fitur / Parameter | Skenario 1 (Cloudflare Tunnel) | Skenario 2 (Port Forwarding & DDNS) | Skenario 3 (Intranet Lokal Gereja) |
| :--- | :--- | :--- | :--- |
| **Akses Luar Internet** | Ya (Sedunia) | Ya (Sedunia) | Tidak (Hanya Area Wi-Fi Gereja) |
| **Ketergantungan Internet** | Wajib ada internet | Wajib ada internet | Tidak butuh internet sama sekali |
| **Sertifikat SSL / HTTPS** | Otomatis & Resmi Sedunia | Let's Encrypt (Resmi) | Mandiri Lokal via `mkcert` |
| **Tembus Blokir CGNAT ISP** | Ya (100% Berhasil) | Tergantung ISP | Tidak terpengaruh ISP |
| **Perlu Atur Router Rumah** | Tidak Perlu | Wajib diatur | Perlu atur DNS IP di router |
| **Biaya Hosting Server** | **Rp 0 (Di Komputer Anda)** | **Rp 0 (Di Komputer Anda)** | **Rp 0 (Di Komputer Anda)** |

---

## 5. DAFTAR PERINTAH PEMELIHARAAN RUTIN (CHEAT SHEET)

Simpan daftar perintah penting ini di terminal Linux Anda untuk memantau kesehatan server GracePoint:

```bash
# 1. Cek Status Web Server Nginx
sudo systemctl status nginx
sudo nginx -t

# 2. Cek Status Keamanan Firewall UFW
sudo ufw status verbose

# 3. Cek Status Fail2ban & IP yang Sedang Diblokir
sudo fail2ban-client status gracepoint-auth

# 4. Membuka Blokir IP Tertentu (Unban IP)
sudo fail2ban-client set gracepoint-auth unbanip <ALAMAT_IP>

# 5. Memantau Log Serangan & Akses Secara Real-Time
sudo tail -f /var/log/nginx/gracepoint_access.log

# 6. Memeriksa Koneksi Port PostgreSQL
sudo ss -tlnp | grep 5432
```

---
*Dokumen ini dibuat khusus untuk arsitektur GracePoint CMS System. Seluruh prosedur di atas dapat dijalankan langsung di lingkungan WSL 2 (Ubuntu) maupun Server Linux Mandiri.*
