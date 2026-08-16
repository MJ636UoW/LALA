from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class RemediationActionType(str, Enum):
    QUARANTINE_FILE = "QUARANTINE_FILE"
    BLOCK_IP = "BLOCK_IP"
    BLOCK_DOMAIN = "BLOCK_DOMAIN"
    ISOLATE_HOST = "ISOLATE_HOST"
    KILL_PROCESS = "KILL_PROCESS"
    DISABLE_PERSISTENCE = "DISABLE_PERSISTENCE"
    ROTATE_CREDENTIALS = "ROTATE_CREDENTIALS"

class RemediationCheckResult(BaseModel):
    allowed: bool
    requires_user_confirmation: bool = True
    reason: str
    action_type: RemediationActionType
    target: str

class RemediationPolicyEngine:
    """
    Remediation Policy Engine for LALA Phase 7.
    Enforces strict confirmation gating for all corrective defensive actions.
    No automatic remediation execution is ever permitted without explicit user confirmation.
    """
    def evaluate_remediation(self, action_type: RemediationActionType, target: str, is_user_confirmed: bool = False) -> RemediationCheckResult:
        if not is_user_confirmed:
            return RemediationCheckResult(
                allowed=False,
                requires_user_confirmation=True,
                reason=f"Remediation Action '{action_type.value}' on target '{target}' requires explicit user confirmation.",
                action_type=action_type,
                target=target
            )

        return RemediationCheckResult(
            allowed=True,
            requires_user_confirmation=True,
            reason=f"User explicitly authorized remediation action '{action_type.value}' on target '{target}'.",
            action_type=action_type,
            target=target
        )
