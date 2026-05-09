from fastapi import APIRouter, BackgroundTasks, Depends, Path, HTTPException
from sqlalchemy.orm import Session

from delivery.api.controllers.otp_controller import (
    download_gtfs,
    get_route,
    get_route_by_id,
    get_stop,
    get_stop_by_id,
)
from infrastructure.db_dependency import get_db
from infrastructure.otp_database import get_otp_db
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token
from repository.auth_identity_repository import AuthIdentityRepository
from usecases.rebuild_graph_usecase import RebuildGraphUseCase

router = APIRouter(
    prefix="/api",
    tags=["Admin - OTP related operations"]
)


@router.get("/admin/otp/download-all")
async def download_all(
    user=Depends(verify_token),
    db: Session = Depends(get_db),
    otp_db: Session = Depends(get_otp_db)
):
    return await download_gtfs(db, otp_db, user_id=user["uid"])


@router.post("/rebuild-graph")
async def rebuild_otp(
    background_tasks: BackgroundTasks,
    user=Depends(verify_token),
    db: Session = Depends(get_db),
    otp_db: Session = Depends(get_otp_db),
):
    auth_repo = AuthIdentityRepository(db)
    auth_identity = auth_repo.get_super_admin_operational_admin_uuids([user["uid"]])

    if not auth_identity:
        raise HTTPException(status_code=403, detail="User not an admin")

    def run():
        usecase = RebuildGraphUseCase(db, otp_db, user["uid"])
        usecase.execute()

    background_tasks.add_task(run)

    return {"message": "Rebuild started"}
    
@router.get("/otp/stops")
async def get_stops(
    user=Depends(verify_token),
    db: Session = Depends(get_db),
    otp_db: Session = Depends(get_otp_db)
):
    return await get_stop(
        db,
        otp_db,
        user_id=user['uid'])
    
@router.get("/otp/stops/{stops_id}")
async def get_stops_by_id(
    stops_id: int = Path(..., description="ID of the stop to retrieve"),
    user=Depends(verify_token),
    db: Session = Depends(get_db),
    otp_db: Session = Depends(get_otp_db)
):
    stops = await get_stop_by_id(
        db,
        otp_db,
        user_id=user['uid'],
        stops_id=stops_id
    )
    if not stops:
        raise HTTPException(status_code=404, detail="Stop not found")
    return stops

@router.get("/otp/routes")
async def get_routes(
    user=Depends(verify_token),
    db: Session = Depends(get_db),
    otp_db: Session = Depends(get_otp_db)
):
    return await get_route(
        db,
        otp_db,
        user_id=user['uid']
    )
    
    
@router.get("/otp/routes/{route_id}")
async def get_routes_by_id(
    route_id: int = Path(..., description="ID of the route to retrieve"),
    user=Depends(verify_token),
    db: Session = Depends(get_db),
    otp_db: Session = Depends(get_otp_db)
):
    routes = await get_route_by_id(
        db,
        otp_db,
        user_id=user['uid'],
        route_id=route_id
    )
    if not routes:
        raise HTTPException(status_code=404, detail="Route not found")
    return routes
        