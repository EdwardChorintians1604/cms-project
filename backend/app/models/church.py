from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Church(Base):
    __tablename__ = "churches"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_code = Column(String(50), unique=True, nullable=False, index=True)
    church_name = Column(String(255), nullable=False, index=True)
    established_date = Column(Date, nullable=True)
    bpp_general_chairman = Column(String(255), nullable=True)
    church_description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=True)

    # Geolocation & Maps
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    google_maps_url = Column(Text, nullable=True)

    # Medsos & Links
    facebook_name = Column(String(255), nullable=True)
    facebook_link = Column(Text, nullable=True)
    instagram_name = Column(String(255), nullable=True)
    instagram_link = Column(Text, nullable=True)
    youtube_name = Column(String(255), nullable=True)
    youtube_link = Column(Text, nullable=True)
    tiktok_name = Column(String(255), nullable=True)
    tiktok_link = Column(Text, nullable=True)

    status = Column(String(50), default="Aktif")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relasi ORM:
    # 1. Relasi ke Admin Cabang (Satu gereja menaungi admin cabang)
    admins = relationship("ChurchAdmin", back_populates="church", cascade="all, delete-orphan")

    # 2. Relasi ke Jemaat (Satu gereja menaungi banyak anggota jemaat)
    jemaat_members = relationship("User", back_populates="church")
