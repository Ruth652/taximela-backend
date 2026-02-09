from infrastructure.route_services import fetch_route_from_otp
from usecases.route_transformer import transform_otp_itinerary

async def get_trip_plan(data):
    result = await fetch_route_from_otp(
        data.from_lat,
        data.from_lon,
        data.to_lat,
        data.to_lon
    )
    if "data" not in result:
        raise Exception(f"Unexpected API response: {result}")

    if "plan" not in result["data"]:
        raise Exception(f"No plan in response: {result}")

    return result["data"]["plan"].get("itineraries", [])

async def get_transformed_trip_plan(data):
    """
    Returns frontend-ready response
    """
    raw_itineraries = await get_trip_plan(data)

    transformed = []
    for itinerary in raw_itineraries:
        transformed.append(transform_otp_itinerary(itinerary))

    return transformed


