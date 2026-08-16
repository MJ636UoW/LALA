import unittest
from lala.automation.executor import AutomationExecutor
from lala.automation.models import ProposedAction, ActionClass

class TestAutomationExecutor(unittest.TestCase):
    def test_execute_read_only_proposal(self):
        executor = AutomationExecutor()
        proposal = ProposedAction(action="read_file", target="D:\\LALA\\README.md", risk_class=ActionClass.READ_ONLY, reason="Test read")
        success, output, msg = executor.execute_proposal("run1", "case1", proposal)
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
