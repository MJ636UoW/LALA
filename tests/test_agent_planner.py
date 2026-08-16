import unittest
from lala.agent.planner import TaskPlanner
from lala.agent.task import TaskRisk

class TestLalaAgentPlanner(unittest.TestCase):
    def test_structured_plan_creation(self):
        """Verify TaskPlanner creates structured risk-classified plans."""
        planner = TaskPlanner()
        plan = planner.create_plan_for_goal("Analyze Python project security")
        self.assertGreater(len(plan.steps), 0)
        self.assertEqual(plan.steps[0].risk, TaskRisk.SAFE)

    def test_risk_classification(self):
        """Verify tool risk level classification."""
        planner = TaskPlanner()
        self.assertEqual(planner.classify_risk("system_info", {}), TaskRisk.SAFE)
        self.assertEqual(planner.classify_risk("file_read", {}), TaskRisk.READ_ONLY)
        self.assertEqual(planner.classify_risk("file_edit", {}), TaskRisk.MODIFY)
        self.assertEqual(planner.classify_risk("git_tool", {"subcommand": "commit"}), TaskRisk.MODIFY)

if __name__ == "__main__":
    unittest.main()
