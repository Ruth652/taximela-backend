from uuid import UUID

from fastapi import APIRouter, Depends, Query
from delivery.api.controllers.contribution_controller import get_contribution_stats_controller, get_user_contributions_controller


router = APIRouter(prefix="/api/contributions", tags=["contributions"])

@router.get("/stats")
async def contribution_stats(stats=Depends(get_contribution_stats_controller)):
    """
    Get contribution statistics for the logged-in user.

    Returns 401 if token is invalid.
    """
    return stats

@router.get("/")
async def get_user_contributions(
        page: int = Query(1, ge=1),
        limit: int = Query(5, ge=1, le=100),
        data=Depends(get_user_contributions_controller)
):
    """
    Get contributions made by a specific user.
    Returns 401 if token is invalid.
    """
    return data