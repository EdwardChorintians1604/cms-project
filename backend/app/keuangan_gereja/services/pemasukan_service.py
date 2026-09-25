import json
from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.audit_transaksi import AuditTransaksiKeuangan
from app.keuangan_gereja.schemas.pemasukan import (
    PemasukanCreate,
    PemasukanUpdate,
    PemasukanFilter,
    PemasukanSummaryKategori,
)
from app.keuangan_gereja.security.kriptografi_sha256 import CryptoKeuanganSHA256

class PemasukanService:
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
            transaksi_tipe="pemasukan",
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
        obj_in: PemasukanCreate,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> PemasukanGereja:
        db_obj = PemasukanGereja(
            church_id=obj_in.church_id,
            tanggal=obj_in.tanggal or date.today(),
            kategori=obj_in.kategori,
            jumlah=float(obj_in.jumlah),
            metode_pembayaran=obj_in.metode_pembayaran,
            keterangan=obj_in.keterangan,
            bukti_transaksi_url=obj_in.bukti_transaksi_url,
            status_verifikasi=obj_in.status_verifikasi or "Verified",
            donor_name=obj_in.donor_name,
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
            deskripsi=f"Mencatat pemasukan {db_obj.kategori} sebesar Rp {db_obj.jumlah:,.2f}",
            sesudah={"jumlah": db_obj.jumlah, "kategori": db_obj.kategori, "tanggal": str(db_obj.tanggal)},
        )
        db.commit()
        return db_obj

    @classmethod
    def get_by_id(cls, db: Session, id: int) -> Optional[PemasukanGereja]:
        return db.query(PemasukanGereja).filter(PemasukanGereja.id == id).first()

    @classmethod
    def get_multi(
        cls,
        db: Session,
        filters: Optional[PemasukanFilter] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[PemasukanGereja], int]:
        query = db.query(PemasukanGereja)
        if filters:
            if filters.church_id:
                query = query.filter(PemasukanGereja.church_id == filters.church_id)
            if filters.kategori:
                query = query.filter(PemasukanGereja.kategori == filters.kategori)
            if filters.start_date:
                query = query.filter(PemasukanGereja.tanggal >= filters.start_date)
            if filters.end_date:
                query = query.filter(PemasukanGereja.tanggal <= filters.end_date)
            if filters.metode_pembayaran:
                query = query.filter(PemasukanGereja.metode_pembayaran == filters.metode_pembayaran)
            if filters.status_verifikasi:
                query = query.filter(PemasukanGereja.status_verifikasi == filters.status_verifikasi)

        total = query.count()
        results = query.order_by(PemasukanGereja.tanggal.desc(), PemasukanGereja.id.desc()).offset(skip).limit(limit).all()
        return results, total

    @classmethod
    def update(
        cls,
        db: Session,
        id: int,
        obj_in: PemasukanUpdate,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> Optional[PemasukanGereja]:
        db_obj = cls.get_by_id(db, id=id)
        if not db_obj:
            return None

        sebelum = {
            "jumlah": db_obj.jumlah,
            "kategori": db_obj.kategori,
            "tanggal": str(db_obj.tanggal),
            "status_verifikasi": db_obj.status_verifikasi,
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
            "status_verifikasi": db_obj.status_verifikasi,
        }

        cls._log_audit(
            db,
            church_id=db_obj.church_id,
            transaksi_id=db_obj.id,
            action="UPDATE",
            user_id=user_id,
            user_role=user_role,
            deskripsi=f"Memperbarui transaksi pemasukan ID #{db_obj.id}",
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
            deskripsi=f"Menghapus transaksi pemasukan ID #{id}",
            sebelum=sebelum,
        )
        db.commit()
        return True

    @classmethod
    def verify(
        cls,
        db: Session,
        id: int,
        status: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
    ) -> Optional[PemasukanGereja]:
        db_obj = cls.get_by_id(db, id=id)
        if not db_obj:
            return None

        sebelum_status = db_obj.status_verifikasi
        db_obj.status_verifikasi = status
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        cls._log_audit(
            db,
            church_id=db_obj.church_id,
            transaksi_id=id,
            action="VERIFY",
            user_id=user_id,
            user_role=user_role,
            deskripsi=f"Verifikasi pemasukan ID #{id} menjadi {status}",
            sebelum={"status_verifikasi": sebelum_status},
            sesudah={"status_verifikasi": status},
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
    ) -> List[PemasukanSummaryKategori]:
        query = db.query(
            PemasukanGereja.kategori,
            func.sum(PemasukanGereja.jumlah).label("total"),
            func.count(PemasukanGereja.id).label("count"),
        ).filter(PemasukanGereja.status_verifikasi == "Verified")

        if church_id:
            query = query.filter(PemasukanGereja.church_id == church_id)
        if start_date:
            query = query.filter(PemasukanGereja.tanggal >= start_date)
        if end_date:
            query = query.filter(PemasukanGereja.tanggal <= end_date)

        rows = query.group_by(PemasukanGereja.kategori).all()
        total_all = sum(r.total or 0.0 for r in rows)

        summaries = []
        for r in rows:
            tot = float(r.total or 0.0)
            pct = (tot / total_all * 100) if total_all > 0 else 0.0
            summaries.append(
                PemasukanSummaryKategori(
                    kategori=r.kategori,
                    total_jumlah=tot,
                    jumlah_transaksi=int(r.count),
                    persentase=round(pct, 2),
                )
            )
        return summaries
