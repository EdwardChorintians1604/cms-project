from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.models.anggaran import AnggaranGereja
from app.keuangan_gereja.schemas.laporan import (
    FuzzyKesehatanRequest,
    FuzzyKesehatanResponse,
)

class FuzzyKesehatanKeuangan:
    """
    Sistem Inferensi Logika Fuzzy (Mamdani Model)
    untuk Evaluasi Kesehatan Finansial Gereja
    """

    @staticmethod
    def _trimf(x: float, a: float, b: float, c: float) -> float:
        """Triangular membership function"""
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a) if b != a else 1.0
        elif b < x < c:
            return (c - x) / (c - b) if c != b else 1.0
        return 0.0

    @staticmethod
    def _trapmf(x: float, a: float, b: float, c: float, d: float) -> float:
        """Trapezoidal membership function"""
        if x <= a or x >= d:
            return 0.0
        elif a < x < b:
            return (x - a) / (b - a) if b != a else 1.0
        elif b <= x <= c:
            return 1.0
        elif c < x < d:
            return (d - x) / (d - c) if d != c else 1.0
        return 0.0

    @classmethod
    def fuzzify_surplus(cls, val: float) -> Dict[str, float]:
        return {
            "defisit": cls._trapmf(val, -1.0, -1.0, -0.05, 0.05),
            "seimbang": cls._trimf(val, -0.1, 0.0, 0.2),
            "surplus": cls._trapmf(val, 0.05, 0.25, 1.0, 1.0),
        }

    @classmethod
    def fuzzify_cadangan(cls, val: float) -> Dict[str, float]:
        return {
            "kritis": cls._trapmf(val, 0.0, 0.0, 0.8, 1.5),
            "waspada": cls._trimf(val, 1.0, 2.5, 4.0),
            "aman": cls._trapmf(val, 3.0, 5.0, 12.0, 100.0),
        }

    @classmethod
    def fuzzify_anggaran(cls, val: float) -> Dict[str, float]:
        return {
            "efisien": cls._trapmf(val, 0.0, 0.0, 0.8, 0.95),
            "sesuai": cls._trimf(val, 0.85, 1.0, 1.15),
            "overbudget": cls._trapmf(val, 1.05, 1.25, 3.0, 10.0),
        }

    @classmethod
    def infer_and_defuzzify(
        cls,
        surplus_ratio: float,
        cadangan_bulan: float,
        kepatuhan_anggaran: float,
    ) -> Tuple[float, str, Dict[str, float], List[str]]:
        # Fuzzifikasi
        f_surplus = cls.fuzzify_surplus(surplus_ratio)
        f_cadangan = cls.fuzzify_cadangan(cadangan_bulan)
        f_anggaran = cls.fuzzify_anggaran(kepatuhan_anggaran)

        # Basis Aturan (Fuzzy Rules - Mamdani)
        # Output fuzzy sets dengan centroid:
        # Sangat Kritis: 15
        # Waspada: 45
        # Cukup Sehat: 70
        # Sangat Sehat: 90
        c_kritis = 15.0
        c_waspada = 45.0
        c_cukup = 70.0
        c_sehat = 90.0

        rules_kritis = []
        rules_waspada = []
        rules_cukup = []
        rules_sehat = []

        # R1: IF defisit AND cadangan kritis THEN Sangat Kritis
        rules_kritis.append(min(f_surplus["defisit"], f_cadangan["kritis"]))
        # R2: IF defisit AND overbudget THEN Sangat Kritis
        rules_kritis.append(min(f_surplus["defisit"], f_anggaran["overbudget"]))
        # R3: IF cadangan kritis AND overbudget THEN Sangat Kritis
        rules_kritis.append(min(f_cadangan["kritis"], f_anggaran["overbudget"]))

        # R4: IF defisit AND cadangan waspada THEN Waspada
        rules_waspada.append(min(f_surplus["defisit"], f_cadangan["waspada"]))
        # R5: IF seimbang AND cadangan waspada THEN Waspada
        rules_waspada.append(min(f_surplus["seimbang"], f_cadangan["waspada"]))
        # R6: IF overbudget AND cadangan waspada THEN Waspada
        rules_waspada.append(min(f_anggaran["overbudget"], f_cadangan["waspada"]))

        # R7: IF seimbang AND cadangan aman THEN Cukup Sehat
        rules_cukup.append(min(f_surplus["seimbang"], f_cadangan["aman"]))
        # R8: IF surplus AND cadangan waspada THEN Cukup Sehat
        rules_cukup.append(min(f_surplus["surplus"], f_cadangan["waspada"]))
        # R9: IF seimbang AND efisien THEN Cukup Sehat
        rules_cukup.append(min(f_surplus["seimbang"], f_anggaran["efisien"]))

        # R10: IF surplus AND cadangan aman AND efisien THEN Sangat Sehat
        rules_sehat.append(min(f_surplus["surplus"], f_cadangan["aman"], f_anggaran["efisien"]))
        # R11: IF surplus AND cadangan aman AND sesuai THEN Sangat Sehat
        rules_sehat.append(min(f_surplus["surplus"], f_cadangan["aman"], f_anggaran["sesuai"]))
        # R12: IF surplus AND cadangan aman THEN Sangat Sehat
        rules_sehat.append(min(f_surplus["surplus"], f_cadangan["aman"]))

        fire_kritis = max(rules_kritis) if rules_kritis else 0.0
        fire_waspada = max(rules_waspada) if rules_waspada else 0.0
        fire_cukup = max(rules_cukup) if rules_cukup else 0.0
        fire_sehat = max(rules_sehat) if rules_sehat else 0.0

        # Defuzzifikasi Centroid Rata-rata Terbobot
        total_weight = fire_kritis + fire_waspada + fire_cukup + fire_sehat
        if total_weight > 0:
            score = (
                (fire_kritis * c_kritis)
                + (fire_waspada * c_waspada)
                + (fire_cukup * c_cukup)
                + (fire_sehat * c_sehat)
            ) / total_weight
        else:
            score = 50.0

        score = max(0.0, min(100.0, score))

        # Penentuan Predikat Kategori & Rekomendasi
        rekomendasi = []
        if score >= 80:
            kategori = "Sangat Sehat"
            rekomendasi = [
                "Keuangan gereja dalam kondisi prima dengan likuiditas dan efisiensi optimal.",
                "Dapat mengalokasikan surplus untuk dana abadi misi atau percepatan pembangunan gedung ibadah.",
                "Pertahankan tata kelola transparansi dan apresiasi keterlibatan jemaat dalam persembahan.",
            ]
        elif score >= 60:
            kategori = "Cukup Sehat"
            rekomendasi = [
                "Kondisi keuangan stabil namun perlu mempertahankan cadangan kas agar tidak tergerus program mendadak.",
                "Optimalkan monitoring pos anggaran bulanan agar seluruh divisi tetap taat pagu.",
                "Pertimbangkan diversifikasi kanal penerimaan digital seperti QRIS.",
            ]
        elif score >= 40:
            kategori = "Waspada"
            rekomendasi = [
                "Terdeteksi potensi defisit atau cadangan kas yang menipis di bawah 3 bulan operasional.",
                "Lakukan penundaan program kerja non-esensial dan batasi renovasi fisik sementara.",
                "Lakukan konsolidasi dengan majelis jemaat mengenai transparansi laporan keuangan.",
            ]
        else:
            kategori = "Sangat Kritis"
            rekomendasi = [
                "PERINGATAN: Defisit akut dengan cadangan kas tidak memadai.",
                "Hentikan seluruh pengeluaran di luar beban pokok operasional dan gaji pelayan.",
                "Admin Utama perlu melakukan audit khusus dan restrukturisasi pos anggaran cabang.",
            ]

        derajat = {
            "sangat_kritis": round(fire_kritis, 3),
            "waspada": round(fire_waspada, 3),
            "cukup_sehat": round(fire_cukup, 3),
            "sangat_sehat": round(fire_sehat, 3),
        }

        return round(score, 2), kategori, derajat, rekomendasi

    @classmethod
    def evaluasi(
        cls,
        db: Session,
        req: Optional[FuzzyKesehatanRequest] = None,
    ) -> FuzzyKesehatanResponse:
        church_id = req.church_id if req else None

        surplus_ratio = req.surplus_defisit_ratio if req and req.surplus_defisit_ratio is not None else None
        cadangan_bulan = req.cadangan_kas_bulan if req and req.cadangan_kas_bulan is not None else None
        kepatuhan = req.kepatuhan_anggaran if req and req.kepatuhan_anggaran is not None else None

        # Jika parameter tidak diberikan oleh user, hitung otomatis dari DB
        if surplus_ratio is None or cadangan_bulan is None or kepatuhan is None:
            p_q = db.query(func.coalesce(func.sum(PemasukanGereja.jumlah), 0.0)).filter(
                PemasukanGereja.status_verifikasi == "Verified"
            )
            k_q = db.query(func.coalesce(func.sum(PengeluaranGereja.jumlah), 0.0)).filter(
                PengeluaranGereja.status_persetujuan == "Disetujui"
            )
            if church_id:
                p_q = p_q.filter(PemasukanGereja.church_id == church_id)
                k_q = k_q.filter(PengeluaranGereja.church_id == church_id)

            tot_p = float(p_q.scalar() or 0.0)
            tot_k = float(k_q.scalar() or 0.0)
            saldo = tot_p - tot_k

            if surplus_ratio is None:
                surplus_ratio = ((tot_p - tot_k) / tot_p) if tot_p > 0 else 0.0
                surplus_ratio = max(-1.0, min(1.0, surplus_ratio))

            if cadangan_bulan is None:
                avg_k = tot_k / 6.0 if tot_k > 0 else 1.0  # estimasi rata-rata 6 bulan
                cadangan_bulan = max(0.0, saldo / avg_k) if avg_k > 0 else 6.0

            if kepatuhan is None:
                # Cek target anggaran pengeluaran
                anggaran_q = db.query(func.coalesce(func.sum(AnggaranGereja.target_nominal), 0.0)).filter(
                    AnggaranGereja.jenis.ilike("%pengeluaran%")
                )
                if church_id:
                    anggaran_q = anggaran_q.filter(AnggaranGereja.church_id == church_id)
                target_k = float(anggaran_q.scalar() or 0.0)

                if target_k > 0:
                    kepatuhan = tot_k / target_k
                else:
                    kepatuhan = 1.0  # Normal default

        score, kategori, derajat, rek = cls.infer_and_defuzzify(
            surplus_ratio=surplus_ratio,
            cadangan_bulan=cadangan_bulan,
            kepatuhan_anggaran=kepatuhan,
        )

        return FuzzyKesehatanResponse(
            skor_kesehatan=score,
            kategori_kesehatan=kategori,
            derajat_keanggotaan=derajat,
            rekomendasi_admin=rek,
        )
