from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generator
from lala.llm.models import LocalModelInfo, GenerationRequest, GenerationResponse, LocalProviderHealth
from lala.llm.privacy import LocalLLMPrivacyEngine

class LocalLLMProvider(ABC):
    """
    Abstract Interface for LALA Local LLM Providers.
    All subclasses must perform local inference and validate local loopback endpoints.
    """
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.endpoint = endpoint
        self.is_local = True
        self.privacy_engine = LocalLLMPrivacyEngine()
        # Enforce local endpoint privacy check on initialization
        self.privacy_engine.assert_privacy_policy(self.endpoint)

    @abstractmethod
    def list_models(self) -> List[LocalModelInfo]:
        pass

    @abstractmethod
    def model_info(self, model_name: str) -> Optional[LocalModelInfo]:
        pass

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> GenerationResponse:
        pass

    @abstractmethod
    def health_check(self) -> LocalProviderHealth:
        pass

    @abstractmethod
    def stream(self, request: GenerationRequest) -> Generator[str, None, None]:
        pass
