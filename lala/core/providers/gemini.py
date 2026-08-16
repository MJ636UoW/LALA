from typing import Optional
from lala.core.providers.base import BaseProvider, ModelResponse

class GeminiProvider(BaseProvider):
    """
    Adapter interface for Gemini cloud provider.
    Phase 1: Stub interface, no API keys required, no external API calls.
    """
    def __init__(self, provider_name: str = "gemini", model_name: str = "gemini-flash"):
        super().__init__(provider_name=provider_name, model_name=model_name)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        return ModelResponse(
            content=f"[LALA Gemini Stub Output] Hello Mandar! Response to: '{prompt}'",
            provider_name=self.provider_name,
            model_name=self.model_name
        )

    def is_available(self) -> bool:
        return False # No cloud calls in Phase 1
