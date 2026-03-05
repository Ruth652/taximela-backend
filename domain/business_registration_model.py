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

from infrastructure.database import Base
class BusinessRegistration(Base):
    __tablename__ = "business_registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    business_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    government_id_fan = Column(String, nullable=False)
    government_id_photo_url = Column(Text, nullable=False)
    business_license_photo_url = Column(Text, nullable=False)

    status = Column(String, default="pending_review")

    rejection_reason = Column(Text, nullable=True)

    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)

    category_id = Column(UUID(as_uuid=True), ForeignKey("business_categories.id"))

    reviewed_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("now()"))

    user = relationship("User", back_populates="business_registrations")