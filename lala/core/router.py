from typing import Dict, Optional
from lala.core.config import ModelRouterConfig
from lala.core.providers.base import BaseProvider, ModelResponse
from lala.core.providers.local import LocalProvider
from lala.core.providers.gemini import GeminiProvider
from lala.core.providers.claude import ClaudeProvider
from lala.core.providers.openai_compatible import OpenAICompatibleProvider
from lala.utils.logging import logger

class ModelRouter:
    """
    Model Router balancing local providers (Ollama planned for Phase 2) and cloud adapters.
    Phase 1: Pure in-memory provider routing without network calls.
    """
    def __init__(self, config: Optional[ModelRouterConfig] = None):
        self.config = config or ModelRouterConfig()
        self.providers: Dict[str, BaseProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        # Register default adapter stubs
        self.register_provider("mock_local", LocalProvider())
        self.register_provider("mock_gemini", GeminiProvider())
        self.register_provider("mock_claude", ClaudeProvider())
        self.register_provider("mock_openai", OpenAICompatibleProvider())

    def register_provider(self, name: str, provider: BaseProvider):
        self.providers[name] = provider

    def get_active_provider(self) -> BaseProvider:
        return self.providers.get(self.config.active_provider, LocalProvider())

    def route_request(self, prompt: str, system_prompt: Optional[str] = None, provider_override: Optional[str] = None) -> ModelResponse:
        target_name = provider_override or self.config.active_provider
        
        provider = self.providers.get(target_name)
        if provider and provider.is_available():
            return provider.generate(prompt, system_prompt=system_prompt)
        
        # Fallback to mock_local if primary fails or unavailable
        logger.warning(f"Provider '{target_name}' not available. Falling back to local provider stub.")
        local_provider = self.providers.get("mock_local", LocalProvider())
        return local_provider.generate(prompt, system_prompt=system_prompt)
