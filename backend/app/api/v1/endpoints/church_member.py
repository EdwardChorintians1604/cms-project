from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api import deps
from app.models.church_member import ChurchMember
from app.models.church import Church
from app.schemas.church_member import (
    ChurchMemberCreate,
    ChurchMemberUpdate,
    ChurchMemberResponse
)

router = APIRouter()

@router.get("/", response_model=List[ChurchMemberResponse])
def get_church_members(
    church_code: Optional[str] = Query(None, description="Kode Cabang Gereja"),
    search: Optional[str] = Query(None, description="Pencarian nama, no HP, atau No Anggota"),
    attendance_status: Optional[str] = Query(None, description="Filter keaktifan"),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(deps.get_db)
):
    query = db.query(ChurchMember)

    if church_code and church_code != "DEFAULT":
        query = query.filter(ChurchMember.church_code == church_code)
    
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                ChurchMember.name.ilike(search_fmt),
                ChurchMember.phone.ilike(search_fmt),
                ChurchMember.member_no.ilike(search_fmt),
                ChurchMember.email.ilike(search_fmt)
            )
        )

    if attendance_status and attendance_status != "all":
        query = query.filter(ChurchMember.attendance_status == attendance_status)

    members = query.order_by(ChurchMember.id.asc()).offset(skip).limit(limit).all()
    
    # Auto-seed initial sample members if completely empty for this church
    if len(members) == 0 and church_code and church_code != "DEFAULT":
        seed_default_members(church_code=church_code, db=db)
        members = db.query(ChurchMember).filter(ChurchMember.church_code == church_code).order_by(ChurchMember.id.asc()).all()

    return members

