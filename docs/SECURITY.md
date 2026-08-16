# LALA Security Model & Audit Specifications

System Identity: **LALA**  
Target User: **Mandar**

---

## 🔐 Permission Levels

1. **`SAFE_AUTOMATIC`**: Read-only system queries (`SystemInfoTool`).
2. **`READ_ONLY`**: Path-sanitized file reading, file listing, code static analysis.
3. **`USER_CONFIRMATION_REQUIRED`**: File edits (`FileEditTool`), git commits (`GitTool`), risky shell commands. Requires explicit user confirmation.
4. **`PRIVILEGED`**: Unrestricted shell or process kill. **Disabled**.

---

## 📜 Append-Only Security Audit Trail (`F:\LALA\Logs\lala_security.log`)

Every tool evaluation and execution produces an immutable audit event:
```text
2026-08-16 11:20:00 UTC | USER:Mandar | TOOL:file_read | TARGET:D:\LALA\README.md | PERMISSION:READ_ONLY | RESULT:SUCCESS
```
