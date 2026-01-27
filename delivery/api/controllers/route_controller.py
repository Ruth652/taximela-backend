from usecases.route_usecase import get_trip_plan

async def plan_trip_controller(request_data):
    return await get_trip_plan(request_data)
