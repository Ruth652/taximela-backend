
from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, Integer, func

from infrastructure.database import Base
from sqlalchemy.orm import relationship



class GTFS(Base):
    __tablename__ = "gtfs_queue"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("contribution_groups.id"), nullable=True) # Optional grouping for batch processing
    
    status = Column(
        Enum(
            "queued",
            "failed",
            "done",
            name="gtfs_status",
        ),
        default="queued",
    )


    queued_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"))
    queued_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime, server_default=func.now())

    admin = relationship("Admin", back_populates="gtfs_queue")
    group = relationship("ContributionGroup", back_populates="gtfs_queue")
    