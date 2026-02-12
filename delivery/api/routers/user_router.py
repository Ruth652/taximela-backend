from fastapi import APIRouter, Depends
from delivery.api.controllers.user_controller import create_user_controller

router = APIRouter(prefix="/users", tags=["users"])

@router.post("")
async def create_user(data=Depends(create_user_controller)):
    return data
