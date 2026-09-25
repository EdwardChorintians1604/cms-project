import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal, engine, Base
from app.models.main_admin import MainAdmin
from app.core.security import get_password_hash

def init_db():
    db_name = engine.url.database
    print(f"Connecting to PostgreSQL database '{db_name}' and creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"❌ Gagal terhubung ke database PostgreSQL: {e}")
        print("💡 Pastikan service PostgreSQL aktif dan database 'cms_database' sudah dibuat di pgAdmin 4!")
        return

    db = SessionLocal()
    try:
        email = "ambatukam09@gmail.com"
        admin = db.query(MainAdmin).filter(MainAdmin.email == email).first()
        if not admin:
            admin = MainAdmin(
                development_id="ER09632HU",
                email=email,
                username="KenwayFrye09",
                password=get_password_hash("Frye1234"),
            )
            db.add(admin)
            db.commit()
            print(f"🎉 Initial superuser '{email}' created successfully in PostgreSQL!")
        else:
            print(f"Superuser '{email}' already exists in PostgreSQL.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during PostgreSQL database initialization: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing PostgreSQL database...")
    init_db()
    print("Done!")

