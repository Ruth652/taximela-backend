
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, Float, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from infrastructure.database import Base
from sqlalchemy.ext.declarative import declarative_base
import enum

#Base = declarative_base()

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



class ContributionStatusEnum(str, enum.Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    queued_for_gtfs = "queued_for_gtfs"
    sent_to_gtfs = "sent_to_gtfs"
    
    

class Contribute(Base):
    __tablename__ = "contributions"
    __table_args__ = {"extend_existing": True} 
    
    

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=True)
    description = Column(Text, nullable=False)  
    trust_score_at_submit = Column(Float, nullable=False)
    status = Column(Enum(ContributionStatusEnum), default=ContributionStatusEnum.pending_review, nullable=False)
