from sqlalchemy import Column, ForeignKey, Integer, String
from infrastructure.otp_database import Base
from sqlalchemy.orm import relationship


class StopTimes(Base):
    __tablename__ = "stop_times"

    trip_id = Column(String, ForeignKey("trips.trip_id"), primary_key=True)
    arrival_time = Column(String)
    departure_time = Column(String)
    stop_id = Column(Integer, ForeignKey("stops.stop_id"))
    stop_sequence = Column(Integer, primary_key=True)
    
    trip = relationship("Trips", back_populates="stop_times")
    stop = relationship("Stops", back_populates="stop_times")