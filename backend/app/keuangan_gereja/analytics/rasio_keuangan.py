from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.schemas.laporan import RasioKeuanganResponse

class RasioKeuanganGereja:
    @classmethod
    def hitung_rasio(
        cls,
        db: Session,
        church_id: Optional[int] = None,
    ) -> RasioKeuanganResponse:
        p_query = db.query(func.coalesce(func.sum(PemasukanGereja.jumlah), 0.0)).filter(
            PemasukanGereja.status_verifikasi == "Verified"
        )
        k_query = db.query(func.coalesce(func.sum(PengeluaranGereja.jumlah), 0.0)).filter(
            PengeluaranGereja.status_persetujuan == "Disetujui"
        )

        if church_id:
            p_query = p_query.filter(PemasukanGereja.church_id == church_id)
            k_query = k_query.filter(PengeluaranGereja.church_id == church_id)

        tot_pemasukan = float(p_query.scalar() or 0.0)
        tot_pengeluaran = float(k_query.scalar() or 0.0)
        saldo_kas = tot_pemasukan - tot_pengeluaran

        # Rata-rata pengeluaran bulanan (berdasarkan rentang bulan aktif)
        distinct_months = db.query(
            func.count(func.distinct(func.extract('year', PengeluaranGereja.tanggal) * 100 + func.extract('month', PengeluaranGereja.tanggal)))
        )
        if church_id:
            distinct_months = distinct_months.filter(PengeluaranGereja.church_id == church_id)
        n_months = distinct_months.scalar() or 1
        avg_monthly_expense = tot_pengeluaran / max(1, n_months)

        # 1. Cadangan Kas (bulan)
        cadangan_bulan = (saldo_kas / avg_monthly_expense) if avg_monthly_expense > 0 else (12.0 if saldo_kas > 0 else 0.0)
        cadangan_bulan = max(0.0, cadangan_bulan)

        # 2. Operating Expense Ratio
        operasional_query = db.query(func.coalesce(func.sum(PengeluaranGereja.jumlah), 0.0)).filter(
            PengeluaranGereja.status_persetujuan == "Disetujui",
            PengeluaranGereja.kategori.ilike("%operasional%")
        )
        if church_id:
            operasional_query = operasional_query.filter(PengeluaranGereja.church_id == church_id)
        tot_operasional = float(operasional_query.scalar() or 0.0)
        oer = (tot_operasional / tot_pemasukan) if tot_pemasukan > 0 else 0.0

        # 3. Savings / Surplus Ratio
        savings_ratio = ((tot_pemasukan - tot_pengeluaran) / tot_pemasukan) if tot_pemasukan > 0 else 0.0

        # 4. Diakonia Ratio (Misi & Bantuan Sosial)
        diakonia_query = db.query(func.coalesce(func.sum(PengeluaranGereja.jumlah), 0.0)).filter(
            PengeluaranGereja.status_persetujuan == "Disetujui",
            PengeluaranGereja.kategori.ilike("%diakonia%")
        )
        if church_id:
            diakonia_query = diakonia_query.filter(PengeluaranGereja.church_id == church_id)
        tot_diakonia = float(diakonia_query.scalar() or 0.0)
        diakonia_ratio = (tot_diakonia / tot_pengeluaran) if tot_pengeluaran > 0 else 0.0

        # Status Likuiditas
        if cadangan_bulan >= 6.0:
            status = "Sangat Aman (Cadangan Kas > 6 Bulan)"
            catatan = "Kondisi cadangan kas sangat kuat. Gereja memiliki ruang fiskal prima untuk ekspansi misi dan pelayanan pembangunan."
        elif cadangan_bulan >= 3.0:
            status = "Aman (Cadangan Kas 3 - 6 Bulan)"
            catatan = "Likuiditas stabil dan aman sesuai standar tata kelola keuangan nirlaba gerejawi."
        elif cadangan_bulan >= 1.0:
            status = "Waspada (Cadangan Kas 1 - 3 Bulan)"
            catatan = "Cadangan kas menipis. Disarankan memperketat pos pengeluaran operasional non-esensial."
        else:
            status = "Kritis (Cadangan Kas < 1 Bulan)"
            catatan = "Kondisi defisit likuiditas akut. Memerlukan penanganan segera dari Admin Utama dan Majelis Keuangan."

        return RasioKeuanganResponse(
            church_id=church_id,
            cadangan_kas_bulan=round(cadangan_bulan, 2),
            operating_expense_ratio=round(oer, 4),
            savings_ratio=round(savings_ratio, 4),
            diakonia_ratio=round(diakonia_ratio, 4),
            status_likuiditas=status,
            catatan_kesehatan=catatan,
        )
