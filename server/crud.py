from sqlalchemy.orm import Session
from . import models, schemas
import datetime

def create_log(db: Session, log: schemas.LogInput):
    db_log = models.DrowsinessLog(
        driver_id=log.driver_id,
        drowsy_score=log.drowsy_score,
        led=log.led,
        buzzer=log.buzzer,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs(db: Session, limit: int = 100):
    return db.query(models.DrowsinessLog).order_by(models.DrowsinessLog.timestamp.desc()).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def verify_user(db: Session, username: str, password: str):
    return db.query(models.User).filter(models.User.username == username, models.User.password == password).first()
