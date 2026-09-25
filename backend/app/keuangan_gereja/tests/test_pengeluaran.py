from datetime import date
import pytest
from app.models.church import Church
from app.keuangan_gereja.models.pengeluaran import PengeluaranGereja
from app.keuangan_gereja.models.audit_transaksi import AuditTransaksiKeuangan
from app.keuangan_gereja.schemas.pengeluaran import PengeluaranCreate, PengeluaranUpdate, PengeluaranFilter
from app.keuangan_gereja.services.pengeluaran_service import PengeluaranService

def test_pengeluaran_crud_and_approval(db):
    church = db.query(Church).filter(Church.church_code == "GEREJA-TEST-02").first()
    if not church:
        church = Church(
            church_code="GEREJA-TEST-02",
            church_name="GKI Test Cabang Barat",
            address="Jl. Barat No. 5",
        )
        db.add(church)
        db.commit()
        db.refresh(church)

    # 1. Test Create Pengeluaran (Pending Approval)
    data_in = PengeluaranCreate(
        church_id=church.id,
        tanggal=date(2026, 3, 2),
        kategori="Operasional",
        jumlah=1200000.0,
        metode_pembayaran="Transfer Bank",
        penerima="PLN & PDAM",
        keterangan="Tagihan Listrik & Air Maret",
        status_persetujuan="Pending",
    )
    pengeluaran = PengeluaranService.create(db, data_in, user_id="staff_keuangan", user_role="church_admin")
    assert pengeluaran.id is not None
    assert pengeluaran.status_persetujuan == "Pending"

    # 2. Test Approval Workflow
    approved = PengeluaranService.approve(
        db,
        id=pengeluaran.id,
        status="Disetujui",
        approver_name="Pendeta Jemaat / Admin Utama",
        user_id="main_admin_1",
        user_role="superadmin",
    )
    assert approved.status_persetujuan == "Disetujui"
    assert approved.disetujui_oleh == "Pendeta Jemaat / Admin Utama"

    # 3. Test Audit Log
    audit = db.query(AuditTransaksiKeuangan).filter(
        AuditTransaksiKeuangan.transaksi_id == pengeluaran.id,
        AuditTransaksiKeuangan.action == "APPROVE",
    ).first()
    assert audit is not None
    assert "Disetujui" in audit.deskripsi

    # 4. Test Filter
    filters = PengeluaranFilter(church_id=church.id, status_persetujuan="Disetujui")
    items, count = PengeluaranService.get_multi(db, filters)
    assert count >= 1
    assert any(x.id == pengeluaran.id for x in items)

    # 5. Clean up
    PengeluaranService.delete(db, pengeluaran.id, user_id="main_admin_1")
    assert PengeluaranService.get_by_id(db, pengeluaran.id) is None
