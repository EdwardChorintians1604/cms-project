from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.main_admin import MainAdmin

router = APIRouter()


@router.post("/login")
def login_main_admin(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    admin = (
        db.query(MainAdmin)
        .filter(
            (MainAdmin.email == form_data.username)
            | (MainAdmin.username == form_data.username)
        )
        .first()
    )

    if not admin or not admin.is_active or not security.verify_password(
        form_data.password, admin.password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, username, atau password admin utama salah.",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            f"main_admin:{admin.development_id}",
            expires_delta=access_token_expires,
        ),
        "token_type": "bearer",
        "user": {
            "id": admin.development_id,
            "email": admin.email,
            "username": admin.username,
            "full_name": admin.full_name,
            "role": admin.role,
            "is_active": admin.is_active,
        },
    }