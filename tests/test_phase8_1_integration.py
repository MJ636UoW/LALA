import unittest
from lala.core.orchestrator import Orchestrator

class TestPhase81Integration(unittest.TestCase):
    """Integrated Phase 8.1 Verification Tests."""

    def test_orchestrator_local_llm_privacy_enforced(self):
        orch = Orchestrator()
        status = orch.local_llm_manager.get_status()
        self.assertTrue(status["local_only_mode"])
        self.assertFalse(status["cloud_fallback"])

if __name__ == "__main__":
    unittest.main()
