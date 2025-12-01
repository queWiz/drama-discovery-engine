# in backend/app/crud.py
from sqlalchemy.orm import Session
from . import models

def get_shows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Show).offset(skip).limit(limit).all()

def get_show(db: Session, show_id: int):
    return db.query(models.Show).filter(models.Show.id == show_id).first()