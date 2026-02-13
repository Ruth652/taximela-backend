
from repository.auth_identity_repository import AuthIdentityRepository
from repository.contribution_repository import ContributionRepository
from fastapi import HTTPException, status
from domain.contribution_model import Contribute

import uuid

def _is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(val)
        return True
    except Exception:
        return False

def get_my_contribution_stats(db, requested_user_id: str, firebase_uid: str):
    """
    requested_user_id may be either internal UUID or a firebase uid.
    firebase_uid is the uid from the verified token.
    """
    auth_repo = AuthIdentityRepository(db)

    caller_internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not caller_internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")

    if _is_valid_uuid(requested_user_id):
        requested_internal_uuid = requested_user_id
    else:
        requested_internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(requested_user_id)
        if not requested_internal_uuid:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requested user not found")

    if requested_internal_uuid != caller_internal_uuid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to access this resource")

    repo = ContributionRepository(db)
    return repo.get_contribution_stats_by_user_uuid(requested_internal_uuid)



class submitContributionsUsecase:
    def __init__(self, contribution_repo):
        self.contribution_repo = contribution_repo
        
    
    
    async def execute(self, data, firebase_uid):
        
        internal_user_id = self.contribution_repo.get_user_uuid_by_firebase_uid(firebase_uid)
        
        contribution = Contribute(
            user_id=internal_user_id,
            target_type=data.target_type,
            description=data.description,
            trust_score_at_submit=internal_user_id.trust_score_at_submit,
            status="pending"
        )
        return await self.contribution_repo.save(contribution)

class UpdateContributionStatusUsecase:
    def __init__(self, repo):
        self.repo = repo 

    async def execute(self, contribution_id: str, status: str):
        return await self.repo.update_status(contribution_id, status)

