from sqlalchemy.orm import Session
from usecases.fare_usecase import update_fare_config_usecase, get_active_fare_usecase, get_fare_history_usecase

async def update_fare_config_controller(request_data, db: Session, admin_id: str):
    return update_fare_config_usecase(request_data, db, admin_id)

async def get_active_fare_controller(db: Session):
    return get_active_fare_usecase(db)

async def get_fare_history_controller(db: Session, page: int, limit: int):
    return get_fare_history_usecase(db, page, limit)