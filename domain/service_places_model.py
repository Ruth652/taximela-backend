from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class NearbyPlacesCursor(BaseModel):
    distance: float
    id: str
class TripDetailItem(BaseModel):
    encryptedGeolocation: str

class Itinerary(BaseModel):
    tripDetail: List[TripDetailItem]

class AllRoutesServicePlacesRequest(BaseModel):
    itineraries: List[Itinerary]
    cursor: Optional[NearbyPlacesCursor] = None
    limit: int = Field(default=10, ge=1, le=50)
    radius_m: int = Field(default=300, ge=50, le=5000)
    category_id: Optional[str] = None

class SingleRouteServicePlacesRequest(BaseModel):
    itinerary: Itinerary
    cursor: Optional[NearbyPlacesCursor] = None
    limit: int = Field(default=10, ge=1, le=50)
    radius_m: int = Field(default=300, ge=50, le=5000)
    category_id: Optional[str] = None