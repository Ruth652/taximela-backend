from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from infrastructure.otp_database import Base


class Routes(Base):
    __tablename__ = "routes"

    route_id = Column(Integer, primary_key=True)
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_type = Column(Integer, default=3)    
    
    trips = relationship("Trips", back_populates="route")