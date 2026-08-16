import unittest
from lala.llm.privacy import LocalLLMPrivacyEngine

class TestLLMPrivacy(unittest.TestCase):
    def test_privacy_rejection_of_external_domains(self):
        privacy = LocalLLMPrivacyEngine()
        self.assertFalse(privacy.is_local_endpoint("http://external-llm-service.com:11434"))

if __name__ == "__main__":
    unittest.main()
