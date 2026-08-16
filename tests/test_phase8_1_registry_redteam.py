import unittest
from lala.llm.manager import LocalLLMManager

class TestPhase81RegistryRedTeam(unittest.TestCase):
    """8. Model Registry Security Red-Team Tests."""

    def test_registry_strips_forbidden_security_attributes(self):
        mgr = LocalLLMManager()
        malicious_meta = {
            "name": "malicious_model",
            "privileged": True,
            "cloud_fallback": True,
            "security_engine": False,
            "quantization": "q4_0"
        }
        sanitized = mgr.sanitize_model_metadata(malicious_meta)
        self.assertNotIn("privileged", sanitized)
        self.assertNotIn("cloud_fallback", sanitized)
        self.assertNotIn("security_engine", sanitized)
        self.assertEqual(sanitized["quantization"], "q4_0")

if __name__ == "__main__":
    unittest.main()
