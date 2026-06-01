from repository.fare_repository import FareRepository
from infrastructure.fare_cache import fare_cache
from domain.fare_configurations_model import FareConfiguration, FareUpdateRequests
from fastapi import HTTPException

def _serialize_fare(fare) -> dict:
    return {
        "id": fare.id,
        "base_fare_etb": fare.base_fare_etb,
        "base_distance_km": fare.base_distance_km,
        "step_fare_etb": fare.step_fare_etb,
        "step_distance_km": fare.step_distance_km,
        "is_active": fare.is_active,
        "change_reason": fare.change_reason,
        "created_by": str(fare.created_by) if fare.created_by else None,
        "created_at": fare.created_at.isoformat() if fare.created_at else None,
        "activated_at": fare.activated_at.isoformat() if fare.activated_at else None,
    }


def update_fare_config_usecase(request_data: FareUpdateRequests, db, admin_id):
    repo = FareRepository(db)
    update_dict = request_data.model_dump()
    new_config = repo.update_active_fare(update_dict, admin_id)
    fare_cache.invalidate()
    return _serialize_fare(new_config)


def get_active_fare_usecase(db):
    repo = FareRepository(db)
    fare = repo.get_active_fare()
    if not fare:
        raise HTTPException(status_code=404, detail="No active fare configuration found")
    return _serialize_fare(fare)


def get_fare_history_usecase(db, page: int, limit: int):
    repo = FareRepository(db)
    result = repo.get_fare_history(page, limit)
    return {
        "data": [_serialize_fare(f) for f in result["data"]],
        "total": result["total"],
        "page": result["page"],
        "limit": result["limit"],
    }