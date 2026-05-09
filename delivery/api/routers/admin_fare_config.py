from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from domain.fare_configurations_model import FareUpdateRequests
from delivery.api.controllers.fare_controller import update_fare_config_controller
from delivery.api.dependencies.admin_auth import get_current_operational_admin, get_current_operational_or_superadmin
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/admin/fare", tags=["Admin Fare Management"])


@router.post("/update")
async def update_fare(
    request: FareUpdateRequests,
    admin=Depends(get_current_operational_or_superadmin),
    db: Session = Depends(get_db),
):
    try:
        return await update_fare_config_controller(request, db, admin.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update fare: {str(e)}")

