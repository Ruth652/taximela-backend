from ast import stmt
from unittest import result
from sqlalchemy.orm import Session
from sqlalchemy import func, case, select
from domain.contribution_model import Contribution
from domain.contribution_model import ContributionStatusEnum
import json
from domain import User, Contribution

from sqlalchemy.orm import selectinload



class ContributionRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_contribution_by_id(self, contribution_id):
        return self.db.query(Contribution).filter(Contribution.id == contribution_id).first()

    def get_last_user_contribution(self, user_id, exclude_id=int):
        return (
        self.db.query(Contribution)
        .filter(Contribution.user_id == user_id)
        .filter(Contribution.id != exclude_id)
        .filter(Contribution.status.in_(["approved", "rejected"]))
        .order_by(Contribution.created_at.desc())
        .first()
    )
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
    def save_contribution(self, data, user_id):
        description_str = json.dumps(data.description.dict() if data.description else {})

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        contribution = Contribution(
            user_id=user_id,
            target_type=data.target_type,
            target_id=data.target_id,
            description=description_str,
            status=ContributionStatusEnum.pending_review,
            trust_score_at_submit=user.rating_score if user.rating_score else None
        )
        self.db.add(contribution)
        self.db.commit()
        self.db.refresh(contribution)
        return contribution
    

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
    async def get_contribution_stats_for_all_users(self):
        result = self.db.query(
        func.count(Contribution.id).label("total"),
        func.coalesce(
            func.sum(case((Contribution.status == "pending_review", 1), else_=0)), 0
        ).label("pending"),
        func.coalesce(
            func.sum(case((Contribution.status == "approved", 1), else_=0)), 0
        ).label("approved"),
        func.coalesce(
            func.sum(case((Contribution.status == "rejected", 1), else_=0)), 0
        ).label("rejected"),
    ).all()

        return [
            {
                "total": r.total,
                "pending": r.pending,
                "approved": r.approved,
                "rejected": r.rejected,
            }
            for r in result
        ]
            
    async def get_contributions_by_status(self, status: str, page: int, limit: int):
        total_count = self.db.query(func.count(Contribution.id)) \
            .filter(Contribution.status == status) \
            .scalar()

        stmt = (
            select(Contribution)
            .where(Contribution.status == status)
            .order_by(Contribution.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .options(selectinload(Contribution.user))
        )

        result = self.db.execute(stmt)
        contributions = result.scalars().all()

        contributions_data = [
            {
                "id": str(c.id),
                "user_id": str(c.user_id),
                "full_name": c.user.full_name if c.user else "Unknown",
                "target_type": c.target_type,
                "action": (json.loads(c.description).get("action") if c.description else None),
                "name": (json.loads(c.description).get("name") if c.description else None),
                "lat": (json.loads(c.description).get("lat") if c.description else None),
                "lon": (json.loads(c.description).get("lon") if c.description else None),
                "status": c.status,
                "trust_score": c.trust_score_at_submit,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in contributions
        ]

        return {
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "contributions": contributions_data
        }
    
    
    async def update_status(self, contribution_id: int, status: str):
        obj = self.db.query(Contribution).filter(Contribution.id == contribution_id).first()
        
        if not obj:
            raise None
        
        obj.status = ContributionStatusEnum(status)
        
        self.db.flush()
        self.db.refresh(obj)
        return obj
    
   

