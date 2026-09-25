from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Identity, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "jemaat_users"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), Identity(), primary_key=True, index=True)
    church_id = Column(BigInteger().with_variant(Integer, "sqlite"), ForeignKey("churches.id", ondelete="SET NULL"), nullable=True)
    full_name = Column(String(255), nullable=False, index=True)
    birth_place = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    nik = Column(String(16), unique=True, nullable=False, index=True)
    no_ktp = Column(String(30), nullable=True)
    gender = Column(String(20), nullable=False)
    education = Column(String(20), nullable=False)
    church_domisili = Column(String(255), nullable=False)
    church_central = Column(String(255), nullable=False)
    married = Column(String(20), nullable=False)
    chatecication = Column(String(20), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(25), nullable=False)
    origin = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    photo_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    church = relationship("Church", back_populates="jemaat_members")
