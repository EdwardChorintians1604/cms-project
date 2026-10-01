from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.church_ministry import ChurchMinistry
from app.models.church_structure import ChurchStructure
from app.models.church_admin import ChurchAdmin
from app.schemas.church_ministry import (
    ChurchMinistryCreate,
    ChurchMinistryUpdate,
    ChurchMinistryResponse,
)

router = APIRouter()

@router.get("/", response_model=List[ChurchMinistryResponse])
def get_church_ministries(
    db: Session = Depends(deps.get_db),
    church_code: Optional[str] = Query(None),
    church_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
) -> Any:
    query = db.query(ChurchMinistry)
    
    if church_code and church_code.strip() and church_code.strip().upper() not in ["DEFAULT", "UNDEFINED", "NULL", ""]:
        query = query.filter(ChurchMinistry.church_code == church_code.strip().upper())
        
    if church_id is not None:
        query = query.filter(ChurchMinistry.church_id == church_id)
        
    if category and category.strip() and category != "Semua":
        query = query.filter(ChurchMinistry.category == category.strip())
        
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (ChurchMinistry.name.ilike(term)) |
            (ChurchMinistry.leader_name.ilike(term)) |
            (ChurchMinistry.code.ilike(term)) |
            (ChurchMinistry.description.ilike(term))
        )
        
    return query.order_by(ChurchMinistry.sort_order.asc(), ChurchMinistry.id.asc()).all()

