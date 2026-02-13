from sqlalchemy.orm import Session
from sqlalchemy import func, case
from domain.contribution_model import Contribution
from domain.contribution_model import Contribute, ContributionStatusEnum
import json


class ContributionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_contribution_stats_by_user_uuid(self, user_id):
        result = self.db.query(
            func.count(Contribution.id).label("total"),

            func.coalesce(
                func.sum(
                    case(
                        (Contribution.status == "pending_review", 1),
                        else_=0
                    )
                ), 0
            ).label("pending"),

            func.coalesce(
                func.sum(
                    case(
                        (Contribution.status == "approved", 1),
                        else_=0
                    )
                ), 0
            ).label("approved"),

            func.coalesce(
                func.sum(
                    case(
                        (Contribution.status == "rejected", 1),
                        else_=0
                    )
                ), 0
            ).label("rejected"),
        ).filter(
            Contribution.user_id == user_id
        ).one()

        return {
            "total": result.total,
            "pending": result.pending,
            "approved": result.approved,
            "rejected": result.rejected,
        }

    def get_contributions_by_user_uuid(self, user_id, page:int, limit:int):
        contributions = self.db.query(Contribution).filter(Contribution.user_id == user_id).order_by(Contribution.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

        return [
            {
                "id": c.id,
                "report_type": c.target_type,  
                "description": c.description,
                "status": c.status,
                "created_at": c.created_at,
                "updated_at":c.updated_at,
            }
            for c in contributions
        ]

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

