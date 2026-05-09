
from polyline import decode  
from geopy.distance import geodesic
WALK_SPEED_MPS = 1.3    # meters per second
TAXI_SPEED_KMH = 30     # km/h
PRICE_PER_2_5KM = 10    # birr

def transform_otp_itinerary(otp_itinerary, fare_config):
    total_walk_m = 0
    taxi_distance_km = 0
    total_trip_time_min = 0
    taxi_count = 0
    trip_details = []
    total_actual_fare = 0
    

    for leg in otp_itinerary["legs"]:
        distance_m = leg.get("distance", 0)
        distance_km = distance_m / 1000
        leg_fare = 0

        if leg["mode"] == "WALK":
         
            duration_min = (distance_m / WALK_SPEED_MPS) / 60
            total_walk_m += distance_m
            mapped_mode = "walk"

        elif leg["mode"] == "BUS":
        
            duration_min = (distance_km / TAXI_SPEED_KMH) * 60
            taxi_distance_km += distance_km
            taxi_count += 1
            mapped_mode = "taxi"
            leg_fare = calculate_cost(distance_km, fare_config)
            total_actual_fare += leg_fare

        else:
            continue

        total_trip_time_min += duration_min

        trip_details.append({
            "mode": mapped_mode,
            "from": leg["from"]["name"],
            "to": leg["to"]["name"],
            "estimatedDuration": round(duration_min, 1),
            "estimatedDistance": round(distance_km, 2),
            "estimatedFare": float(leg_fare),
            "encryptedGeolocation": leg["legGeometry"]["points"]
        })

    transfers = max(taxi_count - 1, 0)
    total_trip_distance = (total_walk_m / 1000) + taxi_distance_km

    return {
        "totalTripTime": round(total_trip_time_min, 1),
        "totalTripDistance": round(total_trip_distance, 2),
        "totalWalkDistance": round(total_walk_m / 1000, 2),
        "totalOnTaxiDistance": round(taxi_distance_km, 2),
        "taxi_count": taxi_count,
        "transfers": transfers,
        "costEstimation": {
            "minimumCost": total_actual_fare,
            "maximumCost": total_actual_fare + 10,
        },
        "tripDetail": trip_details
    }
import math

def calculate_cost(taxi_distance_km, fare_config):
    if taxi_distance_km > 0:
        return fare_config.base_fare_etb + math.ceil(
            max(0, taxi_distance_km - fare_config.base_distance_km) / fare_config.step_distance_km
        ) * fare_config.step_fare_etb
    else:
        return 0


    # if taxi_distance_km > 0:
    #     return 10 + math.ceil(max(0, taxi_distance_km - 2.5) / 2.5) * 5
    # else:
    #     return 0