from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

# --- Saldo ---
class SaldoSummaryResponse(BaseModel):
    church_id: Optional[int] = None
    church_name: Optional[str] = None
    total_pemasukan: float
    total_pengeluaran: float
    saldo_akhir: float
    saldo_per_metode: Dict[str, float] = Field(default_factory=dict)
    total_transaksi_pemasukan: int
    total_transaksi_pengeluaran: int

# --- Arus Kas ---
class ArusKasItem(BaseModel):
    periode: str
    pemasukan: float
    pengeluaran: float
    arus_kas_bersih: float
    saldo_kumulatif: float

class ArusKasResponse(BaseModel):
    church_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    items: List[ArusKasItem]
    total_pemasukan: float
    total_pengeluaran: float
    net_cash_flow: float

# --- Anggaran ---
class AnggaranCreate(BaseModel):
    church_id: int
    tahun: int
    bulan: int = Field(default=0, ge=0, le=12)
    jenis: str = Field(..., description="Pemasukan / Pengeluaran")
    kategori: str
    target_nominal: float = Field(..., gt=0)
    catatan: Optional[str] = None

class AnggaranResponse(AnggaranCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AnggaranVsRealisasiItem(BaseModel):
    kategori: str
    jenis: str
    target_anggaran: float
    realisasi: float
    selisih: float
    persentase_tercapai: float
    status: str  # Efisien, Overbudget, Tercapai, Di Bawah Target

class AnggaranVsRealisasiResponse(BaseModel):
    church_id: Optional[int] = None
    tahun: int
    bulan: int
    items: List[AnggaranVsRealisasiItem]
    total_target_pemasukan: float
    total_realisasi_pemasukan: float
    total_target_pengeluaran: float
    total_realisasi_pengeluaran: float

# --- Rekap Bulanan ---
class RekapBulananItem(BaseModel):
    bulan: int
    nama_bulan: str
    tahun: int
    total_pemasukan: float
    total_pengeluaran: float
    surplus_defisit: float

class RekapBulananResponse(BaseModel):
    church_id: Optional[int] = None
    tahun: int
    rekap: List[RekapBulananItem]
    grand_total_pemasukan: float
    grand_total_pengeluaran: float
    grand_total_surplus: float

# --- Analytics Schemas ---
class DescriptiveStats(BaseModel):
    count: int
    total: float
    mean: float
    median: float
    std_dev: float
    min: float
    max: float

class AnalisisDeskriptifResponse(BaseModel):
    church_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    pemasukan_stats: DescriptiveStats
    pengeluaran_stats: DescriptiveStats
    pertumbuhan_mom_pemasukan: float
    pertumbuhan_mom_pengeluaran: float
    proporsi_kategori_pemasukan: List[Dict[str, float]]
    proporsi_kategori_pengeluaran: List[Dict[str, float]]

class ForecastPoint(BaseModel):
    periode: str
    prediksi_pemasukan: float
    prediksi_pengeluaran: float
    estimasi_saldo_bersih: float

class ForecastingResponse(BaseModel):
    church_id: Optional[int] = None
    metode: str
    horizon_bulan: int
    forecast: List[ForecastPoint]
    tren_arah_pemasukan: str  # Meningkat, Menurun, Stabil
    tren_arah_pengeluaran: str

class AnomaliItem(BaseModel):
    transaksi_id: int
    tipe: str  # pemasukan / pengeluaran
    tanggal: date
    kategori: str
    jumlah: float
    z_score: float
    alasan: str

class DeteksiAnomaliResponse(BaseModel):
    church_id: Optional[int] = None
    total_diperiksa: int
    total_anomali: int
    daftar_anomali: List[AnomaliItem]

class RasioKeuanganResponse(BaseModel):
    church_id: Optional[int] = None
    cadangan_kas_bulan: float
    operating_expense_ratio: float
    savings_ratio: float
    diakonia_ratio: float
    status_likuiditas: str
    catatan_kesehatan: str

# --- Fuzzy & SPK Schemas ---
class FuzzyKesehatanRequest(BaseModel):
    church_id: Optional[int] = None
    surplus_defisit_ratio: Optional[float] = None
    cadangan_kas_bulan: Optional[float] = None
    kepatuhan_anggaran: Optional[float] = None

class FuzzyKesehatanResponse(BaseModel):
    skor_kesehatan: float
    kategori_kesehatan: str  # Sangat Kritis, Waspada, Cukup Sehat, Sangat Sehat
    derajat_keanggotaan: Dict[str, float]
    rekomendasi_admin: List[str]

class SPKProgramItem(BaseModel):
    nama_program: str
    urgensi: float = Field(..., ge=1, le=10, description="Skala 1 - 10 (Benefit)")
    dampak_jemaat: float = Field(..., ge=1, le=10, description="Skala 1 - 10 (Benefit)")
    estimasi_biaya: float = Field(..., gt=0, description="Biaya dalam rupiah (Cost)")
    kesiapan_pelaksana: float = Field(..., ge=1, le=10, description="Skala 1 - 10 (Benefit)")
    keselarasan_visi: float = Field(..., ge=1, le=10, description="Skala 1 - 10 (Benefit)")

class SPKProgramRequest(BaseModel):
    church_id: Optional[int] = None
    metode: str = Field(default="TOPSIS", description="TOPSIS atau SAW")
    program_list: List[SPKProgramItem]

class RankedProgramItem(BaseModel):
    ranking: int
    nama_program: str
    skor_preferensi: float
    rekomendasi: str

class SPKProgramResponse(BaseModel):
    metode: str
    hasil_ranking: List[RankedProgramItem]
    kesimpulan_prioritas: str

# --- Security & SHA-256 Schemas ---
class IntegrityCheckResponse(BaseModel):
    status: str
    keterangan: str
    total_diperiksa: int
    terverifikasi_valid: int
    terdeteksi_tampering: int
    anomali_terdeteksi: List[Dict[str, Any]]
    timestamp_audit: str

class BackupCreateRequest(BaseModel):
    church_id: Optional[int] = None

class BackupCreateResponse(BaseModel):
    status: str
    message: str
    filename: str
    filepath: str
    sha256_checksum: str
    file_size_bytes: int
    total_records: int
    saldo_terbackup: float
    timestamp: str

class BackupVerifyRequest(BaseModel):
    filepath: str

class BackupVerifyResponse(BaseModel):
    valid: bool
    status: Optional[str] = None
    recorded_checksum: Optional[str] = None
    calculated_checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BackupListItem(BaseModel):
    filename: str
    filepath: str
    file_size_bytes: int
    created_at: str

