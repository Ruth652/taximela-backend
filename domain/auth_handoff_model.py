from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from infrastructure.database import Base


class AuthHandoffToken(Base):
    __tablename__ = "auth_handoff_tokens"

    token = Column(String(128), primary_key=True, index=True)
    firebase_uid = Column(String(128), nullable=False, index=True)
    purpose = Column(String(64), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
