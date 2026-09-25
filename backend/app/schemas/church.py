from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class ChurchBase(BaseModel):
    church_code: str
    church_name: str
    established_date: Optional[date] = None
    bpp_general_chairman: Optional[str] = None
    church_description: Optional[str] = None
    address: str
    city: Optional[str] = None

    # Geolocation & Maps
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_url: Optional[str] = None

    facebook_name: Optional[str] = None
    facebook_link: Optional[str] = None
    instagram_name: Optional[str] = None
    instagram_link: Optional[str] = None
    youtube_name: Optional[str] = None
    youtube_link: Optional[str] = None
    tiktok_name: Optional[str] = None
    tiktok_link: Optional[str] = None
    status: Optional[str] = "Aktif"

class ChurchCreate(ChurchBase):
    pass

class ChurchUpdate(BaseModel):
    church_code: Optional[str] = None
    church_name: Optional[str] = None
    established_date: Optional[date] = None
    bpp_general_chairman: Optional[str] = None
    church_description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_url: Optional[str] = None
    facebook_name: Optional[str] = None
    facebook_link: Optional[str] = None
    instagram_name: Optional[str] = None
    instagram_link: Optional[str] = None
    youtube_name: Optional[str] = None
    youtube_link: Optional[str] = None
    tiktok_name: Optional[str] = None
    tiktok_link: Optional[str] = None
    status: Optional[str] = None

class ChurchAdminSimple(BaseModel):
    id: int
    admin_name: str
    email: str
    phone: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

class JemaatUserSimple(BaseModel):
    id: int
    full_name: str
    username: str
    email: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True

class ChurchResponse(ChurchBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    admins: Optional[List[ChurchAdminSimple]] = []
    jemaat_members: Optional[List[JemaatUserSimple]] = []

    class Config:
        from_attributes = True
