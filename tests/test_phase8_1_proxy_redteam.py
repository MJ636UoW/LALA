import os
import unittest
from lala.llm.ollama_provider import OllamaProvider

class TestPhase81ProxyRedTeam(unittest.TestCase):
    """4. Proxy Environment Bypass Red-Team Tests."""

    def test_provider_opener_ignores_malicious_proxy_env(self):
        os.environ["HTTP_PROXY"] = "http://malicious-proxy.com:8080"
        os.environ["HTTPS_PROXY"] = "http://malicious-proxy.com:8080"
        try:
            provider = OllamaProvider()
            self.assertIsNotNone(provider.opener)
        finally:
            os.environ.pop("HTTP_PROXY", None)
            os.environ.pop("HTTPS_PROXY", None)

if __name__ == "__main__":
    unittest.main()
