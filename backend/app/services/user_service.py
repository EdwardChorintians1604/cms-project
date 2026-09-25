from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email.ilike(email.strip())).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_nik(db: Session, nik: str) -> Optional[User]:
        return db.query(User).filter(User.nik == nik).first()

    @staticmethod
    def get_by_login_identifier(db: Session, identifier: str) -> Optional[User]:
        clean_identifier = identifier.strip()
        return (
            db.query(User)
            .filter(
                (User.email.ilike(clean_identifier))
                | (User.username == clean_identifier)
                | (User.nik == clean_identifier)
            )
            .first()
        )

    @staticmethod
    def create(db: Session, obj_in: UserCreate) -> User:
        db_obj = User(
            full_name=obj_in.full_name,
            birth_place=obj_in.birth_place,
            birth_date=obj_in.birth_date,
            nik=obj_in.nik,
            no_ktp=obj_in.no_ktp,
            gender=obj_in.gender,
            education=obj_in.education,
            church_domisili=obj_in.church_domisili,
            church_central=obj_in.church_central,
            married=obj_in.married,
            chatecication=obj_in.chatecication,
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            phone=obj_in.phone,
            origin=obj_in.origin,
            address=obj_in.address,
            photo_url=obj_in.photo_url,
            is_active=obj_in.is_active if obj_in.is_active is not None else True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, user_id: int) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_by_login_identifier(db, identifier=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
