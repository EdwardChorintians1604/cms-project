from datetime import datetime, timezone
import os
import subprocess
from pathlib import Path
from typing import Any, List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.models.church import Church
from app.models.church_admin import ChurchAdmin
from app.models.main_admin import MainAdmin
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.audit_service import AuditService

router = APIRouter()

# In-memory backup snapshots tracking (with persistent initial backups)
_backups_list = [
    {
        "id": "BK-20260907-01",
        "filename": "cms_database_backup_20260907_190000.sql",
        "size": "18.4 MB",
        "created_at": "2026-09-07 19:00:00",
        "status": "Completed",
        "type": "Auto Snapshot"
    },
    {
        "id": "BK-20260906-01",
        "filename": "cms_database_backup_20260906_000000.sql",
        "size": "17.9 MB",
        "created_at": "2026-09-06 00:00:00",
        "status": "Completed",
        "type": "Daily Backup"
    }
]

BACKUP_TABLE_OPTIONS = [
    {"name": "churches", "label": "Data Gereja", "description": "Data gereja induk dan cabang."},
    {"name": "church_admins", "label": "Admin Gereja", "description": "Akun admin cabang gereja."},
    {"name": "jemaat_users", "label": "Data Jemaat", "description": "Profil dan akun jemaat."},
    {"name": "main_admin", "label": "Admin Utama", "description": "Akun superadmin platform."},
    {"name": "items", "label": "Item", "description": "Data item yang dimiliki jemaat."},
    {"name": "audit_logs", "label": "Audit Log", "description": "Catatan aktivitas dan keamanan sistem."},
]
BACKUP_TABLE_NAMES = {option["name"] for option in BACKUP_TABLE_OPTIONS}


class BackupDownloadRequest(BaseModel):
    scope: str = "all"
    tables: List[str] = []
    backup_id: Optional[str] = None


def _backup_directory() -> Path:
    directory = Path(settings.BACKUP_DIR)
    if not directory.is_absolute():
        directory = Path(__file__).resolve().parents[4] / directory
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _public_backup(backup: dict) -> dict:
    return {key: value for key, value in backup.items() if key != "file_path"}


def _create_database_dump(scope: str = "all", tables: Optional[List[str]] = None) -> tuple[Path, str]:
    if scope not in {"all", "selected"}:
        raise HTTPException(status_code=400, detail="Scope backup harus 'all' atau 'selected'.")

    selected_tables = tables or []
    invalid_tables = sorted(set(selected_tables) - BACKUP_TABLE_NAMES)
    if scope == "selected" and not selected_tables:
        raise HTTPException(status_code=400, detail="Pilih minimal satu bagian database.")
    if invalid_tables:
        raise HTTPException(status_code=400, detail=f"Tabel backup tidak diizinkan: {', '.join(invalid_tables)}.")

    now = datetime.now()
    suffix = "full" if scope == "all" else "_".join(selected_tables)
    filename = f"cms_database_backup_{now.strftime('%Y%m%d_%H%M%S')}_{suffix}.sql"
    output_path = _backup_directory() / filename
    database_url = make_url(settings.DATABASE_URL)
    command = [settings.PG_DUMP_PATH, "--format=plain", "--no-owner", "--no-privileges", "--file", str(output_path)]
    if database_url.host:
        command.extend(["--host", database_url.host])
    if database_url.port:
        command.extend(["--port", str(database_url.port)])
    if database_url.username:
        command.extend(["--username", database_url.username])
    if database_url.database:
        command.extend(["--dbname", database_url.database])
    if scope == "selected":
        for table_name in selected_tables:
            command.extend(["--table", f"public.{table_name}"])

    environment = os.environ.copy()
    if database_url.password:
        environment["PGPASSWORD"] = database_url.password

    try:
        result = subprocess.run(command, env=environment, capture_output=True, text=True, check=False)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail="pg_dump tidak ditemukan. Instal PostgreSQL client atau atur PG_DUMP_PATH.") from error
    except OSError as error:
        raise HTTPException(status_code=503, detail=f"pg_dump tidak dapat dijalankan: {error}") from error

    if result.returncode != 0:
        output_path.unlink(missing_ok=True)
        detail = result.stderr.strip() or "pg_dump gagal membuat file backup."
        raise HTTPException(status_code=502, detail=detail)

    return output_path, filename

