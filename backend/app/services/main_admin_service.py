from typing import Optional
from sqlalchemy.orm import Session
from app.models.main_admin import MainAdmin
from app.core.security import verify_password

class MainAdminService:
    @staticmethod
    def get_by_id(db: Session, dev_id: str) -> Optional[MainAdmin]:
        return db.query(MainAdmin).filter(MainAdmin.development_id == dev_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[MainAdmin]:
        return db.query(MainAdmin).filter(MainAdmin.email.ilike(email.strip())).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[MainAdmin]:
        return db.query(MainAdmin).filter(MainAdmin.username == username).first()

    @staticmethod
    def get_by_login_identifier(db: Session, identifier: str) -> Optional[MainAdmin]:
        return (
            db.query(MainAdmin)
            .filter(
                (MainAdmin.email == identifier)
                | (MainAdmin.username == identifier)
            )
            .first()
        )

    @staticmethod
    def authenticate(db: Session, identifier: str, password: str) -> Optional[MainAdmin]:
        admin = MainAdminService.get_by_login_identifier(db, identifier=identifier)
        if not admin:
            return None
        # Support both direct match (stored plain text) and hashed password verification
        if admin.password == password:
            return admin
        if verify_password(password, admin.password):
            return admin
        return None

    @staticmethod
    def verify_security_pin(admin: MainAdmin, security_pin: str) -> bool:
        if not admin.dev_token:
            return False
        return admin.dev_token == security_pin or verify_password(security_pin, admin.dev_token)
