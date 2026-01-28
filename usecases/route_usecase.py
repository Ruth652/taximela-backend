from infrastructure.route_services import fetch_route_from_otp

async def get_trip_plan(data):
    result = await fetch_route_from_otp(
        data.from_lat,
        data.from_lon,
        data.to_lat,
        data.to_lon,
        data.date,
        data.time
    )
    return result["data"]["plan"]["itineraries"]



