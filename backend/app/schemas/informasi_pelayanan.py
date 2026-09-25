from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class InformasiPelayananBase(BaseModel):
    church_admin_id: Optional[int] = None
    church_id: Optional[int] = None
    church_name: str
    church_code: Optional[str] = None
    city: Optional[str] = None
    service_name: str
    category: str = "Jadwal Ibadah"
    schedule_day: Optional[str] = None
    schedule_time: Optional[str] = None
    location_room: Optional[str] = None
    target_audience: Optional[str] = "Semua Jemaat"
    description: Optional[str] = None
    pic_name: Optional[str] = None
    pic_contact: Optional[str] = None
    live_stream_url: Optional[str] = None
    status: str = "Aktif"
    is_active: bool = True

class InformasiPelayananCreate(InformasiPelayananBase):
    pass

class InformasiPelayananUpdate(BaseModel):
    church_admin_id: Optional[int] = None
    church_id: Optional[int] = None
    church_name: Optional[str] = None
    church_code: Optional[str] = None
    city: Optional[str] = None
    service_name: Optional[str] = None
    category: Optional[str] = None
    schedule_day: Optional[str] = None
    schedule_time: Optional[str] = None
    location_room: Optional[str] = None
    target_audience: Optional[str] = None
    description: Optional[str] = None
    pic_name: Optional[str] = None
    pic_contact: Optional[str] = None
    live_stream_url: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class InformasiPelayananResponse(InformasiPelayananBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
