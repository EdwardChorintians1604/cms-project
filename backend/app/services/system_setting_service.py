import json
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.system_setting import SystemSetting

DEFAULT_SETTINGS = {
    # 1. Identitas Platform & Gereja
    "site_title": {"group": "general", "value": "GracePoint - Platform Pelayanan Gereja", "desc": "Nama resmi website platform"},
    "site_tagline": {"group": "general", "value": "Soli Deo Gloria — Melayani dengan Kasih & Kesetiaan", "desc": "Motto / Slogan pelayanan gereja"},
    "synod_name": {"group": "general", "value": "Sinode Pusat GracePoint Church Network", "desc": "Nama induk sinode / badan pengurus pusat"},
    "admin_email": {"group": "general", "value": "admin@gracepoint.org", "desc": "Email resmi kontak administrator sistem"},
    "support_phone": {"group": "general", "value": "0812-3456-7890", "desc": "Hotline sekretariat / layanan WhatsApp"},
    "office_address": {"group": "general", "value": "Graha GracePoint Lt. 5, Jl. Jend. Sudirman Kav. 21, Jakarta", "desc": "Alamat kantor pusat sekretariat sinode"},
    "timezone": {"group": "general", "value": "Asia/Jakarta", "desc": "Zona waktu default sistem (WIB)"},
    "date_format": {"group": "general", "value": "DD/MM/YYYY", "desc": "Format penanggalan default"},
    "time_format": {"group": "general", "value": "24h", "desc": "Format waktu (24 jam atau 12 jam)"},
    "system_language": {"group": "general", "value": "id", "desc": "Bahasa antarmuka default (id = Indonesia)"},

    # 2. Preferensi Operasional & Pelayanan
    "allow_member_registration": {"group": "church", "value": "true", "desc": "Izinkan jemaat mendaftar akun mandiri secara online"},
    "require_branch_verification": {"group": "church", "value": "true", "desc": "Pendaftaran cabang baru memerlukan persetujuan manual Superadmin"},
    "enable_public_calendar": {"group": "church", "value": "true", "desc": "Tampilkan kalender kegiatan & hari raya ke publik"},
    "enable_finance_transparency": {"group": "church", "value": "true", "desc": "Tampilkan ringkasan grafik keuangan ke portal jemaat"},

    # 3. Keamanan & Akses
    "session_expiry_days": {"group": "security", "value": "7", "desc": "Masa berlaku token sesi login (hari)"},
    "max_login_attempts": {"group": "security", "value": "5", "desc": "Batas maksimum percobaan login salah sebelum timeout"},
    "enable_audit_logging": {"group": "security", "value": "true", "desc": "Aktifkan pencatatan jejak audit sistem SHA-256"},
    "maintenance_mode": {"group": "security", "value": "false", "desc": "Mode pemeliharaan sistem (publik dialihkan)"},

    # 4. Tema & Tampilan Visual
    "theme_mode": {"group": "theme", "value": "dark", "desc": "Mode tema default (dark, light, system)"},
    "accent_color": {"group": "theme", "value": "amber", "desc": "Warna aksen utama (amber, emerald, sky, purple, rose)"},
    "heading_font": {"group": "theme", "value": "Cinzel", "desc": "Jenis huruf judul (Cinzel / Inter / Roboto)"},
    "ui_density": {"group": "theme", "value": "comfortable", "desc": "Kepadatan elemen antarmuka (comfortable / compact)"},
    "enable_glassmorphism": {"group": "theme", "value": "true", "desc": "Aktifkan efek kaca blur pada kartu & navbar"},
    "enable_micro_animations": {"group": "theme", "value": "true", "desc": "Aktifkan animasi transisi halus interaktif"}
}

class SystemSettingService:
    @staticmethod
    def ensure_defaults(db: Session) -> None:
        """Memastikan semua setting default tersedia dalam database."""
        existing_keys = {s.key for s in db.query(SystemSetting.key).all()}
        new_records = []
        for key, info in DEFAULT_SETTINGS.items():
            if key not in existing_keys:
                new_records.append(
                    SystemSetting(
                        key=key,
                        group=info["group"],
                        value=str(info["value"]),
                        description=info.get("desc"),
                    )
                )
        if new_records:
            db.bulk_save_objects(new_records)
            db.commit()

    @staticmethod
    def get_all_grouped(db: Session) -> Dict[str, Dict[str, Any]]:
        SystemSettingService.ensure_defaults(db)
        settings = db.query(SystemSetting).all()
        grouped: Dict[str, Dict[str, Any]] = {}
        for s in settings:
            if s.group not in grouped:
                grouped[s.group] = {}
            val = s.value
            # Auto parse boolean / numbers if applicable
            if val == "true":
                parsed_val = True
            elif val == "false":
                parsed_val = False
            else:
                try:
                    parsed_val = int(val)
                except (ValueError, TypeError):
                    parsed_val = val
            grouped[s.group][s.key] = parsed_val
        return grouped

    @staticmethod
    def update_bulk(db: Session, updates: Dict[str, Any]) -> Dict[str, Any]:
        SystemSettingService.ensure_defaults(db)
        updated_keys = []
        for key, val in updates.items():
            str_val = "true" if val is True else "false" if val is False else str(val) if val is not None else ""
            setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if setting:
                setting.value = str_val
                updated_keys.append(key)
            else:
                # Cari grup dari DEFAULT_SETTINGS jika ada
                group = DEFAULT_SETTINGS.get(key, {}).get("group", "general")
                desc = DEFAULT_SETTINGS.get(key, {}).get("desc", "")
                db.add(SystemSetting(key=key, group=group, value=str_val, description=desc))
                updated_keys.append(key)

        db.commit()
        return {"updated_count": len(updated_keys), "keys": updated_keys}

    @staticmethod
    def reset_to_defaults(db: Session, group: Optional[str] = None) -> Dict[str, Any]:
        count = 0
        for key, info in DEFAULT_SETTINGS.items():
            if group and info["group"] != group:
                continue
            setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
            str_val = str(info["value"])
            if setting:
                setting.value = str_val
            else:
                db.add(SystemSetting(key=key, group=info["group"], value=str_val, description=info.get("desc")))
            count += 1
        db.commit()
        return {"message": f"Pengaturan berhasil dikembalikan ke default ({count} item)."}
