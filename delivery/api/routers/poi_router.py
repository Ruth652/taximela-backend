# delivery/api/routers/poi_router.py
from fastapi import APIRouter, Query
from delivery.api.controllers.poi_controller import search_poi_controller

router = APIRouter(prefix="/api/poi", tags=["POI"])

@router.get("/search")
async def search_poi(
    query: str = Query(..., min_length=1),
    lang: str = Query("en")
):
    return await search_poi_controller(query, lang)
