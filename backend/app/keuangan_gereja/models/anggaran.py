from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class AnggaranGereja(Base):
    __tablename__ = "anggaran_gereja"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=False, index=True)
    tahun = Column(Integer, nullable=False, index=True)
    bulan = Column(Integer, default=0, nullable=False)  # 0 untuk tahunan, 1-12 untuk bulanan
    jenis = Column(String(50), nullable=False, index=True)  # Pemasukan / Pengeluaran
    kategori = Column(String(100), nullable=False, index=True)
    target_nominal = Column(Float, nullable=False, default=0.0)
    catatan = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    church = relationship("Church", foreign_keys=[church_id])
