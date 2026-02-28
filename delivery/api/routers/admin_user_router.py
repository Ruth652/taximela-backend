from fastapi import APIRouter, Depends, Path
from delivery.api.controllers.user_controller import create_admin_controller, create_user_controller
from infrastructure.db_dependency import get_db
from sqlalchemy.orm import Session
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token

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

@router.post("/admins")
async def create_admin(
    _: dict = Depends(verify_token),
    data=Depends(create_admin_controller)
):
    return data


