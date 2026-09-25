from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.schemas.church_admin import ChurchAdminCreate, ChurchAdminResponse
from app.services.user_service import UserService
from app.services.main_admin_service import MainAdminService
from app.services.church_admin_service import ChurchAdminService
from app.core.rate_limit import limiter

router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT BARU: UNIFIED SINGLE LOGIN (Deteksi Role Otomatis di Server)
# Menggantikan sistem trial-error 3x request dari frontend.
# Frontend cukup kirim 1 request → server deteksi role → kembalikan token + role.
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/unified-login")
@limiter.limit("10/10minutes")
def unified_login(
    request: Request,
    db: Session = Depends(deps.get_db),
    username: str = Form(...),
    password: str = Form(...),
    security_pin: str | None = Form(default=None),
    church_code: str | None = Form(default=None),
) -> Any:
    """
    Login terpadu satu jalur.
    Server mendeteksi role secara otomatis: superadmin → church_admin → jemaat.
    Hanya 1 request per percobaan login (anti rate-limit abuse).
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 1. Cek apakah ini Admin Utama (main_admin)
    admin = MainAdminService.authenticate(db, identifier=username, password=password)
    if admin:
        # Jika security_pin diberikan, wajib valid
        if security_pin:
            if not MainAdminService.verify_security_pin(admin, security_pin):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="PIN keamanan 2FA tidak valid.",
                )
        token = security.create_access_token(
            f"admin:{admin.development_id}", expires_delta=access_token_expires
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "superadmin",
        }

    # 2. Cek apakah ini Admin Gereja Cabang (church_admins)
    church_admin = ChurchAdminService.get_by_login_identifier(db, identifier=username)
    if church_admin and security.verify_password(password, church_admin.password):
        if church_admin.status != "Aktif":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun Admin Gereja belum aktif atau telah dinonaktifkan.",
            )
        if church_code and church_code.strip():
            code_upper = church_code.strip().upper()
            matches_branch = bool(church_admin.church_code and church_admin.church_code.upper() == code_upper)
            matches_parent = bool(church_admin.church and church_admin.church.church_code and church_admin.church.church_code.upper() == code_upper)
            if not (matches_branch or matches_parent):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Kode gereja tidak sesuai dengan akun ini.",
                )
        token = security.create_access_token(
            f"church_admin:{church_admin.id}", expires_delta=access_token_expires
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "church_admin",
        }

    # 3. Cek apakah ini Jemaat Terdaftar (jemaat_users)
    user = UserService.authenticate(db, email=username, password=password)
    if user:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun jemaat belum aktif.",
            )
        token = security.create_access_token(
            f"jemaat:{user.id}", expires_delta=access_token_expires
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "jemaat",
        }

    # Semua gagal → 401
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email/Username atau kata sandi tidak cocok dengan akun mana pun di sistem.",
    )

# 1. KHUSUS LOGIN ADMIN UTAMA / DEVELOPER (Tabel: main_admin)
@router.post("/main-admin/login", response_model=Token)
@limiter.limit("10/10minutes")
def login_main_admin(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    security_pin: str | None = Form(default=None),
) -> Any:
    admin = MainAdminService.authenticate(
        db, identifier=form_data.username, password=form_data.password
    )
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Akses ditolak. Kredensial bukan milik Admin Utama / Developer."
        )

    if not security_pin or not MainAdminService.verify_security_pin(admin, security_pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN keamanan 2FA Superadmin wajib diisi dan tidak valid.",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            f"admin:{admin.development_id}", expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/church-admin/login", response_model=Token)
@limiter.limit("10/10minutes")
def login_church_admin(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    church_code: str | None = Form(default=None),
) -> Any:
    admin = ChurchAdminService.get_by_login_identifier(db, identifier=form_data.username)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Akses ditolak. Email atau kredensial bukan milik Admin Cabang Gereja terdaftar."
        )

    if church_code and church_code.strip():
        code_upper = church_code.strip().upper()
        matches_branch = bool(admin.church_code and admin.church_code.upper() == code_upper)
        matches_parent = bool(admin.church and admin.church.church_code and admin.church.church_code.upper() == code_upper)
        if not (matches_branch or matches_parent):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Kode gereja cabang yang dipilih tidak sesuai dengan akun ini ({admin.church_name} - {admin.church_code})."
            )

    if admin.status != "Aktif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Akun Admin Cabang Gereja ini sedang nonaktif. Silakan hubungi Main Admin."
        )

    # ⚠️ SECURITY WARNING: Baris berikut adalah backdoor hardcoded password untuk keperluan development.
    # WAJIB DIHAPUS sebelum deployment ke production!
    # TODO: Hapus `or form_data.password == "AdminGereja#2026"` sebelum go-live.
    pw_ok = (
        admin.password == form_data.password
        or security.verify_password(form_data.password, admin.password)
        or form_data.password == "AdminGereja#2026"  # ⚠️ HAPUS DI PRODUCTION
    )
    if not pw_ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kata sandi yang Anda masukkan salah. Silakan periksa kembali kata sandi Anda."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            f"church:{admin.id}", expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/church-admin/register", response_model=ChurchAdminResponse)
def register_church_admin(
    *,
    db: Session = Depends(deps.get_db),
    admin_in: ChurchAdminCreate
) -> Any:
    if admin_in.confirm_password and admin_in.password != admin_in.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Konfirmasi kata sandi tidak cocok.",
        )
    
    existing = ChurchAdminService.get_by_email(db, email=admin_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email admin gereja sudah terdaftar.",
        )

    if MainAdminService.get_by_email(db, email=admin_in.email) or UserService.get_by_email(db, email=admin_in.email):
        raise HTTPException(
            status_code=400,
            detail="Email sudah digunakan oleh akun lain dan tidak dapat dipakai sebagai admin gereja.",
        )
    
    if admin_in.church_code:
        code_check = ChurchAdminService.get_by_church_code(db, church_code=admin_in.church_code.strip().upper())
        if code_check:
            raise HTTPException(
                status_code=400,
                detail=f"Kode gereja cabang '{admin_in.church_code.upper()}' sudah terdaftar. Silakan pilih kode lain.",
            )
    
    return ChurchAdminService.create(db, obj_in=admin_in)

# 3. KHUSUS LOGIN JEMAAT / USER GEREJA (Tabel: jemaat_users)
@router.post("/jemaat/login", response_model=Token)
@router.post("/login", response_model=Token)
@limiter.limit("10/10minutes")
def login_jemaat(
    request: Request,
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = UserService.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/Username atau password jemaat salah."
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Akun jemaat belum aktif."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            f"jemaat:{user.id}", expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate
) -> Any:
    if user_in.confirm_password and user_in.password != user_in.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Konfirmasi kata sandi tidak cocok.",
        )

    user = UserService.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email sudah terdaftar.",
        )

    admin_email = MainAdminService.get_by_email(db, email=user_in.email)
    if admin_email or ChurchAdminService.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=400,
            detail="Email yang sudah terdaftar sebagai admin gereja tidak dapat digunakan untuk akun jemaat.",
        )

    user = UserService.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Username sudah terdaftar.",
        )

    user = UserService.get_by_nik(db, nik=user_in.nik)
    if user:
        raise HTTPException(
            status_code=400,
            detail="NIK sudah terdaftar.",
        )

    return UserService.create(db, obj_in=user_in)
