import os
import pytest
from fastapi import HTTPException

from app.models.main_admin import MainAdmin
from app.models.church_admin import ChurchAdmin
from app.models.user import User
from app.keuangan_gereja.api.keuangan import check_church_access, is_main_admin
from app.keuangan_gereja.schemas.laporan import SPKProgramItem, SPKProgramRequest, FuzzyKesehatanRequest
from app.keuangan_gereja.spk.prioritas_program import SPKPrioritasProgram
from app.keuangan_gereja.fuzzy.kesehatan_keuangan import FuzzyKesehatanKeuangan

def test_rbac_main_admin_access():
    main_admin = MainAdmin(
        development_id="DEV-ADMIN-01",
        username="superadmin",
        email="superadmin@cms.id",
        password="testpassword",
    )
    assert is_main_admin(main_admin) is True

    # Main Admin bebas akses church mana pun atau None (konsolidasi pusat)
    assert check_church_access(main_admin, None) is None
    assert check_church_access(main_admin, 10) == 10
    assert check_church_access(main_admin, 99) == 99

def test_rbac_church_admin_access():
    church_admin = ChurchAdmin(
        church_id=5,
        church_code="CHURCH-05",
        church_name="GKI Cabang 5",
        admin_name="Admin Cabang 5",
        email="admin5@gki.org",
        password="testpassword",
    )
    assert is_main_admin(church_admin) is False


    # Church Admin hanya boleh akses cabangnya sendiri (church_id=5)
    assert check_church_access(church_admin, 5) == 5
    assert check_church_access(church_admin, None) == 5

    # Mengakses cabang lain (church_id=8) harus ditolak dengan 403
    with pytest.raises(HTTPException) as exc_info:
        check_church_access(church_admin, 8)
    assert exc_info.value.status_code == 403

def test_rbac_jemaat_rejected():
    jemaat_user = User(
        id=3,
        username="jemaat_biasa",
        email="jemaat@gmail.com",
    )
    with pytest.raises(HTTPException) as exc_info:
        check_church_access(jemaat_user, 5)
    assert exc_info.value.status_code == 403

def test_fuzzy_kesehatan_logic():
    # Test kondisi sangat sehat: surplus tinggi, cadangan kas 6 bulan, kepatuhan tepat
    score, kategori, derajat, rek = FuzzyKesehatanKeuangan.infer_and_defuzzify(
        surplus_ratio=0.35,
        cadangan_bulan=6.0,
        kepatuhan_anggaran=0.95,
    )
    assert score >= 70.0
    assert kategori in ["Cukup Sehat", "Sangat Sehat"]
    assert len(rek) >= 1

    # Test kondisi sangat kritis: defisit, cadangan 0.2 bulan, overbudget
    score_kritis, kat_kritis, _, rek_kritis = FuzzyKesehatanKeuangan.infer_and_defuzzify(
        surplus_ratio=-0.40,
        cadangan_bulan=0.2,
        kepatuhan_anggaran=1.8,
    )
    assert score_kritis <= 45.0
    assert kat_kritis in ["Waspada", "Sangat Kritis"]

def test_spk_topsis_and_saw_prioritas():
    programs = [
        SPKProgramItem(
            nama_program="Renovasi Atap Bocor Ruang Ibadah",
            urgensi=10,
            dampak_jemaat=9,
            estimasi_biaya=15000000.0,
            kesiapan_pelaksana=9,
            keselarasan_visi=10,
        ),
        SPKProgramItem(
            nama_program="Retreat Remaja & Pemuda",
            urgensi=6,
            dampak_jemaat=8,
            estimasi_biaya=25000000.0,
            kesiapan_pelaksana=8,
            keselarasan_visi=8,
        ),
        SPKProgramItem(
            nama_program="Pengadaan Sound System Tambahan",
            urgensi=4,
            dampak_jemaat=5,
            estimasi_biaya=45000000.0,
            kesiapan_pelaksana=6,
            keselarasan_visi=6,
        ),
    ]

    # TOPSIS
    res_topsis = SPKPrioritasProgram.proses_spk(SPKProgramRequest(metode="TOPSIS", program_list=programs))
    assert res_topsis.metode == "TOPSIS"
    assert len(res_topsis.hasil_ranking) == 3
    # Renovasi atap yang paling urgen dan biaya terukur harus ranking 1
    assert res_topsis.hasil_ranking[0].nama_program == "Renovasi Atap Bocor Ruang Ibadah"

    # SAW
    res_saw = SPKPrioritasProgram.proses_spk(SPKProgramRequest(metode="SAW", program_list=programs))
    assert res_saw.metode == "SAW"
    assert len(res_saw.hasil_ranking) == 3
    assert res_saw.hasil_ranking[0].nama_program == "Renovasi Atap Bocor Ruang Ibadah"

