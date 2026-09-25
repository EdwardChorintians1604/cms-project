from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChurchAdmin(Base):
    __tablename__ = "church_admins"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="SET NULL"), nullable=True)
    church_code = Column(String(50), unique=True, index=True, nullable=False)
    church_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    admin_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    password = Column(String(255), nullable=False)
    status = Column(String(20), default="Aktif")

    # Geolocation & Maps
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    google_maps_url = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relasi balik ke tabel churches
    church = relationship("Church", back_populates="admins")

    @property
    def full_name(self):
        return self.admin_name

    @property
    def username(self):
        return self.email

    @property
    def role(self):
        return "church_admin"

    @property
    def is_active(self):
        return self.status == "Aktif"
