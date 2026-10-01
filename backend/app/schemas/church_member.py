from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ChurchMemberBase(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    member_no: Optional[str] = None
    name: str
    gender: Optional[str] = "L"
    phone: Optional[str] = None
    email: Optional[str] = None
    family_role: Optional[str] = "Kepala Keluarga"
    birthdate: Optional[date] = None
    status_baptis: Optional[str] = "Sudah Baptis & Sidi"
    attendance_status: Optional[str] = "Aktif"
    last_attended: Optional[date] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[int] = None

class ChurchMemberCreate(ChurchMemberBase):
    pass

class ChurchMemberUpdate(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    member_no: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    family_role: Optional[str] = None
    birthdate: Optional[date] = None
    status_baptis: Optional[str] = None
    attendance_status: Optional[str] = None
    last_attended: Optional[date] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[int] = None

class ChurchMemberResponse(ChurchMemberBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
