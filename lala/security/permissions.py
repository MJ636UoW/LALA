from enum import Enum
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
    Privileged execution is strictly forbidden in Phase 1.
    """
    def __init__(self, allow_privileged: bool = False):
        self.allow_privileged = allow_privileged

    def evaluate(self, tool_name: str, permission_level: PermissionLevel) -> SecurityCheckResult:
        if permission_level == PermissionLevel.PRIVILEGED:
            if not self.allow_privileged:
                logger.warning(f"Access denied: Tool '{tool_name}' requires PRIVILEGED execution, which is disabled in Phase 1.")
                return SecurityCheckResult(
                    allowed=False,
                    permission_level=permission_level,
                    reason="PRIVILEGED execution is disabled in Phase 1 foundation."
                )

        if permission_level == PermissionLevel.USER_CONFIRMATION_REQUIRED:
            return SecurityCheckResult(
                allowed=False,
                permission_level=permission_level,
                reason="USER_CONFIRMATION_REQUIRED requires explicit user approval."
            )

        return SecurityCheckResult(
            allowed=True,
            permission_level=permission_level,
            reason="Action authorized within allowed permission boundaries."
        )
