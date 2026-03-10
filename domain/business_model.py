# Python built-ins
import uuid
import enum
from typing import Optional

# SQLAlchemy Core + ORM
from sqlalchemy import (
    Column,
    String,
    Float,
    Text,
    TIMESTAMP,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

from pydantic import BaseModel, field_validator


from infrastructure.database import Base
class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    government_id_fan = Column(String, nullable=False)
    government_id_photo_url = Column(Text, nullable=False)
    business_logo = Column(Text, nullable=True)
    license_photo_url = Column(Text, nullable=False)

    status = Column(String, default="active")

    approved_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("business_categories.id"))

    approved_at = Column(TIMESTAMP, server_default=text("now()"))

    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("now()"))

    # Relationships
    owner = relationship("User", back_populates="businesses")
    category = relationship("BusinessCategory", back_populates="businesses")
    approver = relationship("Admin", back_populates="businesses")
    
    
class AdminUpdateBusinessRequest(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None
    @field_validator("status")
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v
    category_id: Optional[uuid.UUID] = None

class BusinessInformation(BaseModel):
    id: uuid.UUID
    name: str
    latitude: float
    longitude: float
    government_id_fan: str
    government_id_photo_url: str
    business_logo: Optional[str]
    license_photo_url: str
    status: Optional[str]
    approved_by: Optional[uuid.UUID]
    approver_name: Optional[str]
    category_id: Optional[uuid.UUID]
    category_name: Optional[str]
    approved_at: Optional[str]
    created_at: str
    updated_at: str
        