from sqlalchemy.orm import Session
from domain.contribution_model import Contribute, ContributionStatusEnum
import json

class ContributionRepository:
    def __init__(self, db: Session):  
        self.db = db  

    async def save(self, contribution: Contribute):
        description_str = json.dumps(contribution.description.dict())

        db_obj = Contribute(
            user_id=contribution.user_id,
            target_type=contribution.target_type,
            target_id=contribution.target_id,
            description=description_str,
            trust_score_at_submit=contribution.trust_score_at_submit,
            status=ContributionStatusEnum.pending_review 
        )
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        
        return db_obj
    
    async def update_status(self, contribution_id: int, status: str):
        obj = self.db.query(Contribute).filter(Contribute.id == contribution_id).first()
        
        if not obj:
            raise ValueError("Contribution not found")
        
        obj.status = ContributionStatusEnum(status)
        
        self.db.commit()    
        self.db.refresh(obj)
        return obj