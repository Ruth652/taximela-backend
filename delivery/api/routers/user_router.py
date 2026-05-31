from fastapi import APIRouter, Depends
from delivery.api.controllers.user_controller import create_user_controller, get_current_user_controller, update_current_user_controller, track_daily_activity_controller, update_user_navigation_done_controller

router = APIRouter(prefix="/users", tags=["Users"])

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