
from datetime import datetime
import uuid

from pydantic import BaseModel
from sqlalchemy import Column, Integer, Boolean, Enum, ForeignKey, Float, DateTime, String
from sqlalchemy.sql import func
from infrastructure.database import Base
from sqlalchemy.orm import relationship
from uuid import UUID as PyUUID
from sqlalchemy.dialects.postgresql import UUID

class Admin(Base):
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    role = Column(
        Enum(
            "operational_admin",
            "super_admin",
            "business_admin",
            name="role"
        )
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="admins")
    
    
    

class CreateAdminRequest(BaseModel):
    user_id: PyUUID
    role: str
    firebase_uid: str | None = None
    
    
class UpdateAdminRequest(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    full_name: str | None = None  # from the user model
    profile_picture_url: str | None = None # from the user model
    updated_at: datetime | None = None # from the user model
    
    
