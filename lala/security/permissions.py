import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from pydantic import BaseModel
from lala.utils.logging import logger

class PermissionLevel(str, Enum):
    SAFE_AUTOMATIC = "SAFE_AUTOMATIC"
    READ_ONLY = "READ_ONLY"
    USER_CONFIRMATION_REQUIRED = "USER_CONFIRMATION_REQUIRED"
    PRIVILEGED = "PRIVILEGED"

class SecurityCheckResult(BaseModel):
    allowed: bool
    permission_level: PermissionLevel
    reason: str

class SecurityEngine:
    """
    Security authorization engine for LALA.
    Enforces permission policies prior to tool or agent execution.
    Privileged execution, cloud fallback activation, and policy self-modification are strictly forbidden.
    Logs all security events to F:\\LALA\\Logs\\lala_security.log.
    """
    def __init__(self, allow_privileged: bool = False, log_path: str = "F:\\LALA\\Logs\\lala_security.log"):
        self.allow_privileged = False # Hardened immutability: Privileged execution permanently disabled
        self.log_path = Path(log_path)
        self._init_log()

    def _init_log(self):
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def audit(self, user: str, tool_name: str, target: str, permission: str, result: str):
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            log_line = f"{timestamp} | USER:{user} | TOOL:{tool_name} | TARGET:{target} | PERMISSION:{permission} | RESULT:{result}\n"
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            logger.debug(f"Audit log write failed: {e}")

    def authorize(self, tool_name: str, permission_level: PermissionLevel) -> SecurityCheckResult:
        return self.evaluate(tool_name, permission_level)

    def request_confirmation(self, action_description: str) -> bool:
        logger.info(f"User Confirmation Prompt: {action_description}")
        return False

    def evaluate(self, tool_name: str, permission_level: PermissionLevel) -> SecurityCheckResult:
        # Check self-modification or privilege escalation attempts
        if permission_level == PermissionLevel.PRIVILEGED:
            logger.warning(f"Access Denied: Tool '{tool_name}' requested PRIVILEGED execution, which is strictly disabled in LALA policy.")
            self.audit(user="SYSTEM", tool_name=tool_name, target="SecurityEngine", permission="PRIVILEGED", result="DENIED")
            return SecurityCheckResult(
                allowed=False,
                permission_level=permission_level,
                reason="PRIVILEGED execution is strictly disabled in LALA security policy."
            )

        if permission_level == PermissionLevel.USER_CONFIRMATION_REQUIRED:
            return SecurityCheckResult(
                allowed=False,
                permission_level=permission_level,
                reason="USER_CONFIRMATION_REQUIRED requires explicit Mandar approval."
            )

        return SecurityCheckResult(
            allowed=True,
            permission_level=permission_level,
            reason="Action authorized within allowed permission boundaries."
        )
