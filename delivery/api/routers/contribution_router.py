# from fastapi import APIRouter, Depends
# from infrastructure.auth.firebase_auth import get_current_firebase_user
# from infrastructure.database import get_db
# from delivery.api.controllers.contribution_controller import (
#     get_contribution_stats_controller
# )

# router = APIRouter(prefix="/contributions", tags=["Contributions"])

# @router.get("/stats/{userId}")
# def get_contribution_stats(
#     userId: str,
#     firebase_user=Depends(get_current_firebase_user),
#     db=Depends(get_db)
# ):
#     return get_contribution_stats_controller(
#         user_id=userId,
#         firebase_user=firebase_user,
#         db=db
#     )


from fastapi import APIRouter, Depends
from delivery.api.controllers.contribution_controller import get_contribution_stats_controller

router = APIRouter(prefix="/contributions", tags=["contributions"])

@router.get("/stats/{user_id}")
async def contribution_stats(user_id: str, stats=Depends(get_contribution_stats_controller)):
    """
    Get contribution statistics for the logged-in user.
    
    Returns 403 if user tries to access another user's stats.
    Returns 401 if token is invalid.
    """
    return stats
