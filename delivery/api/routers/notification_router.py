from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from infrastructure.db_dependency import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token
from usecases.notification_usecase import (
    get_notifications_usecase,
    mark_notifications_read_usecase,
    mark_all_notifications_read_usecase,
)

router = APIRouter(prefix="/api/admin/notifications", tags=["Admin - Notifications"])


class MarkReadRequest(BaseModel):
    notification_ids: List[str]


@router.get("")
async def get_notifications(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    """
    Returns paginated notifications for the authenticated admin.
    Frontend polls this every 60 seconds.
    """
    return get_notifications_usecase(db, user["uid"], page, limit)


@router.patch("/read")
async def mark_as_read(
    body: MarkReadRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    """
    Marks specific notifications as read by their IDs.
    """
    return mark_notifications_read_usecase(db, user["uid"], body.notification_ids)


@router.patch("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    """
    Marks all unread notifications for the authenticated admin as read.
    """
    return mark_all_notifications_read_usecase(db, user["uid"])
