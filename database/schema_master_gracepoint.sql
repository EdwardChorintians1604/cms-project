-- ==============================================================================
-- MASTER SCHEME POSTGRESQL - GRACEPOINT CMS (COMPLETE DATABASE RELEASE)
-- Database Architecture for Cloud PostgreSQL (Neon Serverless / Local PostgreSQL)
-- Target Systems: Super Admin, Church Admin, Jemaat Portal, Multi-Tenant Branches
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. SETUP EXTENSIONS (UUID & Cryptography)
-- ------------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------------------------
-- 2. ENUM TYPES CREATION
-- ------------------------------------------------------------------------------
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role_enum') THEN
        CREATE TYPE role_enum AS ENUM ('superadmin', 'church_admin', 'leader', 'jemaat');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_enum') THEN
        CREATE TYPE gender_enum AS ENUM ('Laki-laki', 'Perempuan');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'education_enum') THEN
        CREATE TYPE education_enum AS ENUM ('SD', 'SMP', 'SMA/SMK', 'D3', 'S1', 'S2', 'S3', 'Lainnya');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'marital_status_enum') THEN
        CREATE TYPE marital_status_enum AS ENUM ('Belum Menikah', 'Menikah', 'Bercerai', 'Janda/Duda');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'membership_status_enum') THEN
        CREATE TYPE membership_status_enum AS ENUM ('Aktif', 'Non-Aktif', 'Pindah', 'Meninggal');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sacrament_type_enum') THEN
        CREATE TYPE sacrament_type_enum AS ENUM ('Baptis_Air', 'Sidi', 'Pernikahan', 'Penyerahan_Anak');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'finance_type_enum') THEN
        CREATE TYPE finance_type_enum AS ENUM ('Pemasukan_Persembahan', 'Pemasukan_Persepuluhan', 'Pemasukan_Donasi', 'Pengeluaran_Operasional', 'Pengeluaran_Sosial');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'finance_method_enum') THEN
        CREATE TYPE finance_method_enum AS ENUM ('Tunai', 'Transfer_Bank', 'QRIS', 'Debit_Credit');
    END IF;
END $$;

