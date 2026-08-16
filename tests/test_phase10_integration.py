import unittest
from lala.core.orchestrator import Orchestrator

class TestPhase10Integration(unittest.TestCase):
    def test_orchestrator_automation_integration(self):
        orch = Orchestrator()
        self.assertIsNotNone(orch.automation)
        status = orch.automation.policy.mode.value
        self.assertEqual(status, "SAFE")

if __name__ == "__main__":
    unittest.main()
