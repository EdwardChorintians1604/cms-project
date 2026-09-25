from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditTransaksiKeuangan(Base):
    __tablename__ = "audit_transaksi_keuangan"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=True, index=True)
    transaksi_tipe = Column(String(50), nullable=False, index=True)  # pemasukan, pengeluaran, anggaran
    transaksi_id = Column(BigInteger().with_variant(Integer, "sqlite"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, VERIFY, APPROVE
    user_id = Column(String(100), nullable=True)
    user_role = Column(String(50), nullable=True)
    deskripsi = Column(Text, nullable=True)
    payload_sebelum = Column(Text, nullable=True)
    payload_sesudah = Column(Text, nullable=True)
    hash_sha256 = Column(String(64), nullable=True, index=True)
    prev_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    church = relationship("Church", foreign_keys=[church_id])

