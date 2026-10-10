import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_styled_heading(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    run = h.runs[0]
    if level == 1:
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(30, 64, 175) # Dark Blue #1E40AF
        run.bold = True
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(15, 118, 110) # Teal #0F766E
        run.bold = True
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(51, 65, 85) # Slate #334155
        run.bold = True
    return h

def add_callout(doc, title, text, box_type="info"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    
    bg_color = "EFF6FF" # Light Blue
    border_color = "3B82F6" # Blue
    title_color = RGBColor(29, 78, 216)
    prefix = "📌 PENTING: "
    
    if box_type == "warning":
        bg_color = "FFFBEB" # Amber
        border_color = "F59E0B"
        title_color = RGBColor(180, 83, 9)
        prefix = "⚠️ PERHATIAN: "
    elif box_type == "success":
        bg_color = "F0FDF4" # Green
        border_color = "22C55E"
        title_color = RGBColor(21, 128, 61)
        prefix = "💡 TIPS REKOMENDASI: "
    elif box_type == "note":
        bg_color = "F8FAFC" # Slate
        border_color = "64748B"
        title_color = RGBColor(51, 65, 85)
        prefix = "ℹ️ CATATAN: "

    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    cell.width = Inches(6.5)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="none"/>\n'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>\n'
        f'  <w:bottom w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    
    r_title = p.add_run(prefix + title + "\n")
    r_title.bold = True
    r_title.font.size = Pt(10)
    r_title.font.color.rgb = title_color
    
    r_text = p.add_run(text)
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = RGBColor(51, 65, 85)
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_str, caption=None):
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(6)
        p_cap.paragraph_format.space_after = Pt(2)
        r_cap = p_cap.add_run(caption)
        r_cap.bold = True
        r_cap.font.size = Pt(9)
        r_cap.font.color.rgb = RGBColor(71, 85, 105)

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    cell.width = Inches(6.5)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>\n'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>\n'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>\n'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(code_str)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)

def create_table_spec(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header styling
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1E40AF") # Deep blue
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            r.font.size = Pt(9.5)
            r.font.name = "Calibri"

    # Row styling
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].text = str(cell_value)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            for r in p.runs:
                r.font.size = Pt(9)
                r.font.name = "Calibri"
                if c_idx == 0:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(15, 23, 42)

    # Column widths
    if not col_widths:
        if len(headers) == 2:
            col_widths = [2.0, 4.5]
        elif len(headers) == 3:
            col_widths = [1.8, 2.2, 2.5]
        elif len(headers) == 4:
            col_widths = [1.5, 1.4, 1.5, 2.1]
        else:
            col_widths = [6.5 / len(headers)] * len(headers)

    for row in table.rows:
        for idx, width in enumerate(col_widths[:len(headers)]):
            row.cells[idx].width = Inches(width)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(4)
    return table

def build_procedure_document():
    doc = Document()
    
    # Page setup - Margins 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
        # Add footer
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("GracePoint CMS • Panduan Standar Deployment Cloud, DNS & SSL (HTTPS)")
        r_ft.font.name = "Calibri"
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = RGBColor(148, 163, 184)

    # Normal Style font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(10.5)
    font.color.rgb = RGBColor(51, 65, 85)

    # Header Document
    p_tag = doc.add_paragraph()
    p_tag.paragraph_format.space_before = Pt(0)
    p_tag.paragraph_format.space_after = Pt(2)
    r_tag = p_tag.add_run("STANDAR OPERASIONAL PROSEDUR (SOP) & PANDUAN INFRASTRUKTUR CLOUD")
    r_tag.font.size = Pt(9.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = RGBColor(15, 118, 110)

    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(2)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("PROSEDUR DEPLOYMENT WEB CLOUD: VERCEL, CLOUDFLARE SSL, & DATABASE POSTGRESQL REAL")
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(30, 64, 175)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(10)
    run_sub = sub_p.add_run("GracePoint CMS (Frontend Vue 3 + Vite, Backend FastAPI Python, & Neon Cloud PostgreSQL)")
    run_sub.font.size = Pt(11.5)
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Metadata block
    meta_p = doc.add_paragraph()
    meta_p.paragraph_format.space_after = Pt(8)
    r_meta = meta_p.add_run("Versi Dokumen: 1.0  |  Status: Panduan Implementasi Produksi  |  Target: Developer & System Administrator")
    r_meta.font.size = Pt(8.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)

    # Divider
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(12)
    r_div = p_div.add_run("―" * 58)
    r_div.font.color.rgb = RGBColor(203, 213, 225)

    # ==========================================
    # BAB 1: RINGKASAN ARSITEKTUR & STRATEGI
    # ==========================================
    add_styled_heading(doc, "Bab 1: Ringkasan Arsitektur & Strategi Deployment", level=1)
    
    p = doc.add_paragraph()
    p.add_run("Aplikasi ").font.color.rgb = RGBColor(51, 65, 85)
    p.add_run("GracePoint CMS").bold = True
    p.add_run(" merupakan platform manajemen gereja modern multi-aktor yang terdiri dari tiga komponen inti: ")
    p.add_run("Frontend (Vue 3 + Vite + Tailwind CSS)").bold = True
    p.add_run(", ")
    p.add_run("Backend (FastAPI RESTful API + Python)").bold = True
    p.add_run(", serta ")
    p.add_run("Database (PostgreSQL Relasional)").bold = True
    p.add_run(". Agar sistem ini dapat diakses secara publik oleh seluruh pengurus gereja dan jemaat menggunakan protokol aman ")
    p.add_run("HTTPS (SSL)").bold = True
    p.add_run(", diperlukan strategi pemisahan hosting yang optimal dan tepat guna.")

    add_callout(
        doc,
        "Mengapa Frontend dan Backend Dipisah Saat Hosting?",
        "Frontend Vue.js adalah kumpulan berkas statis (HTML, CSS, JS) yang paling optimal disajikan melalui CDN Global seperti Vercel. "
        "Sebaliknya, Backend FastAPI membutuhkan runtime Python yang terus aktif (long-running process), mengelola koneksi database secara kontinu, "
        "dan memproses berkas laporan Excel/PDF. Oleh karena itu, Backend lebih tepat di-host pada platform PaaS (Render / Railway / VPS) "
        "alih-alih serverless function Vercel.",
        box_type="info"
    )

    headers_arch = ["Komponen Sistem", "Teknologi / Stack", "Penyedia Hosting Rekomendasi", "Peran & Fungsi"]
    rows_arch = [
        ["Frontend UI", "Vue 3, Vite, Tailwind, ApexCharts", "Vercel (Gratis / Free Tier)", "Menyajikan tampilan dashboard, form data jemaat, dan antarmuka interaktif melalui CDN global."],
        ["Backend API", "Python 3.11+, FastAPI, SQLAlchemy", "Render.com / Railway / VPS", "Memproses business logic, JWT authentication, RBAC multi-aktor, ekspor PDF/Excel, dan REST API."],
        ["Database", "PostgreSQL 16 (17 Tabel Skema)", "Neon.tech / Supabase", "Menyimpan data persisten secara online (Cloud) dengan enkripsi SSL mode required aktif 24/7."],
        ["Domain & DNS", "Custom Domain (.com / .id / .org)", "Registrar (Cloudflare/Niagahoster)", "Identitas nama website resmi yang mudah diingat publik."],
        ["SSL & Security", "Cloudflare DNS & Proxy CDN", "Cloudflare (Free Tier)", "Menyediakan sertifikat SSL (HTTPS otomatis), mitigasi DDoS, DNS Manager, dan Web Application Firewall."]
    ]
    create_table_spec(doc, headers_arch, rows_arch, col_widths=[1.3, 1.5, 1.5, 2.2])

    p_diag = doc.add_paragraph()
    p_diag.add_run("Berikut adalah diagram alur lalu lintas data sistem dalam lingkungan produksi:")
    
    code_diag = (
        "                    [ PENGGUNA / BROWSER INTERNET ]\n"
        "                                   │\n"
        "                                   │ (HTTPS Port 443 / SSL Cloudflare)\n"
        "                                   ▼\n"
        "             ┌───────────────────────────────────────────┐\n"
        "             │          CLOUDFLARE DNS & PROXY           │\n"
        "             │  • Manajemen DNS (A & CNAME Records)      │\n"
        "             │  • Enkripsi SSL/TLS Otomatis (HTTPS)      │\n"
        "             │  • Proteksi DDoS & Edge Caching CDN       │\n"
        "             └─────────────┬─────────────────────────────┘\n"
        "                           │\n"
        "        ┌──────────────────┴──────────────────┐\n"
        "        │ Request Halaman Web                 │ Request API (/api/v1)\n"
        "        │ (namagereja.com)                    │ (api.namagereja.com)\n"
        "        ▼                                     ▼\n"
        " ┌─────────────────────┐             ┌─────────────────────┐\n"
        " │   VERCEL HOSTING    │             │   RENDER / RAILWAY  │\n"
        " │  Frontend Vue 3     │ ── AJAX ──> │  Backend FastAPI   │\n"
        " │  Output: 'dist/'    │ <─ JSON ─── │  Python 3.11+ / APP │\n"
        " └─────────────────────┘             └──────────┬──────────┘\n"
        "                                                │\n"
        "                                                │ DATABASE_URL\n"
        "                                                │ (SSL Mode Required)\n"
        "                                                ▼\n"
        "                                     ┌─────────────────────┐\n"
        "                                     │   NEON POSTGRESQL   │\n"
        "                                     │  (Cloud Database)   │\n"
        "                                     │  17 Master Tables   │\n"
        "                                     └─────────────────────┘"
    )
    add_code_block(doc, code_diag, caption="Gambar 1.1: Diagram Topologi Jaringan & Komunikasi Antar Layanan")

    # ==========================================
    # BAB 2: PENERAPAN DATABASE CLOUD SECARA REAL
    # ==========================================
    add_styled_heading(doc, "Bab 2: Penerapan Database PostgreSQL Secara Real (Neon Cloud)", level=1)
    
    p = doc.add_paragraph()
    p.add_run("Saat pengujian lokal di komputer pengembang, database berjalan di ")
    p.add_run("localhost:5432").bold = True
    p.add_run(". Namun, server hosting di internet ")
    p.add_run("TIDAK BISA").bold = True
    p.add_run(" mengakses `localhost` komputer Anda. Oleh karena itu, database harus dipindahkan ke penyedia database cloud yang dapat diakses online selama 24 jam penuh.")

    add_styled_heading(doc, "2.1 Keunggulan Menggunakan Neon Serverless PostgreSQL", level=2)
    p_neon = doc.add_paragraph()
    p_neon.add_run("Sesuai dengan rancangan pada dokumentasi ")
    p_neon.add_run("PROSEDUR_BACKEND_DAN_API_GRACEPOINT.md").italic = True
    p_neon.add_run(", platform yang sangat direkomendasikan adalah ")
    p_neon.add_run("Neon (neon.tech)").bold = True
    p_neon.add_run(". Keuntungan utamanya meliputi:")

    neon_points = [
        ("Koneksi Terenkripsi SSL Bawaan: ", "Neon mewajibkan parameter `sslmode=require`, memastikan seluruh lalu lintas query dari backend aman dari penyadapan data."),
        ("Bebas Biaya Perawatan Server: ", "Tidak perlu menginstal sistem operasi Linux, konfigurasi port forwarding router, atau mengelola konsumsi memori container database secara manual."),
        ("Fitur Database Branching: ", "Pengembang dapat membuat clone database (Branch Staging/Dev) secara instan dalam hitungan detik tanpa mengganggu data jemaat di branch Production."),
        ("Tersedia Free Tier Memadai: ", "Memberikan kapasitas penyimpanan 0.5 GB dan komputasi memadai yang sangat cukup untuk menampung data ribuan jemaat, transaksi keuangan, dan presensi.")
    ]
    for title, desc in neon_points:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r1 = bp.add_run(title)
        r1.bold = True
        r1.font.color.rgb = RGBColor(15, 118, 110)
        bp.add_run(desc)

    add_styled_heading(doc, "2.2 Langkah Pembuatan Instance Database di Neon", level=2)
    steps_neon = [
        "1. Buka situs resmi https://neon.tech dan lakukan pendaftaran akun (dapat menggunakan akun GitHub).",
        "2. Buat Project Baru dengan nama 'gracepoint-cms'.",
        "3. Pilih Region server terdekat dengan lokasi gereja, yaitu Asia Pacific / Singapore (ap-southeast-1) agar latensi query minimal.",
        "4. Tentukan nama database (misalnya: gracepoint_db) dan simpan password database yang di-generate oleh sistem.",
        "5. Neon Dashboard akan menampilkan connection string resmi yang siap digunakan."
    ]
    for s in steps_neon:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_after = Pt(2)
        p_s.add_run(s)

    add_styled_heading(doc, "2.3 Format Connection String Neon PostgreSQL", level=2)
    p_cs = doc.add_paragraph("Salin URL koneksi dari Neon dan sesuaikan formatnya pada konfigurasi backend (.env):")
    
    code_neon_env = (
        "# Format Umum Connection String Neon Cloud PostgreSQL\n"
        "DATABASE_URL=\"postgresql://[user]:[password]@[endpoint-id].ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require\"\n\n"
        "# Contoh Nyata:\n"
        "DATABASE_URL=\"postgresql://gracepoint_admin:SecretPass90@ep-cool-butterfly-123456.ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require\""
    )
    add_code_block(doc, code_neon_env, caption="Konfigurasi DATABASE_URL untuk Lingkungan Produksi")

    add_styled_heading(doc, "2.4 Prosedur Impor Skema 17 Tabel ke Cloud", level=2)
    p_imp = doc.add_paragraph()
    p_imp.add_run("Untuk membuat seluruh struktur 17 tabel (meliputi `main_admin`, `users`, `members`, `finances`, `church_inventory`, dll.) beserta trigger dan seed datanya, eksekusi skrip ")
    p_imp.add_run("database/schema_master_gracepoint.sql").bold = True
    p_imp.add_run(" ke Neon:")

    code_imp = (
        "# Metode 1: Menggunakan Terminal CLI (psql)\n"
        "psql \"postgresql://gracepoint_admin:SecretPass90@ep-cool-butterfly-123456.ap-southeast-1.aws.neon.tech/gracepoint_db?sslmode=require\" -f database/schema_master_gracepoint.sql\n\n"
        "# Metode 2: Menggunakan Neon Web SQL Editor (Tanpa Install Tools)\n"
        "# 1. Buka Neon Console -> Masuk ke menu 'SQL Editor'\n"
        "# 2. Buka file database/schema_master_gracepoint.sql di text editor, salin seluruh kodenya\n"
        "# 3. Tempelkan ke Neon SQL Editor dan klik tombol 'Run'\n"
        "# 4. Seluruh 17 tabel, sequence, dan initial seed data otomatis terbentuk di cloud."
    )
    add_code_block(doc, code_imp, caption="Langkah Migrasi Skema ke Database Cloud")

    add_callout(
        doc,
        "Pencadangan (Backup) Data Rutin Dari Cloud",
        "Walaupun Neon memiliki fitur Point-in-Time Restore (PITR), pengembang wajib menjadwalkan backup lokal secara berkala menggunakan perintah:\n"
        "pg_dump \"[DATABASE_URL]\" > backups/neon_backup_$(date +%Y%m%d).sql\n"
        "Berkas backup disimpan secara aman di direktori 'backups/' atau Google Drive gereja.",
        box_type="note"
    )

    # ==========================================
    # BAB 3: DEPLOYMENT BACKEND FASTAPI
    # ==========================================
    add_styled_heading(doc, "Bab 3: Deployment Backend FastAPI ke Cloud PaaS", level=1)
    
    p = doc.add_paragraph()
    p.add_run("Backend GracePoint CMS dibangun dengan ")
    p.add_run("FastAPI, SQLAlchemy, Pydantic, Alembic, dan ReportLab/OpenPyXL").bold = True
    p.add_run(". Tempat hosting terbaik yang ramah pemula, memiliki paket gratis, dan mendukung runtime Python native adalah ")
    p.add_run("Render (render.com)").bold = True
    p.add_run(" atau ")
    p.add_run("Railway (railway.app)").bold = True
    p.add_run(".")

    add_styled_heading(doc, "3.1 Persiapan Berkas Konfigurasi Backend", level=2)
    p_prep = doc.add_paragraph("Pastikan file requirements dan start command telah siap sebelum di-deploy:")
    
    code_be_req = (
        "# Berkas: backend/requirements.txt\n"
        "fastapi>=0.110.0\n"
        "uvicorn[standard]>=0.28.0\n"
        "sqlalchemy>=2.0.28\n"
        "alembic>=1.13.1\n"
        "pydantic[email]>=2.6.4\n"
        "pydantic-settings>=2.2.1\n"
        "python-jose[cryptography]>=3.3.0\n"
        "passlib[bcrypt]>=1.7.4\n"
        "bcrypt>=4.0.0\n"
        "python-multipart>=0.0.9\n"
        "python-dotenv>=1.0.1\n"
        "psycopg2-binary>=2.9.9\n"
        "slowapi>=0.1.9\n"
        "httpx>=0.28.1\n"
        "openpyxl>=3.1.0\n"
        "reportlab>=4.0.0\n"
        "gunicorn>=21.2.0"
    )
    add_code_block(doc, code_be_req, caption="Daftar Dependensi Python untuk Lingkungan Produksi")

    add_styled_heading(doc, "3.2 Langkah Deployment di Render.com", level=2)
    steps_render = [
        "1. Masuk ke https://render.com dan buat akun menggunakan GitHub.",
        "2. Klik 'New +' lalu pilih 'Web Service'.",
        "3. Hubungkan repositori GitHub proyek GracePoint CMS Anda.",
        "4. Isi konfigurasi dasar layanan:",
        "   • Name: gracepoint-backend-api",
        "   • Root Directory: backend",
        "   • Environment: Python 3",
        "   • Build Command: pip install -r requirements.txt",
        "   • Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT",
        "5. Klik tombol 'Create Web Service'. Render akan menginstal seluruh library dan menjalankan aplikasi."
    ]
    for s in steps_render:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_after = Pt(2)
        p_s.add_run(s)

    add_styled_heading(doc, "3.3 Pengaturan Environment Variables Backend di Render", level=2)
    p_env = doc.add_paragraph("Masuk ke tab 'Environment' pada dashboard Render dan tambahkan variabel-variabel berikut:")

    headers_env = ["Key (Nama Variabel)", "Contoh Nilai Produksi", "Keterangan"]
    rows_env = [
        ["DATABASE_URL", "postgresql://user:pass@ep-cool.neon.tech/gracepoint_db?sslmode=require", "Connection string database Neon Cloud yang telah dibuat pada Bab 2."],
        ["SECRET_KEY", "b3a9c78d4e5f601278ab9cde45f0123456789abcdef", "Kunci rahasia unik berkekuatan tinggi untuk enkripsi token JWT."],
        ["ALGORITHM", "HS256", "Algoritma hash token JWT."],
        ["ACCESS_TOKEN_EXPIRE_MINUTES", "10080", "Masa berlaku token login (10080 menit = 7 hari)."],
        ["DEBUG", "False", "Wajib disetel False pada server produksi demi keamanan."],
        ["BACKEND_CORS_ORIGINS", "[\"https://namagereja.com\", \"https://www.namagereja.com\"]", "Daftar domain frontend resmi yang diizinkan mengakses API."]
    ]
    create_table_spec(doc, headers_env, rows_env, col_widths=[2.0, 2.7, 1.8])

    add_styled_heading(doc, "3.4 Verifikasi Hasil Deployment Backend", level=2)
    p_ver = doc.add_paragraph()
    p_ver.add_run("Setelah proses deploy selesai, Render akan memberikan URL publik seperti: ")
    p_ver.add_run("https://gracepoint-backend-api.onrender.com").bold = True
    p_ver.add_run(". Uji endpoint berikut di browser:")

    be_tests = [
        ("Akses Root: ", "https://gracepoint-backend-api.onrender.com/ -> Menampilkan JSON pesan selamat datang."),
        ("Akses Swagger UI: ", "https://gracepoint-backend-api.onrender.com/docs -> Menampilkan dokumentasi interaktif seluruh API."),
        ("Akses Endpoint v1: ", "https://gracepoint-backend-api.onrender.com/api/v1/churches -> Menampilkan data gereja.")
    ]
    for title, desc in be_tests:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(2)
        r1 = bp.add_run(title)
        r1.bold = True
        r1.font.color.rgb = RGBColor(15, 118, 110)
        bp.add_run(desc)

    # ==========================================
    # BAB 4: DEPLOYMENT FRONTEND VUE.JS DI VERCEL
    # ==========================================
    add_styled_heading(doc, "Bab 4: Deployment Frontend Vue.js ke Vercel", level=1)
    
    p = doc.add_paragraph()
    p.add_run("Frontend GracePoint CMS berada di folder ")
    p.add_run("frontend/cms-project/").bold = True
    p.add_run(" dan dibangun dengan framework ")
    p.add_run("Vite + Vue 3").bold = True
    p.add_run(". Vercel adalah tempat terbaik untuk meng-host frontend ini karena kecepatannya, gratis, dan otomatis rebuild saat kode di-update di GitHub.")

    add_styled_heading(doc, "4.1 Menyiapkan Berkas Routing SPA (vercel.json)", level=2)
    p_spa = doc.add_paragraph()
    p_spa.add_run("Aplikasi Vue menggunakan ")
    p_spa.add_run("Vue Router (HTML5 History Mode)").bold = True
    p_spa.add_run(". Jika pengguna me-refresh halaman seperti `/inventory` atau `/keuangan`, server hosting dapat memunculkan pesan ")
    p_spa.add_run("404 Not Found").bold = True
    p_spa.add_run(" jika tidak dikonfigurasi. Untuk mencegahnya, buat file ")
    p_spa.add_run("frontend/cms-project/vercel.json").italic = True
    p_spa.add_run(":")

    code_vjson = (
        "{\n"
        "  \"rewrites\": [\n"
        "    {\n"
        "      \"source\": \"/(.*)\",\n"
        "      \"destination\": \"/index.html\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )
    add_code_block(doc, code_vjson, caption="Berkas frontend/cms-project/vercel.json untuk Penanganan Routing SPA")

    add_styled_heading(doc, "4.2 Langkah Import Proyek ke Dashboard Vercel", level=2)
    steps_vercel = [
        "1. Kunjungi https://vercel.com dan masuk menggunakan akun GitHub Anda.",
        "2. Klik tombol 'Add New...' -> 'Project'.",
        "3. Pilih repositori GitHub proyek GracePoint CMS Anda dan klik 'Import'.",
        "4. Konfigurasi Pengaturan Project (PENTING):",
        "   • Project Name: gracepoint-frontend",
        "   • Framework Preset: Vite (akan terdeteksi secara otomatis)",
        "   • Root Directory: Klik 'Edit' lalu pilih folder 'frontend/cms-project'",
        "   • Build Command: npm run build",
        "   • Output Directory: dist",
        "5. Tambahkan Environment Variable pada bagian 'Environment Variables':",
        "   • Key: VITE_API_BASE_URL",
        "   • Value: https://api.namagereja.com/api/v1 (atau https://gracepoint-backend-api.onrender.com/api/v1 jika belum pasang domain)",
        "6. Klik tombol 'Deploy'. Vercel akan meng-compile aplikasi Vue dan mempublikasikannya ke domain sementara, misalnya: https://gracepoint-frontend.vercel.app."
    ]
    for s in steps_vercel:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_after = Pt(2)
        p_s.add_run(s)

    # ==========================================
    # BAB 5: DOMAIN, DNS, & CLOUDFLARE SSL (HTTPS)
    # ==========================================
    add_styled_heading(doc, "Bab 5: Konfigurasi Domain, DNS, & Cloudflare SSL (HTTPS)", level=1)
    
    p = doc.add_paragraph()
    p.add_run("Bab ini menjawab pertanyaan bagaimana cara kerja ")
    p.add_run("DNS").bold = True
    p.add_run(", bagaimana menghubungkan nama domain gereja (misalnya `namagereja.com`), dan bagaimana mendapatkan protokol keamanan gembok hijau ")
    p.add_run("HTTPS (SSL)").bold = True
    p.add_run(" secara otomatis tanpa perlu membeli sertifikat SSL manual.")

    add_styled_heading(doc, "5.1 Pengertian Konseptual DNS & Catatan Records", level=2)
    p_dns = doc.add_paragraph("DNS bekerja seperti buku telepon yang mengarahkan nama domain ke alamat server sebenarnya:")

    headers_dns = ["Tipe DNS Record", "Nama Host / Subdomain", "Fungsi & Penerapan pada GracePoint CMS"]
    rows_dns = [
        ["CNAME", "@ (Root Domain)", "Mengarahkan nama domain utama (misal: namagereja.com) ke server Vercel (cname.vercel-dns.com)."],
        ["CNAME", "www", "Mengarahkan subdomain www.namagereja.com agar selalu sinkron dengan domain utama di Vercel."],
        ["CNAME", "api", "Mengarahkan subdomain api.namagereja.com ke server backend di Render (gracepoint-backend-api.onrender.com)."],
        ["A Record", "Subdomain / Root", "Mengarahkan domain secara langsung ke IP Address statis (hanya digunakan jika memakai VPS Linux sendiri)."]
    ]
    create_table_spec(doc, headers_dns, rows_dns, col_widths=[1.5, 1.8, 3.2])

    add_styled_heading(doc, "5.2 Langkah 1: Pendaftaran Domain & Penghubungan ke Cloudflare", level=2)
    steps_cf = [
        "1. Beli nama domain di penyedia registrar domain (misalnya: Niagahoster, Domainesia, Namecheap, atau Cloudflare Registrar). Contoh nama: 'gracepointpadang.org' atau 'namagereja.com'.",
        "2. Buat akun gratis di https://cloudflare.com.",
        "3. Klik 'Add a Site' di dashboard Cloudflare, lalu masukkan nama domain yang telah Anda beli.",
        "4. Pilih paket 'Free' ($0 / Forever Free).",
        "5. Cloudflare akan memberikan 2 alamat Name Server resmi, contohnya:\n   • amir.ns.cloudflare.com\n   • chloe.ns.cloudflare.com",
        "6. Buka panel kontrol tempat Anda membeli domain (Registrar) -> Masuk ke menu 'Name Servers' / 'DNS Management' -> Ganti Name Server bawaan registrar dengan 2 Name Server Cloudflare tersebut.",
        "7. Tunggu proses propagasi DNS (umumnya 5 menit hingga maksimal 2 jam). Status di Cloudflare akan berubah menjadi 'Active'."
    ]
    for s in steps_cf:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_after = Pt(2)
        p_s.add_run(s)

    add_styled_heading(doc, "5.3 Langkah 2: Mengisi Catatan DNS (DNS Records) di Cloudflare", level=2)
    p_rec = doc.add_paragraph("Masuk ke menu 'DNS' -> 'Records' di Cloudflare, lalu buat catatan berikut:")

    headers_cf_rec = ["Type", "Name", "Target (Points to)", "Proxy Status", "Tujuan"]
    rows_cf_rec = [
        ["CNAME", "@", "cname.vercel-dns.com", "Proxied (Awan Oranye)", "Akses Website Frontend Utama (https://namagereja.com)"],
        ["CNAME", "www", "cname.vercel-dns.com", "Proxied (Awan Oranye)", "Akses Alias www (https://www.namagereja.com)"],
        ["CNAME", "api", "gracepoint-backend-api.onrender.com", "Proxied (Awan Oranye)", "Akses Backend API (https://api.namagereja.com)"]
    ]
    create_table_spec(doc, headers_cf_rec, rows_cf_rec, col_widths=[1.0, 0.8, 2.3, 1.3, 1.1])

    add_callout(
        doc,
        "Apa Arti Ikon 'Proxied' (Awan Oranye ☁️) di Cloudflare?",
        "Status 'Proxied' berarti setiap pengunjung yang mengakses website Anda tidak langsung menghubungi server Vercel atau Render, "
        "melainkan melewati jaringan pelindung Cloudflare terlebih dahulu. Manfaatnya:\n"
        "1. IP server asli Anda tersembunyi dari hacker.\n"
        "2. Sertifikat SSL/HTTPS diaktifkan secara otomatis tanpa biaya.\n"
        "3. Bebas dari serangan DDoS dan spam bot.",
        box_type="success"
    )

    add_styled_heading(doc, "5.4 Langkah 3: Mengaktifkan Enkripsi SSL/TLS (HTTPS) Otomatis", level=2)
    p_ssl = doc.add_paragraph("Agar website langsung dapat diakses dalam format https:// dan muncul lambang gembok aman:")
    steps_ssl = [
        "1. Masuk ke dashboard Cloudflare -> Pilih menu 'SSL/TLS'.",
        "2. Pada opsi Encryption Mode, pilih: 'Full' (atau 'Full (Strict)'). Mode ini mengenkripsi data secara end-to-end dari browser ke Cloudflare, serta dari Cloudflare ke server hosting.",
        "3. Buka sub-menu 'Edge Certificates':",
        "   • Aktifkan opsi 'Always Use HTTPS' (Menjadi ON). Opsi ini otomatis mengalihkan pengguna yang mengetik http:// menjadi https://.",
        "   • Aktifkan opsi 'Automatic HTTPS Rewrites' (Menjadi ON). Mencegah peringatan Mixed Content pada gambar dan aset web.",
        "   • Aktifkan opsi 'Minimum TLS Version': Pilih TLS 1.2 (Standar industri keamanan tertinggi)."
    ]
    for s in steps_ssl:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_after = Pt(2)
        p_s.add_run(s)

    # ==========================================
    # BAB 6: SINKRONISASI CORS & PENGUJIAN AKHIR
    # ==========================================
    add_styled_heading(doc, "Bab 6: Sinkronisasi CORS & Pengujian Akhir (End-to-End)", level=1)
    
    p = doc.add_paragraph()
    p.add_run("Setelah domain kustom ber-SSL aktif, langkah terakhir yang sangat krusial adalah menyinkronkan ")
    p.add_run("CORS (Cross-Origin Resource Sharing)").bold = True
    p.add_run(" pada backend FastAPI agar mengizinkan panggilan data dari domain baru.")

    add_styled_heading(doc, "6.1 Update CORS di Backend Render", level=2)
    p_cors = doc.add_paragraph("Buka Render Dashboard -> Environment Variables -> Edit `BACKEND_CORS_ORIGINS` menjadi:")
    
    code_cors = (
        "# Format Nilai Variabel BACKEND_CORS_ORIGINS di Server Produksi\n"
        "BACKEND_CORS_ORIGINS=[\"https://namagereja.com\",\"https://www.namagereja.com\",\"http://localhost:5173\"]"
    )
    add_code_block(doc, code_cors, caption="Konfigurasi CORS Resmi Domain Produksi")

    add_styled_heading(doc, "6.2 Update API Base URL di Frontend Vercel", level=2)
    p_fe_url = doc.add_paragraph("Buka Vercel Dashboard -> Settings -> Environment Variables -> Edit `VITE_API_BASE_URL`:")
    
    code_fe_url = (
        "# Nilai Environment Variable VITE_API_BASE_URL di Vercel\n"
        "VITE_API_BASE_URL=https://api.namagereja.com/api/v1"
    )
    add_code_block(doc, code_fe_url, caption="Konfigurasi Endpoint API Frontend")
    
    p_note_reb = doc.add_paragraph()
    p_note_reb.add_run("Catatan: ").bold = True
    p_note_reb.add_run("Setelah mengubah Environment Variable di Vercel, lakukan 'Redeploy' pada tab Deployments agar Vite meng-compile ulang berkas dengan URL API yang baru.")

    add_styled_heading(doc, "6.3 Lembar Checklist Pengujian Sistem Produksi", level=2)
    headers_check = ["Modul / Fitur", "Kondisi yang Diuji", "Hasil yang Diharapkan", "Status"]
    rows_check = [
        ["Keamanan SSL", "Akses website via http://namagereja.com", "Otomatis redirect ke https://namagereja.com berstatus gembok hijau.", "Wajib Lulus"],
        ["Autentikasi", "Login Super Admin & Church Admin", "Token JWT tersimpan di LocalStorage & berhasil masuk ke dashboard.", "Wajib Lulus"],
        ["Manajemen Jemaat", "Tambah, ubah, dan hapus biodata anggota jemaat", "Data tersimpan permanen di Neon Cloud PostgreSQL.", "Wajib Lulus"],
        ["Keuangan Gereja", "Input kas masuk/keluar & cetak laporan", "Laporan PDF (ReportLab) dan Excel (OpenPyXL) terunduh sempurna.", "Wajib Lulus"],
        ["Presensi QR Code", "Scan QR Token presensi ibadah jemaat", "Kehadiran tercatat otomatis pada tabel attendances.", "Wajib Lulus"],
        ["Routing SPA", "Refresh halaman di /inventory atau /keuangan", "Halaman tetap terbuka normal tanpa muncul error 404.", "Wajib Lulus"]
    ]
    create_table_spec(doc, headers_check, rows_check, col_widths=[1.5, 2.0, 2.0, 1.0])

    # ==========================================
    # BAB 7: TROUBLESHOOTING & FAQ
    # ==========================================
    add_styled_heading(doc, "Bab 7: Panduan Troubleshooting & FAQ", level=1)
    
    faqs = [
        ("Tanya: Mengapa muncul pesan error 'Blocked by CORS policy' di console browser?",
         "Jawab: Hal ini terjadi karena domain frontend (misal: https://namagereja.com) belum didaftarkan pada list BACKEND_CORS_ORIGINS di backend/app/core/config.py atau di Environment Variable Render. Tambahkan domain tersebut dan restart web service backend."),
        ("Tanya: Mengapa saat halaman di-refresh di Vercel muncul tulisan 404 Page Not Found?",
         "Jawab: Ini adalah perilaku khas aplikasi Single Page Application (SPA). Pastikan Anda telah membuat berkas 'frontend/cms-project/vercel.json' yang berisi aturan penulisan ulang rewrite ke '/index.html' sesuai panduan Bab 4.1."),
        ("Tanya: Apakah database Neon bisa mati jika laptop pengembang dimatikan?",
         "Jawab: Tidak. Database Neon berada di server cloud AWS Singapura yang beroperasi 24 jam sehari, 7 hari seminggu. Website dan database Anda akan tetap aktif meskipun komputer lokal Anda mati total."),
        ("Tanya: Bisakah saya mencoba sistem ini secara online tanpa membeli domain terlebih dahulu?",
         "Jawab: Sangat bisa! Anda dapat menggunakan domain gratis bawaan terlebih dahulu, yaitu: Frontend di 'https://gracepoint-frontend.vercel.app' dan Backend di 'https://gracepoint-backend-api.onrender.com'. Keduanya sudah otomatis memiliki sertifikat SSL https://.")
    ]
    for q, a in faqs:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(4)
        p_q.paragraph_format.space_after = Pt(1)
        r_q = p_q.add_run(q)
        r_q.bold = True
        r_q.font.color.rgb = RGBColor(30, 64, 175)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_after = Pt(6)
        r_a = p_a.add_run(a)
        r_a.font.size = Pt(9.5)

    # Save document
    output_filename = "PROSEDUR_DEPLOYMENT_CLOUD_VERCEL_CLOUDFLARE_DAN_DATABASE.docx"
    doc.save(output_filename)
    print(f"Document saved successfully: {output_filename}")

if __name__ == "__main__":
    build_procedure_document()
