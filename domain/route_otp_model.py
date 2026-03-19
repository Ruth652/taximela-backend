from sqlalchemy import Column, Float, Integer, String

from infrastructure.otp_database import Base


class Routes(Base):
    __tablename__ = "routes"

    route_id = Column(Integer, primary_key=True)
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_type = Column(Integer)    
    
# class UpdateRouteRequest(Base):
#     __allow_unmapped = True
#     route_short_name: str | None = None
#     route_long_name: str | None = None
#     route_type: int | None = None
    