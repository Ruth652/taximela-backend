from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from domain.user_model import UpdateUserRequest, CreateUserRequest
from infrastructure.auth.firebase_auth import get_current_firebase_user
from usecases.user_usecase import create_user_first_login, get_current_user, UserNotFoundError, NoUpdateFieldsError, update_current_user


async def create_user_controller(
    payload:CreateUserRequest | None,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    auth_user_id = firebase_user["uid"]
    email = firebase_user["email"]
    return create_user_first_login(
        db=db,
        firebase_uid=auth_user_id,
        email=email,
        payload=payload.dict()
    )
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
    payload: UpdateUserRequest,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    firebase_uid = firebase_user["uid"]
    
    try:
        updated_user = update_current_user(db, firebase_uid, payload)
    except UserNotFoundError:
        raise HTTPException(404, "User not found")
    except NoUpdateFieldsError:
        raise HTTPException(400, "No valid fields provided")

    return {"message": "Profile updated successfully", "user": updated_user}
