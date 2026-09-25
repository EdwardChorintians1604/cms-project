import numpy as np
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.schemas.laporan import (
    AnomaliItem,
    DeteksiAnomaliResponse,
)

class DeteksiAnomaliKeuangan:
    @staticmethod
    def _detect_outliers(
        records: List[dict],
        threshold_z: float = 2.5,
    ) -> List[AnomaliItem]:
        if len(records) < 4:
            return []

        amounts = np.array([r["jumlah"] for r in records], dtype=float)
        mean = float(np.mean(amounts))
        std = float(np.std(amounts, ddof=1))

        if std == 0:
            return []

        q25, q75 = np.percentile(amounts, [25, 75])
        iqr = q75 - q25
        upper_iqr = q75 + (1.5 * iqr)

        anomalies: List[AnomaliItem] = []
        for r in records:
            val = r["jumlah"]
            z = (val - mean) / std
            is_anomaly = False
            alasan = []

            if abs(z) >= threshold_z:
                is_anomaly = True
                alasan.append(f"Z-Score {z:.2f} melebihi ambang batas {threshold_z}")

            if val > upper_iqr and iqr > 0:
                is_anomaly = True
                alasan.append(f"Nilai Rp {val:,.2f} melebihi batas IQR Rp {upper_iqr:,.2f}")

            if is_anomaly:
                anomalies.append(
                    AnomaliItem(
                        transaksi_id=r["id"],
                        tipe=r["tipe"],
                        tanggal=r["tanggal"],
                        kategori=r["kategori"],
                        jumlah=round(val, 2),
                        z_score=round(float(z), 2),
                        alasan=" & ".join(alasan),
                    )
                )

        return anomalies

    @classmethod
    def scan_anomali(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        threshold_z: float = 2.5,
    ) -> DeteksiAnomaliResponse:
        p_query = db.query(PemasukanGereja).filter(PemasukanGereja.status_verifikasi == "Verified")
        k_query = db.query(PengeluaranGereja).filter(PengeluaranGereja.status_persetujuan == "Disetujui")

        if church_id:
            p_query = p_query.filter(PemasukanGereja.church_id == church_id)
            k_query = k_query.filter(PengeluaranGereja.church_id == church_id)

        p_list = [
            {"id": p.id, "tipe": "pemasukan", "tanggal": p.tanggal, "kategori": p.kategori, "jumlah": float(p.jumlah)}
            for p in p_query.all()
        ]
        k_list = [
            {"id": k.id, "tipe": "pengeluaran", "tanggal": k.tanggal, "kategori": k.kategori, "jumlah": float(k.jumlah)}
            for k in k_query.all()
        ]

        anomali_p = cls._detect_outliers(p_list, threshold_z)
        anomali_k = cls._detect_outliers(k_list, threshold_z)

        all_anomalies = anomali_p + anomali_k
        all_anomalies.sort(key=lambda x: abs(x.z_score), reverse=True)

        total_tx = len(p_list) + len(k_list)

        return DeteksiAnomaliResponse(
            church_id=church_id,
            total_diperiksa=total_tx,
            total_anomali=len(all_anomalies),
            daftar_anomali=all_anomalies,
        )
