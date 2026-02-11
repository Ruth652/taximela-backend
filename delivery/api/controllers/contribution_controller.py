from fastapi import Depends
from sqlalchemy.orm import Session
from usecases.contribution_usecase import get_my_contribution_stats
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user

async def get_contribution_stats_controller(
    user_id: str,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """
    Controller to fetch user contribution stats.
    """
    auth_user_id = firebase_user["uid"]
    return get_my_contribution_stats(db, user_id, auth_user_id)
