from typing import Dict, Any, Optional
from lala.agent.task import TaskStep, TaskRisk
from lala.utils.logging import logger

MAX_RETRIES = 2

class TaskRecoveryManager:
    """
    Automatic Recovery Manager for LALA Agent tasks.
    Performs error classification and safe retries (MAX_RETRIES = 2).
    Never retries destructive operations, permission denials, or security blocks automatically.
    """
    def __init__(self):
        self.retry_counts: Dict[str, int] = {}

    def should_retry(self, step: TaskStep, error_message: str) -> bool:
        # Never retry security permission denials or privileged rejections
        if "Security Policy Denied" in error_message or "Access Denied" in error_message or "USER_CONFIRMATION_REQUIRED" in error_message:
            logger.info(f"Recovery Engine: Refusing automatic retry for security permission denial: '{error_message}'")
            return False

        # Never retry destructive operations automatically
        if step.risk in [TaskRisk.DESTRUCTIVE, TaskRisk.PRIVILEGED]:
            logger.info(f"Recovery Engine: Refusing automatic retry for {step.risk.value} risk step.")
            return False

        step_key = f"{step.step_number}_{step.tool}"
        current_retries = self.retry_counts.get(step_key, 0)
        
        if current_retries < MAX_RETRIES:
            self.retry_counts[step_key] = current_retries + 1
            logger.info(f"Recovery Engine: Scheduling safe retry attempt {current_retries + 1}/{MAX_RETRIES} for step '{step.action}'")
            return True

        return False
