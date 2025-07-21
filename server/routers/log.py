from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/log")
def create_log(log: schemas.LogInput, db: Session = Depends(get_db)):
    new_log = crud.create_log(db, log)
    return {"message": "Log saved", "id": new_log.id}

@router.get("/logs")
def read_logs(limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_logs(db, limit)
