from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
import datetime
from .database import Base

class DrowsinessLog(Base):
    __tablename__ = "drowsiness_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    driver_id = Column(String, index=True)
    drowsy_score = Column(Float)
    led = Column(Boolean)
    buzzer = Column(Boolean)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)