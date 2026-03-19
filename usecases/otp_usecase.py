from fastapi.responses import StreamingResponse
from sqlalchemy import text
import io, zipfile, csv

from repository.otp_repository import OTPRepository

GTFS_STRUCTURE = {
    "agency": ["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang"],
    "stops": ["stop_id", "stop_name", "stop_lat", "stop_lon"],
    "routes": ["route_id", "route_short_name", "route_long_name", "route_type"],
    "trips": ["trip_id", "route_id", "service_id","trip_headsign","shape_id", "direction_id"],
    "stop_times": ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"],
    "calendar": ["service_id", "monday","tuesday","wednesday","thursday","friday","saturday","sunday","start_date","end_date"],
    "shapes": ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence", "shape_dist_traveled"],
    "transfers": ["from_stop_id", "to_stop_id", "transfer_type", "min_transfer_time"]
}

async def DownloadOTPUsecase(otp_db):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as z:
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
    
    
async def GetStopsUsecase(otp_db):
    otp_repo = OTPRepository(otp_db)
    return otp_repo.get_stops()

async def GetStopsByIdUsecase(otp_db, stops_id: int):
    otp_repo = OTPRepository(otp_db)
    return otp_repo.get_stops_by_id(stops_id)

async def GetRouteUsecase(otp_db):
    otp_repo = OTPRepository(otp_db)
    return otp_repo.get_routes()

async def GetRouteByIdUsecase(otp_db, route_id: int):
    otp_repo = OTPRepository(otp_db)
    return otp_repo.get_routes_by_id(route_id)

   