from datetime import date, datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.keuangan_gereja.services.export_service import KeuanganExportService

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.main_admin import MainAdmin
from app.models.church_admin import ChurchAdmin

from app.keuangan_gereja.schemas.pemasukan import (
    PemasukanCreate,
    PemasukanUpdate,
    PemasukanResponse,
    PemasukanFilter,
    PemasukanSummaryKategori,
)
from app.keuangan_gereja.schemas.pengeluaran import (
    PengeluaranCreate,
    PengeluaranUpdate,
    PengeluaranResponse,
    PengeluaranFilter,
    PengeluaranApproval,
    PengeluaranSummaryKategori,
)
from app.keuangan_gereja.schemas.laporan import (
    SaldoSummaryResponse,
    ArusKasResponse,
    AnggaranCreate,
    AnggaranResponse,
    AnggaranVsRealisasiResponse,
    RekapBulananResponse,
    AnalisisDeskriptifResponse,
    ForecastingResponse,
    DeteksiAnomaliResponse,
    RasioKeuanganResponse,
    FuzzyKesehatanRequest,
    FuzzyKesehatanResponse,
    SPKProgramRequest,
    SPKProgramResponse,
    IntegrityCheckResponse,
    BackupCreateRequest,
    BackupCreateResponse,
    BackupVerifyRequest,
    BackupVerifyResponse,
    BackupListItem,
)

from app.keuangan_gereja.services.pemasukan_service import PemasukanService
from app.keuangan_gereja.services.pengeluaran_service import PengeluaranService
from app.keuangan_gereja.services.saldo_service import SaldoService
from app.keuangan_gereja.services.laporan_service import LaporanService
from app.keuangan_gereja.analytics.analisis_deskriptif import AnalisisDeskriptif
from app.keuangan_gereja.analytics.forecasting import ForecastingKeuangan
from app.keuangan_gereja.analytics.deteksi_anomali import DeteksiAnomaliKeuangan
from app.keuangan_gereja.analytics.rasio_keuangan import RasioKeuanganGereja
from app.keuangan_gereja.fuzzy.kesehatan_keuangan import FuzzyKesehatanKeuangan
from app.keuangan_gereja.spk.prioritas_program import SPKPrioritasProgram
from app.keuangan_gereja.security.kriptografi_sha256 import CryptoKeuanganSHA256


router = APIRouter()

def is_main_admin(current_user: Any) -> bool:
    if isinstance(current_user, MainAdmin):
        return True
    if getattr(current_user, "role", None) in ["superadmin", "main_admin"]:
        return True
    if hasattr(current_user, "developer_code") or hasattr(current_user, "development_id"):
        return True
    return False


def check_church_access(current_user: Any, requested_church_id: Optional[int]) -> Optional[int]:
    """
    Validasi hak akses:
    - Main Admin bebas akses seluruh church atau spesifik church_id.
    - Church Admin dibatasi HANYA untuk church miliknya sendiri.
    - User umum (Jemaat) ditolak.
    """
    if is_main_admin(current_user):
        return requested_church_id

    if isinstance(current_user, ChurchAdmin) or getattr(current_user, "church_id", None) is not None:
        user_church_id = getattr(current_user, "church_id", None)
        if requested_church_id is not None and requested_church_id != user_church_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses ditolak: Anda hanya dapat mengakses data keuangan cabang Anda sendiri."
            )
        return user_church_id

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Akses ditolak: Hanya Admin Utama atau Admin Cabang yang berwenang mengakses modul keuangan."
    )

def enforce_not_main_admin_for_transaction_write(current_user: Any):
    if is_main_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak: Admin Utama berstatus Read-Only / Analis Pengawas untuk pencatatan transaksi langsung. Pencatatan transaksi operasional dilakukan oleh Admin / Bendahara Cabang terkait."
        )

# ==============================================================================
# PEMASUKAN
# ==============================================================================

