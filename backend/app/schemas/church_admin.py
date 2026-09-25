from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class ChurchAdminBase(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    church_name: str
    city: Optional[str] = None
    admin_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_url: Optional[str] = None

class ChurchAdminCreate(ChurchAdminBase):
    password: str
    confirm_password: Optional[str] = None

class ChurchAdminUpdate(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    church_name: Optional[str] = None
    city: Optional[str] = None
    admin_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_url: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None

class ChurchAdminResponse(BaseModel):
    id: int
    church_id: Optional[int] = None
    church_code: str
    church_name: str
    city: Optional[str] = None
    admin_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_url: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
