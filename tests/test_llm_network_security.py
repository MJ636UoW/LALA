import unittest
from lala.llm.privacy import LocalLLMPrivacyEngine

class TestLLMNetworkSecurity(unittest.TestCase):
    def test_assert_privacy_policy_raises_on_remote_endpoint(self):
        privacy = LocalLLMPrivacyEngine()
        with self.assertRaises(PermissionError):
            privacy.assert_privacy_policy("http://remote-ollama-server.com:11434")

if __name__ == "__main__":
    unittest.main()
