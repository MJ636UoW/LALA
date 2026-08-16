# LALA Multi-Step Agent Execution Architecture

System Identity: **LALA**  
Target User: **Mandar**

---

## 🔄 Agent Execution Loop Diagram

```text
USER (CLI / Voice)
       ↓
ORCHESTRATOR
       ↓
MEMORY RETRIEVAL (SQLite FTS5 F:\LALA\Memory)
       ↓
MODEL ROUTER (Local Ollama qwen2.5:3b)
       ↓
TOOL PLANNER (Parse structured JSON tool request)
       ↓
SECURITY ENGINE (Permission & Audit check)
       ↓
TOOL EXECUTOR (Execute validated tool)
       ↓
RESULT INJECTION (Pass tool output back to LLM)
       ↓
MODEL (Formulate final answer)
       ↓
OUTPUT (CLI / Sentence-Level Streaming Voice TTS)
```

- **Maximum Tool Iterations**: `MAX_TOOL_ITERATIONS = 5`
- **Voice / CLI Parity**: Voice Pipeline and CLI use identical Orchestrator, Memory, Tools, and Security Engine.
