# LALA Architecture Specification

System Identity: **LALA**  
Target User: **Mandar**

This document specifies the internal module contracts and design guidelines for the 12 subsystems of LALA.

---

## Subsystem Details

### 1. Orchestrator (`lala/core/orchestrator.py`)
- **Role**: Coordinates the core interaction flow.
- **Responsibilities**:
  - Receives user input (text or audio transcription).
  - Maintains active session state and language context.
  - Constructs system prompt via `PersonalityManager`.
  - Dispatches queries to `ModelRouter`.
  - Checks safety policy via `SecurityEngine` before tool execution.

### 2. Model Router (`lala/core/router.py`)
- **Role**: Provider abstraction layer.
- **Providers**:
  - `LocalProvider` (Ollama for offline processing in Phase 2)
  - `GeminiProvider`
  - `ClaudeProvider`
  - `OpenAICompatibleProvider`
- **Fallback Logic**: Prioritizes local providers when available or offline mode is requested; falls back to configured cloud endpoints gracefully.

### 3. Memory (`lala/memory/interface.py`)
- **Role**: Context and memory storage abstraction.
- **Components**:
  - `ConversationContext`: In-memory thread history for active sessions.
  - `MemoryItem`: Abstract schema for persistent key-value and vector memories.
  - `MemoryStore`: Abstract interface for storage implementations (SQLite/Vector DB in Phase 3).

### 4. Voice (`lala/voice/interface.py`)
- **Role**: Multilingual audio processing abstraction.
- **Interfaces**:
  - `SpeechToTextInterface`: Input audio stream -> text string conversion.
  - `TextToSpeechInterface`: Response text string -> output audio stream.
- *Phase 1 includes lightweight stub contracts.*

### 5. Tools (`lala/tools/`)
- **Role**: Extensible tool execution framework.
- **Structure**:
  - `Tool`: Base class with explicit name, description, parameters, and `PermissionLevel`.
  - `ToolRegistry`: Registry managing registered tools and enforcing authorization before invocation.

### 6. API Registry (`lala/api/registry.py`)
- **Role**: Manages model provider endpoints, capability flags, and service metadata.

### 7. Security (`lala/security/permissions.py`)
- **Role**: Safety and access control engine.
- **Permission Levels**:
  1. `SAFE_AUTOMATIC`: Read-only system queries, formatting, basic logic.
  2. `READ_ONLY`: File reading, search operations.
  3. `USER_CONFIRMATION_REQUIRED`: Modifying files, sending network requests.
  4. `PRIVILEGED`: System/shell administrative execution (Disabled in Phase 1).

### 8. Personality / Emotion (`lala/personality/emotion.py`)
- **Role**: Enforces system identity ("LALA") and user relationship ("Mandar").
- **Language Mode**: Embeds dynamic instructions for English, Hindi (हिंदी), and Marathi (मराठी) code-switching.

### 9. Subagents (`lala/subagents/base.py`)
- **Role**: Multi-agent task decomposition and delegation abstraction.
- **Base Class**: `BaseSubagent` defining `run()` and status lifecycle.

### 10. Configuration (`lala/core/config.py`)
- **Role**: Strongly typed configuration management using Pydantic and PyYAML reading `config/default_config.yaml`.

### 11. Logging (`lala/utils/logging.py`)
- **Role**: Structured console logging utility.

### 12. UI (`lala/ui/cli.py`)
- **Role**: User-facing Rich terminal interface supporting interactive messaging, language context indicators, and clean session shutdown.
