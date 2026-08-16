import unittest
from lala.core.orchestrator import Orchestrator

class TestLLMOrchestrator(unittest.TestCase):
    def test_orchestrator_initializes_local_llm_manager(self):
        orch = Orchestrator()
        self.assertIsNotNone(orch.local_llm_manager)
        self.assertEqual(orch.local_llm_manager.get_current_model(), "qwen2.5:3b")

if __name__ == "__main__":
    unittest.main()
