import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from lala.core.orchestrator import Orchestrator

app = FastAPI(
    title="LALA API",
    description="LALA Cybersecurity AI Operating Assistant API & JARVIS HUD",
    version="0.2.0"
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

JARVIS_HUD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LALA — JARVIS HUD AI Operating Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Fira+Code:wght@400;600&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        /* Custom Cyan HUD Scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(5, 11, 20, 0.9);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(0, 240, 255, 0.4);
            border-radius: 4px;
            border: 1px solid #00F0FF;
            box-shadow: 0 0 10px #00F0FF;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #00F0FF;
        }

        html, body {
            background: #050B14;
            color: #00F0FF;
            font-family: 'Orbitron', 'Inter', sans-serif;
            min-height: 100vh;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(0, 240, 255, 0.08) 0%, transparent 60%),
                linear-gradient(rgba(5, 11, 20, 0.95), rgba(5, 11, 20, 0.95)),
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 240, 255, 0.03) 3px, transparent 4px);
        }

        header {
            background: rgba(10, 20, 38, 0.85);
            border-bottom: 2px solid rgba(0, 240, 255, 0.3);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .hud-logo {
            font-size: 1.4rem;
            font-weight: 900;
            letter-spacing: 3px;
            color: #00F0FF;
            text-shadow: 0 0 15px #00F0FF;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.85rem;
            background: rgba(0, 240, 255, 0.1);
            border: 1px solid #00F0FF;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
        }
        .dot { width: 10px; height: 10px; background: #00F0FF; border-radius: 50%; box-shadow: 0 0 10px #00F0FF; animation: pulse 1.5s infinite; }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.3); opacity: 0.5; }
            100% { transform: scale(1); opacity: 1; }
        }

        .hud-links a {
            color: #7DD3FC;
            text-decoration: none;
            font-size: 0.85rem;
            margin-left: 1.5rem;
            font-weight: 600;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        .hud-links a:hover { color: #00F0FF; text-shadow: 0 0 10px #00F0FF; }

        main {
            flex: 1;
            display: flex;
            padding: 1.5rem;
            gap: 1.5rem;
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            min-height: calc(100vh - 80px);
        }

        .jarvis-core-panel {
            flex: 1;
            background: rgba(10, 20, 38, 0.6);
            border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            position: relative;
            box-shadow: inset 0 0 30px rgba(0, 240, 255, 0.1);
            min-height: 450px;
        }

        .arc-reactor {
            width: 260px;
            height: 260px;
            border-radius: 50%;
            border: 3px solid rgba(0, 240, 255, 0.4);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 50px rgba(0, 240, 255, 0.4), inset 0 0 50px rgba(0, 240, 255, 0.4);
            animation: rotateRing 20s linear infinite;
        }
        .arc-reactor-inner {
            width: 180px;
            height: 180px;
            border-radius: 50%;
            border: 2px dashed #FFD700;
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: rotateReverse 12s linear infinite;
        }
        .arc-core {
            width: 100px;
            height: 100px;
            background: radial-gradient(circle, #FFFFFF 0%, #00F0FF 60%, transparent 100%);
            border-radius: 50%;
            box-shadow: 0 0 40px #00F0FF, 0 0 80px #00F0FF;
        }

        @keyframes rotateRing { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes rotateReverse { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }

        .voice-status-text {
            margin-top: 2rem;
            font-size: 1.1rem;
            letter-spacing: 2px;
            text-align: center;
            color: #7DD3FC;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
        }

        .voice-controls {
            margin-top: 1.5rem;
            display: flex;
            gap: 1rem;
        }
        .jarvis-btn {
            background: rgba(0, 240, 255, 0.15);
            border: 2px solid #00F0FF;
            color: #00F0FF;
            padding: 0.8rem 1.5rem;
            border-radius: 30px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            cursor: pointer;
            letter-spacing: 1px;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
            transition: all 0.3s;
        }
        .jarvis-btn:hover {
            background: #00F0FF;
            color: #050B14;
            box-shadow: 0 0 30px #00F0FF;
        }

        .hud-chat-panel {
            flex: 1.2;
            background: rgba(10, 20, 38, 0.7);
            border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 16px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.8);
            min-height: 550px;
            max-height: calc(100vh - 120px);
        }
        .chat-header {
            background: rgba(0, 240, 255, 0.1);
            border-bottom: 1px solid rgba(0, 240, 255, 0.3);
            padding: 1rem 1.5rem;
            font-size: 0.95rem;
            letter-spacing: 2px;
            font-weight: 700;
        }
        .chat-messages {
            flex: 1;
            padding: 1.5rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            font-family: 'Fira Code', monospace;
            font-size: 0.9rem;
            scroll-behavior: smooth;
        }
        .msg {
            padding: 0.9rem 1.2rem;
            border-radius: 10px;
            line-height: 1.6;
            max-width: 88%;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        .msg.user {
            background: rgba(0, 240, 255, 0.15);
            border: 1px solid #00F0FF;
            color: #E0F2FE;
            align-self: flex-end;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
        }
        .msg.jarvis {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(255, 215, 0, 0.5);
            color: #FFD700;
            align-self: flex-start;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        }

        .input-bar {
            border-top: 1px solid rgba(0, 240, 255, 0.3);
            padding: 1rem;
            background: rgba(5, 11, 20, 0.9);
            display: flex;
            gap: 0.75rem;
        }
        input[type="text"] {
            flex: 1;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(0, 240, 255, 0.4);
            border-radius: 8px;
            padding: 0.8rem 1.2rem;
            color: #00F0FF;
            font-family: 'Fira Code', monospace;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: #00F0FF;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
        }

        @media (max-width: 900px) {
            main { flex-direction: column; }
            .hud-chat-panel { max-height: 500px; }
        }
    </style>
</head>
<body>
    <header>
        <div class="hud-logo">
            ⚡ LALA — JARVIS HUD ASSISTANT
        </div>
        <div class="status-badge">
            <div class="dot"></div>
            SYSTEM ONLINE | GEMINI FAST ACTIVE
        </div>
        <div class="hud-links">
            <a href="/docs" target="_blank">API DOCS</a>
            <a href="/health" target="_blank">SYSTEM HEALTH</a>
        </div>
    </header>
    <main>
        <div class="jarvis-core-panel">
            <div class="arc-reactor" id="arcReactor">
                <div class="arc-reactor-inner">
                    <div class="arc-core"></div>
                </div>
            </div>
            <div class="voice-status-text" id="voiceStatus">
                ⚡ PRESS TOGGLE VOICE MODE TO ACTIVATE MIC
            </div>
            <div class="voice-controls">
                <button class="jarvis-btn" id="voiceBtn" onclick="toggleVoiceMode()">🎤 TOGGLE VOICE MODE</button>
            </div>
        </div>

        <div class="hud-chat-panel">
            <div class="chat-header">
                🖥️ COMMAND TERMINAL & THREAT MONITOR
            </div>
            <div class="chat-messages" id="messages">
                <div class="msg jarvis">🤖 JARVIS Core Online. Google Gemini Fast AI Engine configured. Type a query below or activate voice mode.</div>
            </div>
            <div class="input-bar">
                <input type="text" id="userInput" placeholder="Type a command or ask LALA..." onkeypress="handleKey(event)">
                <button class="jarvis-btn" onclick="sendMessage()">TRANSMIT</button>
            </div>
        </div>
    </main>

    <script>
        let isVoiceActive = false;
        let isSpeaking = false;
        let recognition = null;

        function initVoice() {
            window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (window.SpeechRecognition) {
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';

                recognition.onresult = function(event) {
                    if (isSpeaking) return;
                    const lastResult = event.results[event.results.length - 1];
                    const transcript = lastResult[0].transcript.trim();
                    if (!transcript) return;

                    console.log('Voice Input:', transcript);
                    document.getElementById('userInput').value = transcript;
                    sendMessage();
                };

                recognition.onend = function() {
                    if (isVoiceActive && !isSpeaking) {
                        setTimeout(() => { try { recognition.start(); } catch(e){} }, 500);
                    }
                };
            }
        }

        function toggleVoiceMode() {
            isVoiceActive = !isVoiceActive;
            const status = document.getElementById('voiceStatus');
            const btn = document.getElementById('voiceBtn');

            if (isVoiceActive) {
                status.textContent = '🎙️ LISTENING FOR YOUR VOICE...';
                btn.style.borderColor = '#FFD700';
                btn.style.color = '#FFD700';
                if (recognition) { try { recognition.start(); } catch(e){} }
                speakText("Voice mode active.");
            } else {
                status.textContent = '⚡ PRESS TOGGLE VOICE MODE TO ACTIVATE MIC';
                btn.style.borderColor = '#00F0FF';
                btn.style.color = '#00F0FF';
                if (recognition) { try { recognition.stop(); } catch(e){} }
            }
        }

        function speakText(text) {
            if ('speechSynthesis' in window) {
                isSpeaking = true;
                if (recognition) { try { recognition.stop(); } catch(e){} }
                window.speechSynthesis.cancel();

                const utterance = new SpeechSynthesisUtterance(text);
                utterance.pitch = 1.0;
                utterance.rate = 1.0;

                utterance.onend = function() {
                    isSpeaking = false;
                    if (isVoiceActive && recognition) {
                        setTimeout(() => { try { recognition.start(); } catch(e){} }, 500);
                    }
                };

                utterance.onerror = function() {
                    isSpeaking = false;
                    if (isVoiceActive && recognition) {
                        setTimeout(() => { try { recognition.start(); } catch(e){} }, 500);
                    }
                };

                window.speechSynthesis.speak(utterance);
            }
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const prompt = input.value.trim();
            if (!prompt) return;

            const msgs = document.getElementById('messages');
            
            const uDiv = document.createElement('div');
            uDiv.className = 'msg user';
            uDiv.textContent = prompt;
            msgs.appendChild(uDiv);

            input.value = '';
            msgs.scrollTop = msgs.scrollHeight;

            const jDiv = document.createElement('div');
            jDiv.className = 'msg jarvis';
            jDiv.textContent = '⚡ Gemini AI Processing...';
            msgs.appendChild(jDiv);
            msgs.scrollTop = msgs.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                const data = await res.json();
                const outText = data.response || data.detail || 'Command acknowledged.';
                jDiv.textContent = outText;
                if (isVoiceActive) speakText(outText);
            } catch (err) {
                jDiv.textContent = '❌ Transmission Error with LALA Backend.';
            }
            msgs.scrollTop = msgs.scrollHeight;
        }

        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }

        window.onload = initVoice;
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_root():
    return JARVIS_HUD_HTML

@app.get("/api-status")
def api_status():
    return {
        "status": "online",
        "system": "LALA JARVIS Cybersecurity Assistant",
        "version": "0.2.0"
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
