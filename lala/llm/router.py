from typing import Dict, Any, Optional
from lala.llm.models import TaskType, LocalModelInfo, GenerationRequest, GenerationResponse
from lala.llm.ollama_provider import OllamaProvider
from lala.llm.llamacpp_provider import LlamaCppProvider
from lala.utils.logging import logger

class LocalModelRouter:
    """
    Task-Based Local Model Router for LALA Phase 8.
    Routes inference tasks to locally hosted models based on task type.
    Strictly forbids routing to cloud providers.
    """
    def __init__(self, default_model: str = "qwen2.5:3b"):
        self.default_model = default_model
        self.ollama = OllamaProvider()
        self.llamacpp = LlamaCppProvider()
        self.task_model_map: Dict[TaskType, str] = {
            TaskType.GENERAL: default_model,
            TaskType.CODING: default_model,
            TaskType.CYBERSECURITY: default_model,
            TaskType.REVERSE_ENGINEERING: default_model,
            TaskType.ANALYSIS: default_model,
            TaskType.REASONING: default_model
        }

    def route_request(self, prompt: str, task_type: TaskType = TaskType.GENERAL, **kwargs) -> GenerationResponse:
        model_name = self.task_model_map.get(task_type, self.default_model)
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=kwargs.get("system_prompt"),
            model_name=model_name,
            temperature=kwargs.get("temperature", 0.7)
        )

        # Check local providers in order: Ollama -> llama.cpp
        ollama_health = self.ollama.health_check()
        if ollama_health.is_online:
            return self.ollama.generate(request)

        llamacpp_health = self.llamacpp.health_check()
        if llamacpp_health.is_online:
            return self.llamacpp.generate(request)

        # Both local providers offline -> Fail closed
        logger.error("LocalModelRouter Denial: All local LLM providers are offline. Cloud fallback is explicitly disabled.")
        return GenerationResponse(
            text="[LOCAL_MODEL_UNAVAILABLE] Local LLM brain is currently offline. Cloud fallback is explicitly disabled to preserve local data privacy.",
            model_name=model_name,
            provider_name="none",
            is_local=True,
            raw_metadata={"error": "LOCAL_MODEL_UNAVAILABLE"}
        )
