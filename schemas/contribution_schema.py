from typing import List

from pydantic import BaseModel
from typing import Literal, Optional
from enum import Enum


class ContributeSchema(BaseModel):
    target_type: Literal["route", "station"]
    action: Literal["new", "edit", "delete"]
    target_id: Optional[int] = None

    # station
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    details: Optional[str] = None

    # route
    start_stop_id: Optional[int] = None
    end_stop_id: Optional[int] = None
    stops: Optional[List[int]] = None

    trust_score_at_submit: Optional[float] = 0.0

class ContributionStatus(str, Enum):
    approved = "approved"
    rejected = "rejected"

class ContributionUpdateSchema(BaseModel):
    status: ContributionStatus