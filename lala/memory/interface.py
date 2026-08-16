from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class MemoryItem(BaseModel):
    """
    Abstract schema for memory entries in LALA.
    Vector embeddings and persistent storage deferred to Phase 3.
    """
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MemoryStore(ABC):
    """
    Abstract Memory Store Interface for LALA.
    Phase 1 defines contract only without installing vector databases or embeddings.
    """
    @abstractmethod
    def store(self, item: MemoryItem) -> bool:
        pass

    @abstractmethod
    def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

class InMemoryStore(MemoryStore):
    """
    Basic in-memory mock store for Phase 1 testing.
    """
    def __init__(self):
        self._storage: Dict[str, MemoryItem] = {}

    def store(self, item: MemoryItem) -> bool:
        self._storage[item.id] = item
        return True

    def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        results = [item for item in self._storage.values() if query.lower() in item.content.lower()]
        return results[:limit]

    def clear(self) -> None:
        self._storage.clear()