-- ------------------------------------------------------------------------------
-- 3. TABEL SUPER ADMIN & AKUN DEVELOPER (Aktor 1)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS main_admin (
    id SERIAL PRIMARY KEY,
    development_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    dev_token VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 4. TABEL GEREJA & CABANG PELAYANAN (Multi-Tenant Church Branches)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS churches (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,       -- cth: 'gki-harapan', 'gbi-grace'
    name VARCHAR(255) NOT NULL,             -- cth: 'GKI Harapan Indah'
    affiliated_synod VARCHAR(100),          -- cth: 'GKI', 'GBI', 'HKBP', 'GKPS'
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    whatsapp_contact VARCHAR(50),
    instagram_name VARCHAR(100),
    instagram_link TEXT,
    facebook_name VARCHAR(100),
    facebook_link TEXT,
    youtube_name VARCHAR(100),
    youtube_link TEXT,
    tiktok_name VARCHAR(100),
    tiktok_link TEXT,
    website_url TEXT,
    address TEXT NOT NULL,
    city VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(10),
    description TEXT,                       -- Deskripsi sekilas gereja
    qris_image_url TEXT,                    -- Foto QRIS Resmi Gereja
    bank_name VARCHAR(100),                 -- Nama Bank Operasional
    bank_account_number VARCHAR(50),        -- No. Rekening Bank
    bank_account_name VARCHAR(150),          -- Atas Nama Rekening
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 5. TABEL PENGGUNA UTAMA / AUTENTIKASI (users)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    church_id INT REFERENCES churches(id) ON DELETE SET NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role role_enum DEFAULT 'jemaat',
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(25),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 6. TABEL KARTU KELUARGA GEREJA (families)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS families (
    id SERIAL PRIMARY KEY,
    church_id INT REFERENCES churches(id) ON DELETE CASCADE,
    family_code VARCHAR(50) UNIQUE NOT NULL, -- cth: KK-GP-2026-001
    family_name VARCHAR(255) NOT NULL,       -- cth: Keluarga Budi Santoso
    head_of_family_id UUID REFERENCES users(id) ON DELETE SET NULL,
    address TEXT,
    phone VARCHAR(25),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 7. TABEL BIODATA JEMAAT DETAIL (members)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    church_id INT REFERENCES churches(id) ON DELETE CASCADE,
    family_id INT REFERENCES families(id) ON DELETE SET NULL,
    
    -- Identitas Kependudukan & Demografi
    nik VARCHAR(16) UNIQUE NOT NULL,
    no_ktp VARCHAR(30),
    member_no VARCHAR(50) UNIQUE NOT NULL,  -- NIJ / No. Anggota (cth: GP-2026-0001)
    birth_place VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender gender_enum NOT NULL,
    education education_enum DEFAULT 'S1',
    marital_status marital_status_enum DEFAULT 'Belum Menikah',
    catechism_status VARCHAR(20) DEFAULT 'Belum', -- 'Sudah' | 'Belum'
    
    -- Relasi Gereja Asal & Domisili
    church_origin VARCHAR(255) NOT NULL,     -- Gereja asal
    church_affiliation VARCHAR(255) NOT NULL,-- Afiliasi (GPIB, GBI, dsb)
    origin_region VARCHAR(100) NOT NULL,    -- Daerah/Kota asal
    address TEXT NOT NULL,
    photo_url TEXT,
    
    -- Status Keanggotaan Gereja
    membership_status membership_status_enum DEFAULT 'Aktif',
    baptis_status VARCHAR(20) DEFAULT 'Belum Baptis',
    sidi_status VARCHAR(20) DEFAULT 'Belum Sidi',
    qr_code_token VARCHAR(255) UNIQUE,       -- Token QR presensi & kartu digital
    joined_date DATE DEFAULT CURRENT_DATE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 8. TABEL KOMISI & STRUKTUR PELAYANAN (ministries)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ministries (
    id SERIAL PRIMARY KEY,
    church_id INT REFERENCES churches(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,               -- cth: MIN-WORSHIP, MIN-MEDIA
    name VARCHAR(150) NOT NULL,              -- cth: Tim Worship & Praise
    description TEXT,
    leader_id UUID REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(church_id, code)
);

-- ------------------------------------------------------------------------------
-- 9. TABEL ANGGOTA PELAYANAN (ministry_members)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ministry_members (
    id SERIAL PRIMARY KEY,
    ministry_id INT REFERENCES ministries(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_name VARCHAR(100) NOT NULL,         -- cth: Worship Leader, Musician, Singer, Operator
    joined_at DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(ministry_id, user_id, role_name)
);

-- ------------------------------------------------------------------------------
-- 10. TABEL JADWAL IBADAH & PELAYANAN (service_schedules)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS service_schedules (
    id SERIAL PRIMARY KEY,
    church_id INT REFERENCES churches(id) ON DELETE CASCADE,
    service_name VARCHAR(255) NOT NULL,      -- cth: Ibadah Raya Minggu Pagi I
    speaker_name VARCHAR(255) NOT NULL,      -- Nama Pengkhotbah / Hamba Tuhan
    service_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(255) NOT NULL,          -- cth: Gedung Utama Lt. 2
    theme TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 11. TABEL PRESENSI / KEHADIRAN IBADAH & PELAYAN (attendances)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    schedule_id INT REFERENCES service_schedules(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scan_method VARCHAR(20) DEFAULT 'QR_CODE', -- 'QR_CODE' / 'MANUAL'
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(schedule_id, user_id)
);

-- ------------------------------------------------------------------------------
-- 12. TABEL EVENT & HARI BESAR GEREJA (church_events)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS church_events (
    id SERIAL PRIMARY KEY,
    church_id INT REFERENCES churches(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'Hari Besar', -- 'Paskah', 'Natal', 'Retreat', dll.
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    banner_url TEXT,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 13. TABEL SAKRAMEN GEREJA (sacraments)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sacraments (
    id SERIAL PRIMARY KEY,
    church_id INT REFERENCES churches(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sacrament_type sacrament_type_enum NOT NULL,
    certificate_no VARCHAR(100) UNIQUE,
    event_date DATE NOT NULL,
    officiator_name VARCHAR(255) NOT NULL,   -- Nama Pendeta / Pelayan Sakramen
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 14. TABEL KEUANGAN & PERSEMBAHAN (finances)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS finances (
    id SERIAL PRIMARY KEY,
    church_id INT REFERENCES churches(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL, -- Nullable untuk persembahan anonim
    transaction_code VARCHAR(100) UNIQUE NOT NULL, -- cth: TRX-FIN-2026-0001
    finance_type finance_type_enum NOT NULL,
    payment_method finance_method_enum DEFAULT 'QRIS',
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    proof_url TEXT,                         -- Foto bukti transfer / QRIS
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 15. TABEL WARTA JEMAAT & PENGUMUMAN (announcements)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    church_id INT REFERENCES churches(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'Warta Minggu',
    content TEXT NOT NULL,
    attachment_url TEXT,
    author_name VARCHAR(150),
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 16. TABEL LUPA PASSWORD & RESET TOKEN (password_resets)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS password_resets (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    identifier VARCHAR(255) NOT NULL,        -- Email atau NIK
    token VARCHAR(255) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 17. TABEL SESI USER / REMEMBER ME (user_sessions)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(500) NOT NULL,
    device_info TEXT,
    ip_address VARCHAR(45),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- INDEXING UNTUK OPTIMASI PERFORMA DATABASE & PENCARIAN WAKTU-NYATA
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_church ON users(church_id);

CREATE INDEX IF NOT EXISTS idx_members_nik ON members(nik);
CREATE INDEX IF NOT EXISTS idx_members_member_no ON members(member_no);
CREATE INDEX IF NOT EXISTS idx_members_status ON members(membership_status);
CREATE INDEX IF NOT EXISTS idx_members_gender ON members(gender);

CREATE INDEX IF NOT EXISTS idx_schedules_church_date ON service_schedules(church_id, service_date);
CREATE INDEX IF NOT EXISTS idx_finances_church_type ON finances(church_id, finance_type);
CREATE INDEX IF NOT EXISTS idx_events_church_date ON church_events(church_id, start_date);

-- ==============================================================================
-- TRIGGER OTOMATIS TANGGAL UPDATED_AT
-- ==============================================================================
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_main_admin BEFORE UPDATE ON main_admin FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_churches BEFORE UPDATE ON churches FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_users BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_families BEFORE UPDATE ON families FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_members BEFORE UPDATE ON members FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_ministries BEFORE UPDATE ON ministries FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_schedules BEFORE UPDATE ON service_schedules FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_events BEFORE UPDATE ON church_events FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_sacraments BEFORE UPDATE ON sacraments FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
CREATE TRIGGER trigger_update_announcements BEFORE UPDATE ON announcements FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

-- ==============================================================================
-- SEED INITIAL DATA (DUMMY DATA AWAL PENGUJIAN INTEGRASI)
-- ==============================================================================

-- 1. Main Admin (Aktor 1)
INSERT INTO main_admin (development_id, email, username, password, dev_token)
VALUES ('ER09632HU', 'ambatukam09@gmail.com', 'KenwayFrye09', crypt('Frye1234', gen_salt('bf')), '09G547')
ON CONFLICT (development_id) DO NOTHING;

-- 2. Data Gereja Cabang (Churches)
INSERT INTO churches (code, name, affiliated_synod, email, phone, address, city, description)
VALUES 
('gki-harapan', 'GKI Harapan Indah', 'GKI', 'sekretariat@gkiharapan.org', '021-88991234', 'Jl. Harapan Indah No. 12', 'Bekasi', 'Gereja Kristen Indonesia Harapan Indah'),
('gbi-grace', 'GBI Grace Assembly Pusat', 'GBI', 'info@gbigrace.org', '021-77889900', 'Jl. Grace Assembly No. 1', 'Jakarta', 'Gereja Bethel Indonesia Grace Assembly'),
('hkbp-kota', 'HKBP Kota Perjuangan', 'HKBP', 'hkbp@kotaperjuangan.org', '021-55443322', 'Jl. Pemuda No. 45', 'Jakarta', 'Huria Kristen Batak Protestan Kota Perjuangan')
ON CONFLICT (code) DO NOTHING;

-- 3. Akun User Jemaat (Users & Members)
WITH new_user AS (
    INSERT INTO users (username, email, hashed_password, role, full_name, phone, church_id)
    VALUES (
        'jemaat_aktif',
        'jemaat.aktif@systemkita.id',
        crypt('Jemaat#2026', gen_salt('bf')),
        'jemaat',
        'Budi Santoso',
        '081234567890',
        (SELECT id FROM churches WHERE code = 'gki-harapan' LIMIT 1)
    )
    ON CONFLICT (username) DO NOTHING
    RETURNING id, church_id
)
INSERT INTO members (
    user_id, church_id, nik, no_ktp, member_no, birth_place, birth_date, gender, education,
    marital_status, catechism_status, church_origin, church_affiliation, origin_region, address,
    membership_status, baptis_status, sidi_status, qr_code_token
)
SELECT 
    id, church_id, '3171020304950001', '3171020304950001', 'GP-2026-0001', 'Jakarta', '1995-04-03',
    'Laki-laki', 'S1', 'Menikah', 'Sudah', 'GKI Harapan Indah', 'GKI', 'Jakarta',
    'Jl. Sunter Permai No. 88', 'Aktif', 'Sudah Baptis', 'Sudah Sidi', 'QR-GP-3171020304950001'
FROM new_user
ON CONFLICT (nik) DO NOTHING;

-- 4. Komisi Pelayanan (Ministries)
INSERT INTO ministries (church_id, code, name, description)
SELECT id, 'MIN-WORSHIP', 'Tim Praise & Worship', 'Pelayanan Musik, WL, Singer, dan Choir' FROM churches WHERE code = 'gki-harapan'
ON CONFLICT (church_id, code) DO NOTHING;

INSERT INTO ministries (church_id, code, name, description)
SELECT id, 'MIN-MEDIA', 'Tim Media & MultiMedia', 'Pelayanan Sound, Lighting, Live Streaming, dan Slide' FROM churches WHERE code = 'gki-harapan'
ON CONFLICT (church_id, code) DO NOTHING;
