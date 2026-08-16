import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional, Generator
from lala.llm.provider import LocalLLMProvider
from lala.llm.models import (
    LocalModelInfo, GenerationRequest, GenerationResponse, LocalProviderHealth, ModelCapability
)
from lala.utils.logging import logger

class OllamaProvider(LocalLLMProvider):
    """
    Local Ollama LLM Provider for LALA Phase 8.1.
    Uses direct HTTP requests via safe local opener to validated loopback endpoint (http://127.0.0.1:11434).
    Zero shell command execution, zero external proxy leaking, zero cloud fallback.
    """
    def __init__(self, endpoint: str = "http://127.0.0.1:11434"):
        super().__init__(name="ollama", endpoint=endpoint)

    def health_check(self) -> LocalProviderHealth:
        try:
            url = f"{self.endpoint}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with self.opener.open(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return LocalProviderHealth(
                        provider_name=self.name,
                        is_online=True,
                        endpoint=self.endpoint,
                        is_local_endpoint=True,
                        model_available=len(models) > 0,
                        available_models=models
                    )
        except Exception:
            pass

        return LocalProviderHealth(
            provider_name=self.name,
            is_online=False,
            endpoint=self.endpoint,
            is_local_endpoint=True,
            model_available=False,
            available_models=[]
        )

    def list_models(self) -> List[LocalModelInfo]:
        health = self.health_check()
        if not health.is_online:
            return []

        models = []
        for name in health.available_models:
            models.append(LocalModelInfo(
                name=name,
                provider=self.name,
                is_local=True,
                capabilities=[ModelCapability.CHAT, ModelCapability.CODING, ModelCapability.CYBERSECURITY],
                status="available"
            ))
        return models

    def model_info(self, model_name: str) -> Optional[LocalModelInfo]:
        models = self.list_models()
        for m in models:
            if m.name.lower() == model_name.lower():
                return m
        return LocalModelInfo(name=model_name, provider=self.name, is_local=True)

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        self.privacy_engine.assert_privacy_policy(self.endpoint)
        url = f"{self.endpoint}/api/generate"
        payload = {
            "model": request.model_name,
            "prompt": request.prompt,
            "stream": False,
            "options": {"temperature": request.temperature}
        }
        if request.system_prompt:
            payload["system"] = request.system_prompt

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with self.opener.open(req, timeout=30) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    return GenerationResponse(
                        text=res_data.get("response", ""),
                        model_name=request.model_name,
                        provider_name=self.name,
                        is_local=True,
                        prompt_tokens=res_data.get("prompt_eval_count", 0),
                        completion_tokens=res_data.get("eval_count", 0),
                        raw_metadata=res_data
                    )
        except Exception as e:
            logger.error(f"OllamaProvider HTTP Error: {e}")

        return GenerationResponse(
            text="[LOCAL_MODEL_UNAVAILABLE] Local Ollama brain is currently offline. Cloud fallback is explicitly disabled to preserve local data privacy.",
            model_name=request.model_name,
            provider_name=self.name,
            is_local=True,
            raw_metadata={"error": "LOCAL_MODEL_UNAVAILABLE"}
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> GenerationResponse:
        self.privacy_engine.assert_privacy_policy(self.endpoint)
        url = f"{self.endpoint}/api/chat"
        model_name = kwargs.get("model_name", "qwen2.5:3b")
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with self.opener.open(req, timeout=30) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    msg = res_data.get("message", {})
                    return GenerationResponse(
                        text=msg.get("content", ""),
                        model_name=model_name,
                        provider_name=self.name,
                        is_local=True,
                        prompt_tokens=res_data.get("prompt_eval_count", 0),
                        completion_tokens=res_data.get("eval_count", 0),
                        raw_metadata=res_data
                    )
        except Exception as e:
            logger.error(f"OllamaProvider Chat HTTP Error: {e}")

        return GenerationResponse(
            text="[LOCAL_MODEL_UNAVAILABLE] Local Ollama brain is currently offline. Cloud fallback is explicitly disabled to preserve local data privacy.",
            model_name=model_name,
            provider_name=self.name,
            is_local=True,
            raw_metadata={"error": "LOCAL_MODEL_UNAVAILABLE"}
        )

    def stream(self, request: GenerationRequest) -> Generator[str, None, None]:
        response = self.generate(request)
        yield response.text
