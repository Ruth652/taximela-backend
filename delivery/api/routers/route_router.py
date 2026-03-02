# delivery/api/routers/route_router.py

from fastapi import APIRouter, Query
from domain.route_model import PlanRequest
from delivery.api.controllers.route_controller import plan_trip_controller
from repository.auth_identity_repository import AuthIdentityRepository
from infrastructure.database import get_db
from sqlalchemy.orm import Session
from infrastructure.auth.firebase_auth import get_current_firebase_user 
from fastapi import Depends, HTTPException, status, Query

from typing import List  

router = APIRouter(prefix="/routes", tags=["routes"])

@router.post("/plan")
async def plan_trip(
    data: PlanRequest, 
    sortby: str = Query(
        "time", 
        description="Sort by 'time', 'price', 'walk', 'transfers'"
    ),
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
    
):

    auth_repo = AuthIdentityRepository(db)

    # Validate authenticated user exists locally
    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_user["uid"])
    if not internal_uuid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user not found in local DB"
        )

 
    itineraries = await plan_trip_controller(data)

    #sorting
    if sortby == "price":
        itineraries.sort(key=lambda x: x["costEstimation"]["minimumCost"])
    elif sortby == "time":
        itineraries.sort(key=lambda x: x["totalTripTime"])
    elif sortby == "transfers":
        itineraries.sort(key=lambda x: x["transfers"])
    elif sortby == "walk":
        # sum of all walk legs durations
        #itineraries.sort(key=lambda x: sum(leg["estimatedDuration"] for leg in x["tripDetail"] if leg["mode"]=="walk"))
        itineraries.sort(key=lambda x: x["totalWalkDistance"])

    else:
        itineraries.sort(key=lambda x: x["totalTripTime"])

    return itineraries
