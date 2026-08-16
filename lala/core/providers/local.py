import json
import urllib.request
import urllib.error
from typing import Optional, Generator, Dict, Any
from lala.core.providers.base import BaseProvider, ModelResponse
from lala.utils.logging import logger

class LocalProvider(BaseProvider):
    """
    Local Model Provider adapter interfacing directly with Ollama's local HTTP API.
    Zero cloud data leakage; strictly communicates with local 127.0.0.1 endpoint.
    """
    def __init__(
        self,
        provider_name: str = "local",
        model_name: str = "qwen2.5:3b",
        endpoint: str = "http://127.0.0.1:11434",
        temperature: float = 0.7
    ):
        super().__init__(provider_name=provider_name, model_name=model_name)
        self.endpoint = endpoint.rstrip("/")
        self.temperature = temperature

    def check_health(self) -> Dict[str, Any]:
        """
        Check health of local Ollama service and active model availability.
        """
        try:
            req = urllib.request.Request(f"{self.endpoint}/api/tags", headers={"User-Agent": "LALA/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name") for m in data.get("models", [])]
                    model_found = any(self.model_name in m or m.startswith(self.model_name) for m in models)
                    return {
                        "online": True,
                        "endpoint": self.endpoint,
                        "installed_models": models,
                        "model_available": model_found,
                        "active_model": self.model_name
                    }
        except Exception as e:
            return {
                "online": False,
                "endpoint": self.endpoint,
                "installed_models": [],
                "model_available": False,
                "active_model": self.model_name,
                "error": str(e)
            }
        return {"online": False, "endpoint": self.endpoint, "model_available": False}

    def is_available(self) -> bool:
        health = self.check_health()
        return health.get("online", False)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        """
        Non-streaming text generation call to Ollama /api/chat.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": kwargs.get("model_name", self.model_name),
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature)
            }
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.endpoint}/api/chat",
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "LALA/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    message_content = body.get("message", {}).get("content", "")
                    return ModelResponse(
                        content=message_content,
                        provider_name=self.provider_name,
                        model_name=self.model_name,
                        raw_response=body
                    )
        except urllib.error.URLError as e:
            err_msg = (
                f"[LALA Error] Unable to connect to local Ollama at {self.endpoint}.\n"
                f"Ensure Ollama is running and OLLAMA_MODELS is configured.\n"
                f"Details: {e}"
            )
            logger.error(err_msg)
            return ModelResponse(content=err_msg, provider_name=self.provider_name, model_name=self.model_name)
        except Exception as e:
            err_msg = f"[LALA Error] Model execution failed: {e}"
            logger.error(err_msg)
            return ModelResponse(content=err_msg, provider_name=self.provider_name, model_name=self.model_name)

        return ModelResponse(
            content="[LALA Error] Empty or invalid response from local Ollama.",
            provider_name=self.provider_name,
            model_name=self.model_name
        )

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Generator[str, None, None]:
        """
        Streaming response generator sending chunks from Ollama /api/chat.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": kwargs.get("model_name", self.model_name),
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature)
            }
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.endpoint}/api/chat",
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "LALA/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                for line in resp:
                    if line:
                        chunk_str = line.decode("utf-8").strip()
                        if chunk_str:
                            try:
                                chunk_json = json.loads(chunk_str)
                                token = chunk_json.get("message", {}).get("content", "")
                                if token:
                                    yield token
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            yield f"\n[LALA Local Brain Connection Error: {e}]"