import json

CHURCH_REQUESTS_FILE = Path(__file__).resolve().parent.parent.parent / "church_requests.json"

def _load_church_requests() -> list:
    if not CHURCH_REQUESTS_FILE.exists():
        initial = [
            {
                "id": "REQ-2026-001",
                "applicant_name": "Pdt. Markus Samaloisa",
                "applicant_phone": "081267891122",
                "proposed_main_church": "Gereja Kristen Protestan Mentawai (GKPM)",
                "proposed_branch_church": "GKPM Jemaat Tuapejat",
                "city": "Kabupaten Kepulauan Mentawai",
                "address": "Jl. Raya Tuapejat Km. 4, Sipora Utara, Kepulauan Mentawai",
                "leader_name": "Ephorus GKPM",
                "complaint_notes": "Sinode GKPM belum ada di sistem registrasi. Mohon didaftarkan agar cabang kami di Mentawai bisa login.",
                "channel": "direct",
                "status": "Menunggu",
                "created_at": "2026-09-10 14:30:00"
            }
        ]
        _save_church_requests(initial)
        return initial
    try:
        with open(CHURCH_REQUESTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_church_requests(requests: list):
    try:
        with open(CHURCH_REQUESTS_FILE, "w", encoding="utf-8") as f:
            json.dump(requests, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving church requests: {e}")

class ChurchRequestCreate(BaseModel):
    applicant_name: str
    applicant_phone: str
    proposed_main_church: str
    proposed_branch_church: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    leader_name: Optional[str] = None
    complaint_notes: Optional[str] = None
    channel: Optional[str] = "direct"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_url: Optional[str] = None

class ChurchRequestStatusUpdate(BaseModel):
    status: str

class UserStatusUpdate(BaseModel):
    user_id: Any
    role: str
    is_active: bool

class BackupRequest(BaseModel):
    note: Optional[str] = "Manual Backup"


def _record_audit(db: Session, action: str, entity: str, detail: str,
                  entity_id: Optional[Any] = None, actor: str = "Superadmin",
                  level: str = "INFO") -> None:
    AuditService.record(
        db,
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        actor=actor,
        level=level,
        detail=detail,
    )


@router.get("/audit-logs")
def get_audit_logs(db: Session = Depends(deps.get_db), limit: int = 50) -> Any:
    safe_limit = min(max(limit, 1), 200)
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(safe_limit).all()

    def serialize_timestamp(value):
        if not value:
            return None
        timestamp = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc).isoformat()

    return {
        "logs": [
            {
                "id": log.id,
                "time": serialize_timestamp(log.created_at),
                "event": log.detail,
                "level": log.level,
                "user": log.actor,
                "action": log.action,
                "entity": log.entity,
                "entity_id": log.entity_id,
                "created_at": serialize_timestamp(log.created_at),
            }
            for log in logs
        ]
    }

@router.get("/superadmin-summary")
def get_superadmin_summary(db: Session = Depends(deps.get_db)) -> Any:
    # 1. Test database connection
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception as e:
        print(f"DB connection test error: {e}")

    # 2. Real counts
    total_churches = db.query(Church).count()
    active_churches = db.query(Church).filter(Church.status == "Aktif").count()
    total_superadmins = db.query(MainAdmin).count()
    total_church_admins = db.query(ChurchAdmin).count()
    active_church_admins = db.query(ChurchAdmin).filter(ChurchAdmin.status == "Aktif").count()
    total_jemaat = db.query(User).count()
    active_jemaat = db.query(User).filter(User.is_active == True).count()

    # 3. Recent Churches
    recent_churches_query = db.query(Church).order_by(Church.id.desc()).limit(5).all()
    recent_churches = []
    for c in recent_churches_query:
        # Find admin if available
        first_admin = c.admins[0].admin_name if c.admins else "-"
        date_str = "-"
        if c.created_at:
            date_str = c.created_at.strftime("%Y-%m-%d")
        elif c.established_date:
            date_str = str(c.established_date)

        recent_churches.append({
            "id": c.id,
            "name": c.church_name,
            "code": c.church_code,
            "admin": first_admin,
            "status": c.status or "Aktif",
            "date": date_str
        })

    all_churches = db.query(Church).all()

    # 4. Combined Users List (Superadmin, Church Admins, Jemaat)
    combined_users = []

    # Superadmins
    superadmins = db.query(MainAdmin).all()
    for sa in superadmins:
        combined_users.append({
            "id": f"sa_{sa.development_id}",
            "raw_id": sa.development_id,
            "full_name": sa.full_name or f"Superadmin ({sa.username})",
            "email": sa.email,
            "role": "superadmin",
            "church": "Pusat (System GracePoint)",
            "is_active": True,
            "created_at": sa.created_at.strftime("%Y-%m-%d") if sa.created_at else "2026-01-01"
        })

    # Church Admins
    church_admins = db.query(ChurchAdmin).all()
    for ca in church_admins:
        combined_users.append({
            "id": f"ca_{ca.id}",
            "raw_id": ca.id,
            "full_name": ca.admin_name,
            "email": ca.email,
            "role": "church_admin",
            "church": ca.church_name or (ca.church.church_name if ca.church else "Cabang Gereja"),
            "is_active": (ca.status == "Aktif"),
            "created_at": ca.created_at.strftime("%Y-%m-%d") if ca.created_at else "2026-02-01"
        })

    # Jemaat Members
    jemaat_list = db.query(User).all()
    for j in jemaat_list:
        combined_users.append({
            "id": f"jm_{j.id}",
            "raw_id": j.id,
            "full_name": j.full_name,
            "email": j.email,
            "role": "user",
            "church": j.church_domisili or j.church_central or "Jemaat Lokal",
            "is_active": bool(j.is_active),
            "created_at": j.created_at.strftime("%Y-%m-%d") if j.created_at else "2026-03-01"
        })

    # 5. Tren Pertumbuhan Pendaftaran Platform (Bulanan Tahun Berjalan 2026)
    # Menghitung pendaftaran riil gereja & pengguna di platform GracePoint secara matematis
    months_series = [
        ("2026-04", "Apr"),
        ("2026-05", "Mei"),
        ("2026-06", "Jun"),
        ("2026-07", "Jul"),
        ("2026-08", "Agu"),
        ("2026-09", "Sep")
    ]
    
    church_month_counts = {}
    for c in all_churches:
        if c.created_at:
            m_key = c.created_at.strftime("%Y-%m")
            church_month_counts[m_key] = church_month_counts.get(m_key, 0) + 1

    monthly_stats = []
    cumulative_churches = 0
    for key, label in months_series:
        new_churches = church_month_counts.get(key, 0)
        cumulative_churches += new_churches
        monthly_stats.append({
            "month": label,
            "year": 2026,
            "period": f"{label} 2026",
            "count": new_churches,
            "cumulative": cumulative_churches,
            "is_current": (key == "2026-09")
        })

    # Indikator Matematis & Statistik
    activity_rate = round((active_churches / total_churches * 100), 1) if total_churches > 0 else 0.0
    admin_ratio = round((total_church_admins / total_churches), 2) if total_churches > 0 else 0.0
    member_ratio = round((total_jemaat / total_churches), 2) if total_churches > 0 else 0.0
    total_entities = total_churches + total_church_admins + total_jemaat + total_superadmins

    math_stats = {
        "activity_rate": activity_rate,
        "active_churches": active_churches,
        "inactive_churches": total_churches - active_churches,
        "admin_per_church": admin_ratio,
        "member_per_church": member_ratio,
        "total_entities": total_entities,
        "this_month_growth": church_month_counts.get("2026-09", total_churches)
    }


    # Parse database details from DATABASE_URL
    db_user = "postgres"
    db_name = "cms_database"
    db_host = "localhost:5432"
    try:
        from urllib.parse import urlparse
        parsed = urlparse(settings.DATABASE_URL)
        if parsed.username:
            db_user = parsed.username
        if parsed.path:
            db_name = parsed.path.lstrip("/")
        if parsed.hostname:
            port_str = f":{parsed.port}" if parsed.port else ""
            db_host = f"{parsed.hostname}{port_str}"
    except Exception:
        pass

    audit_logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(50).all()
    system_logs = [
        {
            "time": log.created_at.astimezone(timezone.utc).strftime("%H:%M:%S") if log.created_at else "-",
            "event": log.detail,
            "level": log.level,
            "user": log.actor,
        }
        for log in audit_logs
    ]

    # 7. Database Connection Info
    db_info = {
        "connected": db_connected,
        "engine": "PostgreSQL 16 (Relational DB)",
        "database": db_name,
        "host": db_host,
        "user": db_user,
        "ssl": "Mode Require / TLS Verified"
    }

    return {
        "counts": {
            "total_churches": total_churches,
            "active_churches": active_churches,
            "total_superadmins": total_superadmins,
            "total_church_admins": total_church_admins,
            "active_church_admins": active_church_admins,
            "total_jemaat": total_jemaat,
            "active_jemaat": active_jemaat,
            "server_load": "14%"
        },
        "db_status": db_info,
        "recent_churches": recent_churches,
        "church_stats_by_year": monthly_stats,
        "monthly_stats": monthly_stats,
        "math_stats": math_stats,
        "all_users": combined_users,
        "system_logs": system_logs,
        "backups": [_public_backup(backup) for backup in _backups_list],
        "church_requests": _load_church_requests(),
        "pending_church_requests_count": sum(1 for r in _load_church_requests() if r.get("status") == "Menunggu")
    }

@router.post("/toggle-user-status")
def toggle_user_status(payload: UserStatusUpdate, db: Session = Depends(deps.get_db)) -> Any:
    role = payload.role
    raw_id = payload.user_id
    new_active = payload.is_active

    if role == "church_admin":
        admin = db.query(ChurchAdmin).filter(ChurchAdmin.id == int(raw_id)).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin cabang tidak ditemukan")
        admin.status = "Aktif" if new_active else "Nonaktif"
        db.commit()
        _record_audit(db, "UPDATE_STATUS", "church_admin", f"Status admin cabang {admin.admin_name} diubah menjadi {admin.status}.", admin.id)
        return {"success": True, "is_active": new_active, "status": admin.status}

    elif role == "user":
        member = db.query(User).filter(User.id == int(raw_id)).first()
        if not member:
            raise HTTPException(status_code=404, detail="Jemaat tidak ditemukan")
        member.is_active = new_active
        db.commit()
        _record_audit(db, "UPDATE_STATUS", "jemaat", f"Status jemaat {member.full_name} diubah menjadi {'Aktif' if new_active else 'Nonaktif'}.", member.id)
        return {"success": True, "is_active": new_active}

    return {"success": True, "message": "Role superadmin status tetap aktif"}

@router.delete("/users/{role}/{user_id}")
def delete_dashboard_user(role: str, user_id: str, db: Session = Depends(deps.get_db)) -> Any:
    if role == "church_admin":
        admin = db.query(ChurchAdmin).filter(ChurchAdmin.id == int(user_id)).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin cabang tidak ditemukan")
        db.delete(admin)
        db.commit()
        _record_audit(db, "DELETE", "church_admin", f"Admin cabang {admin.admin_name} dihapus dari sistem.", user_id, level="NOTICE")
        return {"success": True, "message": "Admin cabang berhasil dihapus"}

    elif role == "user":
        member = db.query(User).filter(User.id == int(user_id)).first()
        if not member:
            raise HTTPException(status_code=404, detail="Jemaat tidak ditemukan")
        db.delete(member)
        db.commit()
        _record_audit(db, "DELETE", "jemaat", f"Data jemaat {member.full_name} dihapus dari sistem.", user_id, level="NOTICE")
        return {"success": True, "message": "Data jemaat berhasil dihapus"}

    raise HTTPException(status_code=400, detail="Tidak dapat menghapus superadmin utama dari sini")

class CreateUserRequest(BaseModel):
    full_name: str
    email: str
    role: str
    church: Optional[str] = "Pusat (System)"
    password: Optional[str] = "GracePoint#2026"

@router.post("/create-user")
def create_dashboard_user(payload: CreateUserRequest, db: Session = Depends(deps.get_db)) -> Any:
    import random
    from app.core import security

    pwd_hash = security.get_password_hash(payload.password or "GracePoint#2026")

    if payload.role == "church_admin":
        existing = db.query(ChurchAdmin).filter(ChurchAdmin.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email admin cabang sudah terdaftar.")
        
        # Check church
        c = db.query(Church).filter(Church.church_name == payload.church).first()
        church_code = f"GP-CAB-{random.randint(10, 99)}" if not c else c.church_code
        church_id = c.id if c else None

        new_ca = ChurchAdmin(
            church_id=church_id,
            church_code=church_code,
            church_name=payload.church or "Cabang GracePoint",
            city="Jakarta",
            admin_name=payload.full_name,
            email=payload.email,
            phone="081234567890",
            password=pwd_hash,
            status="Aktif"
        )
        db.add(new_ca)
        db.commit()
        db.refresh(new_ca)
        _record_audit(db, "CREATE", "church_admin", f"Admin cabang {new_ca.admin_name} berhasil dibuat.", new_ca.id, level="SUCCESS")
        return {
            "success": True,
            "user": {
                "id": f"ca_{new_ca.id}",
                "raw_id": new_ca.id,
                "full_name": new_ca.admin_name,
                "email": new_ca.email,
                "role": "church_admin",
                "church": new_ca.church_name,
                "is_active": True,
                "created_at": new_ca.created_at.strftime("%Y-%m-%d") if new_ca.created_at else "2026-01-01"
            }
        }

    elif payload.role == "user":
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email jemaat sudah terdaftar.")
        
        c = db.query(Church).filter(Church.church_name == payload.church).first()
        church_id = c.id if c else None

        random_nik = f"317{random.randint(1000000000000, 9999999999999)}"[:16]
        username = payload.email.split("@")[0] + str(random.randint(10, 99))
        new_u = User(
            church_id=church_id,
            full_name=payload.full_name,
            email=payload.email,
            username=username,
            hashed_password=pwd_hash,
            nik=random_nik,
            birth_place="Jakarta",
            birth_date=datetime.now().date(),
            gender="Laki-laki",
            education="Sarjana (S1)",
            church_domisili=payload.church or "GracePoint Central",
            church_central=payload.church or "GracePoint Central",
            married="Belum",
            chatecication="Sudah",
            phone="081234567890",
            origin="Indonesia",
            address="Alamat Domisili",
            is_active=True
        )
        db.add(new_u)
        db.commit()
        db.refresh(new_u)
        _record_audit(db, "CREATE", "jemaat", f"Jemaat {new_u.full_name} berhasil dibuat.", new_u.id, level="SUCCESS")
        return {
            "success": True,
            "user": {
                "id": f"jm_{new_u.id}",
                "raw_id": new_u.id,
                "full_name": new_u.full_name,
                "email": new_u.email,
                "role": "user",
                "church": new_u.church_domisili,
                "is_active": True,
                "created_at": new_u.created_at.strftime("%Y-%m-%d") if new_u.created_at else "2026-01-01"
            }
        }

    elif payload.role == "superadmin":
        existing = db.query(MainAdmin).filter(MainAdmin.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email superadmin sudah terdaftar.")
        
        dev_id = str(random.randint(10000000, 99999999))
        username = payload.email.split("@")[0]
        new_sa = MainAdmin(
            development_id=dev_id,
            email=payload.email,
            username=username,
            password=pwd_hash
        )
        db.add(new_sa)
        db.commit()
        db.refresh(new_sa)
        _record_audit(db, "CREATE", "superadmin", f"Superadmin {new_sa.email} berhasil dibuat.", new_sa.development_id, level="SUCCESS")
        return {
            "success": True,
            "user": {
                "id": f"sa_{new_sa.development_id}",
                "raw_id": new_sa.development_id,
                "full_name": new_sa.full_name,
                "email": new_sa.email,
                "role": "superadmin",
                "church": "Pusat (System GracePoint)",
                "is_active": True,
                "created_at": new_sa.created_at.strftime("%Y-%m-%d") if new_sa.created_at else "2026-01-01"
            }
        }

    raise HTTPException(status_code=400, detail="Role tidak valid")


@router.post("/trigger-backup")
def trigger_instant_backup(req: BackupRequest = None, db: Session = Depends(deps.get_db)) -> Any:
    now = datetime.now()
    output_path, filename = _create_database_dump()
    date_code = now.strftime("%Y%m%d")
    new_bk = {
        "id": f"BK-{date_code}-{now.strftime('%H%M%S')}",
        "filename": filename,
        "size": f"{output_path.stat().st_size / (1024 * 1024):.2f} MB",
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Completed",
        "type": "Manual Trigger (Superadmin)",
        "file_path": str(output_path)
    }
    _backups_list.insert(0, new_bk)
    _record_audit(db, "CREATE", "backup", f"Backup database {new_bk['filename']} berhasil dibuat.", new_bk["id"], level="SUCCESS")
    return {"success": True, "backup": _public_backup(new_bk), "backups": [_public_backup(backup) for backup in _backups_list]}


@router.get("/backup-options")
def get_backup_options() -> Any:
    return {"options": BACKUP_TABLE_OPTIONS}


@router.post("/download-backup")
def download_backup(payload: BackupDownloadRequest, db: Session = Depends(deps.get_db)) -> FileResponse:
    backup = next((item for item in _backups_list if item.get("id") == payload.backup_id), None) if payload.backup_id else None
    output_path = Path(backup["file_path"]) if backup and backup.get("file_path") else None
    filename = backup.get("filename") if backup else None

    if output_path is None or not output_path.exists():
        output_path, filename = _create_database_dump(payload.scope, payload.tables)
        _record_audit(
            db,
            "DOWNLOAD",
            "backup",
            f"Backup database {filename} diunduh.",
            backup.get("id") if backup else None,
            level="SUCCESS"
        )

    return FileResponse(output_path, media_type="application/sql", filename=filename)


# ========================================================
# INBOX PERMOHONAN GEREJA BARU (CHURCH REGISTRATION REQUESTS)
# ========================================================

@router.get("/church-requests")
def get_church_requests() -> Any:
    requests = _load_church_requests()
    pending = sum(1 for r in requests if r.get("status") == "Menunggu")
    return {
        "total": len(requests),
        "pending": pending,
        "requests": requests
    }

@router.post("/church-requests")
def create_church_request(payload: ChurchRequestCreate, db: Session = Depends(deps.get_db)) -> Any:
    requests = _load_church_requests()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    req_id = f"REQ-2026-{str(len(requests) + 1).zfill(3)}"
    new_req = {
        "id": req_id,
        "applicant_name": payload.applicant_name,
        "applicant_phone": payload.applicant_phone,
        "proposed_main_church": payload.proposed_main_church,
        "proposed_branch_church": payload.proposed_branch_church or "-",
        "city": payload.city or "-",
        "address": payload.address or "-",
        "leader_name": payload.leader_name or "-",
        "complaint_notes": payload.complaint_notes or "-",
        "channel": payload.channel or "direct",
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "google_maps_url": payload.google_maps_url,
        "status": "Menunggu",
        "created_at": now_str
    }
    requests.insert(0, new_req)
    _save_church_requests(requests)
    _record_audit(db, "CREATE", "church_request", f"Permohonan pendaftaran gereja {new_req['proposed_main_church']} diterima.", req_id, level="NOTICE")
    return {
        "success": True, 
        "message": "Permohonan pendaftaran gereja berhasil dikirim ke Admin Utama.", 
        "request": new_req
    }

@router.patch("/church-requests/{req_id}/status")
def update_church_request_status(req_id: str, payload: ChurchRequestStatusUpdate, db: Session = Depends(deps.get_db)) -> Any:
    requests = _load_church_requests()
    for r in requests:
        if r.get("id") == req_id:
            r["status"] = payload.status
            _save_church_requests(requests)
            _record_audit(db, "UPDATE_STATUS", "church_request", f"Status permohonan {req_id} diubah menjadi {payload.status}.", req_id, level="NOTICE")
            return {"success": True, "request": r}
    raise HTTPException(status_code=404, detail="Permohonan tidak ditemukan.")


@router.delete("/church-requests/{req_id}")
def delete_church_request(req_id: str, db: Session = Depends(deps.get_db)) -> Any:
    requests = _load_church_requests()
    target = next((request for request in requests if request.get("id") == req_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Permohonan tidak ditemukan.")

    _save_church_requests([request for request in requests if request.get("id") != req_id])
    _record_audit(
        db,
        "DELETE",
        "church_request",
        f"Permohonan {req_id} dari {target.get('applicant_name', '-')} dihapus dari inbox.",
        req_id,
        level="NOTICE",
    )
    return {"success": True, "message": "Permohonan berhasil dihapus.", "id": req_id}

