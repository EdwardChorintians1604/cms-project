import numpy as np
from typing import List, Dict
from app.keuangan_gereja.schemas.laporan import (
    SPKProgramItem,
    SPKProgramRequest,
    SPKProgramResponse,
    RankedProgramItem,
)

class SPKPrioritasProgram:
    """
    Sistem Pendukung Keputusan (SPK)
    Perangkingan Prioritas Program & Alokasi Anggaran Gereja
    Mendukung Metode TOPSIS dan SAW
    """

    # Bobot dan atribut kriteria:
    # 0: Urgensi (Benefit, 25%)
    # 1: Dampak Jemaat (Benefit, 25%)
    # 2: Estimasi Biaya (Cost, 20%)
    # 3: Kesiapan Pelaksana (Benefit, 15%)
    # 4: Keselarasan Visi Misi (Benefit, 15%)
    DEFAULT_WEIGHTS = np.array([0.25, 0.25, 0.20, 0.15, 0.15], dtype=float)
    IS_BENEFIT = [True, True, False, True, True]

    @classmethod
    def hitung_topsis(cls, program_list: List[SPKProgramItem]) -> List[RankedProgramItem]:
        n = len(program_list)
        if n == 0:
            return []
        if n == 1:
            p = program_list[0]
            return [
                RankedProgramItem(
                    ranking=1,
                    nama_program=p.nama_program,
                    skor_preferensi=1.0,
                    rekomendasi="Sangat Direkomendasikan (Tunggal)",
                )
            ]

        # 1. Matriks Keputusan X
        X = np.zeros((n, 5), dtype=float)
        for i, p in enumerate(program_list):
            X[i, 0] = float(p.urgensi)
            X[i, 1] = float(p.dampak_jemaat)
            X[i, 2] = float(p.estimasi_biaya)
            X[i, 3] = float(p.kesiapan_pelaksana)
            X[i, 4] = float(p.keselarasan_visi)

        # 2. Normalisasi Matriks R (Euclidean)
        denom = np.sqrt(np.sum(X ** 2, axis=0))
        # Tangani division by zero
        denom[denom == 0] = 1.0
        R = X / denom

        # 3. Matriks Terbobot V
        V = R * cls.DEFAULT_WEIGHTS

        # 4. Solusi Ideal Positif (A+) dan Solusi Ideal Negatif (A-)
        A_plus = np.zeros(5)
        A_minus = np.zeros(5)

        for j in range(5):
            if cls.IS_BENEFIT[j]:
                A_plus[j] = np.max(V[:, j])
                A_minus[j] = np.min(V[:, j])
            else:
                # Cost criterion (Biaya: makin kecil makin baik)
                A_plus[j] = np.min(V[:, j])
                A_minus[j] = np.max(V[:, j])

        # 5. Jarak Pemisah (Euclidean Distance D+ dan D-)
        D_plus = np.sqrt(np.sum((V - A_plus) ** 2, axis=1))
        D_minus = np.sqrt(np.sum((V - A_minus) ** 2, axis=1))

        # 6. Kedekatan Relatif terhadap Solusi Ideal (Preferensi V_i)
        denom_d = D_plus + D_minus
        denom_d[denom_d == 0] = 1.0
        preference = D_minus / denom_d

        # 7. Pengurutan Ranking
        ranked_indices = np.argsort(preference)[::-1]

        results: List[RankedProgramItem] = []
        for rank, idx in enumerate(ranked_indices, start=1):
            score = float(preference[idx])
            p = program_list[idx]

            if score >= 0.70:
                rekomendasi = "Sangat Direkomendasikan untuk Didanai Penuh"
            elif score >= 0.50:
                rekomendasi = "Direkomendasikan (Dapat Didanai Bertahap)"
            elif score >= 0.35:
                rekomendasi = "Dipertimbangkan (Perlu Penyesuaian Anggaran)"
            else:
                rekomendasi = "Ditunda / Tidak Prioritas Saat Ini"

            results.append(
                RankedProgramItem(
                    ranking=rank,
                    nama_program=p.nama_program,
                    skor_preferensi=round(score, 4),
                    rekomendasi=rekomendasi,
                )
            )

        return results

    @classmethod
    def hitung_saw(cls, program_list: List[SPKProgramItem]) -> List[RankedProgramItem]:
        n = len(program_list)
        if n == 0:
            return []

        X = np.zeros((n, 5), dtype=float)
        for i, p in enumerate(program_list):
            X[i, 0] = float(p.urgensi)
            X[i, 1] = float(p.dampak_jemaat)
            X[i, 2] = float(p.estimasi_biaya)
            X[i, 3] = float(p.kesiapan_pelaksana)
            X[i, 4] = float(p.keselarasan_visi)

        R = np.zeros((n, 5), dtype=float)
        for j in range(5):
            if cls.IS_BENEFIT[j]:
                max_val = np.max(X[:, j])
                R[:, j] = X[:, j] / max_val if max_val > 0 else 0.0
            else:
                min_val = np.min(X[:, j])
                R[:, j] = min_val / X[:, j] if np.all(X[:, j] > 0) else 0.0

        scores = np.sum(R * cls.DEFAULT_WEIGHTS, axis=1)
        ranked_indices = np.argsort(scores)[::-1]

        results: List[RankedProgramItem] = []
        for rank, idx in enumerate(ranked_indices, start=1):
            score = float(scores[idx])
            p = program_list[idx]

            if score >= 0.75:
                rekomendasi = "Sangat Direkomendasikan untuk Didanai Penuh"
            elif score >= 0.55:
                rekomendasi = "Direkomendasikan (Dapat Didanai Bertahap)"
            elif score >= 0.40:
                rekomendasi = "Dipertimbangkan (Perlu Penyesuaian Anggaran)"
            else:
                rekomendasi = "Ditunda / Tidak Prioritas Saat Ini"

            results.append(
                RankedProgramItem(
                    ranking=rank,
                    nama_program=p.nama_program,
                    skor_preferensi=round(score, 4),
                    rekomendasi=rekomendasi,
                )
            )

        return results

    @classmethod
    def proses_spk(cls, req: SPKProgramRequest) -> SPKProgramResponse:
        metode = req.metode.upper() if req.metode else "TOPSIS"
        if metode == "SAW":
            hasil = cls.hitung_saw(req.program_list)
        else:
            hasil = cls.hitung_topsis(req.program_list)
            metode = "TOPSIS"

        if hasil:
            top_program = hasil[0].nama_program
            kesimpulan = (
                f"Berdasarkan analisis multikriteria {metode}, program '{top_program}' "
                f"menempati prioritas nomor 1 dengan skor preferensi tertinggi ({hasil[0].skor_preferensi:.4f}). "
                f"Disarankan Admin Utama memberikan alokasi persetujuan pencairan dana terlebih dahulu."
            )
        else:
            kesimpulan = "Tidak ada usulan program yang dievaluasi."

        return SPKProgramResponse(
            metode=metode,
            hasil_ranking=hasil,
            kesimpulan_prioritas=kesimpulan,
        )
