from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ChurchStructureBase(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    name: str
    title: Optional[str] = None
    role_position: str
    hierarchy_level: Optional[int] = 2
    department: Optional[str] = "BPH"
    parent_id: Optional[int] = None
    ministry_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    period: Optional[str] = "2024 - 2029"
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "Aktif"
    sort_order: Optional[int] = 0

class ChurchStructureCreate(ChurchStructureBase):
    pass

class ChurchStructureUpdate(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    role_position: Optional[str] = None
    hierarchy_level: Optional[int] = None
    department: Optional[str] = None
    parent_id: Optional[int] = None
    ministry_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    period: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None

class ChurchStructureResponse(ChurchStructureBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
