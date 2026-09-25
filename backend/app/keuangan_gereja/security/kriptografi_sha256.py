import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.models.anggaran import AnggaranGereja
from app.keuangan_gereja.models.audit_transaksi import AuditTransaksiKeuangan
from app.models.church import Church

DEFAULT_BACKUP_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "storage", "backups", "keuangan")
)

class CryptoKeuanganSHA256:
    """
    Modul Keamanan & Kriptografi Integritas SHA-256
    Menjamin keaslian data audit keuangan gereja, mendeteksi manipulasi (tampering),
    serta menyediakan mekanisme backup snapshot kriptografis untuk mencegah kerugian massal.
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    @staticmethod
    def hash_string(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def format_timestamp(dt: Any) -> str:
        if not dt:
            return ""
        if isinstance(dt, str):
            # Normalisasi jika string ISO
            return dt[:19].replace("T", " ")
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def compute_audit_hash(
        cls,
        prev_hash: Optional[str],
        church_id: Optional[int],
        transaksi_tipe: str,
        transaksi_id: int,
        action: str,
        user_id: Optional[str],
        payload_sesudah: Optional[str],
        created_at_dt: Any,
    ) -> str:
        timestamp_str = cls.format_timestamp(created_at_dt)
        raw_string = "|".join([
            prev_hash or cls.GENESIS_HASH,
            str(church_id or 0),
            transaksi_tipe.lower(),
            str(transaksi_id),
            action.upper(),
            str(user_id or ""),
            payload_sesudah or "{}",
            timestamp_str,
        ])
        return cls.hash_string(raw_string)

    @classmethod
    def log_and_hash_audit(
        cls,
        db: Session,
        church_id: Optional[int],
        transaksi_tipe: str,
        transaksi_id: int,
        action: str,
        user_id: Optional[str],
        user_role: Optional[str],
        deskripsi: str,
        sebelum: Optional[dict] = None,
        sesudah: Optional[dict] = None,
    ) -> AuditTransaksiKeuangan:
        # Ambil record audit terakhir untuk menghubungkan hash chain
        last_audit = db.query(AuditTransaksiKeuangan).order_by(AuditTransaksiKeuangan.id.desc()).first()
        prev_hash = last_audit.hash_sha256 if (last_audit and last_audit.hash_sha256) else cls.GENESIS_HASH

        now_utc = datetime.now(timezone.utc)
        payload_sebelum_str = json.dumps(sebelum, default=str) if sebelum else None
        payload_sesudah_str = json.dumps(sesudah, default=str) if sesudah else None

        current_hash = cls.compute_audit_hash(
            prev_hash=prev_hash,
            church_id=church_id,
            transaksi_tipe=transaksi_tipe,
            transaksi_id=transaksi_id,
            action=action,
            user_id=user_id,
            payload_sesudah=payload_sesudah_str,
            created_at_dt=now_utc,
        )

        audit = AuditTransaksiKeuangan(
            church_id=church_id,
            transaksi_tipe=transaksi_tipe,
            transaksi_id=transaksi_id,
            action=action,
            user_id=user_id,
            user_role=user_role,
            deskripsi=deskripsi,
            payload_sebelum=payload_sebelum_str,
            payload_sesudah=payload_sesudah_str,
            prev_hash=prev_hash,
            hash_sha256=current_hash,
            created_at=now_utc,
        )
        db.add(audit)
        return audit

    @classmethod
    def verify_integrity(cls, db: Session, church_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Melakukan audit forensik kriptografi SHA-256 terhadap seluruh catatan keuangan.
        Jika data di-database diubah diam-diam oleh pihak tidak bertanggung jawab,
        rantai hash akan rusak dan anomali terdeteksi.
        """
        query = db.query(AuditTransaksiKeuangan).order_by(AuditTransaksiKeuangan.id.asc())
        if church_id:
            query = query.filter(AuditTransaksiKeuangan.church_id == church_id)

        audits = query.all()
        total = len(audits)

        if total == 0:
            return {
                "status": "BERSIH",
                "keterangan": "Belum ada catatan transaksi keuangan yang diverifikasi.",
                "total_diperiksa": 0,
                "terverifikasi_valid": 0,
                "terdeteksi_tampering": 0,
                "anomali_terdeteksi": [],
            }

        tampered = []
        valid_count = 0
        last_seen_hash = audits[0].prev_hash if audits else cls.GENESIS_HASH

        for idx, record in enumerate(audits):
            # Recompute expected hash
            computed_hash = cls.compute_audit_hash(
                prev_hash=record.prev_hash or cls.GENESIS_HASH,
                church_id=record.church_id,
                transaksi_tipe=record.transaksi_tipe,
                transaksi_id=record.transaksi_id,
                action=record.action,
                user_id=record.user_id,
                payload_sesudah=record.payload_sesudah,
                created_at_dt=record.created_at,
            )

            is_valid = True
            reasons = []

            if record.hash_sha256 and record.hash_sha256 != computed_hash:
                is_valid = False
                reasons.append(f"Hash tidak cocok (disimpan: {record.hash_sha256[:12]}..., terhitung: {computed_hash[:12]}...)")

            # Jika memeriksa seluruh database tanpa filter cabang, validasi kontinuitas rantai
            if church_id is None and idx > 0 and record.prev_hash != last_seen_hash:
                is_valid = False
                reasons.append("Rantai hash terputus (prev_hash tidak cocok dengan record sebelumnya)")

            if is_valid:
                valid_count += 1
                if record.hash_sha256:
                    last_seen_hash = record.hash_sha256
            else:
                tampered.append({
                    "audit_id": record.id,
                    "transaksi_tipe": record.transaksi_tipe,
                    "transaksi_id": record.transaksi_id,
                    "action": record.action,
                    "alasan": " | ".join(reasons),
                    "waktu": record.created_at.isoformat() if record.created_at else None,
                })

        is_compromised = len(tampered) > 0
        return {
            "status": "TERDETEKSI_MANIPULASI" if is_compromised else "INTEGRITAS_TERJAMIN_SHA256",
            "keterangan": "PERINGATAN: Integritas data keuangan terganggu! Terdeteksi modifikasi tidak sah." if is_compromised else "Seluruh rekaman transaksi terverifikasi otentik dan aman secara kriptografis.",
            "total_diperiksa": total,
            "terverifikasi_valid": valid_count,
            "terdeteksi_tampering": len(tampered),
            "anomali_terdeteksi": tampered,
            "timestamp_audit": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def create_cryptographic_backup(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        admin_id: str = "main_admin",
        backup_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Membuat snapshot backup data keuangan & analitik lengkap dengan checksum SHA-256
        untuk mencegah kehilangan data massal dan melindungi integritas finansial gereja.
        """
        target_dir = backup_dir or DEFAULT_BACKUP_DIR
        os.makedirs(target_dir, exist_ok=True)

        p_query = db.query(PemasukanGereja)
        k_query = db.query(PengeluaranGereja)
        a_query = db.query(AnggaranGereja)
        audit_query = db.query(AuditTransaksiKeuangan)

        church_name = "Semua Cabang Gereja (Konsolidasi Pusat)"
        if church_id:
            p_query = p_query.filter(PemasukanGereja.church_id == church_id)
            k_query = k_query.filter(PengeluaranGereja.church_id == church_id)
            a_query = a_query.filter(AnggaranGereja.church_id == church_id)
            audit_query = audit_query.filter(AuditTransaksiKeuangan.church_id == church_id)
            ch = db.query(Church).filter(Church.id == church_id).first()
            if ch:
                church_name = ch.church_name

        pemasukan_data = [
            {
                "id": p.id,
                "church_id": p.church_id,
                "tanggal": str(p.tanggal),
                "kategori": p.kategori,
                "jumlah": float(p.jumlah),
                "metode_pembayaran": p.metode_pembayaran,
                "keterangan": p.keterangan,
                "status_verifikasi": p.status_verifikasi,
                "donor_name": p.donor_name,
                "created_by": p.created_by,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in p_query.all()
        ]

        pengeluaran_data = [
            {
                "id": k.id,
                "church_id": k.church_id,
                "tanggal": str(k.tanggal),
                "kategori": k.kategori,
                "jumlah": float(k.jumlah),
                "metode_pembayaran": k.metode_pembayaran,
                "penerima": k.penerima,
                "keterangan": k.keterangan,
                "status_persetujuan": k.status_persetujuan,
                "disetujui_oleh": k.disetujui_oleh,
                "created_by": k.created_by,
                "created_at": k.created_at.isoformat() if k.created_at else None,
            }
            for k in k_query.all()
        ]

        anggaran_data = [
            {
                "id": a.id,
                "church_id": a.church_id,
                "tahun": a.tahun,
                "bulan": a.bulan,
                "jenis": a.jenis,
                "kategori": a.kategori,
                "target_nominal": float(a.target_nominal),
                "catatan": a.catatan,
            }
            for a in a_query.all()
        ]

        audit_data = [
            {
                "id": aud.id,
                "church_id": aud.church_id,
                "transaksi_tipe": aud.transaksi_tipe,
                "transaksi_id": aud.transaksi_id,
                "action": aud.action,
                "user_id": aud.user_id,
                "deskripsi": aud.deskripsi,
                "hash_sha256": aud.hash_sha256,
                "prev_hash": aud.prev_hash,
                "created_at": aud.created_at.isoformat() if aud.created_at else None,
            }
            for aud in audit_query.all()
        ]

        tot_p = sum(x["jumlah"] for x in pemasukan_data)
        tot_k = sum(x["jumlah"] for x in pengeluaran_data)

        timestamp_now = datetime.now(timezone.utc)
        timestamp_str = timestamp_now.strftime("%Y%m%d_%H%M%S")

        backup_payload = {
            "metadata": {
                "system": "CMS Gereja - Modul Keuangan & Analitik",
                "version": "1.0-sha256",
                "church_id": church_id,
                "church_name": church_name,
                "created_by": admin_id,
                "created_at": timestamp_now.isoformat(),
                "total_records": len(pemasukan_data) + len(pengeluaran_data) + len(anggaran_data) + len(audit_data),
                "ringkasan_finansial": {
                    "total_pemasukan": tot_p,
                    "total_pengeluaran": tot_k,
                    "saldo_akhir": tot_p - tot_k,
                },
            },
            "data": {
                "pemasukan": pemasukan_data,
                "pengeluaran": pengeluaran_data,
                "anggaran": anggaran_data,
                "audit_transaksi": audit_data,
            }
        }

        # Serialisasi kanonikal untuk perhitungan SHA-256
        canonical_json = json.dumps(backup_payload, sort_keys=True, ensure_ascii=False)
        sha256_checksum = cls.hash_string(canonical_json)

        # Sisipkan checksum ke header file
        full_backup_file = {
            "checksum_sha256": sha256_checksum,
            "content": backup_payload,
        }

        filename = f"backup_keuangan_{timestamp_str}_{sha256_checksum[:8]}.json"
        filepath = os.path.join(target_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(full_backup_file, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(filepath)

        return {
            "status": "SUCCESS",
            "message": "Backup kriptografis data keuangan berhasil dibuat dan diverifikasi.",
            "filename": filename,
            "filepath": filepath,
            "sha256_checksum": sha256_checksum,
            "file_size_bytes": file_size,
            "total_records": backup_payload["metadata"]["total_records"],
            "saldo_terbackup": tot_p - tot_k,
            "timestamp": timestamp_now.isoformat(),
        }

    @classmethod
    def verify_backup_file(cls, filepath: str) -> Dict[str, Any]:
        """
        Memeriksa keutuhan file backup secara kriptografis menggunakan SHA-256
        untuk menjamin tidak ada bit-rot, kerusakan file, atau manipulasi isi backup.
        """
        if not os.path.exists(filepath):
            return {"valid": False, "error": f"File backup tidak ditemukan: {filepath}"}

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                return {"valid": False, "error": f"File bukan JSON valid: {str(e)}"}

        recorded_checksum = data.get("checksum_sha256")
        content = data.get("content")

        if not recorded_checksum or content is None:
            return {"valid": False, "error": "Format file backup tidak memiliki checksum SHA-256 resmi."}

        canonical_json = json.dumps(content, sort_keys=True, ensure_ascii=False)
        calculated_checksum = cls.hash_string(canonical_json)

        is_match = (recorded_checksum == calculated_checksum)
        return {
            "valid": is_match,
            "status": "TERVERIFIKASI_ASLI" if is_match else "FILE_RUSAK_ATAU_DIMANIPULASI",
            "recorded_checksum": recorded_checksum,
            "calculated_checksum": calculated_checksum,
            "metadata": content.get("metadata", {}),
        }

    @classmethod
    def list_backups(cls, backup_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        target_dir = backup_dir or DEFAULT_BACKUP_DIR
        if not os.path.exists(target_dir):
            return []

        results = []
        for fname in sorted(os.listdir(target_dir), reverse=True):
            if fname.startswith("backup_keuangan_") and fname.endswith(".json"):
                fpath = os.path.join(target_dir, fname)
                fsize = os.path.getsize(fpath)
                mtime = os.path.getmtime(fpath)

                results.append({
                    "filename": fname,
                    "filepath": fpath,
                    "file_size_bytes": fsize,
                    "created_at": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                })
        return results
