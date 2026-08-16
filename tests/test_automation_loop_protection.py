import unittest
from lala.automation.workflow import AutonomousWorkflowEngine

class TestAutomationLoopProtection(unittest.TestCase):
    def test_loop_action_count_capped(self):
        engine = AutonomousWorkflowEngine()
        run = engine.execute_investigation("target.exe")
        self.assertLessEqual(run.action_count, 25)

if __name__ == "__main__":
    unittest.main()
