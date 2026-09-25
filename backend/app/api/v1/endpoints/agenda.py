from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.agenda import AgendaCreate, AgendaUpdate, AgendaResponse
from app.services.agenda_service import AgendaService
from app.services.audit_service import AuditService

router = APIRouter()

def _record_agenda_audit(db: Session, action: str, agenda: AgendaResponse, detail: str, level: str = "INFO") -> None:
    try:
        AuditService.record(
            db,
            action=action,
            entity="agenda",
            entity_id=str(agenda.id),
            actor="Superadmin",
            level=level,
            detail=detail,
        )
    except Exception as e:
        # Prevent audit failures from breaking core operation
        pass

@router.get("/", response_model=List[AgendaResponse])
def read_agendas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 300,
    year: Optional[int] = Query(None, description="Filter tahun"),
    month: Optional[int] = Query(None, description="Filter bulan (1-12)"),
    category: Optional[str] = Query(None, description="Filter kategori kegiatan"),
    status: Optional[str] = Query(None, description="Filter status kegiatan"),
    church_id: Optional[int] = Query(None, description="Filter cabang gereja"),
    search: Optional[str] = Query(None, description="Pencarian nama kegiatan / lokasi / PIC"),
) -> Any:
    """Ambil daftar agenda kegiatan gereja dengan filter."""
    return AgendaService.get_all(
        db,
        skip=skip,
        limit=limit,
        year=year,
        month=month,
        category=category,
        status=status,
        church_id=church_id,
        search=search,
    )

@router.get("/{agenda_id}", response_model=AgendaResponse)
def read_agenda_by_id(
    agenda_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Ambil detail satu agenda kegiatan."""
    agenda = AgendaService.get_by_id(db, agenda_id=agenda_id)
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda kegiatan tidak ditemukan.")
    return agenda

@router.post("/", response_model=AgendaResponse, status_code=status.HTTP_201_CREATED)
def create_agenda(
    *,
    db: Session = Depends(deps.get_db),
    agenda_in: AgendaCreate,
) -> Any:
    """Buat agenda kegiatan baru."""
    agenda = AgendaService.create(db, obj_in=agenda_in)
    _record_agenda_audit(
        db,
        "CREATE",
        agenda,
        f"Agenda kegiatan '{agenda.title}' ({agenda.category}) pada {agenda.start_date} berhasil ditambahkan.",
        "SUCCESS",
    )
    return agenda

@router.put("/{agenda_id}", response_model=AgendaResponse)
def update_agenda(
    *,
    db: Session = Depends(deps.get_db),
    agenda_id: int,
    agenda_in: AgendaUpdate,
) -> Any:
    """Perbarui agenda kegiatan yang sudah ada."""
    agenda = AgendaService.get_by_id(db, agenda_id=agenda_id)
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda kegiatan tidak ditemukan.")
    
    updated_agenda = AgendaService.update(db, db_obj=agenda, obj_in=agenda_in)
    _record_agenda_audit(
        db,
        "UPDATE",
        updated_agenda,
        f"Agenda kegiatan '{updated_agenda.title}' diperbarui.",
    )
    return updated_agenda

@router.delete("/{agenda_id}", response_model=AgendaResponse)
def delete_agenda(
    *,
    db: Session = Depends(deps.get_db),
    agenda_id: int,
) -> Any:
    """Hapus agenda kegiatan dari sistem."""
    agenda = AgendaService.get_by_id(db, agenda_id=agenda_id)
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda kegiatan tidak ditemukan.")
    
    deleted_agenda = AgendaService.delete(db, agenda_id=agenda_id)
    _record_agenda_audit(
        db,
        "DELETE",
        deleted_agenda,
        f"Agenda kegiatan '{deleted_agenda.title}' dihapus dari kalender.",
        "NOTICE",
    )
    return deleted_agenda
