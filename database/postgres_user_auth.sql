-- ==============================================================================
-- SKRIP POSTGRESQL (1 TABEL TUNGGAL) UNTUK USER REGISTER
-- Berdasarkan field formData dari:
-- frontend/cms-project/src/pages/auth/User_Register.vue
--
-- Catatan:
-- - confirmPassword tidak disimpan ke database karena hanya dipakai untuk validasi frontend.
-- - password disimpan sebagai hashed_password, bukan plain text.
-- ==============================================================================

-- 1. SETUP EXTENSION (Untuk UUID dan Enkripsi Password)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. PEMBUATAN TABEL KHUSUS AKUN JEMAAT: jemaat_users
-- Jangan menghapus atau memakai tabel users/main_admin milik admin utama.

CREATE TABLE jemaat_users (
    -- ID & Kredensial Akun
    id BIGSERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_place VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    nik VARCHAR(16) UNIQUE NOT NULL,
    no_ktp VARCHAR(30),
    gender VARCHAR(20) NOT NULL,
    education VARCHAR(20) NOT NULL,
    church_domisili VARCHAR(255) NOT NULL,
    church_central VARCHAR(255) NOT NULL,
    married VARCHAR(20) NOT NULL,
    chatecication VARCHAR(20) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL, -- hasil hash password dari formData.password
    phone VARCHAR(25) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    photo_url TEXT,
    
    -- Status Akun
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_users_nik_digits CHECK (nik ~ '^[0-9]{16}$'),
    CONSTRAINT chk_users_gender CHECK (gender IN ('Laki-laki', 'Perempuan')),
    CONSTRAINT chk_users_education CHECK (education IN ('SD', 'SMP', 'SMA/SMK', 'D3', 'S1', 'S2', 'S3', 'Lainnya')),
    CONSTRAINT chk_users_married CHECK (married IN ('Menikah', 'Belum Menikah', 'Bercerai')),
    CONSTRAINT chk_users_chatecication CHECK (chatecication IN ('Sudah', 'Belum'))
);

-- 3. INDEXING UNTUK OPTIMASI PERFORMANCE
CREATE INDEX idx_jemaat_users_username ON jemaat_users(username);
CREATE INDEX idx_jemaat_users_email ON jemaat_users(email);
CREATE INDEX idx_jemaat_users_nik ON jemaat_users(nik);

-- 4. TRIGGER OTOMATIS UNTUK UPDATED_AT
CREATE OR REPLACE FUNCTION update_jemaat_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_jemaat_users
BEFORE UPDATE ON jemaat_users
FOR EACH ROW
EXECUTE FUNCTION update_jemaat_users_updated_at();

-- 5. DUMMY SEED DATA CONTOH
INSERT INTO jemaat_users (
    full_name, birth_place, birth_date, nik, no_ktp, gender, education,
    church_domisili, church_central, married, chatecication, username, email,
    hashed_password, phone, origin, address, photo_url
) VALUES (
    'Budi Santoso',
    'Jakarta',
    '1995-04-03',
    '3171020304950001',
    '3171020304950001',
    'Laki-laki',
    'S1',
    'GKI Harapan Indah',
    'GKI',
    'Menikah',
    'Sudah',
    'jemaat_aktif',
    'jemaat.aktif@systemkita.id',
    crypt('Jemaat#2026', gen_salt('bf')),
    '081234567890',
    'Jakarta',
    'Jl. Sunter Permai No. 88, Jakarta Utara',
    NULL
) ON CONFLICT (username) DO NOTHING;

-- ==============================================================================
-- CONTOH QUERY UNTUK INTEGRASI CODE BACKEND
-- ==============================================================================

-- A. QUERY REGISTRASI JEMAAT (User_Register.vue)
/*
INSERT INTO jemaat_users (
    full_name, birth_place, birth_date, nik, no_ktp, gender, education,
    church_domisili, church_central, married, chatecication, username, email,
    hashed_password, phone, origin, address, photo_url
) VALUES (
    $1, $2, $3, $4, $5, $6, $7,
    $8, $9, $10, $11, $12, $13,
    crypt($14, gen_salt('bf')), $15, $16, $17, $18
) RETURNING id, username, email, full_name;
*/

-- B. QUERY LOGIN VIA EMAIL / USERNAME / NIK (User_Login.vue)
/*
SELECT id, username, email, hashed_password, full_name, is_active
FROM jemaat_users
WHERE (email = $1 OR username = $1 OR nik = $1)
  AND is_active = TRUE;
*/

-- C. QUERY DAHBOARD ADMIN TAMPIL BIODATA JEMAAT (namapenggunaUntukAdminUtama.vue)
/*
SELECT id, full_name, nik, gender, birth_place, birth_date, phone, email,
       origin, address, church_domisili, church_central, married, chatecication, photo_url
FROM jemaat_users
WHERE ($1::text IS NULL OR full_name ILIKE '%' || $1 || '%' OR nik ILIKE '%' || $1 || '%' OR username ILIKE '%' || $1 || '%')
  AND ($2::text IS NULL OR married = $2)
  AND ($3::text IS NULL OR gender = $3)
ORDER BY created_at DESC;
*/
