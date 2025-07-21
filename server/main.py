# from fastapi import FastAPI, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# import datetime

# # --- Cấu hình database ---
# DATABASE_URL = "sqlite:///./data.db"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # --- Model SQLAlchemy ---
# class DrowsinessLog(Base):
#     __tablename__ = "drowsiness_logs"
#     id = Column(Integer, primary_key=True, index=True)
#     timestamp = Column(DateTime, default=datetime.datetime.utcnow)
#     driver_id = Column(String, index=True)
#     drowsy_score = Column(Float)
#     led = Column(Boolean)
#     buzzer = Column(Boolean)

# # Tạo bảng nếu chưa có
# Base.metadata.create_all(bind=engine)

# # --- Pydantic schema để validate dữ liệu gửi lên ---
# class LogInput(BaseModel):
#     driver_id: str
#     drowsy_score: float
#     led: bool
#     buzzer: bool

# # --- Tạo FastAPI app ---
# app = FastAPI()

# # Dependency để tạo session DB cho mỗi request
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # --- API nhận dữ liệu POST ---
# @app.post("/api/log")
# def create_log(log: LogInput, db: Session = Depends(get_db)):
#     db_log = DrowsinessLog(
#         driver_id=log.driver_id,
#         drowsy_score=log.drowsy_score,
#         led=log.led,
#         buzzer=log.buzzer,
#         timestamp=datetime.datetime.utcnow()
#     )
#     db.add(db_log)
#     db.commit()
#     db.refresh(db_log)
#     return {"message": "Log saved", "id": db_log.id}

# # --- API lấy dữ liệu GET ---
# @app.get("/api/logs")
# def read_logs(limit: int = 100, db: Session = Depends(get_db)):
#     logs = db.query(DrowsinessLog).order_by(DrowsinessLog.timestamp.desc()).limit(limit).all()
#     return logs

# # --- Model người dùng ---
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     password = Column(String)

# # Tạo bảng user nếu chưa có
# Base.metadata.create_all(bind=engine)

# # --- Schema đăng ký người dùng ---
# class UserCreate(BaseModel):
#     username: str
#     password: str

# # --- API: Đăng ký ---
# @app.post("/register")
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     existing_user = db.query(User).filter(User.username == user.username).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username already exists")
#     new_user = User(username=user.username, password=user.password)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return {"message": "User registered", "user_id": new_user.id}

# # --- API: Đăng nhập ---
# @app.post("/login")
# def login(user: UserCreate, db: Session = Depends(get_db)):
#     existing_user = db.query(User).filter(
#         User.username == user.username,
#         User.password == user.password
#     ).first()
#     if not existing_user:
#         raise HTTPException(status_code=401, detail="Invalid username or password")
#     return {"message": f"Welcome {user.username}!"}

from fastapi import FastAPI
from .database import Base, engine
from .routers import log, auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(log.router, prefix="/api", tags=["Logs"])
app.include_router(auth.router, tags=["Auth"])
