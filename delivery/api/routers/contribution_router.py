from fastapi import APIRouter, Depends, Query
from delivery.api.controllers.contribution_controller import get_contribution_stats_controller, get_user_contributions_controller

router = APIRouter(prefix="/contributions", tags=["contributions"])

@router.get("/stats/{user_id}")
async def contribution_stats(user_id: str, stats=Depends(get_contribution_stats_controller)):
    """
    Get contribution statistics for the logged-in user.
    
    Returns 403 if user tries to access another user's stats.
    Returns 401 if token is invalid.
    """
    return stats

@router.get("/{user_id}")
async def get_user_contributions(
        user_id: str,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        data=Depends(get_user_contributions_controller)
):
    """
    Get contributions made by a specific user.
    
    Returns 403 if user tries to access another user's contributions.
    Returns 401 if token is invalid.
    """
    return data