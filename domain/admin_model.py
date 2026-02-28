
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Boolean, Enum, ForeignKey, Float, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from infrastructure.database import Base
from sqlalchemy.orm import relationship

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
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
    email: str
    role: str
    firebase_uid: str | None = None
    
    
    
