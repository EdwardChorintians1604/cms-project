from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    main_auth,
    users,
    items,
    churches,
    church_admins,
    dashboard,
    database_admin,
    agenda,
    system_settings,
    informasi_pelayanan,
    security,
    church_structure,
    church_ministry,
    church_member,
    church_inventory,
)
from app.keuangan_gereja.api.keuangan import router as keuangan_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(main_auth.router, prefix="/main-auth", tags=["main-auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(churches.router, prefix="/churches", tags=["churches"])
api_router.include_router(church_admins.router, prefix="/church-admins", tags=["church-admins"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(database_admin.router, prefix="/database", tags=["database-admin"])
api_router.include_router(keuangan_router, prefix="/keuangan", tags=["keuangan-gereja"])
api_router.include_router(agenda.router, prefix="/agenda", tags=["agenda-kegiatan"])
api_router.include_router(system_settings.router, prefix="/settings", tags=["system-settings"])
api_router.include_router(informasi_pelayanan.router, prefix="/informasi-pelayanan", tags=["informasi-pelayanan"])
api_router.include_router(security.router, prefix="/security", tags=["security-dashboard"])
api_router.include_router(church_structure.router, prefix="/church-structure", tags=["church-structure"])
api_router.include_router(church_ministry.router, prefix="/church-ministries", tags=["church-ministries"])
api_router.include_router(church_member.router, prefix="/church-members", tags=["church-members"])
api_router.include_router(church_inventory.router, prefix="/church-inventories", tags=["church-inventories"])
