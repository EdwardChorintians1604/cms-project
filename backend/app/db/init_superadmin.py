import os
import sys

# Ensure backend directory is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)  # Set CWD to backend directory so relative db paths resolve consistently

from app.core.database import SessionLocal, engine, Base
from app.models.main_admin import MainAdmin
from app.core.security import get_password_hash

def init_superadmin(
    email: str = "ambatukam09@gmail.com",
    username: str = "KenwayFrye09",
    password: str = "Frye1234",
    name: str = "Admin Utama GracePoint",
):
    db_name = engine.url.database
    print(f"Connecting to PostgreSQL database '{db_name}' and creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"❌ Gagal terhubung/membuat tabel di PostgreSQL: {e}")
        print("💡 Pastikan database 'cms_database' sudah dibuat di pgAdmin 4 dan PostgreSQL sedang berjalan!")
        return

    db = SessionLocal()
    try:
        existing_admin = db.query(MainAdmin).filter(MainAdmin.email == email).first()
        if existing_admin:
            # Update password if user already exists
            existing_admin.username = username
            existing_admin.password = get_password_hash(password)
            db.commit()
            print(f"✅ User Admin Utama '{email}' sudah ada. Password & role berhasil diperbarui di PostgreSQL.")
            return

        superadmin = MainAdmin(
            development_id="ER09632HU",
            email=email,
            username=username,
            password=get_password_hash(password),
        )
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        print(f"🎉 SUKSES! Admin Utama berhasil ditambahkan ke PostgreSQL database.")
        print(f"   Email: {email}")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Role: superadmin")
    except Exception as e:
        db.rollback()
        print(f"❌ Gagal membuat Admin Utama: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inisialisasi Admin Utama (PostgreSQL)")
    parser.add_argument("--email", type=str, default="ambatukam09@gmail.com", help="Email Admin Utama")
    parser.add_argument("--username", type=str, default="KenwayFrye09", help="Username Admin Utama")
    parser.add_argument("--password", type=str, default="Frye1234", help="Password Admin Utama")
    args = parser.parse_args()

    init_superadmin(email=args.email, username=args.username, password=args.password)

