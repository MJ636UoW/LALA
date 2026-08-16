import unittest
from lala.core.orchestrator import Orchestrator

class TestPhase7Integration(unittest.TestCase):
    def test_orchestrator_phase7_tools_registered(self):
        orch = Orchestrator()
        self.assertIsNotNone(orch.tools.get_tool("investigate_ioc"))
        self.assertIsNotNone(orch.tools.get_tool("yara_scan"))
        self.assertIsNotNone(orch.tools.get_tool("sigma_rules"))

    def test_execute_investigate_tool(self):
        orch = Orchestrator()
        res = orch.tools.execute_tool("investigate_ioc", target="1.1.1.1")
        self.assertTrue(res.success)
        self.assertEqual(res.output["target"]["value"], "1.1.1.1")

if __name__ == "__main__":
    unittest.main()
