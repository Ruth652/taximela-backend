from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ContributionGroupResponse(BaseModel):
    group_id: int
    target_type: str
    action: str
    target_id: Optional[int]
    contribution_count: int
    latest_contribution_at: datetime
    reference_stops: Optional[List[int]]

class PaginatedContributionGroupResponse(BaseModel):
    page: int
    limit: int
    total: int
    data: List[ContributionGroupResponse]
    
class ApproveContributionGroupRequest(BaseModel):
    group_id: int
    final_payload: Optional[dict] = None
    