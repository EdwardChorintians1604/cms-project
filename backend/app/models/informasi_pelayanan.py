from datetime import datetime, timezone
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class InformasiPelayanan(Base):
    __tablename__ = "informasi_pelayanan"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    
    # Relasi ke Cabang Gereja (Admin Cabang) dan Gereja Induk
    church_admin_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("church_admins.id", ondelete="CASCADE"), nullable=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Metadata Cabang
    church_name = Column(String(255), nullable=False, index=True)
    church_code = Column(String(50), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    
    # Informasi Pelayanan
    service_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, default="Jadwal Ibadah", index=True)
    schedule_day = Column(String(100), nullable=True)     # Contoh: Setiap Hari Minggu, Sabtu, dsb
    schedule_time = Column(String(100), nullable=True)    # Contoh: 09:00 - 11:00 WIB
    location_room = Column(String(255), nullable=True)    # Ruang / Tempat Pelaksanaan
    target_audience = Column(String(100), nullable=True, default="Semua Jemaat") # Semua Jemaat, Pemuda, Anak-anak, Lansia
    description = Column(Text, nullable=True)             # Uraian lengkap informasi pelayanan
    
    # PIC & Kontak
    pic_name = Column(String(150), nullable=True)         # Penanggung jawab / Pelayan
    pic_contact = Column(String(100), nullable=True)      # No WhatsApp / Telp
    live_stream_url = Column(Text, nullable=True)         # Link Live Streaming (YouTube / Zoom)
    
    # Status
    status = Column(String(50), nullable=False, default="Aktif", index=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # ORM Relationships
    church_admin = relationship("ChurchAdmin", foreign_keys=[church_admin_id], lazy="joined")
    church = relationship("Church", foreign_keys=[church_id], lazy="joined")
