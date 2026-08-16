import unittest
from lala.automation.workflow import AutonomousWorkflowEngine, WorkflowState

class TestAutomationWorkflow(unittest.TestCase):
    def test_execute_investigation_workflow(self):
        engine = AutonomousWorkflowEngine()
        run = engine.execute_investigation("sample_target.exe")
        self.assertIsNotNone(run.run_id)
        self.assertIn(run.state, [WorkflowState.COMPLETED, WorkflowState.WAITING_CONFIRMATION])
        self.assertGreater(len(run.executed_actions), 0)

if __name__ == "__main__":
    unittest.main()
