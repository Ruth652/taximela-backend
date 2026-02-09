from fastapi import Depends
from infrastructure.db_dependency import get_db
from repository.contribution_repository import ContributionRepository
from usecases.contribution_usecase import submitContributionsUsecase,  submitContributionsUsecase

async def submit_contribution(
    data,
    db = Depends(get_db)
):
    repo = ContributionRepository(db)
    usecase = submitContributionsUsecase(repo)

    return await usecase.execute(data)
