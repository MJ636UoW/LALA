import unittest
from lala.core.orchestrator import Orchestrator

class TestPhase6Integration(unittest.TestCase):
    def test_orchestrator_intel_initialization(self):
        orch = Orchestrator()
        self.assertIsNotNone(orch.intel_manager)
        self.assertIsNotNone(orch.investigation_manager)
        self.assertIsNotNone(orch.tools.get_tool("intel_lookup"))
        self.assertIsNotNone(orch.tools.get_tool("cve_lookup"))
        self.assertIsNotNone(orch.tools.get_tool("mitre_lookup"))

    def test_intel_lookup_tool_execution(self):
        orch = Orchestrator()
        orch.intel_manager.set_online_enabled(True)
        res = orch.tools.execute_tool("intel_lookup", ioc_type="IP", value="1.1.1.1")
        self.assertTrue(res.success)
        self.assertEqual(res.output["provider"], "IntelligenceManager")

if __name__ == "__main__":
    unittest.main()
