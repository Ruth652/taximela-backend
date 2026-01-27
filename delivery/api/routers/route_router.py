# delivery/api/routers/route_router.py

from fastapi import APIRouter
from domain.route_model import PlanRequest
from delivery.api.controllers.route_controller import plan_trip_controller

router = APIRouter(prefix="/api")

@router.post("/plan")
async def plan_trip(data: PlanRequest):
    return await plan_trip_controller(data)
