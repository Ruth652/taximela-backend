from repository.fare_repository import FareRepository
from infrastructure.fare_cache import fare_cache
from domain.fare_configurations_model import FareUpdateRequests

def update_fare_config_usecase(  request_data: FareUpdateRequests,db, admin_id):
    repo = FareRepository(db)
    
    # Convert Pydantic model to dictionary for the repository
    update_dict = request_data.model_dump()
    
    # database update
    new_config = repo.update_active_fare(update_dict, admin_id)
    
    # Invalidate the cache so the system reflects the new price immediately
    fare_cache.invalidate()
    
    return new_config