# delivery/api/routers/route_router.py

from fastapi import APIRouter, Query
from domain.route_model import PlanRequest
from delivery.api.controllers.route_controller import plan_trip_controller
from typing import List  

router = APIRouter(prefix="/routes", tags=["routes"])

@router.post("/plan")
async def plan_trip(
    data: PlanRequest, 
    sortby: str = Query(
        "time", 
        description="Sort by 'time', 'price', 'walk', 'transfers'"
    )
):
 
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
