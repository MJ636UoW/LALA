import unittest
from lala.llm.manager import LocalLLMManager

class TestLLMModelRegistry(unittest.TestCase):
    def test_manager_model_selection(self):
        mgr = LocalLLMManager()
        self.assertEqual(mgr.get_current_model(), "qwen2.5:3b")
        mgr.set_current_model("llama3:8b")
        self.assertEqual(mgr.get_current_model(), "llama3:8b")

if __name__ == "__main__":
    unittest.main()
