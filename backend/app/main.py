from fastapi import FastAPI
from . import models
from .database import engine
from .routers import shows # Import the new router
from pydantic import BaseModel
from .services.chat_service import get_chat_response

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the routes from the routers folder
app.include_router(shows.router)

@app.get("/")
def root():
    return {"message": "Drama Discovery Engine API is running"}

# Request model for the chat endpoint
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    # This is where the magic happens
    response_text = get_chat_response(request.message)
    return {"response": response_text}