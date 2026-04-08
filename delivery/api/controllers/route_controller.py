from usecases.route_usecase import get_transformed_trip_plan
from usecases.route_service_places_usecase import get_all_routes_service_places
from infrastructure.utils.route_geometry import build_routes_wkt

async def plan_trip_controller(request_data):
    return await get_transformed_trip_plan(request_data)

async def all_routes_service_places_controller(request_data, db):

    routes_wkt = build_routes_wkt(request_data.itineraries)
    #print("WKT:", routes_wkt)

    return get_all_routes_service_places(
        db=db,
        routes_wkt=routes_wkt,
        radius_m=request_data.radius_m,
        limit=request_data.limit,
        cursor_distance=(
            request_data.cursor.distance if request_data.cursor else None
        ),
        cursor_id=(
            request_data.cursor.id if request_data.cursor else None
        ), 
        category_id=request_data.category_id
    )

async def single_route_service_places_controller(request_data, db):

    route_wkt = build_routes_wkt([request_data.itinerary])

    return get_all_routes_service_places(
        db=db,
        routes_wkt=route_wkt,
        radius_m=request_data.radius_m,
        limit=request_data.limit,
        cursor_distance=(
            request_data.cursor.distance if request_data.cursor else None
        ),
        cursor_id=(
            request_data.cursor.id if request_data.cursor else None
        ),
        category_id=request_data.category_id
    )