import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from lala.llm.models import LocalModelInfo, GenerationRequest, GenerationResponse, TaskType
from lala.llm.ollama_provider import OllamaProvider
from lala.llm.llamacpp_provider import LlamaCppProvider
from lala.llm.router import LocalModelRouter
from lala.llm.health import LocalLLMHealthChecker
from lala.llm.privacy import LocalLLMPrivacyEngine

class LocalLLMManager:
    """
    Central Manager for LALA Phase 8 Local LLM Subsystem.
    Manages local model directory (F:\\LALA\\Models\\), local registry, model selection, and router.
    """
    def __init__(self, models_root: str = "F:\\LALA\\Models"):
        self.models_root = Path(models_root)
        self.privacy = LocalLLMPrivacyEngine()
        self.health_checker = LocalLLMHealthChecker()
        self.router = LocalModelRouter()
        self.active_model_name = "qwen2.5:3b"
        self._init_models_dir()

    def _init_models_dir(self):
        try:
            self.models_root.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def get_current_model(self) -> str:
        return self.active_model_name

    def set_current_model(self, model_name: str) -> bool:
        self.active_model_name = model_name
        self.router.default_model = model_name
        return True

    def list_local_models(self) -> List[LocalModelInfo]:
        ollama_models = self.router.ollama.list_models()
        if ollama_models:
            return ollama_models
        llamacpp_models = self.router.llamacpp.list_models()
        if llamacpp_models:
            return llamacpp_models
        return [LocalModelInfo(name=self.active_model_name, provider="ollama", is_local=True)]

    def get_model_info(self, model_name: str) -> Optional[LocalModelInfo]:
        for m in self.list_local_models():
            if m.name.lower() == model_name.lower():
                return m
        return LocalModelInfo(name=model_name, provider="ollama", is_local=True)

    def generate_text(self, prompt: str, task_type: TaskType = TaskType.GENERAL, **kwargs) -> GenerationResponse:
        return self.router.route_request(prompt=prompt, task_type=task_type, **kwargs)

    def get_status(self) -> Dict[str, Any]:
        health_sum = self.health_checker.get_status_summary()
        return {
            "current_model": self.active_model_name,
            "models_root": str(self.models_root),
            "cloud_fallback": False,
            "local_only_mode": True,
            "health": health_sum
        }
