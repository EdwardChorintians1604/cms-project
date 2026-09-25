from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.models.church import Church
from app.keuangan_gereja.schemas.laporan import SaldoSummaryResponse

class SaldoService:
    @classmethod
    def get_saldo_summary(cls, db: Session, church_id: Optional[int] = None) -> SaldoSummaryResponse:
        p_query = db.query(
            func.coalesce(func.sum(PemasukanGereja.jumlah), 0.0).label("total"),
            func.count(PemasukanGereja.id).label("count")
        ).filter(PemasukanGereja.status_verifikasi == "Verified")

        k_query = db.query(
            func.coalesce(func.sum(PengeluaranGereja.jumlah), 0.0).label("total"),
            func.count(PengeluaranGereja.id).label("count")
        ).filter(PengeluaranGereja.status_persetujuan == "Disetujui")

        church_name = "Seluruh Gereja (Konsolidasi Pusat)"
        if church_id:
            p_query = p_query.filter(PemasukanGereja.church_id == church_id)
            k_query = k_query.filter(PengeluaranGereja.church_id == church_id)
            church = db.query(Church).filter(Church.id == church_id).first()
            if church:
                church_name = church.church_name

        total_pemasukan, count_p = p_query.first()
        total_pengeluaran, count_k = k_query.first()

        total_pemasukan = float(total_pemasukan or 0.0)
        total_pengeluaran = float(total_pengeluaran or 0.0)
        saldo_akhir = total_pemasukan - total_pengeluaran

        # Breakdown per metode pembayaran
        p_metode = db.query(
            PemasukanGereja.metode_pembayaran,
            func.sum(PemasukanGereja.jumlah).label("total")
        ).filter(PemasukanGereja.status_verifikasi == "Verified")
        if church_id:
            p_metode = p_metode.filter(PemasukanGereja.church_id == church_id)
        p_metode_rows = p_metode.group_by(PemasukanGereja.metode_pembayaran).all()

        k_metode = db.query(
            PengeluaranGereja.metode_pembayaran,
            func.sum(PengeluaranGereja.jumlah).label("total")
        ).filter(PengeluaranGereja.status_persetujuan == "Disetujui")
        if church_id:
            k_metode = k_metode.filter(PengeluaranGereja.church_id == church_id)
        k_metode_rows = k_metode.group_by(PengeluaranGereja.metode_pembayaran).all()

        saldo_per_metode: Dict[str, float] = {}
        for row in p_metode_rows:
            metode = row.metode_pembayaran or "Lainnya"
            saldo_per_metode[metode] = saldo_per_metode.get(metode, 0.0) + float(row.total or 0.0)

        for row in k_metode_rows:
            metode = row.metode_pembayaran or "Lainnya"
            saldo_per_metode[metode] = saldo_per_metode.get(metode, 0.0) - float(row.total or 0.0)

        return SaldoSummaryResponse(
            church_id=church_id,
            church_name=church_name,
            total_pemasukan=round(total_pemasukan, 2),
            total_pengeluaran=round(total_pengeluaran, 2),
            saldo_akhir=round(saldo_akhir, 2),
            saldo_per_metode={k: round(v, 2) for k, v in saldo_per_metode.items()},
            total_transaksi_pemasukan=int(count_p or 0),
            total_transaksi_pengeluaran=int(count_k or 0),
        )
