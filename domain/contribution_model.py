from sqlalchemy import Column, String, Text, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contribute(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=True)
    description = Column(Text, nullable=False)  # store dict directly
    trust_score_at_submit = Column(Float, nullable=False)
