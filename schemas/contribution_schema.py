from uuid import UUID
from pydantic import BaseModel
from typing import Literal, Optional, Dict, Any
from enum import Enum

class DescriptionSchema(BaseModel):
    action: Optional[str] = None
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    details: Optional[str] = None

class ContributeSchema(BaseModel):
    target_type: Literal["route", "station"]
    target_id: Optional[str] = None
    description: DescriptionSchema
    trust_score_at_submit: Optional[float] = None
    

class ContributionStatus(str, Enum):
    approved = "approved"
    rejected = "rejected"

class ContributionUpdateSchema(BaseModel):
    status: ContributionStatus