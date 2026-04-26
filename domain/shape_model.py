from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from infrastructure.otp_database import Base


class Shapes(Base):
    __tablename__ = "shapes"

    shape_id = Column(String)
    shape_pt_sequence = Column(Integer, primary_key=True)

    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_dist_traveled = Column(Float)

