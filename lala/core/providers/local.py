from typing import Optional
from lala.core.providers.base import BaseProvider, ModelResponse

class LocalProvider(BaseProvider):
    """
    Adapter interface for local model runtimes (Ollama planned for Phase 2).
    Phase 1: Stub implementation only, zero downloads, zero network calls.
    """
    def __init__(self, provider_name: str = "mock_local", model_name: str = "ollama-placeholder", endpoint: str = "http://localhost:11434"):
        super().__init__(provider_name=provider_name, model_name=model_name)
        self.endpoint = endpoint

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        return ModelResponse(
            content=f"[LALA Local Stub Output] Hello Mandar! Received prompt: '{prompt}'",
            provider_name=self.provider_name,
            model_name=self.model_name
        )

    def is_available(self) -> bool:
        # Phase 1: Offline stub is ready
        return True
