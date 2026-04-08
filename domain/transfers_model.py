from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from infrastructure.otp_database import Base


class Transfer(Base):
    __tablename__ = "transfers"

    from_stop_id = Column(Integer, ForeignKey("stops.stop_id"), primary_key=True)
    to_stop_id = Column(Integer, ForeignKey("stops.stop_id"), primary_key=True)
    transfer_type = Column(Integer, default=0)
    min_transfer_time = Column(Integer, default=800)
    
    from_stop = relationship(
    "Stops",
    foreign_keys=[from_stop_id],
    back_populates="from_transfers"
)

    to_stop = relationship(
        "Stops",
        foreign_keys=[to_stop_id],
        back_populates="to_transfers"
)
    
    