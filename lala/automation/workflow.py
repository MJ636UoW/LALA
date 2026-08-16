import uuid
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from lala.automation.models import WorkflowRun, WorkflowState, AutomationMode, ProposedAction, ActionClass
from lala.automation.policy import AutomationPolicyEngine
from lala.automation.executor import AutomationExecutor
from lala.automation.planner import AutomationPlanner
from lala.investigation.manager import InvestigationManager
from lala.utils.logging import logger

MAX_ACTIONS = 25
MAX_RUNTIME_SEC = 300

class AutonomousWorkflowEngine:
    """
    Deterministic Autonomous Investigation Workflow Engine for LALA Phase 10.
    Executes end-to-end cybersecurity investigations: Target Classification -> Evidence Collection -> Local RAG -> Static Analysis -> Threat Scoring -> Policy Evaluation.
    Enforces hard limits, loop protection, pause/resume/abort states.
    """
    def __init__(self, mode: AutomationMode = AutomationMode.SAFE):
        self.policy = AutomationPolicyEngine(mode=mode)
        self.executor = AutomationExecutor(policy=self.policy)
        self.planner = AutomationPlanner(policy=self.policy)
        self.investigation_mgr = InvestigationManager()
        self.active_runs: Dict[str, WorkflowRun] = {}
        self.is_paused = False

    def set_automation_mode(self, mode: AutomationMode):
        self.policy.set_mode(mode)
        self.executor.policy.set_mode(mode)

    def pause(self):
        self.is_paused = True
        logger.info("AutonomousWorkflowEngine: Execution PAUSED by user.")

    def resume(self):
        self.is_paused = False
        logger.info("AutonomousWorkflowEngine: Execution RESUMED by user.")

    def abort(self, run_id: str):
        if run_id in self.active_runs:
            self.active_runs[run_id].state = WorkflowState.ABORTED
            logger.info(f"AutonomousWorkflowEngine: Run '{run_id}' ABORTED by user.")

    def execute_investigation(self, target: str, parent_run_id: Optional[str] = None, dry_run: bool = False) -> WorkflowRun:
        run_id = f"run_{str(uuid.uuid4())[:8]}"
        case_id = f"case_{str(uuid.uuid4())[:8]}"
        start_dt = datetime.now(timezone.utc)
        deadline_dt = datetime.fromtimestamp(time.time() + MAX_RUNTIME_SEC, tz=timezone.utc)

        run = WorkflowRun(
            run_id=run_id,
            parent_run_id=parent_run_id,
            case_id=case_id,
            target=target,
            mode=self.policy.mode,
            state=WorkflowState.RUNNING,
            depth=1,
            start_time=start_dt.isoformat(),
            deadline=deadline_dt.isoformat()
        )
        self.active_runs[run_id] = run
        self.executor.dry_run = dry_run

        start_time_ts = time.time()

        try:
            # Stage 1: Case Creation
            case = self.investigation_mgr.create_case(title=f"Automated Investigation: {target}")
            
            proposals = self.planner.propose_investigation_steps(target)
            proposals.append(ProposedAction(action="create_report", target=target, risk_class=ActionClass.LOCAL_MODIFICATION, reason="Generate investigation report"))

            for proposal in proposals:
                if self.is_paused:
                    run.state = WorkflowState.WAITING_CONFIRMATION
                    break

                if time.time() - start_time_ts > MAX_RUNTIME_SEC:
                    run.state = WorkflowState.TIMEOUT
                    logger.warning(f"AutonomousWorkflowEngine: Run '{run_id}' TIMED OUT after {MAX_RUNTIME_SEC} seconds.")
                    break

                if run.action_count >= MAX_ACTIONS:
                    logger.warning(f"AutonomousWorkflowEngine: Run '{run_id}' reached MAX_ACTIONS limit ({MAX_ACTIONS}).")
                    break

                run.action_count += 1
                success, output, msg = self.executor.execute_proposal(run_id, case_id, proposal)
                
                run.executed_actions.append({
                    "step": run.action_count,
                    "action": proposal.action,
                    "target": proposal.target,
                    "risk_class": proposal.risk_class.value,
                    "success": success,
                    "message": msg,
                    "output": output
                })

                if not success and "USER_CONFIRMATION_REQUIRED" in msg:
                    run.state = WorkflowState.WAITING_CONFIRMATION
                    if isinstance(output, dict) and "approval_request" in output:
                        run.pending_approvals.append(output["approval_request"])

            if run.state == WorkflowState.RUNNING:
                run.state = WorkflowState.COMPLETED

        except Exception as e:
            logger.error(f"AutonomousWorkflowEngine Failure in run '{run_id}': {e}")
            run.state = WorkflowState.FAILED

        return run
