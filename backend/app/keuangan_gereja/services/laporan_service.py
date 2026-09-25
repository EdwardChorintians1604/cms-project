import calendar
from datetime import date
from typing import List, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.models.anggaran import AnggaranGereja
from app.keuangan_gereja.schemas.laporan import (
    ArusKasItem,
    ArusKasResponse,
    AnggaranCreate,
    AnggaranResponse,
    AnggaranVsRealisasiItem,
    AnggaranVsRealisasiResponse,
    RekapBulananItem,
    RekapBulananResponse,
)

class LaporanService:
    @classmethod
    def get_arus_kas(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> ArusKasResponse:
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

        pemasukan_list = p_query.order_by(PemasukanGereja.tanggal.asc()).all()
        pengeluaran_list = k_query.order_by(PengeluaranGereja.tanggal.asc()).all()

        # Group by YYYY-MM
        periods = set()
        p_by_period = defaultdict(float)
        k_by_period = defaultdict(float)

        for p in pemasukan_list:
            period = p.tanggal.strftime("%Y-%m")
            periods.add(period)
            p_by_period[period] += p.jumlah

        for k in pengeluaran_list:
            period = k.tanggal.strftime("%Y-%m")
            periods.add(period)
            k_by_period[period] += k.jumlah

        sorted_periods = sorted(list(periods))
        cumulative_balance = 0.0
        items: List[ArusKasItem] = []

        total_p = 0.0
        total_k = 0.0

        for period in sorted_periods:
            p_val = p_by_period[period]
            k_val = k_by_period[period]
            net = p_val - k_val
            cumulative_balance += net
            total_p += p_val
            total_k += k_val

            items.append(
                ArusKasItem(
                    periode=period,
                    pemasukan=round(p_val, 2),
                    pengeluaran=round(k_val, 2),
                    arus_kas_bersih=round(net, 2),
                    saldo_kumulatif=round(cumulative_balance, 2),
                )
            )

        return ArusKasResponse(
            church_id=church_id,
            start_date=start_date,
            end_date=end_date,
            items=items,
            total_pemasukan=round(total_p, 2),
            total_pengeluaran=round(total_k, 2),
            net_cash_flow=round(total_p - total_k, 2),
        )

    @classmethod
    def get_anggaran_vs_realisasi(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        tahun: Optional[int] = None,
        bulan: int = 0,
    ) -> AnggaranVsRealisasiResponse:
        current_year = tahun or date.today().year

        anggaran_query = db.query(AnggaranGereja).filter(
            AnggaranGereja.tahun == current_year,
            AnggaranGereja.bulan == bulan,
        )
        if church_id:
            anggaran_query = anggaran_query.filter(AnggaranGereja.church_id == church_id)

        anggaran_list = anggaran_query.all()

        p_query = db.query(
            PemasukanGereja.kategori,
            func.sum(PemasukanGereja.jumlah).label("total")
        ).filter(
            PemasukanGereja.status_verifikasi == "Verified",
            func.extract("year", PemasukanGereja.tanggal) == current_year,
        )
        k_query = db.query(
            PengeluaranGereja.kategori,
            func.sum(PengeluaranGereja.jumlah).label("total")
        ).filter(
            PengeluaranGereja.status_persetujuan == "Disetujui",
            func.extract("year", PengeluaranGereja.tanggal) == current_year,
        )

        if bulan > 0:
            p_query = p_query.filter(func.extract("month", PemasukanGereja.tanggal) == bulan)
            k_query = k_query.filter(func.extract("month", PengeluaranGereja.tanggal) == bulan)
        if church_id:
            p_query = p_query.filter(PemasukanGereja.church_id == church_id)
            k_query = k_query.filter(PengeluaranGereja.church_id == church_id)

        realisasi_p = {row.kategori: float(row.total or 0.0) for row in p_query.group_by(PemasukanGereja.kategori).all()}
        realisasi_k = {row.kategori: float(row.total or 0.0) for row in k_query.group_by(PengeluaranGereja.kategori).all()}

        items: List[AnggaranVsRealisasiItem] = []
        tot_target_p = 0.0
        tot_target_k = 0.0

        handled_kategoris = set()

        for a in anggaran_list:
            handled_kategoris.add((a.jenis.lower(), a.kategori))
            if a.jenis.lower() == "pemasukan":
                tot_target_p += a.target_nominal
                real = realisasi_p.get(a.kategori, 0.0)
                selisih = real - a.target_nominal
                pct = (real / a.target_nominal * 100) if a.target_nominal > 0 else 0.0
                status = "Tercapai" if real >= a.target_nominal else "Di Bawah Target"
            else:
                tot_target_k += a.target_nominal
                real = realisasi_k.get(a.kategori, 0.0)
                selisih = a.target_nominal - real
                pct = (real / a.target_nominal * 100) if a.target_nominal > 0 else 0.0
                status = "Efisien" if real <= a.target_nominal else "Overbudget"

            items.append(
                AnggaranVsRealisasiItem(
                    kategori=a.kategori,
                    jenis=a.jenis,
                    target_anggaran=round(a.target_nominal, 2),
                    realisasi=round(real, 2),
                    selisih=round(selisih, 2),
                    persentase_tercapai=round(pct, 2),
                    status=status,
                )
            )

        # Kategori realisasi yang belum dianggarkan
        for kat, real in realisasi_p.items():
            if ("pemasukan", kat) not in handled_kategoris:
                items.append(
                    AnggaranVsRealisasiItem(
                        kategori=kat,
                        jenis="Pemasukan",
                        target_anggaran=0.0,
                        realisasi=round(real, 2),
                        selisih=round(real, 2),
                        persentase_tercapai=100.0,
                        status="Non-Anggaran",
                    )
                )

        for kat, real in realisasi_k.items():
            if ("pengeluaran", kat) not in handled_kategoris:
                items.append(
                    AnggaranVsRealisasiItem(
                        kategori=kat,
                        jenis="Pengeluaran",
                        target_anggaran=0.0,
                        realisasi=round(real, 2),
                        selisih=round(-real, 2),
                        persentase_tercapai=0.0,
                        status="Overbudget (Tanpa Anggaran)",
                    )
                )

        tot_real_p = sum(realisasi_p.values())
        tot_real_k = sum(realisasi_k.values())

        return AnggaranVsRealisasiResponse(
            church_id=church_id,
            tahun=current_year,
            bulan=bulan,
            items=items,
            total_target_pemasukan=round(tot_target_p, 2),
            total_realisasi_pemasukan=round(tot_real_p, 2),
            total_target_pengeluaran=round(tot_target_k, 2),
            total_realisasi_pengeluaran=round(tot_real_k, 2),
        )

    @classmethod
    def get_rekap_bulanan(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        tahun: Optional[int] = None,
    ) -> RekapBulananResponse:
        current_year = tahun or date.today().year

        p_query = db.query(
            func.extract("month", PemasukanGereja.tanggal).label("m"),
            func.sum(PemasukanGereja.jumlah).label("total")
        ).filter(
            PemasukanGereja.status_verifikasi == "Verified",
            func.extract("year", PemasukanGereja.tanggal) == current_year,
        )

        k_query = db.query(
            func.extract("month", PengeluaranGereja.tanggal).label("m"),
            func.sum(PengeluaranGereja.jumlah).label("total")
        ).filter(
            PengeluaranGereja.status_persetujuan == "Disetujui",
            func.extract("year", PengeluaranGereja.tanggal) == current_year,
        )

        if church_id:
            p_query = p_query.filter(PemasukanGereja.church_id == church_id)
            k_query = k_query.filter(PengeluaranGereja.church_id == church_id)

        p_rows = {int(r.m): float(r.total or 0.0) for r in p_query.group_by("m").all()}
        k_rows = {int(r.m): float(r.total or 0.0) for r in k_query.group_by("m").all()}

        rekap: List[RekapBulananItem] = []
        grand_p = 0.0
        grand_k = 0.0

        for m in range(1, 13):
            p_val = p_rows.get(m, 0.0)
            k_val = k_rows.get(m, 0.0)
            surplus = p_val - k_val
            grand_p += p_val
            grand_k += k_val

            rekap.append(
                RekapBulananItem(
                    bulan=m,
                    nama_bulan=calendar.month_name[m],
                    tahun=current_year,
                    total_pemasukan=round(p_val, 2),
                    total_pengeluaran=round(k_val, 2),
                    surplus_defisit=round(surplus, 2),
                )
            )

        return RekapBulananResponse(
            church_id=church_id,
            tahun=current_year,
            rekap=rekap,
            grand_total_pemasukan=round(grand_p, 2),
            grand_total_pengeluaran=round(grand_k, 2),
            grand_total_surplus=round(grand_p - grand_k, 2),
        )

    @classmethod
    def create_anggaran(cls, db: Session, obj_in: AnggaranCreate) -> AnggaranGereja:
        db_obj = AnggaranGereja(
            church_id=obj_in.church_id,
            tahun=obj_in.tahun,
            bulan=obj_in.bulan,
            jenis=obj_in.jenis,
            kategori=obj_in.kategori,
            target_nominal=float(obj_in.target_nominal),
            catatan=obj_in.catatan,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get_anggaran_list(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        tahun: Optional[int] = None,
    ) -> List[AnggaranGereja]:
        query = db.query(AnggaranGereja)
        if church_id:
            query = query.filter(AnggaranGereja.church_id == church_id)
        if tahun:
            query = query.filter(AnggaranGereja.tahun == tahun)
        return query.order_by(AnggaranGereja.tahun.desc(), AnggaranGereja.bulan.asc()).all()
