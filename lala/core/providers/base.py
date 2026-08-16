from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ModelResponse(BaseModel):
    content: str
    provider_name: str
    model_name: str
    raw_response: Optional[Dict[str, Any]] = None

class BaseProvider(ABC):
    """
    Abstract Base Class for all LALA AI Model Providers.
    Phase 1 establishes clean interface contracts without requiring API keys or network calls.
    """
    def __init__(self, provider_name: str, model_name: str):
        self.provider_name = provider_name
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ModelResponse:
        """
        Generate text output from the provider.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available in the current environment.
        """
        pass
