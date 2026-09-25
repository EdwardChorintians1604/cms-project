from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, Text
from app.core.database import Base

class MainAdmin(Base):
    __tablename__ = "main_admin"

    development_id = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(Text, nullable=False)
    dev_token = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def id(self):
        return self.development_id

    @property
    def full_name(self):
        return f"Main Admin ({self.username})"

    @property
    def role(self):
        return "superadmin"

    @property
    def is_active(self):
        return True
