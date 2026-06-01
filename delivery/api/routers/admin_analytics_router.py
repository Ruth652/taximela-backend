from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Literal

from infrastructure.db_dependency import get_db
from delivery.api.controllers.admin_analytics_controller import (
    get_admin_total_analytics_controller,
    get_contribution_trend_controller
    )
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

@router.get("/contributions/trend")
async def get_contribution_trend(
    period: Literal["weekly", "monthly"] = Query("weekly"),
    admin=Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    return await get_contribution_trend_controller(
        db=db,
        period=period
    )