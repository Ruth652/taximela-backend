from pydantic import BaseModel

class PoiResponse(BaseModel):
    name: str
    lat: float
    lon: float
    category: str | None = None

