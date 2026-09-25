from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class PemasukanBase(BaseModel):
    church_id: int
    tanggal: Optional[date] = None
    kategori: str = Field(..., description="Kategori pemasukan seperti Persembahan Umum, Perpuluhan, dll.")
    jumlah: float = Field(..., gt=0, description="Nominal pemasukan")
    metode_pembayaran: str = Field(default="Tunai", description="Tunai, Transfer Bank, QRIS")
    keterangan: Optional[str] = None
    bukti_transaksi_url: Optional[str] = None
    status_verifikasi: Optional[str] = Field(default="Verified", description="Pending, Verified, Rejected")
    donor_name: Optional[str] = None

class PemasukanCreate(PemasukanBase):
    pass

class PemasukanUpdate(BaseModel):
    tanggal: Optional[date] = None
    kategori: Optional[str] = None
    jumlah: Optional[float] = Field(None, gt=0)
    metode_pembayaran: Optional[str] = None
    keterangan: Optional[str] = None
    bukti_transaksi_url: Optional[str] = None
    status_verifikasi: Optional[str] = None
    donor_name: Optional[str] = None

class PemasukanResponse(PemasukanBase):
    id: int
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PemasukanFilter(BaseModel):
    church_id: Optional[int] = None
    kategori: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    metode_pembayaran: Optional[str] = None
    status_verifikasi: Optional[str] = None

class PemasukanSummaryKategori(BaseModel):
    kategori: str
    total_jumlah: float
    jumlah_transaksi: int
    persentase: float
