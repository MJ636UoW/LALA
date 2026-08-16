import unittest
from lala.llm.ollama_provider import OllamaProvider
from lala.llm.llamacpp_provider import LlamaCppProvider

class TestLLMProvider(unittest.TestCase):
    def test_provider_initialization_local(self):
        ollama = OllamaProvider()
        self.assertTrue(ollama.is_local)
        self.assertEqual(ollama.endpoint, "http://127.0.0.1:11434")

        llamacpp = LlamaCppProvider()
        self.assertTrue(llamacpp.is_local)
        self.assertEqual(llamacpp.endpoint, "http://127.0.0.1:8080")

if __name__ == "__main__":
    unittest.main()
