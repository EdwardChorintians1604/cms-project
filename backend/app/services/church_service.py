from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.church import Church
from app.schemas.church import ChurchCreate, ChurchUpdate

class ChurchService:
    @staticmethod
    def get_by_id(db: Session, church_id: int) -> Optional[Church]:
        return db.query(Church).filter(Church.id == church_id).first()

    @staticmethod
    def get_by_code(db: Session, church_code: str) -> Optional[Church]:
        return db.query(Church).filter(Church.church_code == church_code).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Church]:
        return db.query(Church).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, obj_in: ChurchCreate) -> Church:
        db_obj = Church(
            church_code=obj_in.church_code,
            church_name=obj_in.church_name,
            established_date=obj_in.established_date,
            bpp_general_chairman=obj_in.bpp_general_chairman,
            church_description=obj_in.church_description,
            address=obj_in.address,
            city=obj_in.city,
            latitude=obj_in.latitude,
            longitude=obj_in.longitude,
            google_maps_url=obj_in.google_maps_url,
            facebook_name=obj_in.facebook_name,
            facebook_link=obj_in.facebook_link,
            instagram_name=obj_in.instagram_name,
            instagram_link=obj_in.instagram_link,
            youtube_name=obj_in.youtube_name,
            youtube_link=obj_in.youtube_link,
            tiktok_name=obj_in.tiktok_name,
            tiktok_link=obj_in.tiktok_link,
            status=obj_in.status or "Aktif"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, db_obj: Church, obj_in: ChurchUpdate) -> Church:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, church_id: int) -> Optional[Church]:
        db_obj = db.query(Church).filter(Church.id == church_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj
