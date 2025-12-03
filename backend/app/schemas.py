# in backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class ShowBase(BaseModel):
    title: str
    synopsis: Optional[str] = None
    image_url: Optional[str] = None
    reviews: Optional[str] = None
    
    genres: List[str] = []
    tags: List[str] = []      # <--- New
    rating: Optional[float] = 0.0 # <--- New
    year: Optional[int] = 0
    
    tropes: Optional[List[str]] = None
    verdict: Optional[str] = None # <--- New

class Show(ShowBase):
    id: int

    class Config:
        # This allows the Pydantic model to read data from ORM objects
        from_attributes = True 