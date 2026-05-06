from enum import Enum

from fastapi import APIRouter, Depends, Query
from delivery.api.controllers.contribution_group_controller import ContributionGroupController
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token
from sqlalchemy.orm import Session
from infrastructure.db_dependency import get_db
from schemas.contribution_group import ApproveContributionGroupRequest
from infrastructure.otp_database import get_otp_db 

class TargetType(str, Enum):
    station = "station"
    route = "route"

class ActionType(str, Enum):
    new = "new"
    edit = "edit"
    delete = "delete"

router = APIRouter(
    prefix="/contribution-groups",
    tags=["Admin - Contribution Groups Management"]
)


@router.get("/")
def get_contribution_groups(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    target_type: TargetType = Query(
        TargetType.station,
        description="Type of target"
    ),
    action: ActionType = Query(
        ActionType.new,
        description="Type of action"
    ),
    
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    controller = ContributionGroupController(user, db, otp_db=None)

    return controller.get_groups(
        page=page,
        limit=limit,
        target_type=target_type,
        action=action
    )
    
    
@router.get("/{group_id}")
def get_contribution_group_by_id(
    group_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    controller = ContributionGroupController(user, db, otp_db=None)

    return controller.get_group_by_id(group_id=group_id)

@router.post("/approve")
def approve_contribution(
    request: ApproveContributionGroupRequest,
    db: Session = Depends(get_db),
    otp_db: Session = Depends(get_otp_db),
    user: dict = Depends(verify_token),
):
    controller = ContributionGroupController(user, db, otp_db)
    return controller.approve_group(request)