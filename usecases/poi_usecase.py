from repository.poi_repository import PoiRepository

class PoiUseCase:

    @staticmethod
    def search(query: str, lang: str):
        # todo - will add business logic here( filtering based on distance ...)
        return PoiRepository.search_places(query, lang)
