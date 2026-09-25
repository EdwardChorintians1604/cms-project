import numpy as np
from datetime import date
from typing import List, Optional, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session

from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.schemas.laporan import (
    ForecastPoint,
    ForecastingResponse,
)

class ForecastingKeuangan:
    @staticmethod
    def _predict_series(y_vals: List[float], horizon: int) -> Tuple[List[float], str]:
        if not y_vals:
            return [0.0] * horizon, "Stabil"
        if len(y_vals) == 1:
            val = float(y_vals[0])
            return [round(val, 2)] * horizon, "Stabil"

        x = np.arange(len(y_vals), dtype=float)
        y = np.array(y_vals, dtype=float)

        # Regresi linier: y = m * x + c
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]

        predictions = []
        for i in range(len(y_vals), len(y_vals) + horizon):
            pred = m * i + c
            # Keuangan tidak boleh bernilai negatif untuk prediksi kasar
            pred = max(0.0, float(pred))
            predictions.append(round(pred, 2))

        if m > 1000:
            trend = "Meningkat"
        elif m < -1000:
            trend = "Menurun"
        else:
            trend = "Stabil"

        return predictions, trend

    @classmethod
    def generate_forecast(
        cls,
        db: Session,
        church_id: Optional[int] = None,
        horizon_bulan: int = 3,
    ) -> ForecastingResponse:
        p_query = db.query(PemasukanGereja).filter(PemasukanGereja.status_verifikasi == "Verified")
        k_query = db.query(PengeluaranGereja).filter(PengeluaranGereja.status_persetujuan == "Disetujui")

        if church_id:
            p_query = p_query.filter(PemasukanGereja.church_id == church_id)
            k_query = k_query.filter(PengeluaranGereja.church_id == church_id)

        pemasukan_list = p_query.all()
        pengeluaran_list = k_query.all()

        # Agregasi bulanan YYYY-MM
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
        y_pemasukan = [p_by_period[p] for p in sorted_periods]
        y_pengeluaran = [k_by_period[p] for p in sorted_periods]

        pred_p, trend_p = cls._predict_series(y_pemasukan, horizon_bulan)
        pred_k, trend_k = cls._predict_series(y_pengeluaran, horizon_bulan)

        # Buat label periode masa depan
        today = date.today()
        start_year = today.year
        start_month = today.month

        forecast_points: List[ForecastPoint] = []
        for step in range(1, horizon_bulan + 1):
            future_month = start_month + step
            future_year = start_year + (future_month - 1) // 12
            future_month = ((future_month - 1) % 12) + 1
            period_label = f"{future_year:04d}-{future_month:02d}"

            p_val = pred_p[step - 1]
            k_val = pred_k[step - 1]
            net_val = round(p_val - k_val, 2)

            forecast_points.append(
                ForecastPoint(
                    periode=period_label,
                    prediksi_pemasukan=p_val,
                    prediksi_pengeluaran=k_val,
                    estimasi_saldo_bersih=net_val,
                )
            )

        return ForecastingResponse(
            church_id=church_id,
            metode="Linear Trend Regression",
            horizon_bulan=horizon_bulan,
            forecast=forecast_points,
            tren_arah_pemasukan=trend_p,
            tren_arah_pengeluaran=trend_k,
        )
