from pydantic import BaseModel

class LocationRequest(BaseModel):
    lat: float
    lng: float
