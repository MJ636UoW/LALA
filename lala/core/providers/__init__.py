"""
LALA Model Provider Interfaces
"""
from lala.core.providers.base import BaseProvider, ModelResponse
from lala.core.providers.local import LocalProvider
from lala.core.providers.gemini import GeminiProvider
from lala.core.providers.claude import ClaudeProvider
from lala.core.providers.openai_compatible import OpenAICompatibleProvider

__all__ = [
    "BaseProvider",
    "ModelResponse",
    "LocalProvider",
    "GeminiProvider",
    "ClaudeProvider",
    "OpenAICompatibleProvider",
]
