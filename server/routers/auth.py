from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = crud.create_user(db, user)
    return {"message": "User registered", "user_id": new_user.id}

@router.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.verify_user(db, user.username, user.password)
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": f"Welcome {user.username}!"}
