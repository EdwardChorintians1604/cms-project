from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple

from fastapi import Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.audit_log import AuditLog


ACTOR_ROLES = {
    "admin": "superadmin",
    "main_admin": "superadmin",
    "church": "church_admin",
    "jemaat": "user",
}


class AuditService:
    @staticmethod
    def actor_from_request(request: Request) -> tuple[str, str]:
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return "anonymous", "anonymous"

        try:
            payload = jwt.decode(
                authorization.removeprefix("Bearer "),
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            subject = str(payload.get("sub", "anonymous"))
            prefix, _, actor_id = subject.partition(":")
            return ACTOR_ROLES.get(prefix, "unknown"), actor_id or subject
        except (JWTError, ValueError):
            return "unknown", "invalid-token"

    @staticmethod
    def record(
        db: Session,
        *,
        action: str,
        entity: str,
        detail: str,
        actor: str = "Superadmin",
        entity_id: Optional[Any] = None,
        level: str = "INFO",
    ) -> AuditLog:
        log = AuditLog(
            action=action,
            entity=entity,
            entity_id=str(entity_id) if entity_id is not None else None,
            actor=actor,
            level=level,
            detail=detail,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        AuditService._detect_anomaly(db, log)
        return log

    @staticmethod
    def record_request(db: Session, request: Request, status_code: int) -> None:
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        role, actor_id = AuditService.actor_from_request(request)
        client_id = request.client.host if request.client else "unknown-client"
        if request.url.path.endswith("/login") and status_code >= 400:
            AuditService.record_login_failure(db, f"{role}:{actor_id}", client_id)
            return
        action = f"HTTP_{request.method}"
        level = "WARNING" if request.method == "DELETE" or status_code >= 400 else "INFO"
        detail = f"{request.method} {request.url.path} selesai dengan status {status_code}."
        AuditService.record(
            db,
            action=action,
            entity=request.url.path,
            detail=detail,
            actor=f"{role}:{actor_id}",
            entity_id=client_id,
            level=level,
        )

    @staticmethod
    def record_login_failure(db: Session, actor: str, identifier: str) -> None:
        AuditService.record(
            db,
            action="LOGIN_FAILED",
            entity="authentication",
            detail=f"Percobaan login gagal untuk {identifier}.",
            actor=actor,
            entity_id=identifier,
            level="WARNING",
        )

    @staticmethod
    def _detect_anomaly(db: Session, current: AuditLog) -> None:
        now = current.created_at or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        recent = db.query(AuditLog).filter(
            AuditLog.actor == current.actor,
            AuditLog.created_at >= now - timedelta(minutes=1),
            AuditLog.id != current.id,
        ).count()
        failed_logins = db.query(AuditLog).filter(
            AuditLog.action == "LOGIN_FAILED",
            AuditLog.entity_id == current.entity_id,
            AuditLog.created_at >= now - timedelta(minutes=10),
        ).count()

        anomaly = None
        if failed_logins >= 5:
            anomaly = f"Anomali: {failed_logins + 1} percobaan login gagal untuk {current.entity_id} dalam 10 menit."
        elif recent >= 30:
            anomaly = f"Anomali: aktivitas tinggi dari {current.actor}, {recent + 1} event dalam 1 menit."

        if anomaly:
            db.add(AuditLog(
                action="ANOMALY_DETECTED",
                entity="security",
                entity_id=current.entity_id,
                actor="Audit Engine",
                level="ERROR",
                detail=anomaly,
            ))
            db.commit()


async def audit_request_middleware(request: Request, call_next):
    response = await call_next(request)
    db = SessionLocal()
    try:
        try:
            AuditService.record_request(db, request, response.status_code)
        except Exception:
            db.rollback()
    finally:
        db.close()
    return response
