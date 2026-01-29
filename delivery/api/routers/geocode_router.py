from fastapi import APIRouter, Query
from domain.geocode_model import LocationRequest
from infrastructure.geocoding_service import reverse_geocode

router = APIRouter()

@router.post("/reverse-geocode")
def get_place_name(loc: LocationRequest, lang: str = Query("en", description="Language: 'en' or 'am'")):
    name = reverse_geocode(loc.lat, loc.lng, lang)
    return {"name": name}
