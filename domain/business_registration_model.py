# # Python built-ins
# import uuid
# import enum
# from typing import Optional

# # SQLAlchemy Core + ORM
# from sqlalchemy import (
#     Column,
#     String,
#     Float,
#     Text,
#     TIMESTAMP,
#     ForeignKey
# )

# from pydantic import BaseModel, HttpUrl
# from uuid import UUID
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import text
# from uuid import UUID  # ✅ for Pydantic

# from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID

# from infrastructure.database import Base
# class BusinessRegistration(Base):
    
#     __tablename__ = "business_registrations"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

#     business_name = Column(String, nullable=False)
#     latitude = Column(Float, nullable=False)
#     longitude = Column(Float, nullable=False)

#     government_id_fan = Column(String, nullable=False)
#     government_id_photo_url = Column(Text, nullable=False)
#     business_license_photo_url = Column(Text, nullable=False)

#     status = Column(String, default="pending_review")

#     rejection_reason = Column(Text, nullable=True)

#     reviewed_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)

#     category_id = Column(UUID(as_uuid=True), ForeignKey("business_categories.id"))

#     reviewed_at = Column(TIMESTAMP, nullable=True)

#     created_at = Column(TIMESTAMP, server_default=text("now()"))
#     updated_at = Column(TIMESTAMP, server_default=text("now()"))

#     user = relationship("User", back_populates="business_registrations")
# class BusinessRegistrationRequest(BaseModel):
#     business_name: str
#     business_logo: HttpUrl
#     category_id: UUID
#     latitude: float
#     longitude: float
#     government_id_fan: str
#     business_licence_number: str
#     government_id_photo_url: HttpUrl
#     business_license_photo_url: HttpUrl




    # Python built-ins
import uuid
from typing import Optional
from uuid import UUID  # ✅ for Pydantic

# SQLAlchemy Core + ORM
from sqlalchemy import (
    Column,
    String,
    Float,
    Text,
    TIMESTAMP,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID  # ✅ alias
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

# Pydantic
from pydantic import BaseModel, HttpUrl, Field
from infrastructure.database import Base
from enum import Enum



class BusinessRegistration(Base):
    __tablename__ = "business_registrations"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"))

    business_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    government_id_fan = Column(String, nullable=False)
    government_id_photo_url = Column(Text, nullable=False)
    business_license_photo_url = Column(Text, nullable=False)

    #business_logo = Column(Text, nullable=True)
    #business_licence_number = Column(String, nullable=True)

    status = Column(String, default="pending_review")

    rejection_reason = Column(Text, nullable=True)

    reviewed_by = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)

    category_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("business_categories.id"))

    reviewed_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("now()"))

    user = relationship("User", back_populates="business_registrations")


class BusinessRegistrationRequest(BaseModel):
    business_name: str
    #business_logo: HttpUrl
    category_id: UUID  # ✅ Python UUID
    latitude: float
    longitude: float
    government_id_fan: str
    business_licence_number: str
    government_id_photo_url: HttpUrl
    business_license_photo_url: HttpUrl


class StatusEnum(str, Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"

class GetBusinessesRegistrationParams(BaseModel):
    status: Optional[StatusEnum] = Field(None)
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)