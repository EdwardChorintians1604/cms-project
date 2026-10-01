from datetime import datetime, timezone, date
from sqlalchemy import BigInteger, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChurchInventory(Base):
    __tablename__ = "church_inventories"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=True, index=True)
    church_code = Column(String(50), nullable=True, index=True)
    
    # Kode & Identitas Inventaris / Fasilitas
    item_code = Column(String(50), nullable=True, index=True) # misal: GDG-01, AST-SND-01, MOB-01
    name = Column(String(255), nullable=False, index=True) # misal: Gedung Ibadah Utama (Sanctuary)
    category = Column(String(100), default="Gedung & Ruangan", index=True) # Gedung & Ruangan, Sound & Multimedia, Alat Musik, Kendaraan, Sarana Prasarana
    
    # Kapasitas & Spesifikasi
    capacity_or_qty = Column(String(100), nullable=True) # misal: "600 Kursi", "150 Orang", "4 Set"
    location = Column(String(255), nullable=True) # Lantai 1, Ruang FOH Sound, Garasi, dll
    condition = Column(String(50), default="Sangat Baik", index=True) # Sangat Baik, Baik, Perlu Perbaikan, Rusak
    
    # Pengelolaan Peminjaman
    is_loanable = Column(Boolean, default=True) # Apakah bisa dipinjam oleh pihak luar / internal
    status = Column(String(50), default="Tersedia", index=True) # Tersedia, Sedang Dipinjam, Dalam Pemeliharaan
    operational_fee_note = Column(String(255), nullable=True) # Estimasi infaq / biaya operasional kebersihan
    
    # Penanggung Jawab Fasilitas
    pic_name = Column(String(255), nullable=True)
    pic_phone = Column(String(50), nullable=True)
    icon = Column(String(50), default="🏛️")
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relasi ke Peminjaman
    loans = relationship("ChurchInventoryLoan", back_populates="inventory", cascade="all, delete-orphan")


class ChurchInventoryLoan(Base):
    __tablename__ = "church_inventory_loans"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="CASCADE"), nullable=True, index=True)
    church_code = Column(String(50), nullable=True, index=True)
    
    # Nomor Registrasi Peminjaman
    loan_code = Column(String(50), nullable=True, index=True) # misal: PINJAM-2026-001
    
    # Hubungan ke Inventaris / Gedung
    inventory_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("church_inventories.id", ondelete="SET NULL"), nullable=True, index=True)
    inventory_name = Column(String(255), nullable=False)
    
    # Identitas Peminjam (Mendukung Pihak Luar Gereja & Internal)
    borrower_type = Column(String(50), default="Pihak Luar Gereja / Eksternal", index=True) # Pihak Luar Gereja / Eksternal, Internal Komisi Gereja, Jemaat Pribadi
    borrower_name = Column(String(255), nullable=False, index=True) # Nama lengkap peminjam / penanggung jawab
    borrower_institution = Column(String(255), nullable=True) # Nama lembaga / keluarga / organisasi luar
    borrower_phone = Column(String(50), nullable=False) # WhatsApp utama untuk notifikasi
    borrower_email = Column(String(255), nullable=True)
    borrower_identity_no = Column(String(50), nullable=True) # No. KTP / NIK peminjam luar
    
    # Detail Pemakaian & Jadwal
    event_purpose = Column(Text, nullable=False) # Keperluan acara: Resepsi Pernikahan, Seminar, Retreat, dll
    start_date = Column(Date, nullable=False)
    start_time = Column(String(50), nullable=True) # misal: "09:00 WIB"
    end_date = Column(Date, nullable=False)
    end_time = Column(String(50), nullable=True) # misal: "17:00 WIB"
    
    # Status & Kondisi
    loan_status = Column(String(50), default="Diajukan", index=True) # Diajukan, Disetujui / Aktif, Selesai / Dikembalikan, Ditolak
    initial_condition = Column(String(255), default="Kondisi baik dan lengkap")
    return_condition = Column(String(255), nullable=True) # Kondisi saat dikembalikan
    
    # Biaya & Catatan
    infaq_or_fee = Column(Float, default=0.0) # Kontribusi operasional / infaq kebersihan
    admin_notes = Column(Text, nullable=True) # Catatan persetujuan admin gereja
    wa_notified = Column(Boolean, default=False) # Status notifikasi WhatsApp

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    inventory = relationship("ChurchInventory", back_populates="loans")
