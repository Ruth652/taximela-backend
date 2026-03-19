from fastapi import HTTPException
from repository.auth_identity_repository import AuthIdentityRepository
from usecases.otp_usecase import DownloadOTPUsecase, GetRouteByIdUsecase, GetRouteUsecase, GetStopsByIdUsecase, GetStopsUsecase

async def download_gtfs(db, otp_db, user_id):
    auth_repo = AuthIdentityRepository(db)
    auth_identity = auth_repo.get_super_admin_operational_admin_uuids([user_id])

    if not auth_identity:
        raise HTTPException(status_code=404, detail="User not an admin")

    return await DownloadOTPUsecase(otp_db)

async def get_stop(db, otp_db, user_id):
    auth_repo = AuthIdentityRepository(db)
    auth_identity = auth_repo.get_user_uuid_by_firebase_uid(user_id)

    if not auth_identity:
        raise HTTPException(status_code=404, detail="User not found")

    return await GetStopsUsecase(otp_db)

async def get_stop_by_id(db, otp_db, user_id, stops_id):
    auth_repo = AuthIdentityRepository(db)
    auth_identity = auth_repo.get_user_uuid_by_firebase_uid(user_id)
    if not auth_identity:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await GetStopsByIdUsecase(otp_db, stops_id)

async def get_route(db, otp_db, user_id):
    auth_repo = AuthIdentityRepository(db)
    auth_identity = auth_repo.get_user_uuid_by_firebase_uid(user_id)

    if not auth_identity:
        raise HTTPException(status_code=404, detail="User not found")

    return await GetRouteUsecase(otp_db)

async def get_route_by_id(db, otp_db, user_id, route_id):
    auth_repo = AuthIdentityRepository(db)
    auth_identity = auth_repo.get_user_uuid_by_firebase_uid(user_id)
    if not auth_identity:
        raise HTTPException(status_code=404, detail="User not found")
    
    return await GetRouteByIdUsecase(otp_db, route_id)