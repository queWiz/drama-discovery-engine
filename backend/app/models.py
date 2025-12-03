# in backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, JSON, Float
from .database import Base

class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, unique=True)
    synopsis = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    reviews = Column(Text, nullable=True)
    
    # --- UPDATED COLUMNS ---
    genres = Column(JSON)          # e.g., ["Thriller", "Mystery"]
    tags = Column(JSON)            # e.g., ["Strong Male Lead", "Murder"]
    rating = Column(Float)         # e.g., 8.7
    year = Column(Integer, nullable=True)
    
    # --- AI ANALYSIS COLUMNS ---
    tropes = Column(JSON)          # AI detected vibes
    verdict = Column(String)       # "Underrated", "Overrated", "Rated Fairly"