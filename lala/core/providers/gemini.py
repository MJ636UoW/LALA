import os
import json
import urllib.request
from typing import Optional
from lala.core.providers.base import BaseProvider, ModelResponse
from lala.utils.logging import logger

FAST_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]

class GeminiProvider(BaseProvider):
    """
    Ultra-Fast Adapter for Google Gemini cloud provider.
    Uses gemini-3.5-flash-lite for sub-second responses (~1.1s).
    """
    def __init__(self, provider_name: str = "gemini", model_name: str = "gemini-3.5-flash-lite", api_key: Optional[str] = None):
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

        full_text = f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_text}]
                }
            ]
        }
        req_data = json.dumps(payload).encode("utf-8")

        models_to_try = [self.model_name] + [m for m in FAST_MODELS if m != self.model_name]

        last_error = None
        for model in models_to_try:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_json = json.loads(response.read().decode("utf-8"))
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text_out = parts[0].get("text", "")
                            return ModelResponse(
                                content=text_out,
                                provider_name=self.provider_name,
                                model_name=model
                            )
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini model '{model}' failed: {e}. Trying fast fallback...")
                continue

        return ModelResponse(
            content=f"[Gemini Provider Error]: Response timeout or service unavailable ({last_error}). Please try again.",
            provider_name=self.provider_name,
            model_name=self.model_name
        )
