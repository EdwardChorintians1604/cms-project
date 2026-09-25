from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.informasi_pelayanan import InformasiPelayanan
from app.schemas.informasi_pelayanan import InformasiPelayananCreate, InformasiPelayananUpdate

class InformasiPelayananService:
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        church_admin_id: Optional[int] = None,
        church_id: Optional[int] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[InformasiPelayanan]:
        query = db.query(InformasiPelayanan)

        if church_admin_id is not None:
            query = query.filter(InformasiPelayanan.church_admin_id == church_admin_id)

        if church_id is not None:
            query = query.filter(InformasiPelayanan.church_id == church_id)

        if category and category != "Semua":
            query = query.filter(InformasiPelayanan.category == category)

        if status and status != "Semua":
            query = query.filter(InformasiPelayanan.status == status)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    InformasiPelayanan.service_name.ilike(term),
                    InformasiPelayanan.church_name.ilike(term),
                    InformasiPelayanan.city.ilike(term),
                    InformasiPelayanan.description.ilike(term),
                    InformasiPelayanan.pic_name.ilike(term),
                    InformasiPelayanan.location_room.ilike(term),
                )
            )

        return query.order_by(InformasiPelayanan.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, item_id: int) -> Optional[InformasiPelayanan]:
        return db.query(InformasiPelayanan).filter(InformasiPelayanan.id == item_id).first()

    @staticmethod
    def create(db: Session, obj_in: InformasiPelayananCreate) -> InformasiPelayanan:
        db_obj = InformasiPelayanan(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(
        db: Session,
        db_obj: InformasiPelayanan,
        obj_in: InformasiPelayananUpdate,
    ) -> InformasiPelayanan:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, item_id: int) -> Optional[InformasiPelayanan]:
        db_obj = db.query(InformasiPelayanan).filter(InformasiPelayanan.id == item_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj
