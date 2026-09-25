from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.system_setting import SettingsBulkUpdate, SettingsGroupedResponse
from app.services.system_setting_service import SystemSettingService
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("/", response_model=SettingsGroupedResponse)
def read_system_settings(
    db: Session = Depends(deps.get_db),
) -> Any:
    """Ambil seluruh pengaturan platform terkelompok."""
    grouped = SystemSettingService.get_all_grouped(db)
    return {"settings": grouped}

@router.put("/")
def update_system_settings(
    data: SettingsBulkUpdate,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Perbarui pengaturan sistem secara massal (bulk update)."""
    result = SystemSettingService.update_bulk(db, updates=data.settings)
    
    try:
        AuditService.record(
            db,
            action="UPDATE_SETTINGS",
            entity="system_setting",
            actor="Superadmin",
            level="INFO",
            detail=f"Superadmin memperbarui {result.get('updated_count')} kunci pengaturan sistem.",
        )
    except Exception:
        pass

    return {
        "status": "success",
        "message": f"{result.get('updated_count')} pengaturan berhasil disimpan.",
        "data": result,
    }

@router.post("/reset")
def reset_system_settings(
    group: Optional[str] = Query(None, description="Grup pengaturan opsional untuk di-reset"),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Kembalikan pengaturan sistem ke nilai awal pabrikan."""
    result = SystemSettingService.reset_to_defaults(db, group=group)
    
    try:
        AuditService.record(
            db,
            action="RESET_SETTINGS",
            entity="system_setting",
            actor="Superadmin",
            level="NOTICE",
            detail=f"Superadmin mereset pengaturan {group or 'seluruh platform'} ke default.",
        )
    except Exception:
        pass

    return result
