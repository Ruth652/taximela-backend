from repository.fare_repository import FareRepository
from infrastructure.fare_cache import fare_cache
from domain.fare_configurations_model import FareConfiguration, FareUpdateRequests
from fastapi import HTTPException

def update_fare_config_usecase(request_data: FareUpdateRequests, db, admin_id):
    repo = FareRepository(db)
    update_dict = request_data.model_dump()
    new_config = repo.update_active_fare(update_dict, admin_id)
    fare_cache.invalidate()
    return new_config

def get_active_fare_usecase(db):
    repo = FareRepository(db)
    fare = repo.get_active_fare()
    if not fare:
        raise HTTPException(status_code=404, detail="No active fare configuration found")
    return fare

def get_fare_history_usecase(db, page: int, limit: int):
    repo = FareRepository(db)
    return repo.get_fare_history(page, limit)