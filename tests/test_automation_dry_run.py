import unittest
from lala.automation.executor import AutomationExecutor
from lala.automation.models import ProposedAction, ActionClass

class TestAutomationDryRun(unittest.TestCase):
    def test_dry_run_mode_simulation(self):
        executor = AutomationExecutor()
        executor.dry_run = True
        proposal = ProposedAction(action="delete_file", target="sample.exe", risk_class=ActionClass.DESTRUCTIVE, reason="Test dry run")
        success, out, msg = executor.execute_proposal("run1", "case1", proposal)
        self.assertTrue(success)
        self.assertEqual(msg, "DRY_RUN_SIMULATED")

if __name__ == "__main__":
    unittest.main()
