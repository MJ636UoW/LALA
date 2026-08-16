# LALA Tool Registry & Safety Catalog

System Identity: **LALA**  
Target User: **Mandar**

---

## 🛠️ Registered Tools & Permission Tiering

| Tool Name | Category | Permission Tier | Path / Execution Security |
| :--- | :--- | :--- | :--- |
| **`system_info`** | System | `SAFE_AUTOMATIC` | Safe CPU, RAM, GPU, and disk read |
| **`file_list`** | Filesystem | `READ_ONLY` | Rejects path traversal (`../../`, UNC, system dirs) |
| **`file_read`** | Filesystem | `READ_ONLY` | Rejects path traversal; reads text files |
| **`file_search`** | Filesystem | `READ_ONLY` | Pattern search within workspace |
| **`python_analysis`** | Analysis | `READ_ONLY` | Safe AST parsing; blocks `os.system`, `eval`, `exec` |
| **`safe_command`** | System | `READ_ONLY` | Whitelisted commands (`python --version`, `git status`, `ollama list`) |
| **`git_tool`** | VCS | `READ_ONLY` / `CONFIRM` | Read status/log automatic; commit/push requires approval |
| **`file_edit`** | Filesystem | `USER_CONFIRMATION_REQUIRED` | Generates diff preview before writing changes |
| **`web_search`** | Web | `CONFIRM` | Interface stub (100% local privacy) |
