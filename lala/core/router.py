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
    Model Router governing AI provider selection (Local Ollama, Google Gemini, Anthropic Claude).
    Priority: Explicit active provider -> Available configured Cloud/Local provider.
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
        self.register_provider("gemini", GeminiProvider())
        self.register_provider("claude", ClaudeProvider())
        self.register_provider("mock_local", LocalProvider(provider_name="mock_local", model_name=local_model))
        self.register_provider("mock_gemini", GeminiProvider())
        self.register_provider("mock_claude", ClaudeProvider())
        self.register_provider("mock_openai", OpenAICompatibleProvider())

    def register_provider(self, name: str, provider: BaseProvider):
        self.providers[name] = provider

    def get_active_provider(self) -> BaseProvider:
        provider_name = self.config.active_provider
        active = self.providers.get(provider_name)
        if active and active.is_available():
            return active

        # Fallback to any available provider in order: Gemini -> Claude -> Local
        for p_name in ["gemini", "claude", "local"]:
            p = self.providers.get(p_name)
            if p and p.is_available():
                return p

        return self.providers.get("local")

    def route_request(self, prompt: str, system_prompt: Optional[str] = None, provider_override: Optional[str] = None) -> ModelResponse:
        target_name = provider_override or self.config.active_provider
        provider = self.providers.get(target_name)

        if provider and provider.is_available():
            return provider.generate(prompt, system_prompt=system_prompt)

        # Auto-route to configured Gemini/Claude if available and local is offline
        for p_name in ["gemini", "claude"]:
            p = self.providers.get(p_name)
            if p and p.is_available():
                logger.info(f"ModelRouter: Routing request to active cloud provider '{p_name}'.")
                return p.generate(prompt, system_prompt=system_prompt)

        if self.config.cloud_fallback:
            logger.warning(f"Provider '{target_name}' unavailable. Attempting cloud fallback...")
            for name, p in self.providers.items():
                if name != target_name and p.is_available():
                    return p.generate(prompt, system_prompt=system_prompt)

        err_msg = (
            "LALA AI providers unavailable. Local Ollama is offline and cloud API keys are unconfigured.\n"
            "Please configure GEMINI_API_KEY or ANTHROPIC_API_KEY in .env."
        )
        logger.error(err_msg)
        return ModelResponse(
            content=err_msg,
            provider_name=target_name,
            model_name="unknown"
        )

    def route_stream(self, prompt: str, system_prompt: Optional[str] = None, provider_override: Optional[str] = None) -> Generator[str, None, None]:
        response = self.route_request(prompt, system_prompt=system_prompt, provider_override=provider_override)
        yield response.content
