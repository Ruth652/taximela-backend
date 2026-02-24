from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from infrastructure.db_dependency import get_db
from delivery.api.controllers.contribution_controller import get_all_contribution_stats, get_contribution_admin_list
from schemas.contribution_schema import ContributionUpdateSchema
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token
from usecases.contribution_usecase import UpdateContributionStatusUsecase


router = APIRouter(
    prefix="/api/admin/contributions",
    tags=["Admin"]
)

@router.patch("/{id}")
async def approve_reject_contribution(
    id: str = Path(..., description="Contribution ID"),
    data: ContributionUpdateSchema = None,
    db: Session = Depends(get_db)
):
    try:
        result = await UpdateContributionStatusUsecase(contribution_id=id, new_status=data.status, db=db)
        return result
    except ValueError as e:
        return {"error": str(e)}

@router.get("/list")
async def get_contribution_admin(
    page: int = 1,
    limit: int = 10,
    status: str = "pending_review",  #default to "pending_review", could be changed to all
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):
    return await get_contribution_admin_list(
        user_id = user["uid"], 
        page=page, limit=limit, status=status, db=db)

@router.get("/stats")
async def get_contribution_stats(
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):
    return await get_all_contribution_stats(db, user["uid"])
