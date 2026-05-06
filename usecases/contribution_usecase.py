from uuid import UUID
from sqlalchemy.orm import Session

from domain.contribution_model import Contribution, ContributionStatusEnum
from repository.gtfs_repository import GTFSRepository
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

def get_my_contribution_stats(db, requested_user_uid: str, firebase_uid: str):
    auth_repo = AuthIdentityRepository(db)

    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")

    try:
        requested_uuid = UUID(requested_user_uid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user UUID")

    if requested_uuid != internal_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this resource"
        )

    repo = ContributionRepository(db)
    return repo.get_contribution_stats_by_user_uuid(internal_uuid)

def get_contributions_by_user(db,requested_user_uid: str, firebase_uid: str, page: int, limit: int):
    
    auth_repo = AuthIdentityRepository(db)

    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)

    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")
    
   # to do check if the id is commuter's or admin's or else return 401 again if necessary 
    print(f"Requested user UID: {requested_user_uid}, Internal UUID: {internal_uuid}")

    try:
        requested_uuid = UUID(requested_user_uid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user UUID")

    if requested_uuid != internal_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this resource"
        )
    repo = ContributionRepository(db)
    return repo.get_contributions_by_user_uuid(internal_uuid, page, limit)


async def GetContributionAdminList(db, requested_user_firebase_uid: str, firebase_uid: str, page: int, limit: int, status: str):
    
    auth_repo = AuthIdentityRepository(db)
    
    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")
    
    if internal_uuid not in auth_repo.get_super_admin_operational_admin_uuids(firebase_uids=[firebase_uid]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not an admin user{internal_uuid}")
    
    repo = ContributionRepository(db)
    return await repo.get_contributions_by_status(status, page, limit)

async def GetContributionStatsAdmin(db, firebase_uid: str):
    
    auth_repo = AuthIdentityRepository(db)
    
    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")
    
    if internal_uuid not in auth_repo.get_super_admin_operational_admin_uuids(firebase_uids=[firebase_uid]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not an admin user{internal_uuid}")
    
    repo = ContributionRepository(db)
    return await repo.get_contribution_stats_for_all_users()

    
async def submitContributionsUsecase(data: ContributeSchema, firebase_uid: str, db: Session):
    
    auth_repo = AuthIdentityRepository(db)
    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)    
    if not internal_uuid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB 2")
    
    if data.action != "new" and not data.target_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="target_id is required for edit or delete actions")
    
    if data.target_type == "route":
        _validate_route(data)
    elif data.target_type == "station":
        _validate_station(data)
        
    repo = ContributionRepository(db)
    return repo.create_contribution(data, internal_uuid)


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user not found in local DB")
    if internal_uuid not in authrepo.get_super_admin_operational_admin_uuids(firebase_uids=[user_id]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not an operational admin user{internal_uuid}") 
   
    admin_id = authrepo.get_admin_id_by_user_id(internal_uuid)
    
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

        gtfs_repo = GTFSRepository(db)
        
        if contribution.target_type == "station":
            group = contribution_repo.find_station_group(
                contribution_payload=contribution.payload,
                action=contribution.action,
            )
            if not group:
                group = contribution_repo.create_contribution_group(
                    target_type="station",
                    action=contribution.action,
                    reference_lat=contribution.payload.get("lat"),
                    reference_lon=contribution.payload.get("lon")  ,
                    target_id=contribution.target_id if contribution.target_id else None 
                )
        
        elif contribution.target_type == "route":
            group = contribution_repo.find_route_group(contribution.payload, contribution.action)
            if not group:
                group = contribution_repo.create_contribution_group(
                    target_type="route",
                    action=contribution.action,
                    reference_stops=contribution.payload.get("stops"),
                    target_id=contribution.target_id if contribution.target_id else None
                )
            
           
        contribution.group_id = group.id
        gtfs_repo.add_to_gtfs_queue(db, group_id=group.id, queued_by=admin_id)
        
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
        
def _validate_station(data):
    if data.action in ["new", "edit"]:
        if not (data.name and data.lat and data.lon):
            raise HTTPException(400, "Missing station fields")
        
def _validate_route(data):
    if data.action in ["new", "edit"]:
        if not data.stops or len(data.stops) < 2:
            raise HTTPException(400, "Route must have at least 2 stops")

        if not data.start_stop_id or not data.end_stop_id:
            raise HTTPException(400, "Start and end stops required")

        if data.stops[0] != data.start_stop_id:
            raise HTTPException(400, "First stop must match start_stop_id")

        if data.stops[-1] != data.end_stop_id:
            raise HTTPException(400, "Last stop must match end_stop_id")
        
   