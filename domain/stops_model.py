from sqlalchemy import Column, Float, Integer, String
from infrastructure.otp_database import Base
from sqlalchemy.orm import relationship
from .transfers_model import Transfer

class Stops(Base):
    __tablename__ = "stops"

    stop_id = Column(Integer, primary_key=True)
    stop_name = Column(String)
    stop_lat = Column(Float)   
    stop_lon = Column(Float)
    
    stop_times = relationship("StopTimes", back_populates="stop") 
    
    from_transfers = relationship(
    "Transfer",
    foreign_keys="Transfer.from_stop_id",
    back_populates="from_stop"
)

    to_transfers = relationship(
        "Transfer",
        foreign_keys="Transfer.to_stop_id",
        back_populates="to_stop"
    ) 
    