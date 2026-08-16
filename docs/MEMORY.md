# LALA Persistent Memory Subsystem Specification

System Identity: **LALA**  
Target User: **Mandar**

---

## 💾 Storage Architecture (`F:\LALA\Memory\lala_memory.db`)

LALA implements a lightweight local persistent memory architecture powered by **SQLite** and **FTS5 full-text indexing**.
- **Database Path**: `F:\LALA\Memory\lala_memory.db`
- **Embeddings Location**: `F:\LALA\Models\Embeddings`

---

## 🔒 Memory Categories & Privacy Policy

| Category | Storage Behavior | User Confirmation |
| :--- | :--- | :--- |
| **`TEMPORARY`** | Transient execution data | Not persisted |
| **`SESSION`** | Active session history | Cleared on exit unless explicitly saved |
| **`PERSISTENT`** | Stored in SQLite (`lala_memory.db`) | Explicit user confirmation required |
| **`SENSITIVE`** | Never automatically saved | Strictly blocked from disk persistence |

---

## 🛠️ CLI Memory Commands

- `/memory` : Display memory statistics and DB status.
- `/memory save <text>` : Permanently store a fact in SQLite memory.
- `/memory search <query>` : Perform SQLite FTS5 full-text search.
- `/memory forget <query>` : Delete matching persistent memory entries.
