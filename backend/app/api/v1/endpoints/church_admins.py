from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.church_admin import ChurchAdminCreate, ChurchAdminUpdate, ChurchAdminResponse
from app.services.church_admin_service import ChurchAdminService

router = APIRouter()

@router.get("/", response_model=List[ChurchAdminResponse])
def read_church_admins(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return ChurchAdminService.get_all(db, skip=skip, limit=limit)

@router.get("/{admin_id}", response_model=ChurchAdminResponse)
def read_church_admin_by_id(
    admin_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    admin = ChurchAdminService.get_by_id(db, admin_id=admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin gereja tidak ditemukan.")
    return admin

@router.post("/", response_model=ChurchAdminResponse, status_code=status.HTTP_201_CREATED)
def create_church_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: ChurchAdminCreate,
) -> Any:
    existing = ChurchAdminService.get_by_email(db, email=admin_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email admin gereja sudah terdaftar.")
    if admin_in.church_code:
        code_check = ChurchAdminService.get_by_church_code(db, church_code=admin_in.church_code.strip().upper())
        if code_check:
            raise HTTPException(status_code=400, detail=f"Kode gereja '{admin_in.church_code}' sudah terdaftar.")
    return ChurchAdminService.create(db, obj_in=admin_in)

@router.put("/{admin_id}", response_model=ChurchAdminResponse)
def update_church_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_id: int,
    admin_in: ChurchAdminUpdate,
) -> Any:
    admin = ChurchAdminService.get_by_id(db, admin_id=admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin gereja tidak ditemukan.")
    return ChurchAdminService.update(db, db_obj=admin, obj_in=admin_in)

@router.delete("/{admin_id}", response_model=ChurchAdminResponse)
def delete_church_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_id: int,
) -> Any:
    admin = ChurchAdminService.delete(db, admin_id=admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin gereja tidak ditemukan.")
    return admin
