from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from infrastructure.otp_database import Base


class Calendar(Base):
    __tablename__ = "calendar"

    service_id = Column(String, primary_key=True)
    monday = Column(Integer)
    tuesday = Column(Integer)
    wednesday = Column(Integer)
    thursday = Column(Integer)
    friday = Column(Integer)
    saturday = Column(Integer)
    sunday = Column(Integer)
    start_date = Column(String)
    end_date = Column(String)
    
    trips = relationship("Trips", back_populates="calendar")