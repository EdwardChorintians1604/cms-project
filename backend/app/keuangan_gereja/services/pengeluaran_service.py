import json
from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.models.audit_transaksi import AuditTransaksiKeuangan
from app.keuangan_gereja.schemas.pengeluaran import (
    PengeluaranCreate,
    PengeluaranUpdate,
    PengeluaranFilter,
    PengeluaranSummaryKategori,
)
from app.keuangan_gereja.security.kriptografi_sha256 import CryptoKeuanganSHA256

class PengeluaranService:
    @staticmethod
    def _log_audit(
        db: Session,
        church_id: Optional[int],
        transaksi_id: int,
        action: str,
        user_id: Optional[str],
        user_role: Optional[str],
        deskripsi: str,
        sebelum: Optional[dict] = None,
        sesudah: Optional[dict] = None,
    ):
        return CryptoKeuanganSHA256.log_and_hash_audit(
            db=db,
            church_id=church_id,
            transaksi_tipe="pengeluaran",
            transaksi_id=transaksi_id,
            action=action,
            user_id=user_id,
            user_role=user_role,
            deskripsi=deskripsi,
            sebelum=sebelum,
            sesudah=sesudah,
        )


    @classmethod
    def create(
        cls,
        db: Session,
        obj_in: PengeluaranCreate,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> PengeluaranGereja:
        db_obj = PengeluaranGereja(
            church_id=obj_in.church_id,
            tanggal=obj_in.tanggal or date.today(),
            kategori=obj_in.kategori,
            jumlah=float(obj_in.jumlah),
            metode_pembayaran=obj_in.metode_pembayaran,
            penerima=obj_in.penerima,
            keterangan=obj_in.keterangan,
            bukti_transaksi_url=obj_in.bukti_transaksi_url,
            status_persetujuan=obj_in.status_persetujuan or "Disetujui",
            disetujui_oleh=user_id if obj_in.status_persetujuan == "Disetujui" else None,
            created_by=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        cls._log_audit(
            db,
            church_id=db_obj.church_id,
            transaksi_id=db_obj.id,
            action="CREATE",
            user_id=user_id,
            user_role=user_role,
            deskripsi=f"Mencatat pengeluaran {db_obj.kategori} sebesar Rp {db_obj.jumlah:,.2f}",
            sesudah={"jumlah": db_obj.jumlah, "kategori": db_obj.kategori, "tanggal": str(db_obj.tanggal)},
        )
        db.commit()
        return db_obj

    @classmethod
    def get_by_id(cls, db: Session, id: int) -> Optional[PengeluaranGereja]:
        return db.query(PengeluaranGereja).filter(PengeluaranGereja.id == id).first()

    @classmethod
    def get_multi(
        cls,
        db: Session,
        filters: Optional[PengeluaranFilter] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[PengeluaranGereja], int]:
        query = db.query(PengeluaranGereja)
        if filters:
            if filters.church_id:
                query = query.filter(PengeluaranGereja.church_id == filters.church_id)
            if filters.kategori:
                query = query.filter(PengeluaranGereja.kategori == filters.kategori)
            if filters.start_date:
                query = query.filter(PengeluaranGereja.tanggal >= filters.start_date)
            if filters.end_date:
                query = query.filter(PengeluaranGereja.tanggal <= filters.end_date)
            if filters.metode_pembayaran:
                query = query.filter(PengeluaranGereja.metode_pembayaran == filters.metode_pembayaran)
            if filters.status_persetujuan:
                query = query.filter(PengeluaranGereja.status_persetujuan == filters.status_persetujuan)

        total = query.count()
        results = query.order_by(PengeluaranGereja.tanggal.desc(), PengeluaranGereja.id.desc()).offset(skip).limit(limit).all()
        return results, total

    @classmethod
    def update(
        cls,
        db: Session,
        id: int,
        obj_in: PengeluaranUpdate,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> Optional[PengeluaranGereja]:
        db_obj = cls.get_by_id(db, id=id)
        if not db_obj:
            return None

        sebelum = {
            "jumlah": db_obj.jumlah,
            "kategori": db_obj.kategori,
            "tanggal": str(db_obj.tanggal),
            "status_persetujuan": db_obj.status_persetujuan,
        }

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        sesudah = {
            "jumlah": db_obj.jumlah,
            "kategori": db_obj.kategori,
            "tanggal": str(db_obj.tanggal),
            "status_persetujuan": db_obj.status_persetujuan,
        }

        cls._log_audit(
            db,
            church_id=db_obj.church_id,
            transaksi_id=db_obj.id,
            action="UPDATE",
            user_id=user_id,
            user_role=user_role,
            deskripsi=f"Memperbarui transaksi pengeluaran ID #{db_obj.id}",
            sebelum=sebelum,
            sesudah=sesudah,
        )
        db.commit()
        return db_obj

    @classmethod
    def delete(
        cls,
        db: Session,
        id: int,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> bool:
        db_obj = cls.get_by_id(db, id=id)
        if not db_obj:
            return False

        church_id = db_obj.church_id
        sebelum = {"jumlah": db_obj.jumlah, "kategori": db_obj.kategori}

        db.delete(db_obj)
        db.commit()

        cls._log_audit(
            db,
            church_id=church_id,
            transaksi_id=id,
            action="DELETE",
            user_id=user_id,
            user_role=user_role,
            deskripsi=f"Menghapus transaksi pengeluaran ID #{id}",
            sebelum=sebelum,
        )
        db.commit()
        return True

    @classmethod
    def approve(
        cls,
        db: Session,
        id: int,
        status: str,
        approver_name: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> Optional[PengeluaranGereja]:
        db_obj = cls.get_by_id(db, id=id)
        if not db_obj:
            return None

        sebelum_status = db_obj.status_persetujuan
        db_obj.status_persetujuan = status
        db_obj.disetujui_oleh = approver_name

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        cls._log_audit(
            db,
            church_id=db_obj.church_id,
            transaksi_id=id,
            action="APPROVE",
            user_id=user_id,
            user_role=user_role,
            deskripsi=f"Approval pengeluaran ID #{id} status: {status} oleh {approver_name}",
            sebelum={"status_persetujuan": sebelum_status},
            sesudah={"status_persetujuan": status, "disetujui_oleh": approver_name},
        )
        db.commit()
        return db_obj

    @classmethod
    def get_summary_by_kategori(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PengeluaranSummaryKategori]:
        query = db.query(
            PengeluaranGereja.kategori,
            func.sum(PengeluaranGereja.jumlah).label("total"),
            func.count(PengeluaranGereja.id).label("count"),
        ).filter(PengeluaranGereja.status_persetujuan == "Disetujui")

        if church_id:
            query = query.filter(PengeluaranGereja.church_id == church_id)
        if start_date:
            query = query.filter(PengeluaranGereja.tanggal >= start_date)
        if end_date:
            query = query.filter(PengeluaranGereja.tanggal <= end_date)

        rows = query.group_by(PengeluaranGereja.kategori).all()
        total_all = sum(r.total or 0.0 for r in rows)

        summaries = []
        for r in rows:
            tot = float(r.total or 0.0)
            pct = (tot / total_all * 100) if total_all > 0 else 0.0
            summaries.append(
                PengeluaranSummaryKategori(
                    kategori=r.kategori,
                    total_jumlah=tot,
                    jumlah_transaksi=int(r.count),
                    persentase=round(pct, 2),
                )
            )
        return summaries
