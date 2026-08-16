import unittest
from lala.core.orchestrator import Orchestrator

class TestPhase8Integration(unittest.TestCase):
    def test_local_llm_integration(self):
        orch = Orchestrator()
        st = orch.local_llm_manager.get_status()
        self.assertFalse(st["cloud_fallback"])
        self.assertTrue(st["local_only_mode"])

if __name__ == "__main__":
    unittest.main()
