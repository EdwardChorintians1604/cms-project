import os
import sys

# Add parent directory to sys.path so app can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.core.database import engine

def run_migration():
    print(f"Connecting to database: {engine.url.render_as_string(hide_password=True)}")
    is_sqlite = engine.url.drivername.startswith("sqlite")
    
    with engine.begin() as conn:
        print("Migrating 'churches' table...")
        if is_sqlite:
            # SQLite does not support IF NOT EXISTS in ADD COLUMN, handle per column
            cols = [
                ("city", "VARCHAR(100)"),
                ("latitude", "FLOAT"),
                ("longitude", "FLOAT"),
                ("google_maps_url", "TEXT")
            ]
            for col, col_type in cols:
                try:
                    conn.execute(text(f"ALTER TABLE churches ADD COLUMN {col} {col_type};"))
                    print(f"  Added column {col} to churches.")
                except Exception as e:
                    print(f"  Column {col} on churches skipped or exists: {e}")
        else:
            conn.execute(text("""
                ALTER TABLE churches ADD COLUMN IF NOT EXISTS city VARCHAR(100);
                ALTER TABLE churches ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION;
                ALTER TABLE churches ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;
                ALTER TABLE churches ADD COLUMN IF NOT EXISTS google_maps_url TEXT;
            """))
            print("  Successfully updated 'churches' table schema.")

        print("Migrating 'church_admins' table...")
        if is_sqlite:
            cols = [
                ("address", "TEXT"),
                ("latitude", "FLOAT"),
                ("longitude", "FLOAT"),
                ("google_maps_url", "TEXT")
            ]
            for col, col_type in cols:
                try:
                    conn.execute(text(f"ALTER TABLE church_admins ADD COLUMN {col} {col_type};"))
                    print(f"  Added column {col} to church_admins.")
                except Exception as e:
                    print(f"  Column {col} on church_admins skipped or exists: {e}")
        else:
            conn.execute(text("""
                ALTER TABLE church_admins ADD COLUMN IF NOT EXISTS address TEXT;
                ALTER TABLE church_admins ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION;
                ALTER TABLE church_admins ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;
                ALTER TABLE church_admins ADD COLUMN IF NOT EXISTS google_maps_url TEXT;
            """))
            print("  Successfully updated 'church_admins' table schema.")

        # Seed/Populate realistic coordinates for existing churches
        print("Seeding coordinate data for churches...")
        seed_churches = [
            {
                "code": "GP-09J5T", # GSJA Jakarta Pusat
                "city": "Jakarta Pusat",
                "lat": -6.1754,
                "lng": 106.8415,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-6.1754,106.8415"
            },
            {
                "code": "GBI-G45KJ098", # GBI Bandung
                "city": "Bandung",
                "lat": -6.8905,
                "lng": 107.6105,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-6.8905,107.6105"
            },
            {
                "code": "GKPM-09HJ12", # GKPM Mentawai
                "city": "Kepulauan Mentawai",
                "lat": -2.7758,
                "lng": 100.2227,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-2.7758,100.2227"
            },
            {
                "code": "GMI_IS45JFG", # GMI Surabaya
                "city": "Surabaya",
                "lat": -7.2915,
                "lng": 112.7602,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-7.2915,112.7602"
            },
            {
                "code": "GKI-HARAPAN-01", # GKI Harapan Indah Bekasi
                "city": "Bekasi",
                "lat": -6.1824,
                "lng": 106.9856,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-6.1824,106.9856"
            },
            {
                "code": "GPDI-CZ09AR2", # GPdI Jakarta Timur
                "city": "Jakarta Timur",
                "lat": -6.2250,
                "lng": 106.9004,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-6.2250,106.9004"
            },
            {
                "code": "IFGF-SEC-09", # IFGF Jakarta Barat
                "city": "Jakarta Barat",
                "lat": -6.1683,
                "lng": 106.7741,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-6.1683,106.7741"
            }
        ]

        for item in seed_churches:
            conn.execute(
                text("""
                    UPDATE churches
                    SET city = :city, latitude = :lat, longitude = :lng, google_maps_url = :gmaps
                    WHERE church_code = :code AND (latitude IS NULL OR city IS NULL);
                """),
                item
            )

        print("Seeding coordinate data for church_admins (cabang)...")
        seed_admins = [
            {
                "code": "GKI-HARAPAN-01",
                "address": "Jl. Harapan Indah Boulevard No. 1, Medan Satria, Bekasi",
                "lat": -6.1824,
                "lng": 106.9856,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-6.1824,106.9856"
            },
            {
                "code": "GP-CAB-01", # GSJA Padang
                "address": "Jl. Pondok No. 88, Padang Barat, Padang",
                "lat": -0.9583,
                "lng": 100.3582,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-0.9583,100.3582"
            },
            {
                "code": "GBI-GRACE-02", # GBI Jakarta Barat
                "address": "Mall Puri Indah Lt. 4, Kembangan, Jakarta Barat",
                "lat": -6.1884,
                "lng": 106.7388,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-6.1884,106.7388"
            },
            {
                "code": "GSJA-CAB-02", # GSJA Madiun
                "address": "Jl. Pahlawan No. 42, Kartoharjo, Madiun",
                "lat": -7.6298,
                "lng": 111.5239,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-7.6298,111.5239"
            },
            {
                "code": "GBI-PDG-09HGJTW", # GBI Bethel Padang
                "address": "Jl. Nipah No. 14, Berok Nipah, Padang",
                "lat": -0.9631,
                "lng": 100.3564,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-0.9631,100.3564"
            },
            {
                "code": "GPDI-CAB-01", # GPdI Karmel Padang
                "address": "Jl. HOS Cokroaminoto No. 25, Padang Barat",
                "lat": -0.9525,
                "lng": 100.3551,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-0.9525,100.3551"
            },
            {
                "code": "GKPM-CAB-MKKT-09CZER", # GKPM Makukuet
                "address": "Desa Makukuet, Pagai Selatan, Kepulauan Mentawai",
                "lat": -2.8512,
                "lng": 100.2845,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-2.8512,100.2845"
            },
            {
                "code": "GKPM-CAB-09SKKP", # GKPM Sikakap
                "address": "Desa Sikakap, Pagai Utara, Kepulauan Mentawai",
                "lat": -2.7758,
                "lng": 100.2227,
                "gmaps": "https://www.google.com/maps/search/?api=1&query=-2.7758,100.2227"
            }
        ]

        for item in seed_admins:
            conn.execute(
                text("""
                    UPDATE church_admins
                    SET address = :address, latitude = :lat, longitude = :lng, google_maps_url = :gmaps
                    WHERE church_code = :code AND (latitude IS NULL OR address IS NULL);
                """),
                item
            )

    print("Migration and seeding completed successfully!")

if __name__ == "__main__":
    run_migration()
