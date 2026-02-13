
from domain.contribution_model import Contribution
from repository.auth_identity_repository import AuthIdentityRepository
from repository.contribution_repository import ContributionRepository
from fastapi import HTTPException, status
# from domain.contribution_model import Contribute


import uuid

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


class submitContributionsUsecase:
    def __init__(self, contribution_repo):
        self.contribution_repo = contribution_repo
        
    async def execute(self, data, firebase_uid):
        
        internal_user_id = self.contribution_repo.get_user_uuid_by_firebase_uid(firebase_uid)
        
        contribution = Contribution(
            user_id=internal_user_id,
            target_type=data.target_type,
            description=data.description,
            trust_score_at_submit=internal_user_id.trust_score_at_submit,
            status="pending_review"
        )
        return await self.contribution_repo.save(contribution)

class UpdateContributionStatusUsecase:
    def __init__(self, repo):
        self.repo = repo 

    async def execute(self, contribution_id: str, status: str):
        return await self.repo.update_status(contribution_id, status)
