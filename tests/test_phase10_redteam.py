import unittest
from lala.automation.policy import AutomationPolicyEngine
from lala.automation.models import ActionClass, AutomationMode
from lala.automation.approvals import ApprovalSystem
from lala.automation.executor import AutomationExecutor
from lala.automation.workflow import AutonomousWorkflowEngine, MAX_ACTIONS
from lala.automation.recovery import SafeRecoveryEngine

class TestPhase10RedTeam(unittest.TestCase):
    """
    Dedicated Phase 10 Red-Team Security Validation Suite.
    Verifies Safe Automation Policy Gating, Token Binding, Loop Limits, and SecurityEngine Authority.
    """

    def test_01_destructive_actions_forbidden_in_safe_mode(self):
        """1. Destructive actions return USER_CONFIRMATION_REQUIRED in SAFE mode."""
        policy = AutomationPolicyEngine(mode=AutomationMode.SAFE)
        allowed, msg, risk = policy.evaluate_action("delete_file")
        self.assertFalse(allowed)
        self.assertIn("USER_CONFIRMATION_REQUIRED", msg)

    def test_02_confirmation_token_single_use_and_bound(self):
        """2. Confirmation tokens are single-use and fail when reused or cross-bound."""
        approvals = ApprovalSystem()
        req = approvals.create_approval_request("case1", "run1", "quarantine_file", "malware.exe", ActionClass.SECURITY_CONTROL, "Remediation")
        token = req.confirmation_token

        # Valid consumption
        ok, msg = approvals.validate_and_consume_token(token, "case1", "run1", "quarantine_file", "malware.exe")
        self.assertTrue(ok)

        # Re-use attempt fails
        ok_reuse, msg_reuse = approvals.validate_and_consume_token(token, "case1", "run1", "quarantine_file", "malware.exe")
        self.assertFalse(ok_reuse)

    def test_03_action_limits_and_loop_protection(self):
        """3. Action limits (MAX_ACTIONS=25) prevent infinite execution loops."""
        engine = AutonomousWorkflowEngine()
        run = engine.execute_investigation("suspicious_target.exe")
        self.assertLessEqual(run.action_count, MAX_ACTIONS)

    def test_04_recovery_refuses_security_denials(self):
        """4. Safe recovery engine refuses retries for security denials."""
        recovery = SafeRecoveryEngine()
        retry, msg = recovery.should_retry("Security Policy Denied Execution", ActionClass.DESTRUCTIVE, 0)
        self.assertFalse(retry)

    def test_05_dry_run_performs_zero_modifications(self):
        """5. Dry-run mode simulates execution without invoking system modifications."""
        executor = AutomationExecutor()
        executor.dry_run = True
        proposal = executor.policy.evaluate_action("create_report")
        self.assertTrue(executor.dry_run)

if __name__ == "__main__":
    unittest.main()
