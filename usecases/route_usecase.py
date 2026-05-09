from infrastructure.route_services import fetch_route_from_otp
from usecases.route_transformer import transform_otp_itinerary
from infrastructure.fare_cache import fare_cache
from sqlalchemy.orm import Session
from fastapi import HTTPException

async def get_trip_plan(data):
    result = await fetch_route_from_otp(
        data.from_lat,
        data.from_lon,
        data.to_lat,
        data.to_lon
    )
    # print("result:", result)

    if "data" not in result:
        raise HTTPException(
            status_code=502,
            detail=f"Routing service error: {result.get('error', 'Unknown error 1')}"
        )
    if "plan" not in result["data"]:
        raise HTTPException(
            status_code=502,
            detail=f"Routing service error: {result.get('error', 'Unknown error 2')}"
        )

    return result["data"]["plan"].get("itineraries", [])

async def get_transformed_trip_plan(data, db: Session):
    """
    Retrived the raw plan, fetches the active fare configuration from cache, 
    Returns frontend-ready response
    """
    raw_itineraries = await get_trip_plan(data)

    # Get the active fare configuration ( via singleton cache)
    active_fare = fare_cache.get_fare(db)

    if not active_fare:
        # Fallback error if the admin hasn't set up any fares yet
        raise HTTPException(
            status_code=500,
            detail="Pricing configuration not found. Please contact administrator."
        )        
    transformed = []
    for itinerary in raw_itineraries:
        transformed.append(transform_otp_itinerary(itinerary, active_fare))

    return transformed


