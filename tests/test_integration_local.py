import unittest
from lala.core.orchestrator import Orchestrator
from lala.core.state import LanguageCode
from lala.core.providers.local import LocalProvider

class TestLocalBrainIntegration(unittest.TestCase):
    """
    Live integration test suite testing local Ollama engine & qwen2.5:3b model.
    Non-blocking: skips gracefully if Ollama server or model is offline.
    """
    @classmethod
    def setUpClass(cls):
        cls.orchestrator = Orchestrator()
        active_provider = cls.orchestrator.router.get_active_provider()
        if not isinstance(active_provider, LocalProvider):
            raise unittest.SkipTest("LocalProvider not configured as active provider.")
        
        cls.health = active_provider.check_health()
        if not cls.health.get("online"):
            raise unittest.SkipTest(f"Ollama server offline at {cls.health.get('endpoint')}.")
        if not cls.health.get("model_available"):
            raise unittest.SkipTest(f"Model '{active_provider.model_name}' not downloaded/loaded in Ollama yet.")

    def test_english_generation(self):
        """Test English generation via real local Ollama model."""
        response = self.orchestrator.process_user_input("State in one sentence who you are and who you serve.")
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 5)

    def test_hindi_generation(self):
        """Test Hindi (हिंदी) generation via real local Ollama model."""
        self.orchestrator.set_language(LanguageCode.HINDI)
        response = self.orchestrator.process_user_input("नमस्ते! आप कौन हैं? मुझे 1 वाक्य में बताओ।")
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 5)

    def test_marathi_generation(self):
        """Test Marathi (मराठी) generation via real local Ollama model."""
        self.orchestrator.set_language(LanguageCode.MARATHI)
        response = self.orchestrator.process_user_input("नमस्कार! तुम्ही कोण आहात? मला एका वाक्यात सांगा.")
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 5)

    def test_code_switching_generation(self):
        """Test multilingual code-switching generation."""
        self.orchestrator.set_language(LanguageCode.ENGLISH)
        prompt = "माझ्या Python project मध्ये bug शोध आणि मला English मध्ये explain कर."
        response = self.orchestrator.process_user_input(prompt)
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 10)

if __name__ == "__main__":
    unittest.main()
