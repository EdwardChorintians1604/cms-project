from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.church_structure import ChurchStructure
from app.models.church_ministry import ChurchMinistry
from app.models.church_admin import ChurchAdmin
from app.schemas.church_structure import ChurchStructureCreate, ChurchStructureUpdate, ChurchStructureResponse

router = APIRouter()

@router.get("/", response_model=List[ChurchStructureResponse])
def get_church_structures(
    db: Session = Depends(deps.get_db),
    church_code: Optional[str] = Query(None),
    church_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
) -> Any:
    query = db.query(ChurchStructure)
    if church_code and church_code.strip() and church_code.strip().upper() not in ["DEFAULT", "UNDEFINED", "NULL", ""]:
        query = query.filter(ChurchStructure.church_code == church_code.strip().upper())
    if church_id is not None:
        query = query.filter(ChurchStructure.church_id == church_id)
    if department and department.strip() and department != "Semua":
        query = query.filter(ChurchStructure.department == department.strip())
        
    return query.order_by(ChurchStructure.hierarchy_level.asc(), ChurchStructure.sort_order.asc(), ChurchStructure.id.asc()).all()

@router.post("/", response_model=ChurchStructureResponse, status_code=status.HTTP_201_CREATED)
def create_church_structure(
    *,
    db: Session = Depends(deps.get_db),
    item_in: ChurchStructureCreate,
) -> Any:
    clean_code = item_in.church_code.strip().upper() if item_in.church_code else None
    
    db_obj = ChurchStructure(
        church_id=item_in.church_id,
        church_code=clean_code,
        name=item_in.name.strip(),
        title=item_in.title.strip() if item_in.title else None,
        role_position=item_in.role_position.strip(),
        hierarchy_level=item_in.hierarchy_level or 2,
        department=item_in.department.strip() if item_in.department else "BPH",
        parent_id=item_in.parent_id,
        ministry_id=item_in.ministry_id,
        phone=item_in.phone.strip() if item_in.phone else None,
        email=item_in.email.strip() if item_in.email else None,
        period=item_in.period.strip() if item_in.period else "2024 - 2029",
        photo_url=item_in.photo_url.strip() if item_in.photo_url else None,
        notes=item_in.notes.strip() if item_in.notes else None,
        status=item_in.status or "Aktif",
        sort_order=item_in.sort_order or 0,
    )
    db.add(db_obj)
    db.flush()
    
    # INTEGRASI OTOMATIS: Jika ditautkan ke lembaga pelayanan, update PIC lembaga tersebut
    if item_in.ministry_id:
        ministry = db.query(ChurchMinistry).filter(ChurchMinistry.id == item_in.ministry_id).first()
        if ministry:
            ministry.leader_structure_id = db_obj.id
            ministry.leader_name = db_obj.name
            ministry.leader_title = db_obj.title or db_obj.role_position
            if db_obj.phone: ministry.phone = db_obj.phone
            if db_obj.email: ministry.email = db_obj.email
            
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{item_id}", response_model=ChurchStructureResponse)
def update_church_structure(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    item_in: ChurchStructureUpdate,
) -> Any:
    db_obj = db.query(ChurchStructure).filter(ChurchStructure.id == item_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Data pejabat struktur tidak ditemukan")
        
    update_data = item_in.model_dump(exclude_unset=True)
    if "church_code" in update_data and update_data["church_code"]:
        update_data["church_code"] = update_data["church_code"].strip().upper()
        
    for field, value in update_data.items():
        setattr(db_obj, field, value)
        
    # SINKRONISASI OTOMATIS KE LEMBAGA PELAYANAN
    if db_obj.ministry_id:
        ministry = db.query(ChurchMinistry).filter(ChurchMinistry.id == db_obj.ministry_id).first()
        if ministry:
            ministry.leader_structure_id = db_obj.id
            if db_obj.name: ministry.leader_name = db_obj.name
            if db_obj.phone: ministry.phone = db_obj.phone
            if db_obj.email: ministry.email = db_obj.email
            
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_church_structure(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
) -> Any:
    db_obj = db.query(ChurchStructure).filter(ChurchStructure.id == item_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Data pejabat struktur tidak ditemukan")
    
    # Lepas tautan pada church_ministries sebelum hapus
    db.query(ChurchMinistry).filter(ChurchMinistry.leader_structure_id == item_id).update({"leader_structure_id": None})
    
    # Reassign subordinates parent_id to parent of deleted node or None
    parent_of_deleted = db_obj.parent_id
    db.query(ChurchStructure).filter(ChurchStructure.parent_id == item_id).update({"parent_id": parent_of_deleted})
    
    db.delete(db_obj)
    db.commit()
    return {"message": "Data pejabat struktur berhasil dihapus", "id": item_id}
