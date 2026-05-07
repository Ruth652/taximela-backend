from fastapi import HTTPException
from repository.auth_identity_repository import AuthIdentityRepository
from usecases.otp_usecase import GTFSService, GetRouteByIdUsecase, GetRouteUsecase, GetStopsByIdUsecase, GetStopsUsecase
from fastapi.responses import StreamingResponse
from sqlalchemy import text
import io
import zipfile
import csv

from repository.otp_repository import OTPRepository

GTFS_STRUCTURE = {
    "agency": ["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang"],
    "stops": ["stop_id", "stop_name", "stop_lat", "stop_lon"],
    "routes": ["route_id", "route_short_name", "route_long_name", "route_type"],
    "trips": ["trip_id", "route_id", "service_id", "trip_headsign", "shape_id", "direction_id"],
    "stop_times": ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"],
    "calendar": ["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"],
    "shapes": ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence", "shape_dist_traveled"],
    "transfers": ["from_stop_id", "to_stop_id", "transfer_type", "min_transfer_time"]
}


async def download_gtfs(db, otp_db, user_id):
    auth_repo = AuthIdentityRepository(db)
    auth_identity = auth_repo.get_super_admin_operational_admin_uuids([user_id])

    if not auth_identity:
        raise HTTPException(status_code=403, detail="User not an admin")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for table, columns in GTFS_STRUCTURE.items():
            result = otp_db.execute(text(f"SELECT * FROM {table}"))
            rows = result.fetchall()
            columns_db = result.keys()

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(columns)

            for row in rows:
                row_dict = dict(zip(columns_db, row))
                writer.writerow([row_dict.get(col, "") for col in columns])

            z.writestr(f"{table}.txt", output.getvalue())

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=gtfs.zip"}
    )

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