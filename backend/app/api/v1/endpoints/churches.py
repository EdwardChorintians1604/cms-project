from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.church import ChurchCreate, ChurchUpdate, ChurchResponse
from app.services.church_service import ChurchService
from app.services.audit_service import AuditService

router = APIRouter()


def _record_church_audit(db: Session, action: str, church: ChurchResponse, detail: str, level: str = "INFO") -> None:
    AuditService.record(
        db,
        action=action,
        entity="church",
        entity_id=str(church.id),
        actor="Superadmin",
        level=level,
        detail=detail,
    )

@router.get("/", response_model=List[ChurchResponse])
def read_churches(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return ChurchService.get_all(db, skip=skip, limit=limit)

@router.get("/{church_id}", response_model=ChurchResponse)
def read_church_by_id(
    church_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    church = ChurchService.get_by_id(db, church_id=church_id)
    if not church:
        raise HTTPException(status_code=404, detail="Gereja tidak ditemukan.")
    return church

@router.post("/", response_model=ChurchResponse, status_code=status.HTTP_201_CREATED)
def create_church(
    *,
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
    church_in: ChurchCreate,
) -> Any:
    existing_church = ChurchService.get_by_code(db, church_code=church_in.church_code)
    if existing_church:
        raise HTTPException(
            status_code=400,
            detail=f"Gereja dengan kode '{church_in.church_code}' sudah terdaftar.",
        )
    church = ChurchService.create(db, obj_in=church_in)
    _record_church_audit(db, "CREATE", church, f"Gereja utama {church.church_name} berhasil didaftarkan.", "SUCCESS")
    return church

@router.put("/{church_id}", response_model=ChurchResponse)
def update_church(
    *,
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
    church_id: int,
    church_in: ChurchUpdate,
) -> Any:
    church = ChurchService.get_by_id(db, church_id=church_id)
    if not church:
        raise HTTPException(status_code=404, detail="Gereja tidak ditemukan.")
    updated_church = ChurchService.update(db, db_obj=church, obj_in=church_in)
    _record_church_audit(db, "UPDATE", updated_church, f"Data gereja utama {updated_church.church_name} diperbarui.")
    return updated_church

@router.delete("/{church_id}", response_model=ChurchResponse)
def delete_church(
    *,
    db: Session = Depends(deps.get_db),
    _: Any = Depends(deps.get_current_superadmin),
    church_id: int,
) -> Any:
    church = ChurchService.get_by_id(db, church_id=church_id)
    if not church:
        raise HTTPException(status_code=404, detail="Gereja tidak ditemukan.")
    deleted_church = ChurchService.delete(db, church_id=church_id)
    _record_church_audit(db, "DELETE", deleted_church, f"Gereja utama {deleted_church.church_name} dihapus dari sistem.", "NOTICE")
    return deleted_church
