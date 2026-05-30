import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from infrastructure.database import Base


class NotificationPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class NotificationType(str, enum.Enum):
    contribution_new = "contribution_new"
    contribution_approved = "contribution_approved"
    contribution_rejected = "contribution_rejected"
    business_application = "business_application"
    business_approved = "business_approved"
    business_rejected = "business_rejected"
    user_suspended = "user_suspended"
    admin_added = "admin_added"
    admin_removed = "admin_removed"
    system_alert = "system_alert"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Who receives this notification
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=False)

    # Content
    type = Column(Enum(NotificationType, name="notification_type"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(
        Enum(NotificationPriority, name="notification_priority"),
        default=NotificationPriority.medium,
        nullable=False
    )
    action_url = Column(String, nullable=True)

    # State
    read = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
