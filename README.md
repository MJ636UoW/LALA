# LALA - Personal AI Operating Assistant

> **AI System**: LALA  
> **Call Name**: LALA  
> **Voice Identity**: LALA  
> **Personality**: LALA  
> **User**: Mandar  

LALA is an extensible, modular personal AI operating assistant designed to operate locally with 100% privacy guarantee. LALA features first-class multilingual code-switching support (English, Hindi, Marathi), persistent memory, modular security controls, and subagent orchestration.

---

## 🏛️ System Architecture & Data Flow

```text
User
  ↓
LALA CLI (py -m lala.main)
  ↓
Orchestrator
  ↓
Model Router (Local Privacy Enforced)
  ↓
LocalProvider (http://127.0.0.1:11434)
  ↓
Ollama Runtime (Weights: F:\LALA\OllamaModels)
  ↓
Local LLM (qwen2.5:3b)
  ↓
Response Stream -> LALA
```

---

## 💾 Storage Architecture (`D:\LALA` vs `F:\LALA`)

- **Source Code Repository**: `D:\LALA` (Codebase, configs, tests)
- **Large AI Data Root**: `F:\LALA`
  - `F:\LALA\OllamaModels`: Ollama model weight storage (`OLLAMA_MODELS`)
  - `F:\LALA\Models`, `F:\LALA\Datasets`, `F:\LALA\Memory`, `F:\LALA\Logs`, `F:\LALA\Cache`, `F:\LALA\Backups`

---

## 🌐 Multilingual Support

LALA supports first-class multilingual interactions:
- **English**: Technical, conversational, and execution queries.
- **Hindi (हिंदी)**: Native conversational and task prompts.
- **Marathi (मराठी)**: Native conversational and task prompts.
- **Code-switching**: Natural fluid switching between English, Hindi, and Marathi in a single interaction.

---

## 🚀 Quick Start (Phase 2 Local Brain)

### Requirements
- **Python 3.11+**
- **Ollama** installed with `qwen2.5:3b` model weights in `F:\LALA\OllamaModels`.

### Running the CLI
```bash
py -m lala.main
```

### Diagnostics Commands inside CLI
- `/status` : View system health, Ollama endpoint, active model, storage paths, and privacy settings.
- `/model`  : View active local model details.
- `/lang hi`: Switch language context to Hindi (हिंदी).
- `/lang mr`: Switch language context to Marathi (मराठी).
- `/exit`   : Exit cleanly.

### Running Tests
```bash
# Run 100% offline test suite
py -m unittest discover -s tests

# Run optional integration test (when Ollama is online)
py -m unittest tests/test_integration_local.py
```

---

## 🛣️ Roadmap

- [x] **Phase 1**: Core Architecture & Lightweight Foundation (Interfaces, Security, Router, Offline CLI & Test Suite)
- [x] **Phase 2**: Local AI Brain & Hardware-aware Ollama Model Selection (`qwen2.5:3b` on `F:\LALA`)
- [ ] **Phase 3**: Persistent Memory & Vector RAG Integration
- [ ] **Phase 4**: Multilingual Offline Voice Pipeline (Whisper / TTS)
- [ ] **Phase 5**: Subagents, Computer Automation & Browser Control
