from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from infrastructure.database import Base


class EntityTypeEnum(str, enum.Enum):
    user = "user"
    admin = "admin"


class AuthIdentity(Base):
    __tablename__ = "auth_identities"

    firebase_uid = Column(String, primary_key=True, index=True)
    entity_type = Column(Enum(EntityTypeEnum), default=EntityTypeEnum.user, nullable=False)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    user = relationship(
        "User",
        back_populates="auth_identity",
        uselist=False
    )
