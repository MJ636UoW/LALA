import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from lala.core.orchestrator import Orchestrator

app = FastAPI(
    title="LALA API",
    description="LALA Cybersecurity AI Operating Assistant API",
    version="0.1.0"
)

orchestrator: Optional[Orchestrator] = None

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@app.on_event("startup")
def startup_event():
    global orchestrator
    try:
        orchestrator = Orchestrator()
    except Exception as e:
        print(f"Warning: Orchestrator initialization error: {e}")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "LALA Cybersecurity Assistant API",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "lala-api"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    global orchestrator
    if not orchestrator:
        try:
            orchestrator = Orchestrator()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Orchestrator error: {e}")

    resp = orchestrator.process_user_input(req.prompt)
    return ChatResponse(response=resp)
