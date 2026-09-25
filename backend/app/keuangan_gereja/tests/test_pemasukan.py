from datetime import date
import pytest
from app.models.church import Church
from app.keuangan_gereja.models.pemasukan import PemasukanGereja
from app.keuangan_gereja.models.audit_transaksi import AuditTransaksiKeuangan
from app.keuangan_gereja.schemas.pemasukan import PemasukanCreate, PemasukanUpdate, PemasukanFilter
from app.keuangan_gereja.services.pemasukan_service import PemasukanService
from app.keuangan_gereja.services.saldo_service import SaldoService

def test_pemasukan_crud_and_saldo(db):
    # 1. Siapkan data gereja dummy
    church = db.query(Church).filter(Church.church_code == "GEREJA-TEST-01").first()
    if not church:
        church = Church(
            church_code="GEREJA-TEST-01",
            church_name="GKI Test Pusat",
            address="Jl. Merdeka No. 10",
        )
        db.add(church)
        db.commit()
        db.refresh(church)

    # 2. Test Create Pemasukan
    data_in = PemasukanCreate(
        church_id=church.id,
        tanggal=date(2026, 3, 1),
        kategori="Persembahan Mingguan",
        jumlah=5000000.0,
        metode_pembayaran="Tunai",
        keterangan="Ibadah Raya 1",
        donor_name="Jemaat Umum",
    )
    pemasukan = PemasukanService.create(db, data_in, user_id="admin_1", user_role="superadmin")
    assert pemasukan.id is not None
    assert pemasukan.jumlah == 5000000.0
    assert pemasukan.status_verifikasi == "Verified"

    # Cek audit log otomatis
    audit = db.query(AuditTransaksiKeuangan).filter(
        AuditTransaksiKeuangan.transaksi_id == pemasukan.id,
        AuditTransaksiKeuangan.transaksi_tipe == "pemasukan",
    ).first()
    assert audit is not None
    assert audit.action == "CREATE"

    # 3. Test Get Multi & Filter
    filters = PemasukanFilter(church_id=church.id, kategori="Persembahan Mingguan")
    items, total = PemasukanService.get_multi(db, filters)
    assert total >= 1
    assert any(item.id == pemasukan.id for item in items)

    # 4. Test Update Pemasukan
    update_data = PemasukanUpdate(jumlah=5500000.0, keterangan="Koreksi hitungan kantong persembahan")
    updated = PemasukanService.update(db, pemasukan.id, update_data, user_id="admin_1")
    assert updated.jumlah == 5500000.0

    # 5. Test Saldo Calculation
    saldo = SaldoService.get_saldo_summary(db, church_id=church.id)
    assert saldo.total_pemasukan >= 5500000.0
    assert saldo.saldo_akhir >= 5500000.0

    # 6. Test Summary by Kategori
    summary = PemasukanService.get_summary_by_kategori(db, church_id=church.id)
    assert len(summary) >= 1
    assert any(s.kategori == "Persembahan Mingguan" for s in summary)

    # 7. Test Delete
    del_res = PemasukanService.delete(db, pemasukan.id, user_id="admin_1")
    assert del_res is True
    assert PemasukanService.get_by_id(db, pemasukan.id) is None
