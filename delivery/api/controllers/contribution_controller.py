
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.contribution_schema import ContributeSchema
from usecases.contribution_usecase import GetContributionStatsAdmin, GetPreviousContributionStatus, get_my_contribution_stats
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user
from repository.contribution_repository import ContributionRepository
from usecases.contribution_usecase import submitContributionsUsecase, UpdateContributionStatusUsecase, get_contributions_by_user, GetContributionAdminList
from sqlalchemy.orm import Session

async def get_contribution_stats_controller(
    user_id: str,
    firebase_user: dict = Depends(get_current_firebase_user),
    
    db: Session = Depends(get_db)
):
    """
    Controller to fetch user contribution stats.
    """
    print(firebase_user)

    auth_user_id = firebase_user["uid"]
    return get_my_contribution_stats(db, user_id, auth_user_id)

async def submit_contribution(
    data: ContributeSchema,
    firebase_user: UUID = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    firebase_uid = str(firebase_user)    
    
    return await submitContributionsUsecase(data, firebase_uid, db)

async def get_user_contributions_controller(
    user_id:str,
    page:int,
    limit:int,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    auth_user_id = firebase_user["uid"]

    return get_contributions_by_user(db, user_id, auth_user_id, page, limit)

# async def update_contribution_status(
#     contribution_id: int,
#     data,
#     db: Session = Depends(get_db)
# ):
#     repo = ContributionRepository(db)
#     usecase = UpdateContributionStatusUsecase(repo)
    
#     try:
#         result = await usecase.execute(contribution_id, data.status)
        
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
    
#     return {"message": "Contribution status updated successfully", "contribution": result}


async def get_contribution_admin_list(
    user_id: str,
    page: int,
    limit: int,
    status: str,
    db: Session,
):
    auth_user_id = user_id 
    
    return await GetContributionAdminList(
        db=db,
        requested_user_firebase_uid=user_id,
        firebase_uid=auth_user_id,
        page=page,
        limit=limit,
        status=status,)
async def get_all_contribution_stats(
    db: Session,
    user_id: str
):
    auth_user_id = user_id 
    return await GetContributionStatsAdmin(db, user_id, auth_user_id)
