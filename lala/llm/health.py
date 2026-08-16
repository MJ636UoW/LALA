from typing import Dict, List, Any
from lala.llm.models import LocalProviderHealth
from lala.llm.ollama_provider import OllamaProvider
from lala.llm.llamacpp_provider import LlamaCppProvider

class LocalLLMHealthChecker:
    """
    Health Checker for LALA Phase 8 Local LLM Providers.
    Assesses availability of local Ollama and llama.cpp loopback endpoints.
    """
    def __init__(self):
        self.ollama = OllamaProvider()
        self.llamacpp = LlamaCppProvider()

    def check_all(self) -> Dict[str, LocalProviderHealth]:
        return {
            "ollama": self.ollama.health_check(),
            "llamacpp": self.llamacpp.health_check()
        }

    def get_status_summary(self) -> Dict[str, Any]:
        healths = self.check_all()
        active_provider = "ollama" if healths["ollama"].is_online else ("llamacpp" if healths["llamacpp"].is_online else "none")
        return {
            "active_provider": active_provider,
            "cloud_fallback": False,
            "local_only_mode": True,
            "providers": {k: v.model_dump() for k, v in healths.items()}
        }
