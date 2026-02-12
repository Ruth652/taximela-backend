from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user
from usecases.user_usecase import create_user_first_login

async def create_user_controller(
    payload: dict | None = None,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    auth_user_id = firebase_user["uid"]
    email = firebase_user["email"]
    return create_user_first_login(
        db=db,
        firebase_uid=auth_user_id,
        email=email,
        payload=payload
    )
