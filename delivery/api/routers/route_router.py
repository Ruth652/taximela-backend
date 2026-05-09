# delivery/api/routers/route_router.py

from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from domain.route_model import PlanRequest
from domain.service_places_model import AllRoutesServicePlacesRequest
from domain.service_places_model import SingleRouteServicePlacesRequest
from delivery.api.controllers.route_controller import (
    plan_trip_controller,
    all_routes_service_places_controller,
    single_route_service_places_controller
)
from repository.auth_identity_repository import AuthIdentityRepository
from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user

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

 
    itineraries = await plan_trip_controller(data, db)

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
@router.post("/service-places/all")
async def all_route_service_places(
    data: AllRoutesServicePlacesRequest,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    auth_repo = AuthIdentityRepository(db)

    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_user["uid"])
    if not internal_uuid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user not found in local DB"
        )

    return await all_routes_service_places_controller(data, db)

@router.post("/service-places/single")
async def single_route_service_places(
    data: SingleRouteServicePlacesRequest,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    auth_repo = AuthIdentityRepository(db)

    internal_uuid = auth_repo.get_user_uuid_by_firebase_uid(firebase_user["uid"])
    if not internal_uuid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user not found in local DB"
        )

    return await single_route_service_places_controller(data, db)