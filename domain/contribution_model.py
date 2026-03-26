from sqlalchemy import Column, Index, Integer, Float, DateTime, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from infrastructure.database import Base
import enum
from sqlalchemy.orm import relationship


class Contribution(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    status = Column(
        Enum(
            "pending_review",
            "approved",
            "rejected",
            name="contribution_status"
        ),
        default="pending_review"
    )

    target_type = Column(String, nullable=False)   
    action = Column(String, nullable=False)        

    target_id = Column(Integer, nullable=True)

    payload = Column(JSONB, nullable=False)        

    trust_score_at_submit = Column(Float, )

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    group_id = Column(Integer, ForeignKey("contribution_groups.id"), nullable=True) 

    user = relationship("User", back_populates="contributions")
    group = relationship("ContributionGroup", back_populates="contributions")



class ContributionStatusEnum(str, enum.Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    