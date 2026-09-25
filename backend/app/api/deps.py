from typing import Any, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.user_service import UserService
from app.services.main_admin_service import MainAdminService
from app.services.church_admin_service import ChurchAdminService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, TypeError, ValueError):
        raise credentials_exception
    
    if token_data.sub is None:
        raise credentials_exception
        
    sub = str(token_data.sub)
    if sub.startswith("main_admin:") or sub.startswith("admin:"):
        admin_id = sub.split(":", 1)[1]
        admin = MainAdminService.get_by_id(db, dev_id=admin_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        return admin
    elif sub.startswith("church:") or sub.startswith("church_admin:"):
        try:
            church_admin_id = int(sub.split(":", 1)[1])
        except (TypeError, ValueError):
            raise credentials_exception
        church_admin = ChurchAdminService.get_by_id(db, admin_id=church_admin_id)
        if not church_admin:
            raise HTTPException(status_code=404, detail="Church admin not found")
        return church_admin
    elif sub.startswith("jemaat:"):
        try:
            user_id = int(sub.split(":", 1)[1])
        except (TypeError, ValueError):
            raise credentials_exception
        user = UserService.get_by_id(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    else:
        # Fallback for plain IDs
        try:
            numeric_id = int(sub)
        except ValueError:
            raise credentials_exception
        user = UserService.get_by_id(db, user_id=numeric_id)
        if user:
            return user
        admin = MainAdminService.get_by_id(db, dev_id=numeric_id)
        if admin:
            return admin
        raise HTTPException(status_code=404, detail="User not found")

def get_current_active_user(
    current_user: Any = Depends(get_current_user),
) -> Any:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_superadmin(
    current_user: Any = Depends(get_current_active_user),
) -> Any:
    if getattr(current_user, "role", None) != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses DBMS hanya untuk superadmin.")
    return current_user
