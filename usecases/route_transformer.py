
from polyline import decode  
from geopy.distance import geodesic
WALK_SPEED_MPS = 1.3    # meters per second
TAXI_SPEED_KMH = 30     # km/h
PRICE_PER_2_5KM = 10    # birr

def transform_otp_itinerary(otp_itinerary):
    total_walk_m = 0
    taxi_distance_km = 0
    total_trip_time_min = 0
    taxi_count = 0
    trip_details = []

    for leg in otp_itinerary["legs"]:
        # Get leg distance (in meters if available, fallback to 0)
        distance_m = leg.get("distance", 0)
        distance_km = distance_m / 1000

        if leg["mode"] == "WALK":
            # Duration in minutes: distance / speed
            duration_min = (distance_m / WALK_SPEED_MPS) / 60
            total_walk_m += distance_m
            mapped_mode = "walk"

        elif leg["mode"] == "BUS":
            # Duration in minutes: distance / speed
            duration_min = (distance_km / TAXI_SPEED_KMH) * 60
            taxi_distance_km += distance_km
            taxi_count += 1
            mapped_mode = "taxi"

        else:
            continue

        total_trip_time_min += duration_min

        trip_details.append({
            "mode": mapped_mode,
            "from": leg["from"]["name"],
            "to": leg["to"]["name"],
            "estimatedDuration": round(duration_min, 1),
            "estimatedDistance": round(distance_km, 2),
            "encryptedGeolocation": leg["legGeometry"]["points"]
        })

    transfers = max(taxi_count - 1, 0)
    total_trip_distance = (total_walk_m / 1000) + taxi_distance_km

    # Pricing (10 birr per 2.5 km)
    base_cost = (taxi_distance_km / 2.5) * PRICE_PER_2_5KM
    min_cost = round_up_to_5(base_cost)
    max_cost = round_up_to_5(base_cost * 1.1)

    return {
        "totalTripTime": round(total_trip_time_min, 1),
        "totalTripDistance": round(total_trip_distance, 2),
        "totalWalkDistance": round(total_walk_m / 1000, 2),
        "totalOnTaxiDistance": round(taxi_distance_km, 2),
        "taxi_count": taxi_count,
        "transfers": transfers,
        "costEstimation": {
            "minimumCost": round(min_cost, 2),
            "maximumCost": round(max_cost, 2)
        },
        "tripDetail": trip_details
    }

import math
def round_up_to_5(x):
    return math.ceil(x/5) * 5



# from polyline import decode  
# from geopy.distance import geodesic
# import math

# # Speeds
# WALK_SPEED_MPS = 1.3    # 1.3 m/s ~ 4.68 km/h
# TAXI_SPEED_KMH = 30     # km/h

# # Pricing
# PRICE_PER_2_5KM = 10    # birr per 2.5 km

# def round_up_to_5(x):
#     return math.ceil(x / 5) * 5

# def transform_otp_itinerary(otp_itinerary):
#     total_walk_m = 0
#     taxi_distance_km = 0
#     total_trip_time_min = 0
#     taxi_count = 0
#     trip_details = []

#     for leg in otp_itinerary["legs"]:
#         distance_m = leg.get("distance", 0)
#         distance_km = distance_m / 1000

#         if leg["mode"] == "WALK":
#             # Duration in minutes
#             duration_min = (distance_m / WALK_SPEED_MPS) / 60
#             total_walk_m += distance_m
#             mapped_mode = "walk"

#         elif leg["mode"] == "TRANSIT":
#             # Treat TRANSIT as your taxi route
#             duration_min = (distance_km / TAXI_SPEED_KMH) * 60
#             taxi_distance_km += distance_km
#             taxi_count += 1
#             mapped_mode = "taxi"

#         else:
#             # Ignore other modes
#             continue

#         total_trip_time_min += duration_min

#         # Add each leg detail
#         trip_details.append({
#             "mode": mapped_mode,
#             "From": leg["from"]["name"],
#             "To": leg["to"]["name"],
#             "estimatedDuration": round(duration_min, 1),
#             "estimatedDistance": round(distance_km, 2),
#             "encryptedGeolocation": leg["legGeometry"]["points"]
#         })

#     transfers = max(taxi_count - 1, 0)
#     total_trip_distance = (total_walk_m / 1000) + taxi_distance_km

#     # Pricing: 10 birr per 2.5 km of taxi
#     base_cost = (taxi_distance_km / 2.5) * PRICE_PER_2_5KM
#     min_cost = round_up_to_5(base_cost)
#     max_cost = round_up_to_5(base_cost * 1.1)

#     return {
#         "totalTripTime": round(total_trip_time_min, 1),
#         "totalTripDistance": round(total_trip_distance, 2),
#         "totalWalkDistance": round(total_walk_m / 1000, 2),
#         "totalOnTaxiDistance": round(taxi_distance_km, 2),
#         "taxi_count": taxi_count,
#         "transfers": transfers,
#         "costEstimation": {
#             "minimumCost": round(min_cost, 2),
#             "maximumCost": round(max_cost, 2)
#         },
#         "tripDetail": trip_details
#     }