def test_admin_utama_readonly_on_transaction_write():
    from app.keuangan_gereja.api.keuangan import enforce_not_main_admin_for_transaction_write

    main_admin = MainAdmin(
        development_id="DEV-ADMIN-RO",
        username="superadmin_analyst",
        email="analyst@cms.id",
        password="test",
    )
    # Admin Utama dilarang mencatat transaksi langsung
    with pytest.raises(HTTPException) as exc_info:
        enforce_not_main_admin_for_transaction_write(main_admin)
    assert exc_info.value.status_code == 403
    assert "Read-Only" in exc_info.value.detail

    church_admin = ChurchAdmin(
        church_id=1,
        church_code="CHURCH-01",
        church_name="GKI Pusat",
        admin_name="Bendahara Cabang",
        email="bendahara@gki.org",
        password="test",
    )
    # Church admin diizinkan
    enforce_not_main_admin_for_transaction_write(church_admin)

def test_sha256_integrity_verification_and_tamper_detection(db):
    from app.keuangan_gereja.security.kriptografi_sha256 import CryptoKeuanganSHA256
    from app.keuangan_gereja.models.audit_transaksi import AuditTransaksiKeuangan

    # 1. Log transaksi pertama
    a1 = CryptoKeuanganSHA256.log_and_hash_audit(
        db,
        church_id=99,
        transaksi_tipe="pemasukan",
        transaksi_id=101,
        action="CREATE",
        user_id="bendahara_1",
        user_role="church_admin",
        deskripsi="Persembahan minggu 1",
        sesudah={"jumlah": 10000000.0},
    )
    db.commit()

    # 2. Log transaksi kedua (berantai)
    a2 = CryptoKeuanganSHA256.log_and_hash_audit(
        db,
        church_id=99,
        transaksi_tipe="pengeluaran",
        transaksi_id=102,
        action="CREATE",
        user_id="bendahara_1",
        user_role="church_admin",
        deskripsi="Biaya listrik",
        sesudah={"jumlah": 1500000.0},
    )
    db.commit()

    # Verifikasi integritas harus 100% valid
    res_intact = CryptoKeuanganSHA256.verify_integrity(db, church_id=99)
    assert res_intact["status"] == "INTEGRITAS_TERJAMIN_SHA256"
    assert res_intact["terdeteksi_tampering"] == 0

    # 3. Simulasikan serangan / manipulasi data database oleh pihak luar
    a1.payload_sesudah = '{"jumlah": 1000.0}'  # Mengubah data diam-diam di DB
    db.commit()

    # Verifikasi kembali, sistem harus mendeteksi manipulasi
    res_tampered = CryptoKeuanganSHA256.verify_integrity(db, church_id=99)
    assert res_tampered["status"] == "TERDETEKSI_MANIPULASI"
    assert res_tampered["terdeteksi_tampering"] >= 1

    # Kembalikan semula
    db.delete(a1)
    db.delete(a2)
    db.commit()

def test_sha256_cryptographic_backup_and_verify(db, tmp_path):
    from app.keuangan_gereja.security.kriptografi_sha256 import CryptoKeuanganSHA256

    # Test create backup snapshot dengan folder sementara
    backup_res = CryptoKeuanganSHA256.create_cryptographic_backup(
        db=db,
        church_id=None,
        admin_id="admin_utama_pusat",
        backup_dir=str(tmp_path),
    )
    assert backup_res["status"] == "SUCCESS"
    assert len(backup_res["sha256_checksum"]) == 64
    assert os.path.exists(backup_res["filepath"])

    # Test verify backup
    verify_res = CryptoKeuanganSHA256.verify_backup_file(backup_res["filepath"])
    assert verify_res["valid"] is True
    assert verify_res["status"] == "TERVERIFIKASI_ASLI"
    assert verify_res["recorded_checksum"] == backup_res["sha256_checksum"]

