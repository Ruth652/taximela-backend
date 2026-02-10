from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from infrastructure.db_dependency import get_db
from delivery.api.controllers.contribution_controller import update_contribution_status
from schemas.contribution_schema import ContributionUpdateSchema

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
