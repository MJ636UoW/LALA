# LALA Architecture Specification

System Identity: **LALA**  
Target User: **Mandar**

This document specifies internal module contracts and design guidelines for LALA Phase 2.

---

## 🏛️ Local Pipeline Execution Flow

```text
User
  ↓
LALA CLI (lala/ui/cli.py)
  ↓
Orchestrator (lala/core/orchestrator.py)
  ↓
Model Router (lala/core/router.py - Local Privacy Enforced)
  ↓
LocalProvider (lala/core/providers/local.py -> http://127.0.0.1:11434)
  ↓
Ollama Engine (Model storage: F:\LALA\OllamaModels)
  ↓
Local LLM (qwen2.5:3b)
  ↓
Response Stream -> LALA
```

---

## Subsystem Specification

### 1. Orchestrator (`lala/core/orchestrator.py`)
- Coordinates interaction flow.
- Maintains session history and multilingual context.
- Builds prompt via `PersonalityManager`.
- Dispatches query to `ModelRouter`.

### 2. Model Router (`lala/core/router.py`)
- Enforces `LocalProvider` (`qwen2.5:3b`) as default.
- `cloud_fallback: false` strictly enforced.
- Returns explicit error when local Ollama brain is unreachable, preventing cloud data leaks.

### 3. Storage System (`lala/core/config.py`)
- Codebase & configs: `D:\LALA`
- AI data root: `F:\LALA`
  - `F:\LALA\OllamaModels`
  - `F:\LALA\Models`
  - `F:\LALA\Datasets`
  - `F:\LALA\Memory`
  - `F:\LALA\Logs`
  - `F:\LALA\Cache`
  - `F:\LALA\Backups`

### 4. Security (`lala/security/permissions.py`)
- Permission levels: `SAFE_AUTOMATIC`, `READ_ONLY`, `USER_CONFIRMATION_REQUIRED`, `PRIVILEGED`.
- No privileged system execution in Phase 2.

### 5. Personality / Emotion (`lala/personality/emotion.py`)
- Identity: `LALA` serving `Mandar`.
- Persona: intelligent, calm, helpful, technically precise, subtly witty, honest about limitations.
- Multilingual instructions for English, Hindi (हिंदी), and Marathi (मराठी) code-switching.

### 6. Memory & Voice Interfaces (`lala/memory/`, `lala/voice/`)
- Abstract interfaces for Phase 3 (RAG) and Phase 4 (Audio pipeline).
