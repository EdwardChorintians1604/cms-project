from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class AgendaBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "Kegiatan Umum"
    start_date: date
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    church_id: Optional[int] = None
    church_name: Optional[str] = "Semua Cabang"
    organizer: Optional[str] = None
    target_audience: Optional[str] = "Semua Jemaat"
    status: Optional[str] = "Akan Datang"
    color: Optional[str] = "amber"

class AgendaCreate(AgendaBase):
    pass

class AgendaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    church_id: Optional[int] = None
    church_name: Optional[str] = None
    organizer: Optional[str] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    color: Optional[str] = None

class AgendaResponse(AgendaBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