@router.post("/pemasukan", response_model=PemasukanResponse, status_code=status.HTTP_201_CREATED)
def create_pemasukan(
    payload: PemasukanCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    enforce_not_main_admin_for_transaction_write(current_user)
    check_church_access(current_user, payload.church_id)
    user_id = str(getattr(current_user, "id", "admin"))
    user_role = getattr(current_user, "role", "church_admin")
    return PemasukanService.create(db, payload, user_id=user_id, user_role=user_role)

@router.get("/pemasukan", response_model=List[PemasukanResponse])
def get_pemasukan_list(
    church_id: Optional[int] = Query(None),
    kategori: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    metode_pembayaran: Optional[str] = Query(None),
    status_verifikasi: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    filter_obj = PemasukanFilter(
        church_id=target_church,
        kategori=kategori,
        start_date=start_date,
        end_date=end_date,
        metode_pembayaran=metode_pembayaran,
        status_verifikasi=status_verifikasi,
    )
    items, _ = PemasukanService.get_multi(db, filter_obj, skip=skip, limit=limit)
    return items

@router.get("/pemasukan/{id}", response_model=PemasukanResponse)
def get_pemasukan_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    item = PemasukanService.get_by_id(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Data pemasukan tidak ditemukan")
    check_church_access(current_user, item.church_id)
    return item

@router.put("/pemasukan/{id}", response_model=PemasukanResponse)
def update_pemasukan(
    id: int,
    payload: PemasukanUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    enforce_not_main_admin_for_transaction_write(current_user)
    item = PemasukanService.get_by_id(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Data pemasukan tidak ditemukan")
    check_church_access(current_user, item.church_id)
    user_id = str(getattr(current_user, "id", "admin"))
    user_role = getattr(current_user, "role", "church_admin")
    return PemasukanService.update(db, id=id, obj_in=payload, user_id=user_id, user_role=user_role)

@router.delete("/pemasukan/{id}")
def delete_pemasukan(
    id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    enforce_not_main_admin_for_transaction_write(current_user)
    item = PemasukanService.get_by_id(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Data pemasukan tidak ditemukan")
    check_church_access(current_user, item.church_id)
    user_id = str(getattr(current_user, "id", "admin"))
    user_role = getattr(current_user, "role", "church_admin")
    success = PemasukanService.delete(db, id=id, user_id=user_id, user_role=user_role)
    return {"status": "success", "message": "Transaksi pemasukan berhasil dihapus"}


@router.put("/pemasukan/{id}/verify", response_model=PemasukanResponse)
def verify_pemasukan(
    id: int,
    status_verifikasi: str = Query(..., description="Verified / Rejected"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    item = PemasukanService.get_by_id(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Data pemasukan tidak ditemukan")
    check_church_access(current_user, item.church_id)
    user_id = str(getattr(current_user, "id", "admin"))
    user_role = getattr(current_user, "role", "main_admin" if is_main_admin(current_user) else "church_admin")
    updated = PemasukanService.verify(db, id=id, status=status_verifikasi, user_id=user_id, user_role=user_role)
    return updated

@router.get("/pemasukan-summary-kategori", response_model=List[PemasukanSummaryKategori])
def get_pemasukan_summary_kategori(
    church_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return PemasukanService.get_summary_by_kategori(db, church_id=target_church, start_date=start_date, end_date=end_date)

@router.get("/pemasukan/export/excel")
def export_pemasukan_excel(
    church_id: Optional[int] = Query(None),
    kategori: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Ekspor data pemasukan kas gereja ke format Microsoft Excel (.xlsx) menggunakan openpyxl.
    """
    target_church = check_church_access(current_user, church_id)
    filter_obj = PemasukanFilter(
        church_id=target_church,
        kategori=kategori,
        start_date=start_date,
        end_date=end_date,
    )
    items, _ = PemasukanService.get_multi(db, filter_obj, skip=0, limit=5000)
    church_label = f"Cabang ID #{target_church}" if target_church else "Seluruh Cabang Sinode"
    buf = KeuanganExportService.generate_excel("Pemasukan Kas & Persembahan Gereja", items, is_pemasukan=True, church_name=church_label)
    
    filename = f"Laporan_Pemasukan_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/pemasukan/export/pdf")
def export_pemasukan_pdf(
    church_id: Optional[int] = Query(None),
    kategori: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Ekspor laporan resmi pemasukan kas gereja ke format PDF menggunakan ReportLab.
    """
    target_church = check_church_access(current_user, church_id)
    filter_obj = PemasukanFilter(
        church_id=target_church,
        kategori=kategori,
        start_date=start_date,
        end_date=end_date,
    )
    items, _ = PemasukanService.get_multi(db, filter_obj, skip=0, limit=5000)
    church_label = f"Cabang ID #{target_church}" if target_church else "Seluruh Cabang Sinode"
    buf = KeuanganExportService.generate_pdf("Pemasukan Kas & Persembahan Gereja", items, is_pemasukan=True, church_name=church_label)
    
    filename = f"Laporan_Pemasukan_{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# ==============================================================================
# PENGELUARAN
# ==============================================================================

@router.post("/pengeluaran", response_model=PengeluaranResponse, status_code=status.HTTP_201_CREATED)
def create_pengeluaran(
    payload: PengeluaranCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    enforce_not_main_admin_for_transaction_write(current_user)
    check_church_access(current_user, payload.church_id)
    user_id = str(getattr(current_user, "id", "admin"))
    user_role = getattr(current_user, "role", "church_admin")
    return PengeluaranService.create(db, payload, user_id=user_id, user_role=user_role)

@router.get("/pengeluaran", response_model=List[PengeluaranResponse])
def get_pengeluaran_list(
    church_id: Optional[int] = Query(None),
    kategori: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    metode_pembayaran: Optional[str] = Query(None),
    status_persetujuan: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    filter_obj = PengeluaranFilter(
        church_id=target_church,
        kategori=kategori,
        start_date=start_date,
        end_date=end_date,
        metode_pembayaran=metode_pembayaran,
        status_persetujuan=status_persetujuan,
    )
    items, _ = PengeluaranService.get_multi(db, filter_obj, skip=skip, limit=limit)
    return items

@router.get("/pengeluaran/{id}", response_model=PengeluaranResponse)
def get_pengeluaran_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    item = PengeluaranService.get_by_id(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Data pengeluaran tidak ditemukan")
    check_church_access(current_user, item.church_id)
    return item

@router.put("/pengeluaran/{id}", response_model=PengeluaranResponse)
def update_pengeluaran(
    id: int,
    payload: PengeluaranUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    enforce_not_main_admin_for_transaction_write(current_user)
    item = PengeluaranService.get_by_id(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Data pengeluaran tidak ditemukan")
    check_church_access(current_user, item.church_id)
    user_id = str(getattr(current_user, "id", "admin"))
    user_role = getattr(current_user, "role", "church_admin")
    return PengeluaranService.update(db, id=id, obj_in=payload, user_id=user_id, user_role=user_role)

@router.delete("/pengeluaran/{id}")
def delete_pengeluaran(
    id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    enforce_not_main_admin_for_transaction_write(current_user)
    item = PengeluaranService.get_by_id(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Data pengeluaran tidak ditemukan")
    check_church_access(current_user, item.church_id)
    user_id = str(getattr(current_user, "id", "admin"))
    user_role = getattr(current_user, "role", "church_admin")
    PengeluaranService.delete(db, id=id, user_id=user_id, user_role=user_role)
    return {"status": "success", "message": "Transaksi pengeluaran berhasil dihapus"}


@router.put("/pengeluaran/{id}/approve", response_model=PengeluaranResponse)
def approve_pengeluaran(
    id: int,
    payload: PengeluaranApproval,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    item = PengeluaranService.get_by_id(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Data pengeluaran tidak ditemukan")
    check_church_access(current_user, item.church_id)
    approver = getattr(current_user, "name", "Admin")
    user_id = str(getattr(current_user, "id", "admin"))
    user_role = getattr(current_user, "role", "main_admin" if is_main_admin(current_user) else "church_admin")
    return PengeluaranService.approve(
        db,
        id=id,
        status=payload.status_persetujuan,
        approver_name=approver,
        user_id=user_id,
        user_role=user_role,
    )

@router.get("/pengeluaran-summary-kategori", response_model=List[PengeluaranSummaryKategori])
def get_pengeluaran_summary_kategori(
    church_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return PengeluaranService.get_summary_by_kategori(db, church_id=target_church, start_date=start_date, end_date=end_date)

@router.get("/pengeluaran/export/excel")
def export_pengeluaran_excel(
    church_id: Optional[int] = Query(None),
    kategori: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Ekspor data pengeluaran kas gereja ke format Microsoft Excel (.xlsx) menggunakan openpyxl.
    """
    target_church = check_church_access(current_user, church_id)
    filter_obj = PengeluaranFilter(
        church_id=target_church,
        kategori=kategori,
        start_date=start_date,
        end_date=end_date,
    )
    items, _ = PengeluaranService.get_multi(db, filter_obj, skip=0, limit=5000)
    church_label = f"Cabang ID #{target_church}" if target_church else "Seluruh Cabang Sinode"
    buf = KeuanganExportService.generate_excel("Pengeluaran Kas & Beban Operasional Gereja", items, is_pemasukan=False, church_name=church_label)
    
    filename = f"Laporan_Pengeluaran_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/pengeluaran/export/pdf")
def export_pengeluaran_pdf(
    church_id: Optional[int] = Query(None),
    kategori: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Ekspor laporan resmi pengeluaran kas gereja ke format PDF menggunakan ReportLab.
    """
    target_church = check_church_access(current_user, church_id)
    filter_obj = PengeluaranFilter(
        church_id=target_church,
        kategori=kategori,
        start_date=start_date,
        end_date=end_date,
    )
    items, _ = PengeluaranService.get_multi(db, filter_obj, skip=0, limit=5000)
    church_label = f"Cabang ID #{target_church}" if target_church else "Seluruh Cabang Sinode"
    buf = KeuanganExportService.generate_pdf("Pengeluaran Kas & Beban Operasional Gereja", items, is_pemasukan=False, church_name=church_label)
    
    filename = f"Laporan_Pengeluaran_{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# ==============================================================================
# SALDO & LAPORAN
# ==============================================================================

@router.get("/saldo", response_model=SaldoSummaryResponse)
def get_saldo(
    church_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return SaldoService.get_saldo_summary(db, church_id=target_church)

@router.get("/laporan/arus-kas", response_model=ArusKasResponse)
def get_laporan_arus_kas(
    church_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return LaporanService.get_arus_kas(db, church_id=target_church, start_date=start_date, end_date=end_date)

@router.get("/laporan/anggaran-vs-realisasi", response_model=AnggaranVsRealisasiResponse)
def get_anggaran_vs_realisasi(
    church_id: Optional[int] = Query(None),
    tahun: Optional[int] = Query(None),
    bulan: int = Query(0, ge=0, le=12),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return LaporanService.get_anggaran_vs_realisasi(db, church_id=target_church, tahun=tahun, bulan=bulan)

@router.get("/laporan/rekap-bulanan", response_model=RekapBulananResponse)
def get_rekap_bulanan(
    church_id: Optional[int] = Query(None),
    tahun: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return LaporanService.get_rekap_bulanan(db, church_id=target_church, tahun=tahun)

@router.post("/anggaran", response_model=AnggaranResponse, status_code=status.HTTP_201_CREATED)
def create_anggaran(
    payload: AnggaranCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    check_church_access(current_user, payload.church_id)
    return LaporanService.create_anggaran(db, payload)

@router.get("/anggaran", response_model=List[AnggaranResponse])
def get_anggaran(
    church_id: Optional[int] = Query(None),
    tahun: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return LaporanService.get_anggaran_list(db, church_id=target_church, tahun=tahun)

# ==============================================================================
# ANALYTICS (DESKRIPTIF, FORECASTING, ANOMALI, RASIO)
# ==============================================================================

@router.get("/analytics/deskriptif", response_model=AnalisisDeskriptifResponse)
def get_analisis_deskriptif(
    church_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return AnalisisDeskriptif.get_deskriptif(db, church_id=target_church, start_date=start_date, end_date=end_date)

@router.get("/analytics/forecasting", response_model=ForecastingResponse)
def get_forecasting(
    church_id: Optional[int] = Query(None),
    horizon_bulan: int = Query(3, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return ForecastingKeuangan.generate_forecast(db, church_id=target_church, horizon_bulan=horizon_bulan)

@router.get("/analytics/anomali", response_model=DeteksiAnomaliResponse)
def get_deteksi_anomali(
    church_id: Optional[int] = Query(None),
    threshold_z: float = Query(2.5, ge=1.0, le=5.0),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return DeteksiAnomaliKeuangan.scan_anomali(db, church_id=target_church, threshold_z=threshold_z)

@router.get("/analytics/rasio", response_model=RasioKeuanganResponse)
def get_rasio_keuangan(
    church_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, church_id)
    return RasioKeuanganGereja.hitung_rasio(db, church_id=target_church)

# ==============================================================================
# FUZZY INFERENCE & SISTEM PENDUKUNG KEPUTUSAN (SPK)
# ==============================================================================

@router.post("/fuzzy/kesehatan-keuangan", response_model=FuzzyKesehatanResponse)
def post_fuzzy_kesehatan(
    payload: Optional[FuzzyKesehatanRequest] = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    target_church = check_church_access(current_user, payload.church_id if payload else None)
    if payload:
        payload.church_id = target_church
    return FuzzyKesehatanKeuangan.evaluasi(db, req=payload)

@router.post("/spk/prioritas-program", response_model=SPKProgramResponse)
def post_spk_prioritas(
    payload: SPKProgramRequest,
    current_user: Any = Depends(get_current_user),
):
    check_church_access(current_user, payload.church_id)
    return SPKPrioritasProgram.proses_spk(payload)

# ==============================================================================
# KEAMANAN KRIPTOGRAFIS SHA-256 & BACKUP DATA KEUANGAN
# ==============================================================================

@router.get("/keamanan/integritas", response_model=IntegrityCheckResponse)
def verify_keuangan_integrity(
    church_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Audit Forensik Integritas Kriptografis SHA-256
    Memeriksa keaslian catatan keuangan dan mendeteksi pemalsuan/manipulasi data di database.
    """
    target_church = check_church_access(current_user, church_id)
    return CryptoKeuanganSHA256.verify_integrity(db, church_id=target_church)

@router.post("/keamanan/backup", response_model=BackupCreateResponse)
def create_cryptographic_backup(
    payload: Optional[BackupCreateRequest] = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Pembuatan Snapshot Backup Kriptografis Keuangan Gereja
    Menyimpan data analitik dan transaksi lengkap dengan digital digest SHA-256 untuk mencegah kerugian massal.
    """
    target_church = check_church_access(current_user, payload.church_id if payload else None)
    admin_id = str(getattr(current_user, "username", getattr(current_user, "id", "admin_utama")))
    return CryptoKeuanganSHA256.create_cryptographic_backup(
        db=db,
        church_id=target_church,
        admin_id=admin_id,
    )

@router.get("/keamanan/backup/list", response_model=List[BackupListItem])
def list_backups(
    current_user: Any = Depends(get_current_user),
):
    """
    Melihat seluruh riwayat file backup snapshot kriptografis yang tersimpan di server.
    """
    return CryptoKeuanganSHA256.list_backups()

@router.post("/keamanan/backup/verifikasi", response_model=BackupVerifyResponse)
def verify_backup_file(
    payload: BackupVerifyRequest,
    current_user: Any = Depends(get_current_user),
):
    """
    Verifikasi keaslian file backup via SHA-256 untuk memastikan tidak ada kerusakan atau manipulasi file.
    """
    return CryptoKeuanganSHA256.verify_backup_file(payload.filepath)

