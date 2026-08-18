import os
import json
import urllib.request
from typing import Optional
from lala.core.providers.base import BaseProvider, ModelResponse
from lala.utils.logging import logger

class GeminiProvider(BaseProvider):
    """
    Adapter interface for Google Gemini cloud provider.
    Reads GEMINI_API_KEY from environment variables / .env.
    """
    def __init__(self, provider_name: str = "gemini", model_name: str = "gemini-3.6-flash", api_key: Optional[str] = None):
        super().__init__(provider_name=provider_name, model_name=model_name)
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def is_available(self) -> bool:
        key = self.api_key or os.environ.get("GEMINI_API_KEY")
        return bool(key and len(key.strip()) > 0)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        key = self.api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            return ModelResponse(
                content="[Gemini Provider Error] GEMINI_API_KEY is not configured.",
                provider_name=self.provider_name,
                model_name=self.model_name
            )

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={key}"
        
        full_text = f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_text}]
                }
            ]
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text_out = parts[0].get("text", "")
                        return ModelResponse(
                            content=text_out,
                            provider_name=self.provider_name,
                            model_name=self.model_name
                        )
            return ModelResponse(
                content="[Gemini Provider] Empty response received from API.",
                provider_name=self.provider_name,
                model_name=self.model_name
            )
        except Exception as e:
            logger.error(f"GeminiProvider API Error: {e}")
            return ModelResponse(
                content=f"[Gemini Provider API Error]: {e}",
                provider_name=self.provider_name,
                model_name=self.model_name
            )
