import unittest
from lala.core.orchestrator import Orchestrator

class TestPhase9Integration(unittest.TestCase):
    def test_orchestrator_initializes_local_rag_manager(self):
        orch = Orchestrator()
        self.assertIsNotNone(orch.rag_manager)
        status = orch.rag_manager.get_status()
        self.assertTrue(status["offline_mode"])
        self.assertFalse(status["cloud_rag"])

if __name__ == "__main__":
    unittest.main()
