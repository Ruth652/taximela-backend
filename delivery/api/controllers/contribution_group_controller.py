# controllers/contribution_group_controller.py

from http.client import HTTPException

from grpc import Status
from sqlalchemy.orm import Session
from repository.auth_identity_repository import AuthIdentityRepository
from repository.contribution_group_repository import ContributionGroupRepository
from repository.contribution_repository import ContributionRepository
from schemas.contribution_group import ApproveContributionGroupRequest
from usecases.contribution_groups_usecase import ContributionGroupUseCase


class ContributionGroupController:

    def __init__(self, user, db: Session, otp_db: Session):
        self.db = db
        self.user = user
        self.otp_db = otp_db
        

    def get_groups(self, page: int, limit: int, target_type: str = None, action: str = None):
        auth_repo = AuthIdentityRepository(self.db)
        admin = auth_repo.get_super_admin_operational_admin_uuids(firebase_uids=[self.user["uid"]])
        
        if not admin:
            raise HTTPException(status_code=Status.HTTP_403_FORBIDDEN, detail="You are not a super admin user")
        
        repo = ContributionGroupRepository(self.db)
        usecase = ContributionGroupUseCase(repo, self.otp_db)

        return usecase.get_groups(
            page=page,
            limit=limit,
            target_type=target_type,
            action=action
        )
        
    def get_group_by_id(self, group_id: int):
        auth_repo = AuthIdentityRepository(self.db)
        admin = auth_repo.get_super_admin_operational_admin_uuids(firebase_uids=[self.user["uid"]])
        
        if not admin:
            raise HTTPException(status_code=Status.HTTP_403_FORBIDDEN, detail="You are not an authorized admin")
        
        repo = ContributionGroupRepository(self.db)
        usecase = ContributionGroupUseCase(repo, self.otp_db)

        return usecase.get_group_by_id(group_id=group_id)
    
    def approve_group(self, request: ApproveContributionGroupRequest):
        auth_repo = AuthIdentityRepository(self.db)
        admin = auth_repo.get_super_admin_operational_admin_uuids(
            firebase_uids=[self.user["uid"]]
        )

        if not admin:
            raise HTTPException(
                status_code=Status.HTTP_403_FORBIDDEN,
                detail="You are not an authorized admin",
            )

        repo = ContributionGroupRepository(self.db)
        usecase = ContributionGroupUseCase(repo, self.otp_db)

        return usecase.approve_group(request)