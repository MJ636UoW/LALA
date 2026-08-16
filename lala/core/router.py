from typing import Dict, Optional, Generator
from lala.core.config import ModelRouterConfig
from lala.core.providers.base import BaseProvider, ModelResponse
from lala.core.providers.local import LocalProvider
from lala.core.providers.gemini import GeminiProvider
from lala.core.providers.claude import ClaudeProvider
from lala.core.providers.openai_compatible import OpenAICompatibleProvider
from lala.utils.logging import logger

class ModelRouter:
    """
    Model Router governing AI provider selection.
    In Phase 2: 'local' Ollama is the strict default provider.
    Cloud fallback is explicitly DISABLED to guarantee local privacy.
    """
    def __init__(self, config: Optional[ModelRouterConfig] = None):
        self.config = config or ModelRouterConfig()
        self.providers: Dict[str, BaseProvider] = {}
        self._register_configured_providers()

    def _register_configured_providers(self):
        # Register providers based on config
        local_cfg = self.config.providers.get("local")
        local_model = local_cfg.model_name if local_cfg else "qwen2.5:3b"
        local_endpoint = local_cfg.endpoint if local_cfg else "http://127.0.0.1:11434"
        local_temp = local_cfg.temperature if local_cfg else 0.7

        self.register_provider("local", LocalProvider(
            provider_name="local",
            model_name=local_model,
            endpoint=local_endpoint,
            temperature=local_temp
        ))
        self.register_provider("mock_local", LocalProvider(provider_name="mock_local", model_name=local_model))
        self.register_provider("mock_gemini", GeminiProvider())
        self.register_provider("mock_claude", ClaudeProvider())
        self.register_provider("mock_openai", OpenAICompatibleProvider())

    def register_provider(self, name: str, provider: BaseProvider):
        self.providers[name] = provider

    def get_active_provider(self) -> BaseProvider:
        provider_name = self.config.active_provider
        return self.providers.get(provider_name, self.providers.get("local"))

    def route_request(self, prompt: str, system_prompt: Optional[str] = None, provider_override: Optional[str] = None) -> ModelResponse:
        target_name = provider_override or self.config.active_provider
        provider = self.providers.get(target_name)

        if provider and provider.is_available():
            return provider.generate(prompt, system_prompt=system_prompt)

        # Check cloud_fallback policy
        if self.config.cloud_fallback:
            logger.warning(f"Provider '{target_name}' unavailable. Attempting cloud fallback...")
            for name, p in self.providers.items():
                if name != target_name and p.is_available():
                    return p.generate(prompt, system_prompt=system_prompt)

        # Local privacy policy error message (zero cloud leak)
        err_msg = (
            "LALA local brain is unavailable. Ollama is not running or the configured model is unavailable.\n"
            "Cloud fallback is explicitly disabled to preserve local data privacy."
        )
        logger.error(err_msg)
        return ModelResponse(
            content=err_msg,
            provider_name=target_name,
            model_name="unknown"
        )

    def route_stream(self, prompt: str, system_prompt: Optional[str] = None, provider_override: Optional[str] = None) -> Generator[str, None, None]:
        target_name = provider_override or self.config.active_provider
        provider = self.providers.get(target_name)

        if provider and isinstance(provider, LocalProvider) and provider.is_available():
            yield from provider.generate_stream(prompt, system_prompt=system_prompt)
        elif provider and provider.is_available():
            response = provider.generate(prompt, system_prompt=system_prompt)
            yield response.content
        else:
            yield (
                "LALA local brain is unavailable. Ollama is not running or the configured model is unavailable.\n"
                "Cloud fallback is explicitly disabled to preserve local data privacy."
            )
