from fastapi import Depends, HTTPException
from infrastructure.db_dependency import get_db
from repository.contribution_repository import ContributionRepository
from usecases.contribution_usecase import submitContributionsUsecase, UpdateContributionStatusUsecase
from sqlalchemy.orm import Session

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
