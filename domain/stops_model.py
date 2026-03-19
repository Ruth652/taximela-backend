from sqlalchemy import Column, Float, Integer, String

from infrastructure.otp_database import Base


class Stops(Base):
    __tablename__ = "stops"

    stop_id = Column(Integer, primary_key=True)
    stop_name = Column(String)
    stop_lat = Column(Float)   
    stop_lon = Column(Float)
    
    
# class UpdateStopRequest(Base):
#     stop_name: str | None = None
#     stop_lat: float | None = None
#     stop_lon: float | None = None
    