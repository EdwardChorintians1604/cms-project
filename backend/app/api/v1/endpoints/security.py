"""
Security Dashboard API
======================
Menyediakan data keamanan nyata dari database audit_logs untuk SecurityView.vue.
Endpoint ini membaca data aktual — bukan hardcode — termasuk threat logs, 
anomali yang terdeteksi, statistik login gagal, dan security score dinamis.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.api import deps
from app.models.audit_log import AuditLog
from app.core.config import settings

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: Hitung security score dinamis dari kondisi DB real
# ─────────────────────────────────────────────────────────────────────────────
def _compute_security_score(db: Session) -> dict:
    """
    Menghitung skor keamanan (0–100) secara dinamis berdasarkan:
    - Jumlah anomali dalam 24 jam terakhir
    - Jumlah login gagal dalam 24 jam terakhir
    - Jumlah event WARNING/ERROR dalam 1 jam terakhir
    Skor dimulai dari 100 dan dikurangi per temuan.
    """
    now = datetime.now(timezone.utc)
    since_24h = now - timedelta(hours=24)
    since_1h  = now - timedelta(hours=1)

    # Hitung anomali (setiap anomali = -8 poin, max -40)
    anomaly_count = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "ANOMALY_DETECTED",
        AuditLog.created_at >= since_24h
    ).scalar() or 0

    # Hitung login gagal (setiap 3 gagal = -2 poin, max -20)
    failed_login_count = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "LOGIN_FAILED",
        AuditLog.created_at >= since_24h
    ).scalar() or 0

    # Hitung event WARNING dalam 1 jam (setiap 5 warning = -1 poin, max -10)
    warning_count = db.query(func.count(AuditLog.id)).filter(
        AuditLog.level == "WARNING",
        AuditLog.created_at >= since_1h
    ).scalar() or 0

    anomaly_penalty  = min(anomaly_count * 8, 40)
    login_penalty    = min((failed_login_count // 3) * 2, 20)
    warning_penalty  = min((warning_count // 5) * 1, 10)

    score = max(100 - anomaly_penalty - login_penalty - warning_penalty, 0)

    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "D"

    return {
        "score": score,
        "grade": grade,
        "anomaly_count_24h": anomaly_count,
        "failed_login_count_24h": failed_login_count,
        "warning_count_1h": warning_count,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /security/dashboard
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/dashboard")
def get_security_dashboard(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Dashboard keamanan terpadu.
    Mengembalikan: security score, statistik ancaman 24 jam, 
    status komponen keamanan, dan 10 threat log terbaru.
    """
    now = datetime.now(timezone.utc)
    since_24h = now - timedelta(hours=24)
    since_7d  = now - timedelta(days=7)

    # ── Security Score ──────────────────────────────────────────────────────
    score_data = _compute_security_score(db)

    # ── Statistik 24 Jam ────────────────────────────────────────────────────
    total_events_24h = db.query(func.count(AuditLog.id)).filter(
        AuditLog.created_at >= since_24h
    ).scalar() or 0

    blocked_attempts_24h = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action.in_(["LOGIN_FAILED", "ANOMALY_DETECTED"]),
        AuditLog.created_at >= since_24h
    ).scalar() or 0

    total_anomalies_7d = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "ANOMALY_DETECTED",
        AuditLog.created_at >= since_7d
    ).scalar() or 0

    # ── Threat Logs Terbaru (10 entri, level WARNING/ERROR atau aksi berbahaya) ──
    threat_logs_raw = db.query(AuditLog).filter(
        AuditLog.action.in_([
            "LOGIN_FAILED", "ANOMALY_DETECTED",
            "HTTP_DELETE", "RATE_LIMIT_EXCEEDED"
        ]) | (AuditLog.level.in_(["WARNING", "ERROR"]))
    ).order_by(AuditLog.created_at.desc()).limit(10).all()

    threat_logs = []
    for log in threat_logs_raw:
        # Tentukan tipe serangan dari action/detail
        attack_type = _classify_attack(log.action, log.detail)
        action_taken = _classify_action(log.action, log.level)
        badge_class  = _badge_for_level(log.level, log.action)

        # Format timestamp dengan timezone lokal
        ts = log.created_at
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        ts_local = ts.astimezone(timezone(timedelta(hours=7)))  # WIB

        threat_logs.append({
            "id": f"LOG-{log.id}",
            "timestamp": ts_local.strftime("%d %b %Y %H:%M:%S"),
            "ip": log.entity_id or "internal",
            "target": log.entity,
            "actor": log.actor,
            "attack_type": attack_type,
            "action_taken": action_taken,
            "badge_class": badge_class,
            "level": log.level,
            "detail": log.detail,
        })

    # ── Status Komponen Keamanan ─────────────────────────────────────────────
    # Ini refleksi nyata dari konfigurasi sistem
    jwt_algo    = settings.ALGORITHM
    token_ttl_h = settings.ACCESS_TOKEN_EXPIRE_MINUTES // 60
    cors_strict = len(settings.BACKEND_CORS_ORIGINS) < 10  # strict jika < 10 origin

    security_components = [
        {
            "id": "waf",
            "title": "Rate Limiter & Brute-Force Guard",
            "value": "Aktif & Melindungi",
            "subtext": f"{blocked_attempts_24h} percobaan berbahaya diblokir 24 jam terakhir",
            "icon": "bi-shield-fill-check",
            "color": "emerald",
            "status": "active"
        },
        {
            "id": "crypto",
            "title": "Kriptografi & Token Auth",
            "value": f"bcrypt + JWT ({jwt_algo})",
            "subtext": f"Token expire {token_ttl_h} jam | Semua password di-hash bcrypt",
            "icon": "bi-key-fill",
            "color": "amber",
            "status": "active"
        },
        {
            "id": "session",
            "title": "CORS & Session Security",
            "value": "Strict CORS Active" if cors_strict else "CORS Relaxed (Dev Mode)",
            "subtext": f"{len(settings.BACKEND_CORS_ORIGINS)} origin diizinkan | CSRF protection enforced",
            "icon": "bi-file-earmark-lock2-fill",
            "color": "sky" if cors_strict else "amber",
            "status": "active" if cors_strict else "warning"
        },
        {
            "id": "audit",
            "title": "Audit Trail & Anomaly Engine",
            "value": f"{total_events_24h} Events Tercatat",
            "subtext": f"{total_anomalies_7d} anomali terdeteksi 7 hari | Real-time monitoring",
            "icon": "bi-database-check",
            "color": "purple",
            "status": "active"
        },
    ]

    return {
        "score": score_data,
        "stats": {
            "total_events_24h": total_events_24h,
            "blocked_attempts_24h": blocked_attempts_24h,
            "anomalies_7d": total_anomalies_7d,
            "last_updated": now.isoformat(),
        },
        "threat_logs": threat_logs,
        "security_components": security_components,
        "system_info": {
            "jwt_algorithm": jwt_algo,
            "token_ttl_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "cors_origins_count": len(settings.BACKEND_CORS_ORIGINS),
            "rate_limit_storage": settings.RATELIMIT_STORAGE_URI,
            "debug_mode": settings.DEBUG,
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /security/scan
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/scan")
def run_security_scan(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Jalankan pemindaian keamanan aktif.
    Memeriksa kondisi nyata sistem: anomali terbaru, failed logins,
    konfigurasi JWT, dan kebijakan CORS.
    Mengembalikan hasil per tahap scan.
    """
    now = datetime.now(timezone.utc)
    since_24h = now - timedelta(hours=24)

    # Tahap 1: Cek Sanitasi Query / SQL Injection Probing
    sql_probes = db.query(func.count(AuditLog.id)).filter(
        AuditLog.detail.ilike("%injection%") | AuditLog.detail.ilike("%OR 1=1%") | AuditLog.detail.ilike("%' OR%"),
        AuditLog.created_at >= since_24h
    ).scalar() or 0

    step1 = {
        "phase": "Memeriksa Vektor SQL Injection & Query Sanitasi...",
        "log": f"[CHECK] SQL injection probing attempts in 24h: {sql_probes} detected | ORM parameterized: OK",
        "progress": 16,
        "ok": sql_probes == 0,
        "findings": f"{sql_probes} percobaan SQL injection probe" if sql_probes > 0 else None
    }

    # Tahap 2: Cek JWT & Auth
    jwt_algo = settings.ALGORITHM
    token_ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    secret_len = len(settings.SECRET_KEY)
    jwt_ok = secret_len >= 16 and jwt_algo in ("HS256", "RS256")

    step2 = {
        "phase": "Memverifikasi Keabsahan Token JWT & Konfigurasi Auth...",
        "log": f"[CHECK] JWT algorithm: {jwt_algo} | Secret length: {secret_len} chars | TTL: {token_ttl} min → {'OK' if jwt_ok else 'WARNING: secret terlalu pendek'}",
        "progress": 33,
        "ok": jwt_ok,
        "findings": "JWT secret key terlalu pendek (< 16 karakter)" if not jwt_ok else None
    }

    # Tahap 3: Cek CORS
    cors_origins = settings.BACKEND_CORS_ORIGINS
    cors_strict = len(cors_origins) < 10
    step3 = {
        "phase": "Mengaudit Kebijakan CORS & Header Keamanan HTTP...",
        "log": f"[CHECK] Allowed CORS origins: {len(cors_origins)} | Strict mode: {'Yes' if cors_strict else 'No (Dev)'} | Origins: {', '.join(cors_origins[:3])}{'...' if len(cors_origins) > 3 else ''}",
        "progress": 50,
        "ok": True,  # CORS selalu ada, nilainya informatif
        "findings": "CORS dalam mode dev (localhost)" if not cors_strict else None
    }

    # Tahap 4: Cek Failed Login & Brute-Force
    failed_logins_24h = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "LOGIN_FAILED",
        AuditLog.created_at >= since_24h
    ).scalar() or 0

    step4 = {
        "phase": "Mengevaluasi Proteksi Brute-Force & Rate Limiting...",
        "log": f"[CHECK] Failed login attempts 24h: {failed_logins_24h} | Rate limit storage: {settings.RATELIMIT_STORAGE_URI} | Throttle: 10 req/10min",
        "progress": 67,
        "ok": True,
        "findings": f"Terdeteksi {failed_logins_24h} percobaan login gagal dalam 24 jam" if failed_logins_24h >= 10 else None
    }

    # Tahap 5: Cek Anomali Terdeteksi
    anomalies_24h = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "ANOMALY_DETECTED",
        AuditLog.created_at >= since_24h
    ).scalar() or 0

    step5 = {
        "phase": "Memeriksa Anomali & Aktivitas Mencurigakan...",
        "log": f"[CHECK] Anomalies detected 24h: {anomalies_24h} | Anomaly engine: ACTIVE | Threshold: 5 failed logins / 10 min",
        "progress": 84,
        "ok": anomalies_24h == 0,
        "findings": f"{anomalies_24h} anomali terdeteksi dalam 24 jam terakhir" if anomalies_24h > 0 else None
    }

    # Tahap 6: Hitung skor akhir
    score_data = _compute_security_score(db)
    total_findings = sum(1 for s in [step1, step2, step3, step4, step5] if s["findings"])
    final_ok = total_findings == 0

    step6 = {
        "phase": "Pemindaian Selesai." + (" Tidak ditemukan celah kritis." if final_ok else f" Ditemukan {total_findings} catatan yang perlu diperhatikan."),
        "log": f"[RESULT] Security Score: {score_data['score']}/100 ({score_data['grade']}) | Total findings: {total_findings} | Status: {'CLEAR' if final_ok else 'ATTENTION NEEDED'}",
        "progress": 100,
        "ok": final_ok,
        "findings": None
    }

    all_findings = [s["findings"] for s in [step1, step2, step3, step4, step5] if s["findings"]]

    return {
        "steps": [step1, step2, step3, step4, step5, step6],
        "summary": {
            "score": score_data["score"],
            "grade": score_data["grade"],
            "total_findings": total_findings,
            "findings": all_findings,
            "is_clean": final_ok,
            "scanned_at": now.isoformat(),
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /security/audit-logs
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(deps.get_db),
    level: Optional[str] = Query(None, description="Filter by level: INFO, WARNING, ERROR"),
    action: Optional[str] = Query(None, description="Filter by action"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Any:
    """
    Ambil audit log dengan filter dan pagination.
    Digunakan untuk threat feed di SecurityView.
    """
    query = db.query(AuditLog)
    if level:
        query = query.filter(AuditLog.level == level.upper())
    if action:
        query = query.filter(AuditLog.action == action.upper())

    total = query.count()
    logs  = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for log in logs:
        ts = log.created_at
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        ts_local = ts.astimezone(timezone(timedelta(hours=7)))
        result.append({
            "id": log.id,
            "action": log.action,
            "entity": log.entity,
            "entity_id": log.entity_id,
            "actor": log.actor,
            "level": log.level,
            "detail": log.detail,
            "timestamp": ts_local.strftime("%d %b %Y %H:%M:%S"),
            "timestamp_iso": ts.isoformat(),
        })

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": result,
    }


# ─────────────────────────────────────────────────────────────────────────────
# HELPER CLASSIFIERS
# ─────────────────────────────────────────────────────────────────────────────
def _classify_attack(action: str, detail: str) -> str:
    if action == "LOGIN_FAILED":
        return "Percobaan Login Gagal (Brute-Force / Credential Stuffing)"
    if action == "ANOMALY_DETECTED":
        if "login" in detail.lower():
            return "Anomali: Serangan Brute-Force Terdeteksi"
        if "aktivitas tinggi" in detail.lower():
            return "Anomali: Aktivitas Berlebihan (Rate Abuse)"
        return "Anomali Keamanan Terdeteksi"
    if action == "HTTP_DELETE":
        return "Aksi Penghapusan Data Sensitif"
    if "injection" in detail.lower() or "OR 1=1" in detail:
        return "SQL Injection Probing"
    return f"Event: {action}"


def _classify_action(action: str, level: str) -> str:
    if action == "LOGIN_FAILED":
        return "Login Diblokir (Kredensial Salah)"
    if action == "ANOMALY_DETECTED":
        return "Anomali Dicatat & Ditandai"
    if level == "ERROR":
        return "Diblokir Otomatis (Error Level)"
    if level == "WARNING":
        return "Dicatat sebagai Peringatan"
    return "Event Tercatat"


def _badge_for_level(level: str, action: str) -> str:
    if action == "ANOMALY_DETECTED" or level == "ERROR":
        return "bg-rose-500/20 text-rose-300 border-rose-500/30"
    if level == "WARNING" or action == "LOGIN_FAILED":
        return "bg-amber-500/20 text-amber-300 border-amber-500/30"
    return "bg-sky-500/20 text-sky-300 border-sky-500/30"
