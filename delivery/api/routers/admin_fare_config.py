from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from infrastructure.db_dependency import get_db as get_db_dep
from domain.fare_configurations_model import FareUpdateRequests
from delivery.api.controllers.fare_controller import (
    update_fare_config_controller,
    get_active_fare_controller,
    get_fare_history_controller,
)
from delivery.api.dependencies.admin_auth import get_current_operational_or_superadmin
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token

router = APIRouter(tags=["Fare Management"])


# ─── Admin endpoints ──────────────────────────────────────────────────────────

@router.post("/admin/fare/update")
async def update_fare(
    request: FareUpdateRequests,
    admin=Depends(get_current_operational_or_superadmin),
    db: Session = Depends(get_db),
):
    """
    Create a new active fare configuration.
    Deactivates the previous one and invalidates the in-memory cache.
    Requires operational_admin or super_admin.
    """
    try:
        return await update_fare_config_controller(request, db, admin.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update fare: {str(e)}")


@router.get("/admin/fare/active")
async def get_active_fare(
    admin=Depends(get_current_operational_or_superadmin),
    db: Session = Depends(get_db),
):
    """
    Returns the currently active fare configuration.
    Requires operational_admin or super_admin.
    """
    return await get_active_fare_controller(db)


@router.get("/admin/fare/history")
async def get_fare_history(
    page: int = 1,
    limit: int = 20,
    admin=Depends(get_current_operational_or_superadmin),
    db: Session = Depends(get_db),
):
    """
    Returns paginated history of all fare configurations (newest first).
    Requires operational_admin or super_admin.
    """
    return await get_fare_history_controller(db, page, limit)


# ─── Public (authenticated user) endpoint ────────────────────────────────────

@router.get("/fare/active")
async def get_current_fare(
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Returns the currently active fare configuration.
    Available to any authenticated user — used by frontend to display pricing info.
    """
    return await get_active_fare_controller(db)
