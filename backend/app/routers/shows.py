from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas # Go up one level to find these
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/shows/", response_model=List[schemas.Show])
def read_shows(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_shows(db, skip=skip, limit=limit)

@router.get("/shows/{show_id}", response_model=schemas.Show)
def read_show(show_id: int, db: Session = Depends(get_db)):
    db_show = crud.get_show(db, show_id=show_id)
    if db_show is None:
        raise HTTPException(status_code=404, detail="Show not found")
    return db_show