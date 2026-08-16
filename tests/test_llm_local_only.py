import unittest
from lala.llm.privacy import LocalLLMPrivacyEngine

class TestLLMLocalOnly(unittest.TestCase):
    def test_local_endpoint_validation(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertTrue(privacy.is_local_endpoint("http://127.0.0.1:11434"))
        self.assertTrue(privacy.is_local_endpoint("http://localhost:11434"))
        self.assertTrue(privacy.is_local_endpoint("http://127.0.0.1:8080"))

    def test_reject_cloud_endpoints(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertFalse(privacy.is_local_endpoint("https://api.openai.com/v1"))
        self.assertFalse(privacy.is_local_endpoint("https://api.anthropic.com"))
        self.assertFalse(privacy.is_local_endpoint("https://generativelanguage.googleapis.com"))
        self.assertFalse(privacy.is_local_endpoint("http://8.8.8.8:11434"))

if __name__ == "__main__":
    unittest.main()
