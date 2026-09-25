from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PengeluaranBase(BaseModel):
    church_id: int
    tanggal: Optional[date] = None
    kategori: str = Field(..., description="Kategori pengeluaran: Operasional, Gaji & Honor, Fasilitas, Diakonia, dll.")
    jumlah: float = Field(..., gt=0, description="Nominal pengeluaran")
    metode_pembayaran: str = Field(default="Tunai", description="Tunai, Transfer Bank, QRIS")
    penerima: Optional[str] = None
    keterangan: Optional[str] = None
    bukti_transaksi_url: Optional[str] = None
    status_persetujuan: Optional[str] = Field(default="Disetujui", description="Pending, Disetujui, Ditolak")

class PengeluaranCreate(PengeluaranBase):
    pass

class PengeluaranUpdate(BaseModel):
    tanggal: Optional[date] = None
    kategori: Optional[str] = None
    jumlah: Optional[float] = Field(None, gt=0)
    metode_pembayaran: Optional[str] = None
    penerima: Optional[str] = None
    keterangan: Optional[str] = None
    bukti_transaksi_url: Optional[str] = None
    status_persetujuan: Optional[str] = None

class PengeluaranApproval(BaseModel):
    status_persetujuan: str = Field(..., description="Disetujui / Ditolak")
    catatan: Optional[str] = None

class PengeluaranResponse(PengeluaranBase):
    id: int
    disetujui_oleh: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PengeluaranFilter(BaseModel):
    church_id: Optional[int] = None
    kategori: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    metode_pembayaran: Optional[str] = None
    status_persetujuan: Optional[str] = None

class PengeluaranSummaryKategori(BaseModel):
    kategori: str
    total_jumlah: float
    jumlah_transaksi: int
    persentase: float
