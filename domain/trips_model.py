from sqlalchemy import Column, ForeignKey, Integer, String
from infrastructure.otp_database import Base
from sqlalchemy.orm import relationship
from .stops_model import Stops
from .route_otp_model import Routes


class Trips(Base):
    __tablename__ = "trips"

    trip_id = Column(String, primary_key=True)

    route_id = Column(Integer, ForeignKey("routes.route_id"), nullable=False)

    service_id = Column(
        String,
        ForeignKey("calendar.service_id"),
        nullable=False,
        default="everyday"
    )

    trip_headsign = Column(String, nullable=True)

    shape_id = Column(String,nullable=True)

    direction_id = Column(Integer, default=0)
    
    route = relationship("Routes", back_populates="trips")
    stop_times = relationship("StopTimes", back_populates="trip")
    calendar = relationship("Calendar", back_populates="trips")