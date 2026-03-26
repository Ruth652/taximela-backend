from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, case, select
from domain.contribution_group_model import ContributionGroup
from domain.contribution_model import Contribution, ContributionStatusEnum
from domain import User
import json


class ContributionRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Get single contribution ---
    def get_contribution_by_id(self, contribution_id: int):
        return self.db.query(Contribution).filter(Contribution.id == contribution_id).first()

    # --- Get last user contribution, excluding one ---
    def get_last_user_contribution(self, user_id: int, exclude_id: int = None):
        query = self.db.query(Contribution).filter(Contribution.user_id == user_id)
        if exclude_id:
            query = query.filter(Contribution.id != exclude_id)
        return query.filter(Contribution.status.in_(["approved", "rejected"])) \
                    .order_by(Contribution.created_at.desc()) \
                    .first()

    # --- Contribution stats per user ---
    def get_contribution_stats_by_user_uuid(self, user_id: int):
        result = self.db.query(
            func.count(Contribution.id).label("total"),
            func.coalesce(func.sum(case((Contribution.status == "pending_review", 1), else_=0)), 0).label("pending"),
            func.coalesce(func.sum(case((Contribution.status == "approved", 1), else_=0)), 0).label("approved"),
            func.coalesce(func.sum(case((Contribution.status == "rejected", 1), else_=0)), 0).label("rejected"),
        ).filter(Contribution.user_id == user_id).one()

        return {
            "total": result.total,
            "pending": result.pending,
            "approved": result.approved,
            "rejected": result.rejected,
        }

    # --- Create a new contribution ---
    def create_contribution(self, data, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        db_obj = Contribution(
            target_type=data.target_type,
            action=data.action,
            target_id=data.target_id,
            payload=data.model_dump(),  # JSONB payload
            user_id=user_id,
            status="pending_review"
        )

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    # --- Paginated contributions by user ---
    def get_contributions_by_user_uuid(self, user_id: int, page: int, limit: int):
        base_query = self.db.query(Contribution).filter(Contribution.user_id == user_id)
        total_count = base_query.count()

        contributions = (
            base_query
            .order_by(Contribution.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        data = [
            {
                "id": c.id,
                "target_type": c.target_type,
                "action": c.action,
                "target_id": c.target_id,
                "payload": c.payload,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in contributions
        ]

        return {
            "data": data,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }

    # --- Stats for all users ---
    async def get_contribution_stats_for_all_users(self):
        result = self.db.query(
            func.count(Contribution.id).label("total"),
            func.coalesce(func.sum(case((Contribution.status == "pending_review", 1), else_=0)), 0).label("pending"),
            func.coalesce(func.sum(case((Contribution.status == "approved", 1), else_=0)), 0).label("approved"),
            func.coalesce(func.sum(case((Contribution.status == "rejected", 1), else_=0)), 0).label("rejected"),
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

    # --- Paginated contributions by status ---
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
                "action": c.action,
                "payload": c.payload,
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

    # --- Update contribution status ---
    async def update_status(self, contribution_id: int, status: str):
        obj = self.db.query(Contribution).filter(Contribution.id == contribution_id).first()
        if not obj:
            raise ValueError("Contribution not found")

        obj.status = ContributionStatusEnum(status)
        self.db.flush()
        self.db.refresh(obj)
        return obj
    
    def find_station_group(self, contribution_payload: dict, action: str):
        lat = contribution_payload.get("lat")
        lon = contribution_payload.get("lon")
        target_id = contribution_payload.get("target_id") 

        query = (
            self.db.query(ContributionGroup)
            .filter(ContributionGroup.target_type == "station")
            .filter(ContributionGroup.action == action)
        )

        if action == "delete" and target_id:
            group = query.filter(ContributionGroup.target_id == target_id).first()
            return group

        if action == "edit":
           if target_id:
            group = query.filter(ContributionGroup.target_id == target_id).first()
            if group:
                if lat and lon and group.reference_lat and group.reference_lon:
                    if (lat - group.reference_lat)**2 + (lon - group.reference_lon)**2 <= 0.000025:
                        return group
                    else:
                        return None  # same id but far away → new group
                return group
        # No target_id → cannot group
        return None
    
    def create_contribution_group(self, target_type: str, action: str, reference_lat: float = None, reference_lon: float = None, reference_stops: list = None, target_id: int = None):
        group = ContributionGroup(
            target_type=target_type,
            action=action,
            target_id=target_id,
            reference_lat=reference_lat,
            reference_lon=reference_lon,
            reference_stops=reference_stops,
            
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group
    
    def find_route_group(self, contribution_payload: dict, action: str, similarity_threshold: float = 0.7):
        target_id = contribution_payload.get("target_id")
        stops = contribution_payload.get("stops", [])

        if action == "new" or not target_id:
            return None
        
        query = (
                    self.db.query(ContributionGroup)
                    .filter(ContributionGroup.target_type == "route")
                    .filter(ContributionGroup.action == action)
                )
        
        if action == "delete" and target_id:
            group = query.filter(ContributionGroup.target_id == target_id).first()
            return group

        # query by target_id instead of primary key
        if action == "edit":
            if not stops:
                return None

            group = query.filter(ContributionGroup.target_id == target_id).first()

            if not group:
                return None

            reference_stops = getattr(group, "reference_stops", [])
            intersection = len(set(reference_stops) & set(stops))
            max_len = max(len(reference_stops), len(stops))
            similarity = intersection / max_len if max_len > 0 else 0

            if similarity >= similarity_threshold:
                return group

        return None