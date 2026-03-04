from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from domain.admin_model import UpdateAdminRequest
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user
from usecases.admin_usecase import (
    delete_admin_usecase,
    list_users_for_admin,
    update_admin_usecase,
    update_user_status_usecase,
    AdminPermissionsError,
    UserNotFoundError
)
from pydantic import BaseModel


class UpdateStatusRequest(BaseModel):
    status: str


async def list_users_controller(
    page: int = 1,
    limit: int = 20,
    status: str = None,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    try:
        firebase_uid = firebase_user["uid"]
        return list_users_for_admin(db, firebase_uid, page, limit, status)
    except AdminPermissionsError as e:
        raise HTTPException(status_code=403, detail=str(e))

async def update_admin_controller(
    firebase_id: dict,
    admin_id: str,
    payload: UpdateAdminRequest,
    db: Session
):
    try:
        firebase_uid = firebase_id["uid"]
        admin = update_admin_usecase(db, firebase_uid, admin_id, payload)
        return {"message": "Admin Updated successfully",
                "admin_id": admin.id,
                "role": admin.role,
                "is_active": admin.is_active
                
                }
    except AdminPermissionsError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

async def delete_admin_controller(
    firebase_id: dict,
    admin_id: str,
    db: Session
):
    try:
        firebase_uid = firebase_id["uid"]
        admin = delete_admin_usecase(db, firebase_uid, admin_id)
        return {"message": "Admin Deleted successfully",
                "admin_id": admin.id,
                "role": admin.role,
                "is_active": admin.is_active
                
                }
    except AdminPermissionsError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

async def update_user_status_controller(
    user_id: str,
    payload: UpdateStatusRequest,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    try:
        firebase_uid = firebase_user["uid"]
        user = update_user_status_usecase(db, firebase_uid, user_id, payload.status)
        return {"message": "Status Updated successfully"}
    except AdminPermissionsError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

