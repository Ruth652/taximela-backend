from sqlalchemy import Column, String, Text, Integer, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum


Base = declarative_base()

class ContributionStatusEnum(str, enum.Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    queued_for_gtfs = "queued_for_gtfs"
    sent_to_gtfs = "sent_to_gtfs"
    
    

class Contribute(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=True)
    description = Column(Text, nullable=False)  
    trust_score_at_submit = Column(Float, nullable=False)
    status = Column(Enum(ContributionStatusEnum), default=ContributionStatusEnum.pending_review, nullable=False)
