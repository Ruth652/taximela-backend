
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from usecases.contribution_usecase import get_my_contribution_stats
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user
from repository.contribution_repository import ContributionRepository
from usecases.contribution_usecase import submitContributionsUsecase, UpdateContributionStatusUsecase
from sqlalchemy.orm import Session

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

async def submit_contribution(
    data,
    db = Depends(get_db)
):
    repo = ContributionRepository(db)
    usecase = submitContributionsUsecase(repo)

    return await usecase.execute(data)

async def update_contribution_status(
    contribution_id: int,
    data,
    db: Session = Depends(get_db)
):
    repo = ContributionRepository(db)
    usecase = UpdateContributionStatusUsecase(repo)
    
    try:
        result = await usecase.execute(contribution_id, data.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"message": "Contribution status updated successfully", "contribution": result}
