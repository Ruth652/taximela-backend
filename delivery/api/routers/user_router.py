from fastapi import APIRouter, Depends
from pydantic import BaseModel
from delivery.api.controllers.user_controller import (
    create_user_controller,
    get_current_user_controller,
    update_current_user_controller,
    track_daily_activity_controller,
    update_user_navigation_done_controller,
    update_fcm_token_controller,
)
from infrastructure.auth.firebase_auth import get_current_firebase_user
from infrastructure.db_dependency import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])


class FCMTokenRequest(BaseModel):
    fcm_token: str


@router.post("")
async def create_user(data=Depends(create_user_controller)):
    return data


@router.get("/me")
async def get_user(data=Depends(get_current_user_controller)):
    return data


@router.patch("/me")
async def update_user(data=Depends(update_current_user_controller)):
    return data


@router.post("/activity/daily")
async def track_daily_activity(data=Depends(track_daily_activity_controller)):
    return data


@router.post("/navigation-done")
async def update_navigation_done(data=Depends(update_user_navigation_done_controller)):
    return data


@router.patch("/me/fcm-token")
async def update_fcm_token(
    body: FCMTokenRequest,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db),
):
    """
    Called by the mobile app whenever the FCM token is refreshed.
    Stores the latest token so the backend can send push notifications.
    """
    from usecases.user_usecase import update_fcm_token, UserNotFoundError
    from fastapi import HTTPException
    try:
        return update_fcm_token(db, firebase_user["uid"], body.fcm_token)
    except UserNotFoundError:
        raise HTTPException(404, "User not found")