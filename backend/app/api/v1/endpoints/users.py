from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.get("/me")
def read_user_me(
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    role = getattr(current_user, "role", "jemaat")
    if role == "church_admin":
        return {
            "id": current_user.id,
            "church_id": current_user.church_id,
            "church_code": current_user.church_code,
            "church_name": current_user.church_name,
            "city": current_user.city,
            "admin_name": current_user.admin_name,
            "email": current_user.email,
            "phone": current_user.phone,
            "address": getattr(current_user, "address", None),
            "latitude": getattr(current_user, "latitude", None),
            "longitude": getattr(current_user, "longitude", None),
            "google_maps_url": getattr(current_user, "google_maps_url", None),
            "role": "church_admin",
            "status": current_user.status,
        }
    elif role == "superadmin":
        return {
            "id": getattr(current_user, "id", None),
            "development_id": getattr(current_user, "development_id", None),
            "developer_name": getattr(current_user, "developer_name", "Super Administrator"),
            "email": getattr(current_user, "email", "admin@gracepoint.or.id"),
            "role": "superadmin",
        }
    return current_user

@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    user = UserService.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="User dengan email ini sudah terdaftar.",
        )
    user = UserService.create(db, obj_in=user_in)
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    user = UserService.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan.",
        )
    user = UserService.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
) -> Any:
    user = UserService.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan.",
        )
    user = UserService.delete(db, user_id=user_id)
    return user
