import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import shutil
import os

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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
        run.font.color.rgb = RGBColor(30, 64, 175) # Dark Blue
        run.bold = True
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(15, 118, 110) # Teal
        run.bold = True
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(51, 65, 85) # Slate
        run.bold = True
    return h

def create_table_spec(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header styling
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1E40AF") # Deep blue
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            r.font.size = Pt(10)
            r.font.name = "Calibri"

    # Row styling
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].text = str(cell_value)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            for r in p.runs:
                r.font.size = Pt(9.5)
                r.font.name = "Calibri"
                if c_idx == 0:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(15, 23, 42)

    # Column widths
    if not col_widths:
        if len(headers) == 4:
            col_widths = [1.8, 1.4, 1.5, 2.3]
        elif len(headers) == 3:
            col_widths = [2.0, 2.0, 3.0]
        else:
            col_widths = [2.0, 5.0]

    for row in table.rows:
        for idx, width in enumerate(col_widths[:len(headers)]):
            row.cells[idx].width = Inches(width)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table

def generate_updated_docx():
    doc = Document()
    
    # Page setup - Margins 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Normal Style font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(51, 65, 85)

    # Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("PERANCANGAN DBMS & INTEGRASI TABEL CMS GRACEPOINT")
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(30, 64, 175)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(12)
    run_sub = sub_p.add_run("Spesifikasi Struktur Database, Record Field, Primary Key (PK), & Foreign Key (FK)")
    run_sub.font.size = Pt(12)
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Divider line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(12)
    r_div = p_div.add_run("_________________________________________________________________________________")
    r_div.font.color.rgb = RGBColor(203, 213, 225)

    # 1. Pendahuluan & Penjelasan Relasi
    add_styled_heading(doc, "1. Pendahuluan & Penjelasan Integrasi Relasi Tabel", level=1)
    
    p = doc.add_paragraph()
    p.add_run("Dokumen ini merupakan pembaruan resmi spesifikasi database ")
    p.add_run("CMS_Database GracePoint").bold = True
    p.add_run(". Struktur tabel tetap memperthankan 11 entitas sesuai dengan rancangan asli Anda, dengan penambahan kejelasan peran ")
    p.add_run("Primary Key (PK)").bold = True
    p.add_run(" dan ")
    p.add_run("Foreign Key (FK)").bold = True
    p.add_run(" untuk memastikan seluruh tabel terintegrasi secara sempurna tanpa redundansi data.")

    headers_rel = ["Prinsip Integrasi", "Penjelasan Teknis DBMS", "Manfaat pada GracePoint CMS"]
    rows_rel = [
        ["Primary Key (PK)", "Identitas unik untuk setiap baris record pada suatu tabel.", "Menjamin setiap data (Gereja, User, Ibadah) memiliki ID tunggal yang tidak bisa tertukar."],
        ["Foreign Key (FK)", "Kunci penghubung dari tabel anak yang menunjuk ke Primary Key di tabel induk.", "Menghubungkan data Ibadah, Pelayanan, Keuangan, dan Berita langsung ke ID Gereja (Church_ID)."],
        ["Integritas Data (JOIN)", "Pengambilan data gabungan otomatis melalui query SQL/ORM tanpa perlu menduplikasi teks.", "Nama Gereja dan Alamat Gereja cukup disimpan 1x di tabel Church. Tabel Worship & Services tinggal mengambilnya via relasi FK."]
    ]
    create_table_spec(doc, headers_rel, rows_rel, [1.8, 2.6, 2.6])

    # 2. Detail 11 Tabel
    add_styled_heading(doc, "2. Spesifikasi Detail 11 Tabel & Struktur Relasi", level=1)

    tables_spec = [
        {
            "name": "1. Tabel: Main_Admin",
            "desc": "Bagian admin utama sistem yang memegang kewenangan tertinggi (Superadmin / Developer).",
            "pk": "Development_ID",
            "fk": "Tidak ada (Tabel Induk Utama)",
            "fields": [
                ["Development_ID", "INTEGER / UUID", "PRIMARY KEY, Autoincrement", "ID Unik Developer / Superadmin"],
                ["Email", "VARCHAR(255)", "Unique, Not Null", "Email login admin utama"],
                ["Username", "VARCHAR(100)", "Unique, Not Null", "Username unik admin utama"],
                ["Password", "VARCHAR(255)", "Not Null", "Hashed password terenkripsi"],
                ["Dev_Token", "VARCHAR(255)", "Nullable", "Token akses/API developer"]
            ],
            "relation_note": "Mengelola data Church dan memiliki kewenangan mengonfigurasi seluruh sistem CMS."
        },
        {
            "name": "2. Tabel: Church_Admin",
            "desc": "Bagian yang berisi data pengurus / admin untuk tiap-tiap gereja lokal.",
            "pk": "Admin_ID",
            "fk": "Church_ID -> Menunjuk ke Church(Church_ID)",
            "fields": [
                ["Admin_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Admin Gereja"],
                ["Church_ID", "INTEGER", "FOREIGN KEY, Not Null", "Kunci penghubung ke tabel Church"],
                ["Nama_Pengurus", "VARCHAR(150)", "Not Null", "Nama pengurus / admin gereja"],
                ["Email_Gereja", "VARCHAR(255)", "Unique, Not Null", "Email resmi admin gereja"],
                ["Nomor_WhatsApp", "VARCHAR(20)", "Nullable", "Nomor kontak WhatsApp admin"],
                ["Password", "VARCHAR(255)", "Not Null", "Hashed password login admin gereja"]
            ],
            "relation_note": "Terhubung ke Church_ID sehingga tiap Admin Gereja hanya dapat mengelola data gerejanya sendiri."
        },
        {
            "name": "3. Tabel: User (Jemaat)",
            "desc": "Bagian yang berisi tentang data-data jemaat gereja.",
            "pk": "User_ID",
            "fk": "Church_ID -> Menunjuk ke Church(Church_ID) [Nullable]",
            "fields": [
                ["User_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Jemaat"],
                ["Church_ID", "INTEGER", "FOREIGN KEY, Nullable", "Gereja tempat jemaat terdaftar"],
                ["Nama_Lengkap", "VARCHAR(150)", "Not Null", "Nama lengkap jemaat"],
                ["NIK", "VARCHAR(20)", "Unique, Nullable", "Nomor Induk Kependudukan"],
                ["No_KTP", "VARCHAR(20)", "Nullable", "Nomor KTP jemaat"],
                ["Tempat_Lahir", "VARCHAR(100)", "Nullable", "Kota tempat lahir"],
                ["Tanggal_Lahir", "DATE", "Nullable", "Tanggal lahir jemaat"],
                ["Jenis_Kelamin", "VARCHAR(15)", "Nullable", "Laki-laki / Perempuan"],
                ["Pendidikan", "VARCHAR(50)", "Nullable", "Tingkat pendidikan terakhir"],
                ["Daerah_Asal", "VARCHAR(100)", "Nullable", "Kota / daerah asal jemaat"],
                ["Proses_Katekisasi", "TEXT", "Nullable", "Status katekisasi & Ayat Emas yang diterima"],
                ["No_HP", "VARCHAR(20)", "Nullable", "Nomor handphone / WA jemaat"],
                ["Alamat", "TEXT", "Nullable", "Alamat tempat tinggal"],
                ["Email", "VARCHAR(255)", "Unique, Nullable", "Email jemaat untuk akun/notifikasi"],
                ["Password", "VARCHAR(255)", "Nullable", "Hashed password jika jemaat memiliki akun login"],
                ["Pas_Foto", "VARCHAR(255)", "Nullable", "Path / URL foto profil jemaat"]
            ],
            "relation_note": "Terhubung ke Church_ID untuk mengelompokkan jemaat berdasarkan gereja lokalnya."
        },
        {
            "name": "4. Tabel: Church",
            "desc": "Bagian ini berisi nama-nama gereja yang telah dikumpulkan / didaftarkan oleh admin utama.",
            "pk": "Church_ID",
            "fk": "Tidak ada (Tabel Induk Gereja)",
            "fields": [
                ["Church_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Gereja"],
                ["Nama_Gereja", "VARCHAR(200)", "Not Null", "Nama lengkap gereja"],
                ["Alamat_Gereja", "TEXT", "Not Null", "Alamat fisik lokasi gereja"],
                ["Lokasi_GMaps_Gereja", "TEXT", "Nullable", "Link Google Maps lokasi gereja"],
                ["No_Telpon", "VARCHAR(20)", "Nullable", "Nomor telepon resmi gereja"],
                ["Email", "VARCHAR(255)", "Nullable", "Email resmi gereja"]
            ],
            "relation_note": "Induk utama bagi tabel Church_Admin, Finance, Worship, Church_News, Church_Services, dan Church_Spesific_Anniversary."
        },
        {
            "name": "5. Tabel: Finance",
            "desc": "Bagian ini berisi tentang keuangan yang disediakan dalam gereja.",
            "pk": "Finance_ID",
            "fk": "Church_ID -> Menunjuk ke Church(Church_ID)",
            "fields": [
                ["Finance_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Transaksi Keuangan"],
                ["Church_ID", "INTEGER", "FOREIGN KEY, Not Null", "Kunci relasi ke gereja terkait"],
                ["Nama_Keuangan", "VARCHAR(150)", "Not Null", "Judul / Kategori transaksi keuangan"],
                ["Biaya_Pengeluaran", "DECIMAL(15,2)", "Default: 0.00", "Nominal pengeluaran"],
                ["Biaya_Pemasukan", "DECIMAL(15,2)", "Default: 0.00", "Nominal pemasukan"]
            ],
            "relation_note": "Terhubung ke Church_ID sehingga laporan keuangan dapat dipisahkan per gereja secara rapi."
        },
        {
            "name": "6. Tabel: Worship (Ibadah Gereja)",
            "desc": "Bagian jadwal dan informasi ibadah gereja (Online / Offline).",
            "pk": "Worship_ID",
            "fk": "Church_ID -> Menunjuk ke Church(Church_ID)",
            "fields": [
                ["Worship_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Jadwal Ibadah"],
                ["Church_ID", "INTEGER", "FOREIGN KEY, Not Null", "Kunci relasi ke gereja penyelenggara"],
                ["Name_worship", "VARCHAR(150)", "Not Null", "Nama ibadah (misal: Ibadah Raya 1)"],
                ["Worship_Classification", "VARCHAR(100)", "Nullable", "Klasifikasi ibadah (Umum, Pemuda, Anak)"],
                ["Link_Ibadah_Online", "TEXT", "Nullable", "Link streaming ibadah (YouTube/Zoom)"],
                ["Date_and_Time", "DATETIME", "Not Null", "Waktu dan tanggal pelaksanaan ibadah"]
            ],
            "relation_note": "Terhubung ke Church_ID. Nama Gereja dan Alamat Gereja otomatis diambil dari tabel Church melalui JOIN relasi FK."
        },
        {
            "name": "7. Tabel: Church_News",
            "desc": "Bagian ini digunakan Admin gereja untuk membuat berita gereja.",
            "pk": "News_ID",
            "fk": "Church_ID -> Menunjuk ke Church(Church_ID), Author_ID -> Menunjuk ke User/Admin",
            "fields": [
                ["News_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Berita"],
                ["Church_ID", "INTEGER", "FOREIGN KEY, Not Null", "Gereja pembuat berita"],
                ["News_Title", "VARCHAR(250)", "Not Null", "Judul berita gereja"],
                ["News_Classification", "VARCHAR(100)", "Nullable", "Kategori berita (Warta, Kegiatan, Duka)"],
                ["News_Photo", "VARCHAR(255)", "Nullable", "Path / URL foto berita"],
                ["Author", "VARCHAR(150)", "Not Null", "Nama / ID Penulis berita"],
                ["Fields", "TEXT", "Not Null", "Isi lengkap artikel / berita gereja"]
            ],
            "relation_note": "Terhubung ke Church_ID agar berita tampil di portal jemaat gereja yang bersangkutan."
        },
        {
            "name": "8. Tabel: Church_Services (Pelayanan Tiap-tiap Gereja)",
            "desc": "Bagian pendataan komisi / divisi pelayanan tiap-tiap gereja.",
            "pk": "Services_ID",
            "fk": "Church_ID -> Menunjuk ke Church(Church_ID)",
            "fields": [
                ["Services_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Pelayanan"],
                ["Church_ID", "INTEGER", "FOREIGN KEY, Not Null", "Kunci relasi ke gereja"],
                ["Nama_Pelayanan", "VARCHAR(150)", "Not Null", "Nama komisi/divisi (Musik, Usher, Media)"],
                ["Deskripsi_Pelayanan", "TEXT", "Nullable", "Deskripsi peranan pelayanan"],
                ["Jenis_Pelayanan", "VARCHAR(100)", "Nullable", "Kategori (Internal, Eksternal, Diakonia)"],
                ["Date_And_Time", "DATETIME", "Nullable", "Jadwal rutin pertemuan / pelayanan"]
            ],
            "relation_note": "Terhubung ke Church_ID. Informasi gereja diakses langsung via relasi FK."
        },
        {
            "name": "9. Tabel: Church_General_Anniversary",
            "desc": "Bagian peringatan hari besar umum gereja (Nasional / Kalender Gerejawi).",
            "pk": "Church_General_Anniversary_ID",
            "fk": "Tidak ada (Berlaku untuk seluruh gereja)",
            "fields": [
                ["Church_General_Anniversary_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Hari Raya Umum"],
                ["Nama_Anniversary", "VARCHAR(200)", "Not Null", "Nama Hari Raya (Paskah, Natal, Pentakosta)"],
                ["Tanggal_Hari_Raya", "DATE", "Not Null", "Tanggal peringatan hari raya"],
                ["Deskripsi_Anniversary", "TEXT", "Nullable", "Keterangan dan makna hari raya"]
            ],
            "relation_note": "Merupakan data master umum yang dapat diakses oleh semua gereja dalam sistem."
        },
        {
            "name": "10. Tabel: Church_Spesific_Anniversary",
            "desc": "Bagian peringatan hari raya / HUT khusus untuk gereja spesifik.",
            "pk": "Church_Spesific_Anniversary_ID",
            "fk": "Church_ID -> Menunjuk ke Church(Church_ID)",
            "fields": [
                ["Church_Spesific_Anniversary_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Hari Raya Spesifik"],
                ["Church_ID", "INTEGER", "FOREIGN KEY, Not Null", "Kunci relasi ke gereja terkait"],
                ["Nama_Anniversary_Spesific", "VARCHAR(200)", "Not Null", "Nama peringatan khusus (HUT Gereja, dll)"],
                ["Tanggal", "DATE", "Not Null", "Tanggal pelaksanaan peringatan"],
                ["Deskripsi_Anniversary", "TEXT", "Nullable", "Deskripsi detail acara peringatan"]
            ],
            "relation_note": "Terhubung ke Church_ID sehingga peringatan HUT spesifik hanya muncul di gereja bersangkutan."
        },
        {
            "name": "11. Tabel: User_Anniversary",
            "desc": "Bagian peringatan ulang tahun / anniversary jemaat.",
            "pk": "User_Anniversary_ID",
            "fk": "User_ID -> Menunjuk ke User(User_ID)",
            "fields": [
                ["User_Anniversary_ID", "INTEGER", "PRIMARY KEY, Autoincrement", "ID Unik Anniversary Jemaat"],
                ["User_ID", "INTEGER", "FOREIGN KEY, Not Null", "Kunci relasi ke data Jemaat"],
                ["Deskripsi_Anniversary", "TEXT", "Nullable", "Keterangan (Ulang Tahun Kelahiran / Pernikahan)"],
                ["Tanggal", "DATE", "Nullable", "Tanggal peringatan anniversary jemaat"]
            ],
            "relation_note": "Terhubung ke User_ID. Nama Lengkap dan Tanggal Lahir otomatis terhubung dari tabel User."
        }
    ]

    for tdata in tables_spec:
        add_styled_heading(doc, tdata["name"], level=2)
        p_desc = doc.add_paragraph(tdata["desc"])
        
        # Key summary box
        p_keys = doc.add_paragraph()
        p_keys.paragraph_format.space_after = Pt(2)
        r_pk = p_keys.add_run("• Primary Key (PK): ")
        r_pk.bold = True
        r_pk.font.color.rgb = RGBColor(15, 118, 110)
        p_keys.add_run(tdata["pk"] + "\n")
        
        r_fk = p_keys.add_run("• Foreign Key (FK): ")
        r_fk.bold = True
        r_fk.font.color.rgb = RGBColor(180, 83, 9)
        p_keys.add_run(tdata["fk"])

        # Table specification
        headers_f = ["Nama Record / Field", "Tipe Data", "Constraint", "Keterangan Properti"]
        create_table_spec(doc, headers_f, tdata["fields"], [2.2, 1.3, 1.7, 1.8])

        # Relation note
        p_rel = doc.add_paragraph()
        p_rel.paragraph_format.space_after = Pt(8)
        r_rel_lbl = p_rel.add_run("Penjelasan Integrasi Relasi: ")
        r_rel_lbl.bold = True
        r_rel_lbl.font.color.rgb = RGBColor(30, 64, 175)
        p_rel.add_run(tdata["relation_note"])

    # 3. Kesimpulan & Garansi Integrasi Data
    add_styled_heading(doc, "3. Garansi Integrasi Data & Penutup", level=1)
    p_end = doc.add_paragraph()
    p_end.add_run("Dengan perbaikan struktur di atas, seluruh 11 tabel buatan Anda tetap utuh 100% dan kini memiliki fondasi relasi yang sangat kuat melalui ")
    p.add_run("Primary Key dan Foreign Key").bold = True
    p_end.add_run(". Data antar tabel dijamin terhubung secara sempurna saat diimplementasikan ke dalam backend FastAPI (SQLAlchemy) maupun database PostgreSQL.")

    # Save to file
    target_path = r"d:\cms-project\Database DBMS CMS GracePoint.docx"
    backup_target_path = r"d:\cms-project\Database DBMS CMS GracePoint (Updated).docx"
    try:
        doc.save(target_path)
        print(f"Successfully generated updated file at: {target_path}")
    except PermissionError:
        doc.save(backup_target_path)
        print(f"File {target_path} is locked by Word. Saved updated file to: {backup_target_path}")

    # Copy to documentation folder if exists
    doc_dir = r"d:\cms-project\documentation"
    if os.path.exists(doc_dir):
        doc_copy = os.path.join(doc_dir, "Database_DBMS_CMS_GracePoint_Updated.docx")
        doc.save(doc_copy)
        print(f"Saved copy to: {doc_copy}")

if __name__ == "__main__":
    generate_updated_docx()
