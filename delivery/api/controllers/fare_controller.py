from sqlalchemy.orm import Session
from usecases.fare_usecase import update_fare_config_usecase

async def update_fare_config_controller(request_data, db: Session, admin_id: str):
    """
    Orchestrates the fare update process.
    """
    # We call the usecase and return the result
    return update_fare_config_usecase( request_data, db, admin_id)