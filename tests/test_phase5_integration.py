import unittest
from lala.core.orchestrator import Orchestrator

class TestLalaPhase5Integration(unittest.TestCase):
    def test_orchestrator_workspace_integration(self):
        """Verify Phase 5 Orchestrator initializes WorkspaceScanner and TaskPlanner."""
        orch = Orchestrator()
        self.assertIsNotNone(orch.workspace_scanner)
        self.assertIsNotNone(orch.task_planner)
        self.assertIsNotNone(orch.agent_executor)

    def test_workspace_tool_execution(self):
        """Verify WorkspaceScanTool execution through tool registry."""
        orch = Orchestrator()
        res = orch.tools.execute_tool("workspace_scan", path="D:\\LALA")
        self.assertTrue(res.success)
        self.assertEqual(res.output["project_type"], "PYTHON")

if __name__ == "__main__":
    unittest.main()
