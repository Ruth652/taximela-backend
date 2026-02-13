from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from infrastructure.db_dependency import get_db
from delivery.api.controllers.contribution_controller import get_contribution_admin_list, update_contribution_status
from schemas.contribution_schema import ContributionUpdateSchema
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token


router = APIRouter(
    prefix="/api/admin/contributions",
    tags=["Admin"]
)

@router.put("/{id}")
async def approve_reject_contribution(
    id: str = Path(..., description="Contribution ID"),
    data: ContributionUpdateSchema = None,
    db: Session = Depends(get_db)
):
    return await update_contribution_status(id, data, db)

@router.get("/list")
async def get_contribution_admin(
    page: int = 1,
    limit: int = 10,
    status: str = "pending_review",  #default to "pending", should be changed later
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):
    return await get_contribution_admin_list(
        user_id = user["uid"], 
        page=page, limit=limit, status=status, db=db)
