from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from infrastructure.database import Base

class Contribution(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(
        Enum(
            "pending_review",
            "approved",
            "queued_for_gtfs",
            "sent_to_gtfs",
            "rejected",
            name="contribution_status"
        )
    )
    trust_score_at_submit = Column(Float)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
