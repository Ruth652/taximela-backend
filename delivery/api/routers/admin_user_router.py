from fastapi import APIRouter, Depends, HTTPException, Path
from delivery.api.controllers.user_controller import create_admin_controller, create_user_controller

from domain.admin_model import CreateAdminRequest, UpdateAdminRequest
from infrastructure.db_dependency import get_db
from sqlalchemy.orm import Session
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token

from delivery.api.controllers.admin_controllers import (
    UpdateStatusRequest,
    delete_admin_controller,
    list_users_controller,
    update_admin_controller,
    update_user_status_controller,
    list_admins_controller
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin - User Management"]
)

@router.get("/users")
async def list_users(data=Depends(list_users_controller)):
    return data

@router.get("/admins")
async def list_admins(data=Depends(list_admins_controller)):
    return data

@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str = Path(..., description="User ID"),
    data=Depends(update_user_status_controller)
):
    return data

@router.post("/admins")
async def create_admin(
    data: CreateAdminRequest = None,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    try:
        result = await create_admin_controller(
            payload=data, 
            firebase_user=user, 
            db=db
            )
        return result
    except HTTPException as e:
        raise e
    except ValueError as e:
        return {"error": str(e)}
    
    

@router.patch("/admins/{admin_id}")
async def update_admin(
    admin_id: str = Path(..., description="Admin ID"),
    data: UpdateAdminRequest = None,
    db: Session = Depends(get_db),
    user:dict = Depends(verify_token)
):
    try:
        result = await update_admin_controller(
            firebase_id=user, 
            admin_id=admin_id, 
            payload=data, 
            db=db
            )
        return result
    except HTTPException as e:
        raise e
    except ValueError as e:
        return {"error": str(e)}
    
@router.patch("/admins/{admin_id}/delete")
async def delete_admin(
    admin_id: str = Path(..., description="Admin ID"),
    db: Session = Depends(get_db),
    user:dict = Depends(verify_token)
):
    try:
        result = await delete_admin_controller(
            firebase_id=user, 
            admin_id=admin_id, 
            db=db
            )
        return result
    except HTTPException as e:
        raise e
    except ValueError as e:
        return {"error": str(e)}

    