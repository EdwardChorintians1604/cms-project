import numpy as np
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.schemas.laporan import (
    DescriptiveStats,
    AnalisisDeskriptifResponse,
)

class AnalisisDeskriptif:
    @staticmethod
    def _calc_stats(values: List[float]) -> DescriptiveStats:
        if not values:
            return DescriptiveStats(
                count=0,
                total=0.0,
                mean=0.0,
                median=0.0,
                std_dev=0.0,
                min=0.0,
                max=0.0,
            )
        arr = np.array(values, dtype=float)
        return DescriptiveStats(
            count=int(len(arr)),
            total=round(float(np.sum(arr)), 2),
            mean=round(float(np.mean(arr)), 2),
            median=round(float(np.median(arr)), 2),
            std_dev=round(float(np.std(arr, ddof=1 if len(arr) > 1 else 0)), 2),
            min=round(float(np.min(arr)), 2),
            max=round(float(np.max(arr)), 2),
        )

    @classmethod
    def get_deskriptif(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> AnalisisDeskriptifResponse:
        p_query = db.query(PemasukanGereja).filter(PemasukanGereja.status_verifikasi == "Verified")
        k_query = db.query(PengeluaranGereja).filter(PengeluaranGereja.status_persetujuan == "Disetujui")

        if church_id:
            p_query = p_query.filter(PemasukanGereja.church_id == church_id)
            k_query = k_query.filter(PengeluaranGereja.church_id == church_id)
        if start_date:
            p_query = p_query.filter(PemasukanGereja.tanggal >= start_date)
            k_query = k_query.filter(PengeluaranGereja.tanggal >= start_date)
        if end_date:
            p_query = p_query.filter(PemasukanGereja.tanggal <= end_date)
            k_query = k_query.filter(PengeluaranGereja.tanggal <= end_date)

        pemasukan_rows = p_query.all()
        pengeluaran_rows = k_query.all()

        p_vals = [float(p.jumlah) for p in pemasukan_rows]
        k_vals = [float(k.jumlah) for k in pengeluaran_rows]

        p_stats = cls._calc_stats(p_vals)
        k_stats = cls._calc_stats(k_vals)

        # Proporsi kategori pemasukan
        p_kat_sums = {}
        for p in pemasukan_rows:
            p_kat_sums[p.kategori] = p_kat_sums.get(p.kategori, 0.0) + p.jumlah
        p_props = []
        for kat, total in p_kat_sums.items():
            pct = (total / p_stats.total * 100) if p_stats.total > 0 else 0.0
            p_props.append({"kategori": kat, "total": round(total, 2), "persen": round(pct, 2)})

        # Proporsi kategori pengeluaran
        k_kat_sums = {}
        for k in pengeluaran_rows:
            k_kat_sums[k.kategori] = k_kat_sums.get(k.kategori, 0.0) + k.jumlah
        k_props = []
        for kat, total in k_kat_sums.items():
            pct = (total / k_stats.total * 100) if k_stats.total > 0 else 0.0
            k_props.append({"kategori": kat, "total": round(total, 2), "persen": round(pct, 2)})

        # Growth MoM (Bulan ini vs Bulan sebelumnya)
        today = date.today()
        cur_year, cur_month = today.year, today.month
        prev_month = cur_month - 1 if cur_month > 1 else 12
        prev_year = cur_year if cur_month > 1 else cur_year - 1

        def get_monthly_sum(items, yr, mo):
            return sum(float(x.jumlah) for x in items if x.tanggal.year == yr and x.tanggal.month == mo)

        p_cur = get_monthly_sum(pemasukan_rows, cur_year, cur_month)
        p_prev = get_monthly_sum(pemasukan_rows, prev_year, prev_month)
        p_mom = ((p_cur - p_prev) / p_prev * 100) if p_prev > 0 else (100.0 if p_cur > 0 else 0.0)

        k_cur = get_monthly_sum(pengeluaran_rows, cur_year, cur_month)
        k_prev = get_monthly_sum(pengeluaran_rows, prev_year, prev_month)
        k_mom = ((k_cur - k_prev) / k_prev * 100) if k_prev > 0 else (100.0 if k_cur > 0 else 0.0)

        return AnalisisDeskriptifResponse(
            church_id=church_id,
            start_date=start_date,
            end_date=end_date,
            pemasukan_stats=p_stats,
            pengeluaran_stats=k_stats,
            pertumbuhan_mom_pemasukan=round(p_mom, 2),
            pertumbuhan_mom_pengeluaran=round(k_mom, 2),
            proporsi_kategori_pemasukan=sorted(p_props, key=lambda x: x["total"], reverse=True),
            proporsi_kategori_pengeluaran=sorted(k_props, key=lambda x: x["total"], reverse=True),
        )
