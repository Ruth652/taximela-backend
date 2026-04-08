# repositories/contribution_group_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from domain.contribution_model import Contribution
from domain.contribution_group_model import ContributionGroup
from schemas.contribution_schema import ContributionStatus


class ContributionGroupRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_paginated_groups(
        self,
        page: int = 1,
        limit: int = 10,
        target_type: str = None,
        action: str = None,
    ):
        offset = (page - 1) * limit

        query = (
            self.db.query(
                ContributionGroup.id.label("group_id"),
                ContributionGroup.target_type,
                ContributionGroup.action,
                ContributionGroup.target_id,
                ContributionGroup.reference_stops,
                func.count(Contribution.id).label("contribution_count"),
                func.max(Contribution.created_at).label("latest_contribution_at"),
            )
            .join(Contribution, Contribution.group_id == ContributionGroup.id)
            .group_by(ContributionGroup.id)
        )

        # 🔹 Optional filters
        if target_type:
            query = query.filter(ContributionGroup.target_type == target_type)

        if action:
            query = query.filter(ContributionGroup.action == action)

        # 🔹 Total count (important: same filters)
        total_query = (
            self.db.query(func.count(func.distinct(ContributionGroup.id)))
            .join(Contribution, Contribution.group_id == ContributionGroup.id)
        )

        if target_type:
            total_query = total_query.filter(ContributionGroup.target_type == target_type)

        if action:
            total_query = total_query.filter(ContributionGroup.action == action)

        total = total_query.scalar()

        results = (
            query
            .order_by(desc(func.max(Contribution.created_at)))
            .offset(offset)
            .limit(limit)
            .all()
        )

        return total, results
    
    def get_group_by_id(self, group_id: int):
        group = (
            self.db.query(ContributionGroup)
            .filter(ContributionGroup.id == group_id)
            .first()
        )
        return group
    
    
    
    