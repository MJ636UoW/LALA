from typing import Dict, Any, List
from lala.automation.workflow import AutonomousWorkflowEngine
from lala.automation.models import WorkflowRun

class AutomationScheduler:
    """
    Scheduler & Task Coordinator for LALA Phase 10 Autonomous Investigations.
    Coordinates workflow runs and status tracking.
    """
    def __init__(self, workflow_engine: Optional[AutonomousWorkflowEngine] = None):
        self.engine = workflow_engine or AutonomousWorkflowEngine()

    def run_investigation(self, target: str, dry_run: bool = False) -> WorkflowRun:
        return self.engine.execute_investigation(target=target, dry_run=dry_run)

    def get_status(self) -> Dict[str, Any]:
        return {
            "automation_mode": self.engine.policy.mode.value,
            "is_paused": self.engine.is_paused,
            "active_runs": len(self.engine.active_runs),
            "max_actions_per_run": 25,
            "max_runtime_seconds": 300
        }
