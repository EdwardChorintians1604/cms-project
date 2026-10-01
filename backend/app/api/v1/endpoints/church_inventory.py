from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.api import deps
from app.models.church_inventory import ChurchInventory, ChurchInventoryLoan
from app.models.church import Church
from app.schemas.church_inventory import (
    ChurchInventoryCreate,
    ChurchInventoryUpdate,
    ChurchInventoryResponse,
    ChurchInventoryLoanCreate,
    ChurchInventoryLoanUpdate,
    ChurchInventoryLoanResponse
)

router = APIRouter()

# ==============================================================================
# 1. INVENTARIS & GEDUNG/RUANGAN (church_inventories)
# ==============================================================================

@router.get("/", response_model=List[ChurchInventoryResponse])
def get_inventories(
    church_code: Optional[str] = Query(None, description="Kode Cabang Gereja"),
    category: Optional[str] = Query(None, description="Filter kategori inventaris"),
    status: Optional[str] = Query(None, description="Filter status ketersediaan"),
    search: Optional[str] = Query(None, description="Pencarian nama atau kode"),
    db: Session = Depends(deps.get_db)
):
    query = db.query(ChurchInventory)
    if church_code and church_code != "DEFAULT":
        query = query.filter(ChurchInventory.church_code == church_code)
    if category and category != "Semua":
        query = query.filter(ChurchInventory.category == category)
    if status and status != "Semua":
        query = query.filter(ChurchInventory.status == status)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                ChurchInventory.name.ilike(search_fmt),
                ChurchInventory.item_code.ilike(search_fmt),
                ChurchInventory.location.ilike(search_fmt),
                ChurchInventory.pic_name.ilike(search_fmt)
            )
        )
    return query.order_by(ChurchInventory.id.asc()).all()


