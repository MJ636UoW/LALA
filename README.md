<<<<<<< HEAD
# LALA
MY_LALA
=======
# LALA - Personal AI Operating Assistant

> **AI System**: LALA  
> **Call Name**: LALA  
> **Voice Identity**: LALA  
> **Personality**: LALA  
> **User**: Mandar  

LALA is an extensible, modular personal AI operating assistant system designed to operate locally or in a hybrid local/cloud model. LALA features first-class multilingual code-switching support (English, Hindi, Marathi), persistent memory, modular security controls, and subagent orchestration.

---

## 🏛️ System Architecture Overview

LALA is structured around 12 core subsystems:

```text
LALA
|
+-- Orchestrator          (Central pipeline execution engine)
+-- Model Router          (Local Ollama & cloud provider balance)
+-- Memory                (Session state & abstract persistent memory interfaces)
+-- Voice                 (Abstract Speech-to-Text & Text-to-Speech interfaces)
+-- Tools                 (Tool schema registry & security authorization engine)
+-- API Registry          (Provider metadata registry)
+-- Security              (Permission controls: SAFE_AUTOMATIC, READ_ONLY, CONFIRM, PRIVILEGED)
+-- Personality / Emotion (LALA prompt system & dynamic tone control)
+-- Subagents             (Base subagent & task delegation abstraction)
+-- Configuration         (Typed Pydantic & YAML settings)
+-- Logging               (Structured logger utility)
+-- UI                    (Rich interactive terminal UI)
```

---

## 🌐 Multilingual Support

LALA supports first-class multilingual interactions:
- **English**: Full technical, conversation, and execution capabilities.
- **Hindi (हिंदी)**: Native conversational and task prompts.
- **Marathi (मराठी)**: Native conversational and task prompts.
- **Code-switching**: Natural fluid switching between English, Hindi, and Marathi in a single interaction.

---

## 🚀 Quick Start (Phase 1 Foundation)

### Requirements
- **Python 3.11+**

### Installation
```bash
# Navigate to directory
cd d:\LALA

# Install lightweight dependencies
py -m pip install -r requirements.txt
```

### Running the CLI
```bash
py -m lala.main
```

### Running Tests
```bash
py -m unittest discover -s tests
```

---

## 🛣️ Roadmap

- [x] **Phase 1**: Core Architecture & Lightweight Foundation (Interfaces, Security, Router, Offline CLI & Test Suite)
- [ ] **Phase 2**: Local AI Brain & Hardware-aware Ollama Model Selection
- [ ] **Phase 3**: Persistent Memory & Vector RAG Integration
- [ ] **Phase 4**: Multilingual Offline Voice Pipeline (Whisper / TTS)
- [ ] **Phase 5**: Subagents, Computer Automation & Browser Control
>>>>>>> 3a6a7ff (feat: initial LALA Phase 1 foundation)
