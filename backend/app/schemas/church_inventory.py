from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# --- SCHEMAS INVENTARIS / GEDUNG ---
class ChurchInventoryBase(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    item_code: Optional[str] = None
    name: str
    category: Optional[str] = "Gedung & Ruangan"
    capacity_or_qty: Optional[str] = None
    location: Optional[str] = None
    condition: Optional[str] = "Sangat Baik"
    is_loanable: Optional[bool] = True
    status: Optional[str] = "Tersedia"
    operational_fee_note: Optional[str] = None
    pic_name: Optional[str] = None
    pic_phone: Optional[str] = None
    icon: Optional[str] = "🏛️"
    description: Optional[str] = None

class ChurchInventoryCreate(ChurchInventoryBase):
    pass

class ChurchInventoryUpdate(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    item_code: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    capacity_or_qty: Optional[str] = None
    location: Optional[str] = None
    condition: Optional[str] = None
    is_loanable: Optional[bool] = None
    status: Optional[str] = None
    operational_fee_note: Optional[str] = None
    pic_name: Optional[str] = None
    pic_phone: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None

class ChurchInventoryResponse(ChurchInventoryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- SCHEMAS PEMINJAMAN INVENTARIS & GEDUNG ---
class ChurchInventoryLoanBase(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    loan_code: Optional[str] = None
    inventory_id: Optional[int] = None
    inventory_name: str
    borrower_type: Optional[str] = "Pihak Luar Gereja / Eksternal"
    borrower_name: str
    borrower_institution: Optional[str] = None
    borrower_phone: str
    borrower_email: Optional[str] = None
    borrower_identity_no: Optional[str] = None
    event_purpose: str
    start_date: date
    start_time: Optional[str] = "09:00 WIB"
    end_date: date
    end_time: Optional[str] = "17:00 WIB"
    loan_status: Optional[str] = "Diajukan"
    initial_condition: Optional[str] = "Kondisi baik dan lengkap"
    return_condition: Optional[str] = None
    infaq_or_fee: Optional[float] = 0.0
    admin_notes: Optional[str] = None
    wa_notified: Optional[bool] = False

class ChurchInventoryLoanCreate(ChurchInventoryLoanBase):
    pass

class ChurchInventoryLoanUpdate(BaseModel):
    church_id: Optional[int] = None
    church_code: Optional[str] = None
    loan_code: Optional[str] = None
    inventory_id: Optional[int] = None
    inventory_name: Optional[str] = None
    borrower_type: Optional[str] = None
    borrower_name: Optional[str] = None
    borrower_institution: Optional[str] = None
    borrower_phone: Optional[str] = None
    borrower_email: Optional[str] = None
    borrower_identity_no: Optional[str] = None
    event_purpose: Optional[str] = None
    start_date: Optional[date] = None
    start_time: Optional[str] = None
    end_date: Optional[date] = None
    end_time: Optional[str] = None
    loan_status: Optional[str] = None
    initial_condition: Optional[str] = None
    return_condition: Optional[str] = None
    infaq_or_fee: Optional[float] = None
    admin_notes: Optional[str] = None
    wa_notified: Optional[bool] = None

class ChurchInventoryLoanResponse(ChurchInventoryLoanBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
