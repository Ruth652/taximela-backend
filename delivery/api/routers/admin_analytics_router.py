from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from infrastructure.db_dependency import get_db
from delivery.api.controllers.admin_analytics_controller import get_admin_businesses_growth_analytics_controller, get_admin_total_analytics_controller, get_admin_users_growth_analytics_controller
from delivery.api.dependencies.admin_auth import get_current_super_admin

router = APIRouter(
    prefix="/api/admin/analytics",
    tags=["Admin - Analytics"]
)


@router.get("/total")
async def get_total_analytics(
    admin=Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    return await get_admin_total_analytics_controller(db)

@router.get("/users-growth")
async def get_users_growth_analytics(
    admin=Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    return await get_admin_users_growth_analytics_controller(db)

@router.get("/businesses-growth")
async def get_businesses_growth_analytics(
    admin=Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    return await get_admin_businesses_growth_analytics_controller(db)