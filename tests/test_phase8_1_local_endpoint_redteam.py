import unittest
from lala.llm.privacy import LocalLLMPrivacyEngine

class TestPhase81LocalEndpointRedTeam(unittest.TestCase):
    """1. Local LLM Endpoint Hardening Red-Team Tests."""

    def test_loopback_ips_accepted(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertTrue(privacy.is_local_endpoint("http://127.0.0.1:11434"))
        self.assertTrue(privacy.is_local_endpoint("http://127.0.0.2:11434"))
        self.assertTrue(privacy.is_local_endpoint("http://localhost:11434"))

    def test_lan_and_public_ips_rejected(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertFalse(privacy.is_local_endpoint("http://192.168.1.100:11434"))
        self.assertFalse(privacy.is_local_endpoint("http://10.0.0.5:11434"))
        self.assertFalse(privacy.is_local_endpoint("http://172.16.0.1:11434"))
        self.assertFalse(privacy.is_local_endpoint("http://169.254.169.254:11434"))
        self.assertFalse(privacy.is_local_endpoint("http://8.8.8.8:11434"))

    def test_cloud_provider_urls_rejected(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertFalse(privacy.is_local_endpoint("https://api.openai.com/v1"))
        self.assertFalse(privacy.is_local_endpoint("https://api.anthropic.com"))
        self.assertFalse(privacy.is_local_endpoint("https://generativelanguage.googleapis.com"))

if __name__ == "__main__":
    unittest.main()
