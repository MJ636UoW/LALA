import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
from lala.utils.logging import logger

SECRET_KEYS = ["api_key", "secret", "password", "token", "auth", "virustotal_key", "abuseipdb_key", "otx_key", "nvd_key"]

class AutomationAuditLogger:
    """
    Audit Logger for LALA Phase 10 Autonomous Operations.
    Appends structured, immutable audit log entries to F:\\LALA\\Logs\\lala_automation.log.
    Sanitizes raw secrets and credentials.
    """
    def __init__(self, log_path: str = "F:\\LALA\\Logs\\lala_automation.log"):
        self.log_path = log_path
        self._init_dir()

    def _init_dir(self):
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        except Exception:
            pass

    def sanitize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        clean = {}
        for k, v in entry.items():
            if any(s in k.lower() for s in SECRET_KEYS):
                clean[k] = "[REDACTED_SECRET]"
            elif isinstance(v, str) and any(s in v.lower() for s in SECRET_KEYS):
                clean[k] = "[REDACTED_SECRET_STRING]"
            else:
                clean[k] = v
        return clean

    def log_action(self, run_id: str, case_id: str, action: str, target: str, risk: str, decision: str, result: str, provider: str = "local", retry_count: int = 0):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
            "case_id": case_id,
            "action": action,
            "target": target,
            "risk": risk,
            "decision": decision,
            "result": result,
            "provider": provider,
            "retry_count": retry_count
        }
        sanitized = self.sanitize_entry(entry)
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(sanitized) + "\n")
        except Exception as e:
            logger.error(f"AutomationAuditLogger Write Error: {e}")
