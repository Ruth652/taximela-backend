from fastapi import Depends, HTTPException, UploadFile, Form, File
from typing import Optional
from sqlalchemy.orm import Session
from domain.admin_model import CreateAdminRequest
from infrastructure.database import get_db
from domain.user_model import UpdateUserRequest, CreateUserRequest
from infrastructure.auth.firebase_auth import create_firebase_user, get_current_firebase_user
from usecases.user_usecase import (
    create_admin_first_login,
    create_user_first_login,
    get_current_user,
    update_current_user,
    PermissionDeniedError,
    track_daily_activity,
    update_current_user,
    UserNotFoundError,
    NoUpdateFieldsError,
    PermissionDeniedError,
    track_daily_activity,
    update_user_navigation_done,
    InvalidFullNameError,
    InvalidLanguageError,
    
)



async def create_user_controller(
    payload:CreateUserRequest | None,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    auth_user_id = firebase_user["uid"]
    email = firebase_user["email"]
    fcm_token = payload.fcm_token if payload else None

    return create_user_first_login(
        db=db,
        firebase_uid=auth_user_id,
        email=email,
        payload=payload.dict(),
        fcm_token=fcm_token
    )
    
async def create_admin_controller(
    payload: CreateAdminRequest | None,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    auth_user_id = firebase_user["uid"]

    try:
        return create_admin_first_login(
            db=db,
            creator_firebase_uid=auth_user_id,
            new_user=payload,
            create_firebase_user=create_firebase_user
        )
    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="Authenticated user not found in local DB")
    except PermissionDeniedError:
        raise HTTPException(status_code=403, detail="Only super admins can create new admins")
    
   
   
async def get_current_user_controller(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    firebase_uid = firebase_user["uid"]
    user = get_current_user(db, firebase_uid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

async def update_current_user_controller(
    full_name: Optional[str] = Form(None),
    preferred_language: Optional[str] = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    firebase_uid = firebase_user["uid"]

    try:
        updated_user = await update_current_user(
            db=db,
            firebase_uid=firebase_uid,
            full_name=full_name,
            preferred_language=preferred_language,
            profile_picture=profile_picture
        )

    except UserNotFoundError:
        raise HTTPException(404, "User not found")

    except NoUpdateFieldsError:
        raise HTTPException(400, "No valid fields provided")

    except InvalidFullNameError as e:
        raise HTTPException(400, str(e))

    except InvalidLanguageError as e:
        raise HTTPException(400, str(e))

    return {
        "message": "Profile updated successfully",
        "user": updated_user
    }

async def track_daily_activity_controller(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    firebase_uid = firebase_user["uid"]

    return track_daily_activity(db, firebase_uid)

async def update_user_navigation_done_controller(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    firebase_uid = firebase_user["uid"]

    try:
        user = get_current_user(db, firebase_uid)
        if not user:
            raise UserNotFoundError()

        return update_user_navigation_done(db, firebase_uid)

    except UserNotFoundError:
        raise HTTPException(404, "User not found")
