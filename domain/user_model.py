from sqlalchemy import Column, Integer, String, Enum, Float, TIMESTAMP, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import Optional
from pydantic import BaseModel, validator, Field
from sqlalchemy.sql import text

import enum, uuid

from infrastructure.database import Base


class UserStatusEnum(str, enum.Enum):
    active = "active"
    suspended = "suspended"


class ReputationTierEnum(str, enum.Enum):
    flagged = "flagged"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.active)

    rating_score = Column(Float, default=0)
    reputation_tier = Column(Enum(ReputationTierEnum), default=ReputationTierEnum.silver)

    preferred_language = Column(String(10), default="en")
    profile_picture_url = Column(Text, nullable=True)
    rejection_streak_count = Column(Integer, default=0)

    is_commuter = Column(Boolean, nullable=False, default=False)
    is_business_owner = Column(Boolean, nullable=False, default=False)

    deleted_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("now()"))

    auth_identity = relationship(
        "AuthIdentity",
        back_populates="user",
        uselist=False
    )
    contributions = relationship("Contribution", back_populates="user")
    admins = relationship("Admin", back_populates="user")

    business_registrations = relationship(
        "BusinessRegistration",
        back_populates="user"
    )

    businesses = relationship(
        "Business",
        back_populates="owner"
    )
    
class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = Field(
        None, 
        max_length=100, 
        description="User's full name (max 100 characters)"
    )
    preferred_language: Optional[str] = Field(
        None, 
        description="Language preference: 'en' for English, 'am' for Amharic"
    )
    profile_picture_url: Optional[str] = Field(
        None, 
        max_length=500, 
        description="URL to the user's profile picture"
    )

    @validator("preferred_language")
    def validate_language(cls, v):
        if v is not None and v not in ("en", "am"):
            raise ValueError("preferred_language must be 'en' or 'am'")
        return v

class CreateUserRequest(BaseModel):
    full_name: str = Field(
        ...,
        max_length=100,
        description="User's full name (max 100 characters)"
    )
    preferred_language: Optional[str] = Field(
        "en",
        description="Language preference: 'en' for English, 'am' for Amharic"
    )

    is_commuter: Optional[bool] = Field(
        False,
        description="Indicates whether the user is a commuter"
    )

    is_business_owner: Optional[bool] = Field(
        False,
        description="Indicates whether the user is a business owner"
    )


    @validator("preferred_language")
    def validate_language(cls, v):
        if v is not None and v not in ("en", "am"):
            raise ValueError("preferred_language must be 'en' or 'am'")
        return v
