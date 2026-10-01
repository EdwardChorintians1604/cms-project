from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChurchMinistry(Base):
    __tablename__ = "church_ministries"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=True, index=True)
    church_code = Column(String(50), nullable=True, index=True)
    
    # Identitas Lembaga / Departemen Pelayanan
    name = Column(String(255), nullable=False, index=True) # misal: Komisi Pemuda & Remaja (Youth)
    code = Column(String(50), nullable=True) # misal: KPR, SM, W&M, DIAK
    category = Column(String(100), default="Kategorial Usia", index=True) 
    
    # Kepemimpinan & Kontak (Tertaut ke Struktur)
    leader_structure_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("church_structures.id", ondelete="SET NULL"), nullable=True, index=True)
    leader_name = Column(String(255), nullable=True) # Nama Ketua / Koordinator Lembaga
    leader_title = Column(String(100), nullable=True) # Gelar / Jabatan rohani
    phone = Column(String(50), nullable=True) # No WA / Telepon PIC
    email = Column(String(255), nullable=True) # Email departemen
    
    # Operasional & Pertemuan
    member_count = Column(Integer, default=0) # Estimasi jumlah anggota / pelayan
    meeting_schedule = Column(String(255), nullable=True) # misal: Setiap Sabtu, 19:00 WIB
    location_room = Column(String(255), nullable=True) # Ruang pertemuan / kantor sekretariat
    budget_allocation = Column(String(100), nullable=True) # misal: Kas Anggaran Rutin Cabang
    
    # Deskripsi & Visi Pelayanan
    description = Column(Text, nullable=True)
    vision_mission = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    
    status = Column(String(50), default="Aktif", index=True) # Aktif, Non-Aktif, Reorganisasi
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    church = relationship("Church", backref="ministries")
    leader_officer = relationship("ChurchStructure", foreign_keys=[leader_structure_id], lazy="joined")
