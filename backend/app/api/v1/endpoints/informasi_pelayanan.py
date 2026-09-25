from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.informasi_pelayanan import (
    InformasiPelayananCreate,
    InformasiPelayananUpdate,
    InformasiPelayananResponse,
)
from app.services.informasi_pelayanan_service import InformasiPelayananService
from app.services.audit_service import AuditService

router = APIRouter()

def _record_audit(db: Session, action: str, entity_id: str, detail: str, level: str = "INFO"):
    try:
        AuditService.record(
            db,
            action=action,
            entity="informasi_pelayanan",
            entity_id=entity_id,
            actor="Admin",
            level=level,
            detail=detail,
        )
    except Exception:
        pass

@router.get("/", response_model=List[InformasiPelayananResponse])
def get_informasi_pelayanan_list(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    church_admin_id: Optional[int] = Query(None, description="Filter ID admin/cabang gereja"),
    church_id: Optional[int] = Query(None, description="Filter ID gereja induk"),
    category: Optional[str] = Query(None, description="Filter kategori pelayanan"),
    status: Optional[str] = Query(None, description="Filter status (Aktif, dll)"),
    search: Optional[str] = Query(None, description="Pencarian nama pelayanan / cabang / deskripsi"),
) -> Any:
    """Ambil daftar informasi pelayanan yang diadakan oleh cabang-cabang gereja terdaftar."""
    return InformasiPelayananService.get_all(
        db,
        skip=skip,
        limit=limit,
        church_admin_id=church_admin_id,
        church_id=church_id,
        category=category,
        status=status,
        search=search,
    )

@router.get("/{item_id}", response_model=InformasiPelayananResponse)
def get_informasi_pelayanan_by_id(
    item_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Ambil detail informasi pelayanan spesifik."""
    item = InformasiPelayananService.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Informasi pelayanan tidak ditemukan.")
    return item

@router.post("/", response_model=InformasiPelayananResponse, status_code=status.HTTP_201_CREATED)
def create_informasi_pelayanan(
    item_in: InformasiPelayananCreate,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Terbitkan informasi pelayanan baru (dapat dilakukan oleh admin cabang)."""
    item = InformasiPelayananService.create(db, obj_in=item_in)
    _record_audit(
        db,
        action="CREATE",
        entity_id=str(item.id),
        detail=f"Informasi pelayanan '{item.service_name}' ({item.category}) berhasil diterbitkan untuk cabang '{item.church_name}'.",
        level="SUCCESS",
    )
    return item

@router.put("/{item_id}", response_model=InformasiPelayananResponse)
def update_informasi_pelayanan(
    item_id: int,
    item_in: InformasiPelayananUpdate,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Perbarui informasi pelayanan cabang."""
    item = InformasiPelayananService.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Informasi pelayanan tidak ditemukan.")
    updated_item = InformasiPelayananService.update(db, db_obj=item, obj_in=item_in)
    _record_audit(
        db,
        action="UPDATE",
        entity_id=str(item_id),
        detail=f"Informasi pelayanan '{updated_item.service_name}' pada cabang '{updated_item.church_name}' diperbarui.",
    )
    return updated_item

@router.delete("/{item_id}", response_model=InformasiPelayananResponse)
def delete_informasi_pelayanan(
    item_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Hapus informasi pelayanan cabang."""
    item = InformasiPelayananService.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Informasi pelayanan tidak ditemukan.")
    deleted_item = InformasiPelayananService.delete(db, item_id=item_id)
    _record_audit(
        db,
        action="DELETE",
        entity_id=str(item_id),
        detail=f"Informasi pelayanan '{deleted_item.service_name}' cabang '{deleted_item.church_name}' dihapus.",
        level="NOTICE",
    )
    return deleted_item
