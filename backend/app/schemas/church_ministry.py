from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ChurchMinistryBase(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    name: str
    code: Optional[str] = None
    category: Optional[str] = "Kategorial Usia"
    leader_structure_id: Optional[int] = None
    leader_name: Optional[str] = None
    leader_title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    member_count: Optional[int] = 0
    meeting_schedule: Optional[str] = None
    location_room: Optional[str] = None
    budget_allocation: Optional[str] = None
    description: Optional[str] = None
    vision_mission: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[str] = "Aktif"
    sort_order: Optional[int] = 0

class ChurchMinistryCreate(ChurchMinistryBase):
    pass

class ChurchMinistryUpdate(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None
    leader_structure_id: Optional[int] = None
    leader_name: Optional[str] = None
    leader_title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    member_count: Optional[int] = None
    meeting_schedule: Optional[str] = None
    location_room: Optional[str] = None
    budget_allocation: Optional[str] = None
    description: Optional[str] = None
    vision_mission: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None

class ChurchMinistryResponse(ChurchMinistryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
