from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class ModelCapability(str, Enum):
    CHAT = "chat"
    CODING = "coding"
    REASONING = "reasoning"
    CYBERSECURITY = "cybersecurity"
    REVERSE_ENGINEERING = "reverse_engineering"
    ANALYSIS = "analysis"

class TaskType(str, Enum):
    GENERAL = "GENERAL"
    CODING = "CODING"
    CYBERSECURITY = "CYBERSECURITY"
    REVERSE_ENGINEERING = "REVERSE_ENGINEERING"
    ANALYSIS = "ANALYSIS"
    REASONING = "REASONING"

class LocalModelInfo(BaseModel):
    name: str
    provider: str = "ollama"
    is_local: bool = True
    capabilities: List[ModelCapability] = Field(default_factory=lambda: [ModelCapability.CHAT, ModelCapability.CODING])
    context_length: int = 4096
    quantization: str = "q4_0"
    status: str = "available"
    parameters: Optional[str] = "3B"

class GenerationRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    model_name: str = "qwen2.5:3b"
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False

class GenerationResponse(BaseModel):
    text: str
    model_name: str
    provider_name: str
    is_local: bool = True
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

class LocalProviderHealth(BaseModel):
    provider_name: str
    is_online: bool
    endpoint: str
    is_local_endpoint: bool = True
    model_available: bool
    available_models: List[str] = Field(default_factory=list)
