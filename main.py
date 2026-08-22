import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from lala.core.orchestrator import Orchestrator
from lala.malware.dynamic_analyzer import DynamicMalwareAnalyzer

app = FastAPI(
    title="LALA API",
    description="LALA Cybersecurity AI Operating Assistant API & JARVIS HUD",
    version="0.4.0"
)

_orchestrator_instance: Optional[Orchestrator] = None
_dynamic_analyzer_instance: Optional[DynamicMalwareAnalyzer] = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance

def get_dynamic_analyzer() -> DynamicMalwareAnalyzer:
    global _dynamic_analyzer_instance
    if _dynamic_analyzer_instance is None:
        _dynamic_analyzer_instance = DynamicMalwareAnalyzer()
    return _dynamic_analyzer_instance

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str = "default"
    status: str = "success"

JARVIS_HUD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LALA — JARVIS Pentester & Malware Analysis HUD</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Fira+Code:wght@400;600&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
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
            max-width: 1600px;
            width: 100%;
            margin: 0 auto;
            min-height: calc(100vh - 80px);
        }

        /* Left Sidebar: Recent Chats & Sandbox Controls */
        .sidebar-panel {
            width: 300px;
            background: rgba(10, 20, 38, 0.7);
            border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 16px;
            display: flex;
            flex-direction: column;
            padding: 1.2rem;
            gap: 1.2rem;
            box-shadow: 0 0 25px rgba(0, 0, 0, 0.6);
        }
        .new-chat-btn {
            background: rgba(0, 240, 255, 0.2);
            border: 2px solid #00F0FF;
            color: #00F0FF;
            padding: 0.8rem;
            border-radius: 12px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            cursor: pointer;
            text-align: center;
            letter-spacing: 1px;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
            transition: all 0.3s;
        }
        .new-chat-btn:hover {
            background: #00F0FF;
            color: #050B14;
            box-shadow: 0 0 25px #00F0FF;
        }

        .recent-title {
            font-size: 0.85rem;
            letter-spacing: 2px;
            color: #7DD3FC;
            font-weight: 700;
        }
        .recent-chats-list {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }
        .chat-item {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(0, 240, 255, 0.2);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: #94A3B8;
        }
        .chat-item:hover, .chat-item.active {
            border-color: #00F0FF;
            color: #00F0FF;
            background: rgba(0, 240, 255, 0.1);
        }

        /* Center JARVIS Arc Reactor Panel */
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
            width: 240px;
            height: 240px;
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
            width: 160px;
            height: 160px;
            border-radius: 50%;
            border: 2px dashed #FFD700;
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: rotateReverse 12s linear infinite;
        }
        .arc-core {
            width: 90px;
            height: 90px;
            background: radial-gradient(circle, #FFFFFF 0%, #00F0FF 60%, transparent 100%);
            border-radius: 50%;
            box-shadow: 0 0 40px #00F0FF, 0 0 80px #00F0FF;
        }

        @keyframes rotateRing { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes rotateReverse { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }

        .voice-status-text {
            margin-top: 1.5rem;
            font-size: 1rem;
            letter-spacing: 2px;
            text-align: center;
            color: #7DD3FC;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
        }

        .voice-controls {
            margin-top: 1.2rem;
            display: flex;
            gap: 1rem;
        }
        .jarvis-btn {
            background: rgba(0, 240, 255, 0.15);
            border: 2px solid #00F0FF;
            color: #00F0FF;
            padding: 0.75rem 1.2rem;
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

        /* Right Panel: HUD Chat & Telemetry Interface */
        .hud-chat-panel {
            flex: 1.4;
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
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .reset-btn {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid #EF4444;
            color: #EF4444;
            padding: 0.3rem 0.8rem;
            border-radius: 8px;
            font-size: 0.75rem;
            cursor: pointer;
            font-family: 'Orbitron', sans-serif;
            transition: all 0.3s;
        }
        .reset-btn:hover { background: #EF4444; color: #FFFFFF; }

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
            gap: 0.6rem;
            align-items: center;
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
        .upload-icon-btn {
            background: rgba(0, 240, 255, 0.15);
            border: 1px solid #00F0FF;
            color: #00F0FF;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1rem;
            transition: all 0.3s;
        }
        .upload-icon-btn:hover { background: #00F0FF; color: #050B14; }

        @media (max-width: 1000px) {
            main { flex-direction: column; }
            .sidebar-panel { width: 100%; height: auto; }
            .hud-chat-panel { max-height: 500px; }
        }
    </style>
</head>
<body>
    <header>
        <div class="hud-logo">
            ⚡ LALA — UNIVERSAL AI COMPANION & OPERATING ASSISTANT
        </div>
        <div class="status-badge">
            <div class="dot"></div>
            LIVE WEB SEARCH ACTIVE | UNIVERSAL PERSONAL COMPANION
        </div>
        <div class="hud-links">
            <a href="/docs" target="_blank">API DOCS</a>
            <a href="/health" target="_blank">SYSTEM HEALTH</a>
        </div>
    </header>
    <main>
        <!-- Left Sidebar: Recent Chats & Sandbox Trigger -->
        <div class="sidebar-panel">
            <button class="new-chat-btn" onclick="startNewChat()">+ NEW CHAT SESSION</button>
            <button class="new-chat-btn" style="background: rgba(255,215,0,0.15); border-color: #FFD700; color: #FFD700;" onclick="triggerSandboxAnalysis()">🔬 DETONATE IN gVISOR</button>
            
            <div class="recent-title">CONVERSATION TOPICS</div>
            <div class="recent-chats-list" id="recentChats">
                <div class="chat-item active" onclick="switchSession('default', this)">💬 Personal & Life Partner</div>
                <div class="chat-item" onclick="switchSession('web_search', this)">🌐 Live Google Web Search</div>
                <div class="chat-item" onclick="switchSession('cybersecurity', this)">🛡️ Cybersecurity & Coding</div>
                <div class="chat-item" onclick="switchSession('malware_sandbox', this)">🔬 Malware Sandbox & PE</div>
            </div>
        </div>

        <!-- Center: JARVIS Arc Reactor Core -->
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

        <!-- Right: HUD Terminal Panel -->
        <div class="hud-chat-panel">
            <div class="chat-header">
                <span>🖥️ COMMAND TERMINAL & OPERATING MONITOR</span>
                <button class="reset-btn" onclick="resetTopic()">🔄 RESET TOPIC</button>
            </div>
            <div class="chat-messages" id="messages">
                <div class="msg jarvis">🤖 LALA Universal Operating Partner Online. Here for your personal questions, life advice, live web search, coding, cybersecurity, or whatever is on your mind, Mandar.</div>
            </div>
            <div class="input-bar">
                <input type="file" id="fileInput" style="display: none;" onchange="uploadFile()">
                <button class="upload-icon-btn" onclick="document.getElementById('fileInput').click()" title="Upload File / Document">📎</button>
                <input type="text" id="userInput" placeholder="Ask LALA, type 'end of topic', or ask to analyze sample..." onkeypress="handleKey(event)">
                <button class="jarvis-btn" onclick="sendMessage()">TRANSMIT</button>
            </div>
        </div>
    </main>

    <script>
        let currentSessionId = 'default';
        let isVoiceActive = false;
        let isSpeaking = false;
        let recognition = null;

        function startNewChat() {
            currentSessionId = 'session_' + Date.now().toString().slice(-6);
            const list = document.getElementById('recentChats');
            const item = document.createElement('div');
            item.className = 'chat-item active';
            item.textContent = '💬 Session ' + currentSessionId.slice(-4);
            item.onclick = function() { switchSession(currentSessionId, item); };
            
            document.querySelectorAll('.chat-item').forEach(el => el.classList.remove('active'));
            list.prepend(item);

            const msgs = document.getElementById('messages');
            msgs.innerHTML = '<div class="msg jarvis">🤖 New Pentest Session Started (' + currentSessionId + '). Ready for your commands, Mandar.</div>';
        }

        function switchSession(sid, el) {
            currentSessionId = sid;
            document.querySelectorAll('.chat-item').forEach(item => item.classList.remove('active'));
            el.classList.add('active');

            const msgs = document.getElementById('messages');
            msgs.innerHTML = '<div class="msg jarvis">🤖 Switched to session [' + sid + ']. Conversation history loaded.</div>';
        }

        function resetTopic() {
            document.getElementById('userInput').value = 'end of topic';
            sendMessage();
        }

        async function triggerSandboxAnalysis() {
            const msgs = document.getElementById('messages');
            const jDiv = document.createElement('div');
            jDiv.className = 'msg jarvis';
            jDiv.textContent = '🔬 gVisor Sandbox Detonating Sample... Capturing ProcMon process creation & Wireshark PCAP packets...';
            msgs.appendChild(jDiv);
            msgs.scrollTop = msgs.scrollHeight;

            try {
                const res = await fetch('/sandbox/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file_name: 'Pokemon_Brock.exe' })
                });
                const data = await res.json();
                jDiv.textContent = data.summary || 'Sandbox detonation completed.';
                if (isVoiceActive) speakText('gVisor sandbox detonation analysis complete.');
            } catch (err) {
                jDiv.textContent = '❌ Sandbox execution error.';
            }
            msgs.scrollTop = msgs.scrollHeight;
        }

        let taskQueue = [];
        let isProcessingQueue = false;

        function cleanTextForSpeech(text) {
            if (!text) return '';
            let clean = text;
            clean = clean.replace(/```[\s\S]*?```/g, 'Code block omitted.');
            clean = clean.replace(/`([^`]+)`/g, '$1');
            clean = clean.replace(/^#+\s+/gm, '');
            clean = clean.replace(/\*\*([^*]+)\*\*/g, '$1');
            clean = clean.replace(/\*([^*]+)\*/g, '$1');
            clean = clean.replace(/__([^_]+)__/g, '$1');
            clean = clean.replace(/_([^_]+)_/g, '$1');
            clean = clean.replace(/^\s*[\-*+]\s+/gm, '');
            clean = clean.replace(/^\s*\d+\.\s+/gm, '');
            clean = clean.replace(/[#*~`>|_]/g, '');
            return clean.trim();
        }

        function getBestVoice() {
            if (!('speechSynthesis' in window)) return null;
            const voices = window.speechSynthesis.getVoices();
            const preferred = voices.find(v => 
                v.name.includes('Google UK English Female') || 
                v.name.includes('Google US English') ||
                v.name.includes('Natural') || 
                v.name.includes('Zira') || 
                v.name.includes('Jenny') || 
                v.name.includes('Samantha') || 
                v.name.includes('Karen') ||
                v.name.includes('Female')
            );
            return preferred || voices[0] || null;
        }

        function initVoice() {
            window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (window.SpeechRecognition) {
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';

                recognition.onstart = function() {
                    // Interrupt TTS speaking if user starts talking
                    if ('speechSynthesis' in window && window.speechSynthesis.speaking) {
                        window.speechSynthesis.cancel();
                        isSpeaking = false;
                    }
                };

                recognition.onresult = function(event) {
                    const lastResult = event.results[event.results.length - 1];
                    const transcript = lastResult[0].transcript.trim();
                    if (!transcript) return;

                    console.log('Voice Input Received:', transcript);
                    document.getElementById('userInput').value = transcript;
                    sendMessage();
                };

                recognition.onend = function() {
                    if (isVoiceActive && !isSpeaking) {
                        setTimeout(() => { try { recognition.start(); } catch(e){} }, 400);
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
                speakText("Voice mode active. I am here for you.");
            } else {
                status.textContent = '⚡ PRESS TOGGLE VOICE MODE TO ACTIVATE MIC';
                btn.style.borderColor = '#00F0FF';
                btn.style.color = '#00F0FF';
                if (recognition) { try { recognition.stop(); } catch(e){} }
                if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            }
        }

        function speakText(text) {
            if ('speechSynthesis' in window) {
                isSpeaking = true;
                if (recognition) { try { recognition.stop(); } catch(e){} }
                window.speechSynthesis.cancel();

                const cleanSpokenText = cleanTextForSpeech(text);
                const utterance = new SpeechSynthesisUtterance(cleanSpokenText);
                
                const voice = getBestVoice();
                if (voice) utterance.voice = voice;
                
                utterance.pitch = 1.15; // Warmer, cute, natural accent tone
                utterance.rate = 1.05;  // Lively conversational pace

                utterance.onend = function() {
                    isSpeaking = false;
                    if (isVoiceActive && recognition) {
                        setTimeout(() => { try { recognition.start(); } catch(e){} }, 400);
                    }
                };

                utterance.onerror = function() {
                    isSpeaking = false;
                    if (isVoiceActive && recognition) {
                        setTimeout(() => { try { recognition.start(); } catch(e){} }, 400);
                    }
                };

                window.speechSynthesis.speak(utterance);
            }
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const prompt = input.value.trim();
            if (!prompt) return;

            input.value = '';
            taskQueue.push(prompt);
            
            if (!isProcessingQueue) {
                processTaskQueue();
            }
        }

        async function processTaskQueue() {
            if (taskQueue.length === 0) {
                isProcessingQueue = false;
                return;
            }

            isProcessingQueue = true;
            const prompt = taskQueue.shift();

            const msgs = document.getElementById('messages');
            
            const uDiv = document.createElement('div');
            uDiv.className = 'msg user';
            uDiv.textContent = prompt;
            msgs.appendChild(uDiv);
            msgs.scrollTop = msgs.scrollHeight;

            const jDiv = document.createElement('div');
            jDiv.className = 'msg jarvis';
            jDiv.textContent = '⚡ LALA Processing...';
            msgs.appendChild(jDiv);
            msgs.scrollTop = msgs.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, session_id: currentSessionId })
                });
                const data = await res.json();
                if (res.ok) {
                    const outText = data.response || 'Acknowledged.';
                    jDiv.textContent = outText;
                    if (isVoiceActive) speakText(outText);
                } else {
                    jDiv.textContent = '⚠️ Backend Notice: ' + (data.detail || 'Service initializing, please retry.');
                }
            } catch (err) {
                jDiv.textContent = '⚡ Server is updating. Please retry in a moment.';
            }
            msgs.scrollTop = msgs.scrollHeight;

            // Process next message in queue sequentially
            setTimeout(processTaskQueue, 300);
        }

        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            if (!fileInput.files || fileInput.files.length === 0) return;

            const file = fileInput.files[0];
            const msgs = document.getElementById('messages');

            const uDiv = document.createElement('div');
            uDiv.className = 'msg user';
            uDiv.textContent = '📎 Uploading & Analyzing File: ' + file.name;
            msgs.appendChild(uDiv);
            msgs.scrollTop = msgs.scrollHeight;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('session_id', currentSessionId);

            const jDiv = document.createElement('div');
            jDiv.className = 'msg jarvis';
            jDiv.textContent = '🔬 LALA Analyzing Document / File...';
            msgs.appendChild(jDiv);
            msgs.scrollTop = msgs.scrollHeight;

            try {
                const res = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                jDiv.textContent = data.analysis || ('Document ' + file.name + ' uploaded and indexed successfully.');
                if (isVoiceActive) speakText(data.analysis || 'File analysis complete.');
            } catch (err) {
                jDiv.textContent = '❌ Error uploading file to LALA backend.';
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

class SandboxAnalyzeRequest(BaseModel):
    file_name: str = "sample.exe"
    file_path: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def read_root():
    return JARVIS_HUD_HTML

@app.get("/api-status")
def api_status():
    return {
        "status": "online",
        "system": "LALA JARVIS Cybersecurity Assistant",
        "version": "0.4.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "lala-api"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        orch = get_orchestrator()
        resp = orch.process_user_input(req.prompt, session_id=req.session_id or "default")
        return ChatResponse(response=resp, session_id=req.session_id or "default")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")

@app.post("/sandbox/analyze")
def sandbox_analyze_endpoint(req: SandboxAnalyzeRequest):
    try:
        analyzer = get_dynamic_analyzer()
        target_path = req.file_path or req.file_name
        report = analyzer.run_full_analysis(target_path, sample_name=req.file_name)
        return {
            "report_id": report.report_id,
            "file_name": report.file_name,
            "threat_level": report.threat_level.value,
            "summary": report.summary,
            "static_results": report.static_results.model_dump() if report.static_results else {},
            "dynamic_results": report.dynamic_results.model_dump() if report.dynamic_results else {},
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sandbox analysis failed: {str(e)}")

@app.post("/upload")
async def upload_file_endpoint(file: UploadFile = File(...), session_id: str = Form("default")):
    try:
        orch = get_orchestrator()
        content_bytes = await file.read()
        filename = file.filename or "uploaded_file"
        
        text_content = ""
        try:
            text_content = content_bytes.decode("utf-8", errors="replace")[:10000]
        except Exception:
            text_content = f"[Binary / Media File: {filename}, size: {len(content_bytes)} bytes]"

        prompt = f"Analyze this uploaded document/file '{filename}':\n\n{text_content}\n\nProvide a technical pentester summary and key security observations for Mandar."
        analysis_res = orch.process_user_input(prompt, session_id=session_id)

        return {
            "filename": filename,
            "analysis": analysis_res,
            "session_id": session_id,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload processing failed: {str(e)}")
