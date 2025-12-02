from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # IMPORT THIS
from . import models
from .database import engine
from .routers import shows # Import the new router
from pydantic import BaseModel
from .services.chat_service import get_chat_response

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Allow your Vue app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes from the routers folder
app.include_router(shows.router)

@app.get("/")
def root():
    return {"message": "Drama Discovery Engine API is running"}

# Request model for the chat endpoint
class ChatRequest(BaseModel):
    message: str
    genre: str | None = "All"
    rating: int | None = 0
    year: str | None = "All"    # Values: "All", "2020+", "2015-2019", "Classic"
    trope: str | None = None

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    # This is where the magic happens
    result = get_chat_response(
        request.message, 
        request.genre, 
        request.rating, 
        request.year, 
        request.trope
    )
    return result