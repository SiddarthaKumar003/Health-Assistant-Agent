from fastapi import FastAPI
from pydantic import BaseModel

from backend.agents.health_agent import ask_health_agent


app = FastAPI(
    title="HealthMate AI",
    description="Agentic AI Health Assistant",
    version="0.1.0"
)


from typing import Optional


class ChatRequest(BaseModel):
    message: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@app.get("/")
def root():
    return {
        "message": "HealthMate AI is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    response = ask_health_agent(
        message=request.message,
        latitude=request.latitude,
        longitude=request.longitude,
    )

    return {
        "response": response
    }