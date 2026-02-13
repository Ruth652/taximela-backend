from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    user=Depends(verify_token)
):
    print("Received contribution:", contribution)
    firebase_uid = user["uid"]

    identity = db.query(AuthIdentity)\
        .filter(AuthIdentity.firebase_uid == firebase_uid)\
        .first()

    if not identity:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = identity.entity_id
    print(f"User ID: {user_id}, Contribution: {contribution}")

    repo = ContributionRepository(db)
    db_obj = await repo.save(contribution, user_id)
    return {
        "id": db_obj.id,
        "message": "Contribution saved successfully"
    }

