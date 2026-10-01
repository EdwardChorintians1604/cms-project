from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChurchMember(Base):
    __tablename__ = "church_members"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=True, index=True)
    church_code = Column(String(50), nullable=True, index=True)
    
    # Nomor Induk Anggota / Jemaat (misal: JM-001)
    member_no = Column(String(50), nullable=True, index=True)
    
    # Identitas Pribadi
    name = Column(String(255), nullable=False, index=True)
    gender = Column(String(10), default="L") # L atau P
    phone = Column(String(50), nullable=True) # WhatsApp
    email = Column(String(255), nullable=True)
    
    # Profil Keluarga
    family_role = Column(String(50), default="Kepala Keluarga") # Kepala Keluarga, Istri, Pemuda, Pemudi, Anak, Lansia
    
    # Tanggal Lahir & Status Rohani
    birthdate = Column(Date, nullable=True) # YYYY-MM-DD
    status_baptis = Column(String(100), default="Sudah Baptis & Sidi") # Sudah Baptis & Sidi, Sudah Baptis, Belum Baptis
    
    # Status Keaktifan & Presensi
    attendance_status = Column(String(50), default="Aktif", index=True) # Aktif, Perhatian Khusus, Pasif, Pindah
    last_attended = Column(Date, nullable=True) # Tanggal terakhir hadir ibadah
    
    # Alamat & Catatan Pastoral
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relasi opsional ke user app (jika ada)
    user_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("jemaat_users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    church = relationship("Church", backref="registered_members")
