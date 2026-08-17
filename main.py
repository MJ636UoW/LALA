import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LALA — Cybersecurity Intelligence Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #0B0F19; color: #E2E8F0; font-family: 'Inter', sans-serif; height: 100vh; display: flex; flex-direction: column; }
        header { background: #111827; border-bottom: 1px solid #1E293B; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-family: 'Fira Code', monospace; font-size: 1.25rem; font-weight: 700; color: #38BDF8; display: flex; align-items: center; gap: 0.5rem; }
        .status-dot { width: 10px; height: 10px; background-color: #22C55E; border-radius: 50%; box-shadow: 0 0 10px #22C55E; }
        .nav-links { display: flex; gap: 1rem; }
        .nav-links a { color: #94A3B8; text-decoration: none; font-size: 0.9rem; font-weight: 600; transition: color 0.2s; }
        .nav-links a:hover { color: #38BDF8; }
        main { flex: 1; display: flex; flex-direction: column; max-width: 900px; width: 100%; margin: 0 auto; padding: 2rem 1rem; gap: 1.5rem; }
        .hero { background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; }
        .hero h1 { font-size: 1.5rem; color: #F8FAFC; margin-bottom: 0.5rem; }
        .hero p { color: #94A3B8; font-size: 0.95rem; }
        .chat-box { flex: 1; background: #111827; border: 1px solid #1E293B; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; min-height: 400px; }
        .messages { flex: 1; padding: 1.5rem; overflow-y: auto; display: flex; flex-direction: column; gap: 1rem; font-family: 'Fira Code', monospace; font-size: 0.9rem; }
        .msg { padding: 0.75rem 1rem; border-radius: 8px; max-width: 85%; line-height: 1.5; white-space: pre-wrap; }
        .msg.user { background: #0284C7; color: #FFFFFF; align-self: flex-end; }
        .msg.lala { background: #1E293B; color: #38BDF8; border: 1px solid #334155; align-self: flex-start; }
        .input-area { border-top: 1px solid #1E293B; padding: 1rem; background: #0B0F19; display: flex; gap: 0.75rem; }
        input[type="text"] { flex: 1; background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 0.75rem 1rem; color: #F8FAFC; font-family: 'Inter', sans-serif; font-size: 0.95rem; outline: none; }
        input[type="text"]:focus { border-color: #38BDF8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2); }
        button { background: #0284C7; color: #FFFFFF; border: none; border-radius: 8px; padding: 0.75rem 1.5rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #0369A1; }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <div class="status-dot"></div>
            LALA CYBERSECURITY PLATFORM
        </div>
        <div class="nav-links">
            <a href="/docs" target="_blank">Swagger API Docs</a>
            <a href="/health" target="_blank">Health Check</a>
        </div>
    </header>
    <main>
        <div class="hero">
            <h1>🛡️ LALA Cybersecurity AI Assistant</h1>
            <p>100% Local Autonomous Investigation & Threat Intelligence Engine</p>
        </div>
        <div class="chat-box">
            <div class="messages" id="messages">
                <div class="msg lala">🚀 LALA Online. Type a query, command, or request below.</div>
            </div>
            <div class="input-area">
                <input type="text" id="userInput" placeholder="Ask LALA or type '/automation status'..." onkeypress="handleKey(event)">
                <button onclick="sendMessage()">Send Request</button>
            </div>
        </div>
    </main>
    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const prompt = input.value.trim();
            if (!prompt) return;

            const msgs = document.getElementById('messages');
            
            // Add user message
            const uDiv = document.createElement('div');
            uDiv.className = 'msg user';
            uDiv.textContent = prompt;
            msgs.appendChild(uDiv);

            input.value = '';
            msgs.scrollTop = msgs.scrollHeight;

            // Loading state
            const lDiv = document.createElement('div');
            lDiv.className = 'msg lala';
            lDiv.textContent = 'Thinking...';
            msgs.appendChild(lDiv);
            msgs.scrollTop = msgs.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                const data = await res.json();
                lDiv.textContent = data.response || data.detail || 'Received response.';
            } catch (err) {
                lDiv.textContent = 'Error communicating with LALA API.';
            }
            msgs.scrollTop = msgs.scrollHeight;
        }

        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_TEMPLATE

@app.get("/api-status")
def api_status():
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
