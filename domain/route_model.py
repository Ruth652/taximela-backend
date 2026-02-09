from pydantic import BaseModel

class PlanRequest(BaseModel):
    from_lat: float
    from_lon: float
    to_lat: float
    to_lon: float
    # date: str   # "YYYY-MM-DD"
    # time: str   # "HH:MM:SS"
