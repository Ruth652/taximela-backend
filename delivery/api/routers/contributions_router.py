from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from delivery.api.controllers.contribution_controller import submit_contribution
from domain.auth_identity_model import AuthIdentity
from infrastructure.db_dependency import get_db
from schemas.contribution_schema import ContributeSchema
from repository.contribution_repository import ContributionRepository
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token

router = APIRouter(
    prefix="/contributions",
    tags=["contributions"]
)

@router.post("/")
async def create_contribution(
    contribution: ContributeSchema,
    db: Session = Depends(get_db),
    user =Depends(verify_token)
):
    user_id = user["uid"]
    

    db_obj = await submit_contribution(contribution, user_id, db)
    return {
        "id": db_obj.id,
        "message": "Contribution saved successfully"
    }

