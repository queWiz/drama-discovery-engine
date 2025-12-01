# in backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, JSON
from .database import Base

class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, unique=True)
    synopsis = Column(Text, nullable=True)
    genres = Column(JSON) # Storing a list of strings
    image_url = Column(String, nullable=True)