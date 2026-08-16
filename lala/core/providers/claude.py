from typing import Optional
from lala.core.providers.base import BaseProvider, ModelResponse

class ClaudeProvider(BaseProvider):
    """
    Adapter interface for Claude cloud provider.
    Phase 1: Stub interface, no API keys required, no external API calls.
    """
    def __init__(self, provider_name: str = "claude", model_name: str = "claude-3-5-sonnet"):
        super().__init__(provider_name=provider_name, model_name=model_name)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        return ModelResponse(
            content=f"[LALA Claude Stub Output] Hello Mandar! Response to: '{prompt}'",
            provider_name=self.provider_name,
            model_name=self.model_name
        )

    def is_available(self) -> bool:
        return False # No cloud calls in Phase 1
