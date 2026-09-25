from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel

class SettingItem(BaseModel):
    id: Optional[int] = None
    group: str = "general"
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SettingsBulkUpdate(BaseModel):
    settings: Dict[str, Any]

class SettingsGroupedResponse(BaseModel):
    settings: Dict[str, Dict[str, Any]]
