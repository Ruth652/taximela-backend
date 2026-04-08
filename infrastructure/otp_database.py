from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

OTP_DATABASE_URL = os.getenv("OTP_DATABASE_URL")

engine = create_engine(OTP_DATABASE_URL, echo=False)

OTP_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_otp_db():
    db = OTP_SessionLocal()
    try:
        yield db
    finally:
        db.close()


