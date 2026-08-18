import os
import json
import urllib.request
from typing import Optional
from lala.core.providers.base import BaseProvider, ModelResponse
from lala.utils.logging import logger

class ClaudeProvider(BaseProvider):
    """
    Adapter interface for Anthropic Claude cloud provider.
    Reads ANTHROPIC_API_KEY from environment variables / .env.
    """
    def __init__(self, provider_name: str = "claude", model_name: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        super().__init__(provider_name=provider_name, model_name=model_name)
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

    def is_available(self) -> bool:
        key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        return bool(key and len(key.strip()) > 0)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return ModelResponse(
                content="[Claude Provider Error] ANTHROPIC_API_KEY is not configured.",
                provider_name=self.provider_name,
                model_name=self.model_name
            )

        endpoint = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": self.model_name,
            "max_tokens": 1024,
            "system": system_prompt or "You are LALA, a personal AI operating assistant.",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=req_data,
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                content_blocks = res_json.get("content", [])
                if content_blocks:
                    text_out = content_blocks[0].get("text", "")
                    return ModelResponse(
                        content=text_out,
                        provider_name=self.provider_name,
                        model_name=self.model_name
                    )
            return ModelResponse(
                content="[Claude Provider] Empty response received from API.",
                provider_name=self.provider_name,
                model_name=self.model_name
            )
        except Exception as e:
            logger.error(f"ClaudeProvider API Error: {e}")
            return ModelResponse(
                content=f"[Claude Provider API Error]: {e}",
                provider_name=self.provider_name,
                model_name=self.model_name
            )
