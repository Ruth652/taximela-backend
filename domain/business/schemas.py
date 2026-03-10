from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field,field_validator
from uuid import UUID
from enum import Enum


class BusinessRegistrationStatus(str, Enum):
    active = "active"
    suspended = "suspended"

class BusinessFilterDTO(BaseModel):
    status: Optional[BusinessRegistrationStatus] = Field(
        None,
        description="Filter by application status"
    )

    user_id: Optional[UUID] = Field(
        None,
        description="Filter by user id"
    )
 
    from_date: Optional[datetime] = Field(
        None,
        description="Filter business's created after this date (Format: YYYY-MM-DD)"
    )

    to_date: Optional[datetime] = Field(
        None,
        description="Filter business's created before this date (Format: YYYY-MM-DD)"
    )

    search: Optional[str] = Field(
        None,
        description="Search by category"
    )

    page: int = Field(
        1,
        ge=1,
        description="Page number"
    )

    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Items per page"
    )

    def validate_dates(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValueError(
                    "from_date cannot be greater than to_date"
                )
