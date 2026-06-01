import uuid
import enum
from sqlalchemy import Column, String, Float, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from infrastructure.database import Base


class SubscriptionStatus(str, enum.Enum):
    pending = "pending"       # payment initiated, not yet confirmed
    active = "active"         # payment confirmed, business is featured
    expired = "expired"       # subscription period ended
    cancelled = "cancelled"   # manually cancelled
    failed = "failed"         # payment failed


class BusinessSubscription(Base):
    __tablename__ = "business_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)

    status = Column(
        Enum(SubscriptionStatus, name="subscription_status"),
        default=SubscriptionStatus.pending,
        nullable=False
    )

    amount_etb = Column(Float, nullable=False)
    chapa_tx_ref = Column(String, unique=True, nullable=False)  # our unique tx ID
    chapa_checkout_url = Column(String, nullable=True)          # Chapa redirect URL

    started_at = Column(TIMESTAMP, nullable=True)
    expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