@router.get("/{member_id}", response_model=ChurchMemberResponse)
def get_church_member(
    member_id: int,
    db: Session = Depends(deps.get_db)
):
    member = db.query(ChurchMember).filter(ChurchMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Data jemaat tidak ditemukan")
    return member

@router.post("/", response_model=ChurchMemberResponse, status_code=status.HTTP_201_CREATED)
def create_church_member(
    payload: ChurchMemberCreate,
    db: Session = Depends(deps.get_db)
):
    # Resolve church_id if missing
    church_id = payload.church_id
    if not church_id and payload.church_code:
        ch = db.query(Church).filter(Church.church_code == payload.church_code).first()
        if ch:
            church_id = ch.id

    # Auto-generate member_no if empty
    member_no = payload.member_no
    if not member_no:
        total_for_church = db.query(ChurchMember).filter(ChurchMember.church_code == payload.church_code).count()
        member_no = f"JM-{str(total_for_church + 1).zfill(3)}"

    member_data = payload.model_dump()
    member_data["church_id"] = church_id
    member_data["member_no"] = member_no

    new_member = ChurchMember(**member_data)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.put("/{member_id}", response_model=ChurchMemberResponse)
def update_church_member(
    member_id: int,
    payload: ChurchMemberUpdate,
    db: Session = Depends(deps.get_db)
):
    member = db.query(ChurchMember).filter(ChurchMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Data jemaat tidak ditemukan")

    update_dict = payload.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(member, field, val)

    db.commit()
    db.refresh(member)
    return member

@router.delete("/{member_id}")
def delete_church_member(
    member_id: int,
    db: Session = Depends(deps.get_db)
):
    member = db.query(ChurchMember).filter(ChurchMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Data jemaat tidak ditemukan")

    db.delete(member)
    db.commit()
    return {"status": "success", "message": f"Data jemaat {member.name} berhasil dihapus"}

@router.post("/seed-default", status_code=status.HTTP_201_CREATED)
def seed_default_endpoint(
    church_code: str = Query("GBI-PAD-11", description="Kode Cabang Gereja"),
    db: Session = Depends(deps.get_db)
):
    return seed_default_members(church_code=church_code, db=db)

def seed_default_members(church_code: str, db: Session):
    gbi = db.query(Church).filter(Church.church_code == church_code).first()
    church_id = gbi.id if gbi else None

    defaults = [
        {
            "member_no": "JM-001",
            "name": "Budi Santoso",
            "gender": "L",
            "phone": "081234567890",
            "email": "budi.santoso@email.com",
            "family_role": "Kepala Keluarga",
            "birthdate": date(1985, 9, 26),
            "status_baptis": "Sudah Baptis & Sidi",
            "attendance_status": "Aktif",
            "last_attended": date(2026, 9, 20),
            "address": "Jl. Melati No. 12, Padang",
            "notes": "Aktif dalam persekutuan kaum bapa."
        },
        {
            "member_no": "JM-002",
            "name": "Maria Anggraini",
            "gender": "P",
            "phone": "081298765432",
            "email": "maria.anggraini@email.com",
            "family_role": "Istri",
            "birthdate": date(1988, 4, 12),
            "status_baptis": "Sudah Baptis & Sidi",
            "attendance_status": "Aktif",
            "last_attended": date(2026, 9, 20),
            "address": "Jl. Melati No. 12, Padang",
            "notes": "Pelayan guru sekolah minggu."
        },
        {
            "member_no": "JM-003",
            "name": "David Wijaya",
            "gender": "L",
            "phone": "081344556677",
            "email": "david.wijaya@email.com",
            "family_role": "Pemuda",
            "birthdate": date(2001, 9, 25),
            "status_baptis": "Sudah Baptis",
            "attendance_status": "Perhatian Khusus",
            "last_attended": date(2026, 8, 30),
            "address": "Jl. Mawar Raya Blok C-4, Padang",
            "notes": "Perlu kunjungan pastoral, absen ibadah > 3 pekan karena lembur tugas."
        },
        {
            "member_no": "JM-004",
            "name": "Yohanes Kristianto",
            "gender": "L",
            "phone": "081577889900",
            "email": "yohanes.k@email.com",
            "family_role": "Kepala Keluarga",
            "birthdate": date(1979, 11, 3),
            "status_baptis": "Sudah Baptis & Sidi",
            "attendance_status": "Aktif",
            "last_attended": date(2026, 9, 20),
            "address": "Kompleks Anggrek Asri No. 8, Padang",
            "notes": "Koordinator tim usher & penerima tamu."
        },
        {
            "member_no": "JM-005",
            "name": "Ruth Natalia",
            "gender": "P",
            "phone": "081711223344",
            "email": "ruth.natalia@email.com",
            "family_role": "Pemudi",
            "birthdate": date(2003, 1, 19),
            "status_baptis": "Sudah Baptis",
            "attendance_status": "Perhatian Khusus",
            "last_attended": date(2026, 8, 23),
            "address": "Jl. Mawar Indah No. 19, Padang",
            "notes": "Mahasiswi perantauan, perlu follow-up komisi pemuda."
        },
        {
            "member_no": "JM-006",
            "name": "Hendra Setiawan",
            "gender": "L",
            "phone": "081822334455",
            "email": "hendra.setiawan@email.com",
            "family_role": "Kepala Keluarga",
            "birthdate": date(1982, 9, 28),
            "status_baptis": "Sudah Baptis & Sidi",
            "attendance_status": "Aktif",
            "last_attended": date(2026, 9, 20),
            "address": "Jl. Kenanga Baru No. 45, Padang",
            "notes": "Keluarga jemaat aktif."
        },
    ]

    added = []
    for d in defaults:
        exists = db.query(ChurchMember).filter(
            ChurchMember.church_code == church_code,
            ChurchMember.member_no == d["member_no"]
        ).first()
        if not exists:
            m = ChurchMember(church_id=church_id, church_code=church_code, **d)
            db.add(m)
            added.append(d["name"])

    if added:
        db.commit()
    return {"status": "success", "message": f"Seeded {len(added)} members", "added": added}
