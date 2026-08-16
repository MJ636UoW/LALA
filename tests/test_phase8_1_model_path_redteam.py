import unittest
from lala.llm.manager import LocalLLMManager

class TestPhase81ModelPathRedTeam(unittest.TestCase):
    """9. Model Path Security & Canonicalization Red-Team Tests."""

    def test_model_path_traversal_and_unc_rejected(self):
        mgr = LocalLLMManager()
        self.assertFalse(mgr.is_path_within_models_root("..\\..\\Windows\\System32"))
        self.assertFalse(mgr.is_path_within_models_root("\\\\attacker-server\\share\\model.bin"))
        self.assertFalse(mgr.is_path_within_models_root("C:\\Windows\\System32"))

if __name__ == "__main__":
    unittest.main()
