from fastapi import APIRouter
from domain.geocode_model import LocationRequest
from infrastructure.geocoding_service import reverse_geocode

router = APIRouter()

@router.post("/reverse-geocode")
def get_place_name(loc: LocationRequest):
    name = reverse_geocode(loc.lat, loc.lng)
    return {"name": name}
