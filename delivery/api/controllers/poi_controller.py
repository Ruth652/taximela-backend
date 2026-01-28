from usecases.poi_usecase import PoiUseCase

async def search_poi_controller(query: str, lang: str):
    results = PoiUseCase.search(query, lang)
    return results
