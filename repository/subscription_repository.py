import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from domain.subscription_model import BusinessSubscription, SubscriptionStatus
from domain.business_model import Business


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_pending(self, business_id: uuid.UUID, amount_etb: float, tx_ref: str, checkout_url: str) -> BusinessSubscription:
        sub = BusinessSubscription(
            business_id=business_id,
            status=SubscriptionStatus.pending,
            amount_etb=amount_etb,
            chapa_tx_ref=tx_ref,
            chapa_checkout_url=checkout_url,
        )
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def get_by_tx_ref(self, tx_ref: str) -> BusinessSubscription | None:
        return self.db.query(BusinessSubscription).filter(
            BusinessSubscription.chapa_tx_ref == tx_ref
        ).first()

    def get_active_by_business(self, business_id: uuid.UUID) -> BusinessSubscription | None:
        return self.db.query(BusinessSubscription).filter(
            BusinessSubscription.business_id == business_id,
            BusinessSubscription.status == SubscriptionStatus.active,
        ).first()

    def get_history_by_business(self, business_id: uuid.UUID, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        total = self.db.query(BusinessSubscription).filter(
            BusinessSubscription.business_id == business_id
        ).count()
        records = (
            self.db.query(BusinessSubscription)
            .filter(BusinessSubscription.business_id == business_id)
            .order_by(BusinessSubscription.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return {"data": records, "total": total, "page": page, "limit": limit}

    def activate(self, sub: BusinessSubscription, duration_days: int = 30) -> BusinessSubscription:
        """Activates a subscription and marks the business as featured."""
        now = datetime.utcnow()
        sub.status = SubscriptionStatus.active
        sub.started_at = now
        sub.expires_at = now + timedelta(days=duration_days)

        # Mark business as featured
        business = self.db.query(Business).filter(Business.id == sub.business_id).first()
        if business:
            business.is_featured = True
            business.featured_until = sub.expires_at

        self.db.commit()
        self.db.refresh(sub)
        return sub

    def mark_failed(self, sub: BusinessSubscription) -> BusinessSubscription:
        sub.status = SubscriptionStatus.failed
        self.db.commit()
        return sub

    def expire_stale_subscriptions(self):
        """
        Called by the scheduler — marks expired subscriptions and removes featured status.
        """
        now = datetime.utcnow()
        expired_subs = self.db.query(BusinessSubscription).filter(
            BusinessSubscription.status == SubscriptionStatus.active,
            BusinessSubscription.expires_at <= now,
        ).all()

        for sub in expired_subs:
            sub.status = SubscriptionStatus.expired
            business = self.db.query(Business).filter(Business.id == sub.business_id).first()
            if business:
                business.is_featured = False
                business.featured_until = None

        if expired_subs:
            self.db.commit()

        return len(expired_subs)

    def list_all(self, page: int = 1, limit: int = 20, status: str = None):
        offset = (page - 1) * limit
        query = self.db.query(BusinessSubscription)
        if status:
            query = query.filter(BusinessSubscription.status == status)
        total = query.count()
        records = query.order_by(BusinessSubscription.created_at.desc()).offset(offset).limit(limit).all()
        return {"data": records, "total": total, "page": page, "limit": limit}
