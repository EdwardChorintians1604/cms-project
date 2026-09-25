from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChurchAgenda(Base):
    __tablename__ = "church_agendas"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="Kegiatan Umum", index=True)
    
    # Tanggal & Jam Pelaksanaan
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=True)
    start_time = Column(String(20), nullable=True)
    end_time = Column(String(20), nullable=True)

    # Lokasi & Penyelenggara
    location = Column(String(255), nullable=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="SET NULL"), nullable=True, index=True)
    church_name = Column(String(255), nullable=True, default="Semua Cabang")
    organizer = Column(String(255), nullable=True) # Seksi / Komisi / PIC
    target_audience = Column(String(100), nullable=True, default="Semua Jemaat")

    # Status & Tampilan Visual
    status = Column(String(50), nullable=False, default="Akan Datang", index=True) # Akan Datang | Sedang Berlangsung | Selesai | Dibatalkan
    color = Column(String(50), nullable=True, default="amber") # amber, emerald, sky, purple, rose, indigo

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Optional ORM relationship
    church = relationship("Church", foreign_keys=[church_id], lazy="joined")
