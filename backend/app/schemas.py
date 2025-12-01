# in backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class ShowBase(BaseModel):
    title: str
    synopsis: Optional[str] = None
    image_url: Optional[str] = None
    genres: List[str] = []

class Show(ShowBase):
    id: int

    class Config:
        # This allows the Pydantic model to read data from ORM objects
        from_attributes = True 