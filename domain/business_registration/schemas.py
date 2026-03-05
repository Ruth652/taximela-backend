from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from domain.enums.business_registration_status import BusinessRegistrationStatus


class BusinessRegistrationFilterDTO(BaseModel):
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
        description="Filter applications submitted after this date (Format: YYYY-MM-DD)"
    )

    to_date: Optional[datetime] = Field(
        None,
        description="Filter applications submitted before this date (Format: YYYY-MM-DD)"
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