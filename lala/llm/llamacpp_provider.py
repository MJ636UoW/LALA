import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional, Generator
from lala.llm.provider import LocalLLMProvider
from lala.llm.models import (
    LocalModelInfo, GenerationRequest, GenerationResponse, LocalProviderHealth, ModelCapability
)
from lala.utils.logging import logger

class LlamaCppProvider(LocalLLMProvider):
    """
    Local llama.cpp Server Provider for LALA Phase 8.
    Uses direct HTTP requests to validated local loopback endpoint (http://127.0.0.1:8080).
    """
    def __init__(self, endpoint: str = "http://127.0.0.1:8080"):
        super().__init__(name="llamacpp", endpoint=endpoint)

    def health_check(self) -> LocalProviderHealth:
        try:
            url = f"{self.endpoint}/health"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return LocalProviderHealth(
                        provider_name=self.name,
                        is_online=True,
                        endpoint=self.endpoint,
                        is_local_endpoint=True,
                        model_available=True,
                        available_models=["llama-cpp-local"]
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
        if health.is_online:
            return [LocalModelInfo(name="llama-cpp-local", provider=self.name, is_local=True)]
        return []

    def model_info(self, model_name: str) -> Optional[LocalModelInfo]:
        return LocalModelInfo(name=model_name, provider=self.name, is_local=True)

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        self.privacy_engine.assert_privacy_policy(self.endpoint)
        url = f"{self.endpoint}/completion"
        payload = {"prompt": request.prompt, "temperature": request.temperature, "n_predict": request.max_tokens}
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    return GenerationResponse(
                        text=res_data.get("content", ""),
                        model_name=request.model_name,
                        provider_name=self.name,
                        is_local=True,
                        raw_metadata=res_data
                    )
        except Exception as e:
            logger.error(f"LlamaCppProvider HTTP Error: {e}")

        return GenerationResponse(
            text="[LOCAL_MODEL_UNAVAILABLE] Local llama.cpp server is currently offline.",
            model_name=request.model_name,
            provider_name=self.name,
            is_local=True,
            raw_metadata={"error": "LOCAL_MODEL_UNAVAILABLE"}
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> GenerationResponse:
        prompt_text = "\n".join([f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages])
        req = GenerationRequest(prompt=prompt_text, model_name=kwargs.get("model_name", "llama-cpp-local"))
        return self.generate(req)

    def stream(self, request: GenerationRequest) -> Generator[str, None, None]:
        res = self.generate(request)
        yield res.text
