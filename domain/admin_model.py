
from datetime import datetime
import uuid
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey

from pydantic import BaseModel
from sqlalchemy.sql import func
from infrastructure.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class AdminRole(str, PyEnum):
    operational_admin = "operational_admin"
    super_admin = "super_admin"
    business_admin = "business_admin"


class Admin(Base):
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    role = Column(SQLEnum(AdminRole, name="role"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="admins")
    businesses = relationship("Business", back_populates="approver")
    gtfs_queue = relationship("GTFS", back_populates="admin")
    
    
    

class CreateAdminRequest(BaseModel):
    full_name: str
    email: str
    role: AdminRole
    
    
class UpdateAdminRequest(BaseModel):
    role: AdminRole | None = None
    is_active: bool | None = None
    full_name: str | None = None  # from the user model
    profile_picture_url: str | None = None # from the user model
    updated_at: datetime | None = None # from the user model
    
    
from typing import List, Optional
from pydantic import BaseModel, validator

class AdminListQuery(BaseModel):
    page: int = 1
    limit: int = 20
    status: Optional[str] = None
    role: Optional[List[str]] = None

    @validator("status")
    def validate_status(cls, v):
        allowed_status = {"active", "suspended"}
        if v is not None and v not in allowed_status:
            raise ValueError(f"Status must be one of {allowed_status}")
        return v

    @validator("role", each_item=True)
    def validate_role(cls, v):
        allowed_roles = {"business_admin", "operational_admin"}
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of {allowed_roles}")
        return v

    @validator("role", pre=True, always=True)
    def default_role(cls, v):
        # Default roles if none provided
        if not v:
            return ["business_admin", "operational_admin"]
        return v