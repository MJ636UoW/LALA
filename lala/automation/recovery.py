from typing import Tuple
from lala.automation.models import ActionClass
from lala.utils.logging import logger

MAX_RECOVERY_ATTEMPTS = 2

class SafeRecoveryEngine:
    """
    Safe Recovery Engine for LALA Phase 10.
    Retries ONLY transient network or cache errors (max 2 attempts).
    Strictly refuses automatic retries for security permission denials, confirmation requirements, or policy violations.
    """
    def should_retry(self, error_message: str, risk_class: ActionClass, current_attempts: int) -> Tuple[bool, str]:
        if current_attempts >= MAX_RECOVERY_ATTEMPTS:
            return False, f"Recovery Refusal: Exceeded maximum recovery attempts ({current_attempts}/{MAX_RECOVERY_ATTEMPTS})."

        err_lower = error_message.lower()

        # Security/Permission denials -> Refuse retry
        if "denied" in err_lower or "permission" in err_lower or "unauthorized" in err_lower or "confirmation_required" in err_lower:
            logger.info("SafeRecoveryEngine: Refusing automatic retry for security permission denial.")
            return False, "Recovery Refusal: Automatic retries forbidden for security permission denials."

        if risk_class in [ActionClass.SECURITY_CONTROL, ActionClass.DESTRUCTIVE]:
            return False, f"Recovery Refusal: Automatic retries forbidden for high-risk action class '{risk_class.value}'."

        # Transient errors -> Allow retry
        if "timeout" in err_lower or "connection refused" in err_lower or "temporarily unavailable" in err_lower:
            return True, f"Recovery Authorized: Scheduling safe retry attempt {current_attempts + 1}/{MAX_RECOVERY_ATTEMPTS}."

        return False, "Recovery Refusal: Non-retryable error type."
