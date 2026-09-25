from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract
from app.models.agenda import ChurchAgenda
from app.schemas.agenda import AgendaCreate, AgendaUpdate

class AgendaService:
    @staticmethod
    def get_by_id(db: Session, agenda_id: int) -> Optional[ChurchAgenda]:
        return db.query(ChurchAgenda).filter(ChurchAgenda.id == agenda_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 200,
        year: Optional[int] = None,
        month: Optional[int] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        church_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[ChurchAgenda]:
        query = db.query(ChurchAgenda)

        if year is not None:
            query = query.filter(extract("year", ChurchAgenda.start_date) == year)

        if month is not None:
            query = query.filter(extract("month", ChurchAgenda.start_date) == month)

        if category and category.lower() != "semua":
            query = query.filter(ChurchAgenda.category == category)

        if status and status.lower() != "semua":
            query = query.filter(ChurchAgenda.status == status)

        if church_id is not None:
            query = query.filter(
                or_(
                    ChurchAgenda.church_id == church_id,
                    ChurchAgenda.church_id == None,
                )
            )

        if search:
            q = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    ChurchAgenda.title.ilike(q),
                    ChurchAgenda.description.ilike(q),
                    ChurchAgenda.location.ilike(q),
                    ChurchAgenda.organizer.ilike(q),
                    ChurchAgenda.church_name.ilike(q),
                )
            )

        return query.order_by(ChurchAgenda.start_date.asc(), ChurchAgenda.start_time.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, obj_in: AgendaCreate) -> ChurchAgenda:
        db_obj = ChurchAgenda(
            title=obj_in.title,
            description=obj_in.description,
            category=obj_in.category or "Kegiatan Umum",
            start_date=obj_in.start_date,
            end_date=obj_in.end_date,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            location=obj_in.location,
            church_id=obj_in.church_id,
            church_name=obj_in.church_name or "Semua Cabang",
            organizer=obj_in.organizer,
            target_audience=obj_in.target_audience or "Semua Jemaat",
            status=obj_in.status or "Akan Datang",
            color=obj_in.color or "amber",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, db_obj: ChurchAgenda, obj_in: AgendaUpdate) -> ChurchAgenda:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, agenda_id: int) -> Optional[ChurchAgenda]:
        db_obj = db.query(ChurchAgenda).filter(ChurchAgenda.id == agenda_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj
