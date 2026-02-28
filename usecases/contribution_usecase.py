
from sqlalchemy.orm import Session

from domain.contribution_model import Contribution, ContributionStatusEnum
from repository.auth_identity_repository import AuthIdentityRepository
from repository.contribution_repository import ContributionRepository
from repository.user_repository import UserRepository
from fastapi import HTTPException, status

# from domain.contribution_model import Contribute


import uuid

from schemas.contribution_schema import ContributeSchema

def _is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(val)
        return True
    except Exception:
        return False

def get_my_contribution_stats(db, requested_user_firebase_uid: str, firebase_uid: str):
    if requested_user_firebase_uid != firebase_uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this resource")

    auth_repo = AuthIdentityRepository(db)

    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")

    repo = ContributionRepository(db)
    return repo.get_contribution_stats_by_user_uuid(internal_uuid)

def get_contributions_by_user(db,requested_user_firebase_uid: str, firebase_uid: str, page: int, limit: int):
    if requested_user_firebase_uid != firebase_uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this resource")

    auth_repo = AuthIdentityRepository(db)

    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")

    repo = ContributionRepository(db)
    return repo.get_contributions_by_user_uuid(internal_uuid, page, limit)


async def GetContributionAdminList(db, requested_user_firebase_uid: str, firebase_uid: str, page: int, limit: int, status: str):
    
    auth_repo = AuthIdentityRepository(db)
    
    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")
    
    if internal_uuid not in auth_repo.get_operational_admin_uuids(firebase_uids=[firebase_uid]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not an admin user{internal_uuid}")
    
    repo = ContributionRepository(db)
    return await repo.get_contributions_by_status(status, page, limit)

async def GetContributionStatsAdmin(db, requested_user_firebase_uid: str, firebase_uid: str):
    
    auth_repo = AuthIdentityRepository(db)
    
    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")
    
    if internal_uuid not in auth_repo.get_operational_admin_uuids(firebase_uids=[firebase_uid]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not an admin user{internal_uuid}")
    
    repo = ContributionRepository(db)
    return await repo.get_contribution_stats_for_all_users()

    
async def submitContributionsUsecase(data: ContributeSchema, firebase_uid,db):
    
    auth_repo = AuthIdentityRepository(db)
    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)    
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB 2")
    
    repo = ContributionRepository(db)
    return repo.save_contribution(data, internal_uuid)


async def GetPreviousContributionStatus(user_id, db):
    auth_repo = AuthIdentityRepository(db)
    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(user_id)    
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")
    
    repo = UserRepository(db)
    return repo.get_user_previous_contribution_status(internal_uuid)
  

async def UpdateContributionStatusUsecase(user_id: str, contribution_id: int, new_status: str, db:Session):

    contribution_repo = ContributionRepository(db)
    user_repo = UserRepository(db)
    authrepo = AuthIdentityRepository(db)
    
    internal_uuid = authrepo.get_user_uuid_by_firebase_uid(user_id)
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB 2")
    if internal_uuid not in authrepo.get_super_admin_operational_admin_uuids(firebase_uids=[user_id]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not an operational admin user{internal_uuid}")  
    
    contribution = contribution_repo.get_contribution_by_id(contribution_id)
    if not contribution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contribution not found")
    
    user = user_repo.get_user_by_id(contribution.user_id)

    if new_status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
        
    contribution.status = ContributionStatusEnum(new_status)
    
    if new_status == "approved":
        user.rating_score += 15
        user.rejection_streak_count = 0

    elif new_status == "rejected":
        if user.rejection_streak_count == 0:
            user.rating_score -= 15
        else:
            user.rating_score -= 5
        user.rejection_streak_count += 1
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )

    user.reputational_tier = calculate_reputational_tier(user.rating_score)

    db.commit()
    db.refresh(contribution)
    db.refresh(user)
    contribution_repo.update_status(contribution_id=contribution_id, new_status=contribution.status)
    

    return {
        "message": "Contribution status updated successfully",
        "contribution": contribution,
        "new_score": user.rating_score,
        "new_tier": user.reputational_tier
    }

def calculate_reputational_tier(score):
        if score < 0:
            return "Flagged"
        elif score < 50:
            return "Silver"
        elif score < 200:
            return "Gold"
        else:
            return "Platinum" 
