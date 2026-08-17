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

_orchestrator_instance: Optional[Orchestrator] = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

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
    try:
        orch = get_orchestrator()
        resp = orch.process_user_input(req.prompt)
        return ChatResponse(response=resp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")
