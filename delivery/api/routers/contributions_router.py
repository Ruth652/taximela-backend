from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infrastructure.db_dependency import get_db
from schemas.contribution_schema import ContributeSchema
from repository.contribution_repository import ContributionRepository

router = APIRouter(
    prefix="/contributions",
    tags=["Contributions"]
)

@router.post("/")
async def create_contribution(
    contribution: ContributeSchema,
    db: Session = Depends(get_db)
):
    repo = ContributionRepository(db)
    db_obj = await repo.save(contribution)
    return {
        "id": db_obj.id,
        "message": "Contribution saved successfully"
    }