@router.post("/", response_model=ChurchInventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(
    payload: ChurchInventoryCreate,
    db: Session = Depends(deps.get_db)
):
    church_id = payload.church_id
    if not church_id and payload.church_code:
        ch = db.query(Church).filter(Church.church_code == payload.church_code).first()
        if ch:
            church_id = ch.id

    item_code = payload.item_code
    if not item_code:
        count = db.query(ChurchInventory).filter(ChurchInventory.church_code == payload.church_code).count()
        prefix = "GDG" if "Gedung" in (payload.category or "") else "AST"
        item_code = f"{prefix}-{str(count + 1).zfill(2)}"

    inv_data = payload.model_dump()
    inv_data["church_id"] = church_id
    inv_data["item_code"] = item_code

    new_inv = ChurchInventory(**inv_data)
    db.add(new_inv)
    db.commit()
    db.refresh(new_inv)
    return new_inv


@router.put("/{inv_id}", response_model=ChurchInventoryResponse)
def update_inventory(
    inv_id: int,
    payload: ChurchInventoryUpdate,
    db: Session = Depends(deps.get_db)
):
    inv = db.query(ChurchInventory).filter(ChurchInventory.id == inv_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventaris tidak ditemukan")

    update_dict = payload.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(inv, field, val)

    db.commit()
    db.refresh(inv)
    return inv


@router.delete("/{inv_id}")
def delete_inventory(
    inv_id: int,
    db: Session = Depends(deps.get_db)
):
    inv = db.query(ChurchInventory).filter(ChurchInventory.id == inv_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventaris tidak ditemukan")

    db.delete(inv)
    db.commit()
    return {"status": "success", "message": f"Inventaris {inv.name} berhasil dihapus"}


# ==============================================================================
# 2. BUKU PEMINJAMAN INVENTARIS & GEDUNG (church_inventory_loans)
# ==============================================================================

@router.get("/loans/all", response_model=List[ChurchInventoryLoanResponse])
def get_inventory_loans(
    church_code: Optional[str] = Query(None, description="Kode Cabang Gereja"),
    borrower_type: Optional[str] = Query(None, description="Filter tipe peminjam (Luar / Internal)"),
    loan_status: Optional[str] = Query(None, description="Filter status peminjaman"),
    search: Optional[str] = Query(None, description="Pencarian nama peminjam / lembaga / aset"),
    db: Session = Depends(deps.get_db)
):
    query = db.query(ChurchInventoryLoan)
    if church_code and church_code != "DEFAULT":
        query = query.filter(ChurchInventoryLoan.church_code == church_code)
    if borrower_type and borrower_type != "Semua":
        query = query.filter(ChurchInventoryLoan.borrower_type == borrower_type)
    if loan_status and loan_status != "Semua":
        query = query.filter(ChurchInventoryLoan.loan_status == loan_status)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                ChurchInventoryLoan.borrower_name.ilike(search_fmt),
                ChurchInventoryLoan.borrower_institution.ilike(search_fmt),
                ChurchInventoryLoan.inventory_name.ilike(search_fmt),
                ChurchInventoryLoan.borrower_phone.ilike(search_fmt),
                ChurchInventoryLoan.loan_code.ilike(search_fmt)
            )
        )
    return query.order_by(desc(ChurchInventoryLoan.id)).all()


@router.post("/loans/", response_model=ChurchInventoryLoanResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_loan(
    payload: ChurchInventoryLoanCreate,
    db: Session = Depends(deps.get_db)
):
    church_id = payload.church_id
    if not church_id and payload.church_code:
        ch = db.query(Church).filter(Church.church_code == payload.church_code).first()
        if ch:
            church_id = ch.id

    loan_code = payload.loan_code
    if not loan_code:
        total = db.query(ChurchInventoryLoan).filter(ChurchInventoryLoan.church_code == payload.church_code).count()
        loan_code = f"PINJAM-{date.today().year}-{str(total + 1).zfill(3)}"

    loan_data = payload.model_dump()
    loan_data["church_id"] = church_id
    loan_data["loan_code"] = loan_code

    new_loan = ChurchInventoryLoan(**loan_data)
    db.add(new_loan)

    # Sinkron status inventaris jika status disetujui / aktif
    if payload.inventory_id and "Disetujui" in (payload.loan_status or ""):
        inv = db.query(ChurchInventory).filter(ChurchInventory.id == payload.inventory_id).first()
        if inv:
            inv.status = "Sedang Dipinjam"

    db.commit()
    db.refresh(new_loan)
    return new_loan


@router.put("/loans/{loan_id}", response_model=ChurchInventoryLoanResponse)
def update_inventory_loan(
    loan_id: int,
    payload: ChurchInventoryLoanUpdate,
    db: Session = Depends(deps.get_db)
):
    loan = db.query(ChurchInventoryLoan).filter(ChurchInventoryLoan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Data peminjaman tidak ditemukan")

    update_dict = payload.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(loan, field, val)

    # Sinkronisasi status ketersediaan inventaris
    if loan.inventory_id:
        inv = db.query(ChurchInventory).filter(ChurchInventory.id == loan.inventory_id).first()
        if inv:
            if "Selesai" in loan.loan_status or "Ditolak" in loan.loan_status:
                inv.status = "Tersedia"
            elif "Disetujui" in loan.loan_status or "Aktif" in loan.loan_status:
                inv.status = "Sedang Dipinjam"

    db.commit()
    db.refresh(loan)
    return loan


@router.delete("/loans/{loan_id}")
def delete_inventory_loan(
    loan_id: int,
    db: Session = Depends(deps.get_db)
):
    loan = db.query(ChurchInventoryLoan).filter(ChurchInventoryLoan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Data peminjaman tidak ditemukan")

    # Kembalikan status inventaris jika masih terikat
    if loan.inventory_id:
        inv = db.query(ChurchInventory).filter(ChurchInventory.id == loan.inventory_id).first()
        if inv and inv.status == "Sedang Dipinjam":
            inv.status = "Tersedia"

    db.delete(loan)
    db.commit()
    return {"status": "success", "message": f"Peminjaman {loan.loan_code} berhasil dihapus"}
