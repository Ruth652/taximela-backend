from sqlalchemy.orm import Session
from domain.fare_configurations_model import FareConfiguration
from datetime import datetime

class FareRepository:
    def __init__(self, db: Session):
        self.db = db

    def update_active_fare(self, update_data: dict, admin_id: str):
        # 1. Deactivate current active fare
        self.db.query(FareConfiguration).filter(
            FareConfiguration.is_active == True
        ).update({"is_active": False})

    
        update_data.pop('id', None) 

        # 3. Create the new configuration
        new_fare = FareConfiguration(
            **update_data,
            created_by=admin_id,
            is_active=True,
            activated_at=datetime.utcnow()
        )
        
        self.db.add(new_fare)
        self.db.commit()
        self.db.refresh(new_fare)
        return new_fare