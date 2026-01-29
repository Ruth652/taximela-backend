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
    
    # Get itineraries from OTP response
    itineraries = result.get("plan", {}).get("itineraries", [])
    
    # Add numberOfTransfers to match expected format
    for itinerary in itineraries:
        itinerary["numberOfTransfers"] = itinerary.get("transfers", 0)
    
    return itineraries



