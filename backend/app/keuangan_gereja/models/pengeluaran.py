from datetime import datetime, timezone, date
from sqlalchemy import BigInteger, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class PengeluaranGereja(Base):
    __tablename__ = "pengeluaran_gereja"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=False, index=True)
    tanggal = Column(Date, default=date.today, nullable=False, index=True)
    kategori = Column(String(100), nullable=False, index=True)  # Operasional, Honor/Gaji Pelayan, Fasilitas & Pemeliharaan, Diakonia/Bantuan Sosial, Ibadah & Acara, Misi Penginjilan
    jumlah = Column(Float, nullable=False)
    metode_pembayaran = Column(String(50), default="Tunai", nullable=False)  # Tunai, Transfer Bank, QRIS
    penerima = Column(String(255), nullable=True)
    keterangan = Column(Text, nullable=True)
    bukti_transaksi_url = Column(String(500), nullable=True)
    status_persetujuan = Column(String(50), default="Disetujui", nullable=False)  # Pending, Disetujui, Ditolak
    disetujui_oleh = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    church = relationship("Church", foreign_keys=[church_id])
