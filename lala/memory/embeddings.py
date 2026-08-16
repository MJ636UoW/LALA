from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from lala.utils.logging import logger

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def available(self) -> bool:
        pass

class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local Embedding Provider abstraction for LALA.
    Model weights stored strictly under F:\\LALA\\Models\\Embeddings.
    Gracefully falls back to keyword/FTS search if embedding models are not installed.
    """
    def __init__(self, model_dir: str = "F:\\LALA\\Models\\Embeddings"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def embed_text(self, text: str) -> List[float]:
        # Simple deterministic hash embedding stub for local fallback
        return [float(ord(c)) for c in text[:16]] + [0.0] * max(0, 16 - len(text[:16]))

    def available(self) -> bool:
        return True
