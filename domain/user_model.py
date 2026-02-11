from sqlalchemy import Column, String, Enum, Float, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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

    deleted_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default="now()")
    updated_at = Column(TIMESTAMP, nullable=False, server_default="now()")

    auth_identity = relationship(
        "AuthIdentity",
        back_populates="user",
        uselist=False
    )
