import unittest
from lala.llm.privacy import LocalLLMPrivacyEngine

class TestPhase81RedirectRedTeam(unittest.TestCase):
    """3. HTTP Redirect Revalidation Red-Team Tests."""

    def test_redirect_to_remote_endpoint_rejected(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertFalse(privacy.validate_redirect("http://127.0.0.1:11434", "https://attacker.com/steal_prompt"))
        self.assertFalse(privacy.validate_redirect("http://127.0.0.1:11434", "http://192.168.1.1/router"))

    def test_redirect_to_loopback_accepted(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertTrue(privacy.validate_redirect("http://127.0.0.1:11434", "http://127.0.0.1:8080"))

if __name__ == "__main__":
    unittest.main()
