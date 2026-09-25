from datetime import datetime, timezone, date
from sqlalchemy import BigInteger, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class PemasukanGereja(Base):
    __tablename__ = "pemasukan_gereja"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=False, index=True)
    tanggal = Column(Date, default=date.today, nullable=False, index=True)
    kategori = Column(String(100), nullable=False, index=True)  # Persembahan Umum, Perpuluhan, Ucapan Syukur, Donasi Pembangunan, Diakonia, dll.
    jumlah = Column(Float, nullable=False)
    metode_pembayaran = Column(String(50), default="Tunai", nullable=False)  # Tunai, Transfer Bank, QRIS
    keterangan = Column(Text, nullable=True)
    bukti_transaksi_url = Column(String(500), nullable=True)
    status_verifikasi = Column(String(50), default="Verified", nullable=False)  # Pending, Verified, Rejected
    donor_name = Column(String(255), nullable=True)
    created_by = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to church
    church = relationship("Church", foreign_keys=[church_id])
