from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChurchStructure(Base):
    __tablename__ = "church_structures"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=True, index=True)
    church_code = Column(String(50), nullable=True, index=True)
    
    # Identitas & Jabatan
    name = Column(String(255), nullable=False)
    title = Column(String(100), nullable=True) # Gelar misal: S.Th, M.Th, S.Kom
    role_position = Column(String(255), nullable=False) # Jabatan: Gembala Sidang, Sekretaris, Koordinator Musik, dll.
    
    # Hierarki & Departemen
    hierarchy_level = Column(Integer, default=2) # 1: Pimpinan Utama, 2: BPH / Pengurus Inti, 3: Koordinator Bidang, 4: Anggota/Staf
    department = Column(String(100), default="BPH") # misal: Penggembalaan, BPH, Musik & Multimedia, Pemuda, Sekolah Minggu, Diakonia
    parent_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("church_structures.id", ondelete="SET NULL"), nullable=True)
    
    # Relasi Terpadu ke Lembaga Pelayanan Cabang
    ministry_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("church_ministries.id", ondelete="SET NULL"), nullable=True, index=True)

    # Kontak & Detail
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    period = Column(String(50), default="2024 - 2029")
    photo_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    status = Column(String(50), default="Aktif") # Aktif, Non-Aktif, Purna Tugas
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Self-referential relationship untuk hirarki pohon bagan
    parent = relationship("ChurchStructure", remote_side=[id], backref="subordinates")
    church = relationship("Church", backref="structures")
    ministry = relationship("ChurchMinistry", foreign_keys=[ministry_id], backref="linked_officers")
