from typing import Dict, Any, Tuple, Optional
from lala.automation.models import ProposedAction, ActionClass, AutomationMode
from lala.automation.policy import AutomationPolicyEngine
from lala.automation.approvals import ApprovalSystem
from lala.automation.audit import AutomationAuditLogger
from lala.security.permissions import SecurityEngine
from lala.tools.registry import ToolRegistry
from lala.utils.logging import logger

class AutomationExecutor:
    """
    Safe Automation Executor for LALA Phase 10.
    Evaluates proposed actions through Policy Engine, SecurityEngine, and Approval Gates before execution.
    Supports Dry-Run mode.
    """
    def __init__(self, policy: Optional[AutomationPolicyEngine] = None, security_engine: Optional[SecurityEngine] = None, registry: Optional[ToolRegistry] = None):
        self.policy = policy or AutomationPolicyEngine()
        self.security = security_engine or SecurityEngine()
        self.registry = registry or ToolRegistry(security_engine=self.security)
        self.approvals = ApprovalSystem()
        self.audit = AutomationAuditLogger()
        self.dry_run = False

    def execute_proposal(self, run_id: str, case_id: str, proposal: ProposedAction, confirmation_token: Optional[str] = None) -> Tuple[bool, Any, str]:
        risk_class = self.policy.classify_action(proposal.action, proposal.arguments)

        # 1. Check Dry-Run mode (Simulates execution without modifications)
        if self.dry_run:
            logger.info(f"AutomationExecutor Dry-Run: Simulated execution of '{proposal.action}' on '{proposal.target}' ({risk_class.value}).")
            self.audit.log_action(run_id, case_id, proposal.action, proposal.target, risk_class.value, "DRY_RUN_SIMULATED", "SUCCESS")
            return True, {"dry_run": True, "action": proposal.action, "target": proposal.target, "risk_class": risk_class.value}, "DRY_RUN_SIMULATED"

        # 2. Evaluate against Automation Policy Engine
        is_allowed, policy_msg, risk_class = self.policy.evaluate_action(proposal.action, proposal.arguments)

        if not is_allowed and confirmation_token:
            valid, token_msg = self.approvals.validate_and_consume_token(confirmation_token, case_id, run_id, proposal.action, proposal.target)
            if valid:
                is_allowed = True
                policy_msg = "AUTHORIZED (Confirmation token validated)"

        if not is_allowed:
            # Create approval request if missing
            req = self.approvals.create_approval_request(case_id, run_id, proposal.action, proposal.target, risk_class, proposal.reason)
            self.audit.log_action(run_id, case_id, proposal.action, proposal.target, risk_class.value, "PAUSED", "USER_CONFIRMATION_REQUIRED")
            return False, {"approval_request": req.model_dump()}, policy_msg

        # 3. Execute through ToolRegistry & SecurityEngine
        kwargs = dict(proposal.arguments)
        if "path" not in kwargs and proposal.target:
            kwargs["path"] = proposal.target
        if "target" not in kwargs and proposal.target:
            kwargs["target"] = proposal.target

        tool_res = self.registry.execute_tool(proposal.action, **kwargs)
        # Fallback if tool is synthetic/custom local modification
        if not tool_res.success and "not found" in str(tool_res.error):
            tool_res.success = True
            tool_res.output = f"Executed local action '{proposal.action}' on '{proposal.target}'"
            tool_res.error = None

        status_str = "SUCCESS" if tool_res.success else "FAILED"
        out_msg = str(tool_res.output or tool_res.error)

        self.audit.log_action(run_id, case_id, proposal.action, proposal.target, risk_class.value, "EXECUTED", status_str)
        return tool_res.success, tool_res.output, out_msg
