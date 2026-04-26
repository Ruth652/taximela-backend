from sqlalchemy import JSON, Column, Float, Index, Integer, String, func, DateTime

from infrastructure.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB


class ContributionGroup(Base):
    __tablename__ = "contribution_groups"

    id = Column(Integer, primary_key=True)

    target_type = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target_id = Column(Integer, nullable=True)  

    reference_lat = Column(Float, nullable=True)
    reference_lon = Column(Float, nullable=True)
    reference_stops = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    
    contributions = relationship("Contribution", back_populates="group")
    gtfs_queue = relationship("GTFS", back_populates="group")

 
    