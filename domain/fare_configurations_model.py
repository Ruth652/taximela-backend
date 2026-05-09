import uuid
from datetime import datetime
from sqlalchemy import Column, Float, DateTime, Boolean, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from infrastructure.database import Base
from pydantic import BaseModel, Field
from typing import Optional


class FareConfiguration(Base):
    __tablename__ = "fare_configurations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Fare Logic
    base_fare_etb = Column(Float, nullable=False)        # e.g., 10.0
    base_distance_km = Column(Float, nullable=False)     # e.g., 2.5
    step_fare_etb = Column(Float, nullable=False)        # e.g., 5.0
    step_distance_km = Column(Float, nullable=False)     # e.g., 2.5
    
    # Status & Audit
    is_active = Column(Boolean, default=False, nullable=False)
    change_reason = Column(Text, nullable=True)          
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"))
    created_at = Column(DateTime, server_default=func.now())
    activated_at = Column(DateTime, nullable=True)

class FareUpdateRequests(BaseModel):

    base_fare_etb: float = Field(..., gt=0, description="The new base fare in ETB")
    
    # optional | TaxiMela standards if not provided
    base_distance_km: Optional[float] = Field(2.5, gt=0)
    step_fare_etb: Optional[float] = Field(5.0, gt=0)
    step_distance_km: Optional[float] = Field(2.5, gt=0)
    change_reason: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True