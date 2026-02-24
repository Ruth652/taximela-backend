from fastapi import APIRouter, Depends, Path
from delivery.api.controllers.admin_controllers import (
    list_users_controller,
    update_user_status_controller
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin - User Management"]
)

@router.get("/users")
async def list_users(data=Depends(list_users_controller)):
    return data

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str = Path(..., description="User ID"),
    data=Depends(update_user_status_controller)
):
    return data
