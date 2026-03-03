import uuid
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

from infrastructure.database import Base


class BusinessCategory(Base):
    __tablename__ = "business_categories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("now()")
    )