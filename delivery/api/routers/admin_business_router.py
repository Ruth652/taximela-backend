from fastapi import APIRouter, Depends, Path, Query
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.db_dependency import get_db
from delivery.api.controllers.admin_business_controller import (
    get_business_registrations_controller
)
from delivery.api.dependencies.admin_auth import get_current_operational_admin

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin - Business-management"]
)

@router.get("/business-registrations")
async def get_business_registrations(
    status: str | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_operational_admin),
    db: Session = Depends(get_db),
):
    return await get_business_registrations_controller(
        db=db,
        status=status,
        from_date=from_date,
        to_date=to_date,
        search=search,
        page=page,
        limit=limit
    )