import unittest
from lala.llm.privacy import LocalLLMPrivacyEngine

class TestPhase81DnsRedTeam(unittest.TestCase):
    """2. DNS Rebinding & Hostname Security Red-Team Tests."""

    def test_remote_domain_names_rejected(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertFalse(privacy.is_local_endpoint("http://evil-attacker-server.com:11434"))
        self.assertFalse(privacy.is_local_endpoint("http://ollama.remote.net:11434"))

    def test_localhost_accepted(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertTrue(privacy.is_local_endpoint("http://localhost:11434"))

if __name__ == "__main__":
    unittest.main()
