import unittest
from lala.automation.planner import AutomationPlanner

class TestAutomationPlanner(unittest.TestCase):
    def test_propose_investigation_steps(self):
        planner = AutomationPlanner()
        proposals = planner.propose_investigation_steps("suspicious_file.exe")
        self.assertGreater(len(proposals), 3)
        self.assertEqual(proposals[0].target, "suspicious_file.exe")

if __name__ == "__main__":
    unittest.main()
