from sqlalchemy.orm import Session
from sqlalchemy import func, case
from domain.contribution_model import Contribution

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