@router.post("/", response_model=ChurchMinistryResponse, status_code=status.HTTP_201_CREATED)
def create_church_ministry(
    *,
    db: Session = Depends(deps.get_db),
    item_in: ChurchMinistryCreate,
) -> Any:
    clean_code = item_in.church_code.strip().upper() if item_in.church_code else None
    leader_id = item_in.leader_structure_id
    leader_name = item_in.leader_name.strip() if item_in.leader_name else None
    leader_title = item_in.leader_title.strip() if item_in.leader_title else "Koordinator"
    phone = item_in.phone.strip() if item_in.phone else None
    email = item_in.email.strip() if item_in.email else None
    
    # INTEGRASI OTOMATIS: Jika leader_structure_id dipilih, tarik data profil pejabat
    if leader_id:
        existing_officer = db.query(ChurchStructure).filter(ChurchStructure.id == leader_id).first()
        if existing_officer:
            leader_name = existing_officer.name
            leader_title = existing_officer.title or existing_officer.role_position
            if not phone: phone = existing_officer.phone
            if not email: email = existing_officer.email
    elif leader_name and clean_code:
        # Jika nama ketua diketik baru, cek apakah sudah ada di church_structures
        existing_officer = db.query(ChurchStructure).filter(
            ChurchStructure.church_code == clean_code,
            ChurchStructure.name.ilike(leader_name)
        ).first()
        if existing_officer:
            leader_id = existing_officer.id
            leader_title = existing_officer.title or existing_officer.role_position
            if not phone: phone = existing_officer.phone
            if not email: email = existing_officer.email
        else:
            # Cari atasan default (Wakil Gembala Lvl 2 atau Gembala Lvl 1)
            default_parent = db.query(ChurchStructure).filter(
                ChurchStructure.church_code == clean_code,
                ChurchStructure.hierarchy_level.in_([1, 2])
            ).order_by(ChurchStructure.hierarchy_level.desc()).first()

            # Otomatis buatkan record di Struktur Kepemimpinan Gereja (Level 3 - Koordinator)
            new_officer = ChurchStructure(
                church_id=item_in.church_id,
                church_code=clean_code,
                name=leader_name,
                title=leader_title,
                role_position=f"Koordinator {item_in.name}",
                hierarchy_level=3,
                department=item_in.category or "Pelayanan",
                parent_id=default_parent.id if default_parent else None,
                phone=phone,
                email=email,
                notes=f"Koordinator Lembaga Pelayanan {item_in.name} (Tersinkronisasi Otomatis)",
                status="Aktif",
                sort_order=5
            )
            db.add(new_officer)
            db.flush()
            leader_id = new_officer.id

    db_obj = ChurchMinistry(
        church_id=item_in.church_id,
        church_code=clean_code,
        name=item_in.name.strip(),
        code=item_in.code.strip().upper() if item_in.code else None,
        category=item_in.category.strip() if item_in.category else "Kategorial Usia",
        leader_structure_id=leader_id,
        leader_name=leader_name,
        leader_title=leader_title,
        phone=phone,
        email=email,
        member_count=item_in.member_count or 0,
        meeting_schedule=item_in.meeting_schedule.strip() if item_in.meeting_schedule else None,
        location_room=item_in.location_room.strip() if item_in.location_room else None,
        budget_allocation=item_in.budget_allocation.strip() if item_in.budget_allocation else None,
        description=item_in.description.strip() if item_in.description else None,
        vision_mission=item_in.vision_mission.strip() if item_in.vision_mission else None,
        logo_url=item_in.logo_url.strip() if item_in.logo_url else None,
        status=item_in.status or "Aktif",
        sort_order=item_in.sort_order or 0,
    )
    db.add(db_obj)
    db.flush()
    
    # Tautkan kembali ministry_id pada officer
    if leader_id:
        officer = db.query(ChurchStructure).filter(ChurchStructure.id == leader_id).first()
        if officer:
            officer.ministry_id = db_obj.id
            
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{item_id}", response_model=ChurchMinistryResponse)
def update_church_ministry(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    item_in: ChurchMinistryUpdate,
) -> Any:
    db_obj = db.query(ChurchMinistry).filter(ChurchMinistry.id == item_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Lembaga Pelayanan tidak ditemukan")
        
    update_data = item_in.model_dump(exclude_unset=True)
    if "church_code" in update_data and update_data["church_code"]:
        update_data["church_code"] = update_data["church_code"].strip().upper()
    if "code" in update_data and update_data["code"]:
        update_data["code"] = update_data["code"].strip().upper()
        
    for field, value in update_data.items():
        setattr(db_obj, field, value)
        
    # SINKRONISASI KE STRUKTUR GEREJA JIKA ADA PERUBAHAN PIC
    if db_obj.leader_structure_id:
        officer = db.query(ChurchStructure).filter(ChurchStructure.id == db_obj.leader_structure_id).first()
        if officer:
            officer.ministry_id = db_obj.id
            if db_obj.leader_name: officer.name = db_obj.leader_name
            if db_obj.phone: officer.phone = db_obj.phone
            if db_obj.email: officer.email = db_obj.email
            if db_obj.category: officer.department = db_obj.category
            
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_church_ministry(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
) -> Any:
    db_obj = db.query(ChurchMinistry).filter(ChurchMinistry.id == item_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Lembaga Pelayanan tidak ditemukan")
    
    # Lepas tautan pada church_structures sebelum hapus
    db.query(ChurchStructure).filter(ChurchStructure.ministry_id == item_id).update({"ministry_id": None})
    db.delete(db_obj)
    db.commit()
    return {"message": "Lembaga Pelayanan berhasil dihapus", "id": item_id}

@router.post("/seed-default", response_model=List[ChurchMinistryResponse])
def seed_default_ministries(
    *,
    db: Session = Depends(deps.get_db),
    church_code: str = Query(...),
    church_id: Optional[int] = Query(None),
) -> Any:
    clean_code = church_code.strip().upper()
    existing = db.query(ChurchMinistry).filter(ChurchMinistry.church_code == clean_code).count()
    if existing > 0:
        return db.query(ChurchMinistry).filter(ChurchMinistry.church_code == clean_code).order_by(ChurchMinistry.sort_order.asc()).all()
        
    admin = db.query(ChurchAdmin).filter(ChurchAdmin.church_code == clean_code).first()
    target_church_id = church_id or (admin.church_id if admin else None)
    
    # Ambil officer struktur yang cocok untuk ditautkan otomatis
    structures = db.query(ChurchStructure).filter(ChurchStructure.church_code == clean_code).all()
    struct_map = {s.name.lower(): s.id for s in structures}
    
    default_ministries = [
        {
            "name": "Komisi Pelayanan Anak & Sekolah Minggu",
            "code": "KPA-SM",
            "category": "Kategorial Usia",
            "leader_name": "Ev. Maria Magdalena, S.Th",
            "leader_title": "Koordinator",
            "phone": "085299881122",
            "email": "sekolahminggu@gracepoint.or.id",
            "member_count": 24,
            "meeting_schedule": "Setiap Minggu, 08:30 WIB",
            "location_room": "Ruang Hall Sekolah Minggu Lt. 2",
            "budget_allocation": "Kas Anggaran Anak Cabang",
            "description": "Pembinaan karakter dan iman rohani anak-anak usia balita hingga tunas remaja.",
            "vision_mission": "Membentuk generasi anak yang berakar, bertumbuh, dan berbuah dalam kasih Kristus sejak dini.",
            "status": "Aktif",
            "sort_order": 1
        },
        {
            "name": "Komisi Pemuda & Remaja (Youth & Teens Fellowship)",
            "code": "KPR-YOUTH",
            "category": "Kategorial Usia",
            "leader_name": "Daniel Pratama, S.Kom",
            "leader_title": "Ketua Komisi",
            "phone": "081988776655",
            "email": "youth@gracepoint.or.id",
            "member_count": 45,
            "meeting_schedule": "Setiap Sabtu, 18:30 WIB",
            "location_room": "Ruang Youth Hall Lt. 3",
            "budget_allocation": "Kas Pemuda Cabang",
            "description": "Wadah persekutuan, pertumbuhan rohani, dan ekspresi kreatif generasi muda gereja.",
            "vision_mission": "Menjadi terang dan garam dunia dengan integritas rohani serta dedikasi karya di era digital.",
            "status": "Aktif",
            "sort_order": 2
        },
        {
            "name": "Departemen Musik, Pujian & Multimedia (Worship & Tech)",
            "code": "DMPM-W&M",
            "category": "Musik & Ibadah",
            "leader_name": "Timothy Christian, S.Sn",
            "leader_title": "Koordinator Bidang",
            "phone": "082166778899",
            "email": "worship@gracepoint.or.id",
            "member_count": 35,
            "meeting_schedule": "Latihan: Kamis & Sabtu, 19:00 WIB",
            "location_room": "Main Sanctuary & Ruang Audio Visual",
            "budget_allocation": "Kas Operasional Ibadah",
            "description": "Mengoordinasikan tim Praise & Worship, Visual, Sound System, dan Siaran Live Streaming.",
            "vision_mission": "Memimpin jemaat masuk dalam hadirat Tuhan melalui penyembahan yang berjiwa dan teknologi yang unggul.",
            "status": "Aktif",
            "sort_order": 3
        },
        {
            "name": "Lembaga Pelayanan Diakonia, Doa Syafaat & Sosial",
            "code": "LPD-DIAK",
            "category": "Diakonia & Doa",
            "leader_name": "Pnt. Lukas Marbun",
            "leader_title": "Koordinator",
            "phone": "081377441199",
            "email": "diakonia@gracepoint.or.id",
            "member_count": 18,
            "meeting_schedule": "Doa Pagi: Selasa & Kamis 05:30 WIB",
            "location_room": "Ruang Doa Betania & Kantor Diakonia",
            "budget_allocation": "Kas Kasih & Sosial Jemaat",
            "description": "Pelayanan doa syafaat, perkunjungan jemaat sakit, dan santunan kasih bagi sesama.",
            "vision_mission": "Mewujudkan kasih nyata Kristus bagi jemaat dan sesama yang berbeban berat.",
            "status": "Aktif",
            "sort_order": 4
        },
        {
            "name": "Persekutuan Kaum Wanita / Kaum Ibu (Women Fellowship)",
            "code": "PKW-IBU",
            "category": "Kategorial Usia",
            "leader_name": "Ibu Ruth Simanjuntak, S.Pd",
            "leader_title": "Ketua Komisi",
            "phone": "081266334411",
            "email": "kaumwanita@gracepoint.or.id",
            "member_count": 50,
            "meeting_schedule": "Setiap Rabu, 16:30 WIB",
            "location_room": "Ruang Serbaguna Jemaat",
            "budget_allocation": "Kas Kaum Ibu Cabang",
            "description": "Wadah persekutuan rohani para ibu jemaat dalam membangun keluarga berlandaskan firman.",
            "vision_mission": "Membangun wanita bijak yang menjadi tiang doa keluarga dan gereja.",
            "status": "Aktif",
            "sort_order": 5
        },
        {
            "name": "Persekutuan Kaum Pria / Kaum Bapa (Men of Valor)",
            "code": "PKP-BAPA",
            "category": "Kategorial Usia",
            "leader_name": "Pnt. Andreas Halim, M.M",
            "leader_title": "Ketua Komisi",
            "phone": "081199443322",
            "email": "kaumbapa@gracepoint.or.id",
            "member_count": 42,
            "meeting_schedule": "Setiap Jumat Minggu ke-2 & ke-4, 19:30 WIB",
            "location_room": "Ruang Pertemuan Majelis",
            "budget_allocation": "Kas Kaum Bapa Cabang",
            "description": "Pembinaan kepemimpinan rohani para kepala keluarga dan persekutuan doa para ayah.",
            "vision_mission": "Membangkitkan para pria beriman teguh yang memimpin keluarga dalam takut akan Tuhan.",
            "status": "Aktif",
            "sort_order": 6
        },
        {
            "name": "Komisi Misi, Penginjilan & Komunitas Sel (Rayon)",
            "code": "KMP-MISI",
            "category": "Misi & Penginjilan",
            "leader_name": "Pnt. Markus Sitorus, S.E",
            "leader_title": "Koordinator Misi",
            "phone": "081399887766",
            "email": "misi@gracepoint.or.id",
            "member_count": 28,
            "meeting_schedule": "Komsel Rayon: Setiap Kamis, 19:30 WIB",
            "location_room": "Sekretariat Misi & Rumah-rumah Rayon",
            "budget_allocation": "Kas Misi & Perintisan Cabang",
            "description": "Mengoordinasikan persekutuan sel (Rayon), penginjilan pribadi, dan bakti sosial.",
            "vision_mission": "Menjangkau jiwa bagi Kristus dan memuridkan jemaat melalui komunitas sel.",
            "status": "Aktif",
            "sort_order": 7
        }
    ]
    
    created_list = []
    for item in default_ministries:
        matched_officer_id = struct_map.get(item["leader_name"].lower())
        db_obj = ChurchMinistry(
            church_id=target_church_id,
            church_code=clean_code,
            leader_structure_id=matched_officer_id,
            **item
        )
        db.add(db_obj)
        db.flush()
        
        # Link back officer to ministry
        if matched_officer_id:
            db.query(ChurchStructure).filter(ChurchStructure.id == matched_officer_id).update({"ministry_id": db_obj.id})
            
        created_list.append(db_obj)
        
    db.commit()
    for item in created_list:
        db.refresh(item)
    return created_list
