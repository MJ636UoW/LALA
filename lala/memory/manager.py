import uuid
from typing import List, Dict, Any, Optional
from lala.memory.models import PersistentMemoryItem, MemoryCategory, MemoryType, ConversationEpisode
from lala.memory.store import SQLiteMemoryStore
from lala.memory.embeddings import LocalEmbeddingProvider
from lala.memory.retriever import MemoryRetriever

class MemoryManager:
    """
    Central Memory Subsystem Manager for LALA.
    Coordinates Short-Term Session Context, Episodic Memory, and Persistent Long-Term Knowledge.
    """
    def __init__(self, db_path: str = "F:\\LALA\\Memory\\lala_memory.db"):
        self.store = SQLiteMemoryStore(db_path=db_path)
        self.embedding_provider = LocalEmbeddingProvider()
        self.retriever = MemoryRetriever(self.store, self.embedding_provider)
        self.episodes: List[ConversationEpisode] = []

    def save_memory(self, content: str, category: MemoryCategory = MemoryCategory.PERSISTENT, memory_type: MemoryType = MemoryType.FACT) -> bool:
        item = PersistentMemoryItem(
            id=str(uuid.uuid4()),
            content=content,
            category=category,
            memory_type=memory_type
        )
        return self.store.store(item)

    def search_memory(self, query: str, limit: int = 5) -> List[PersistentMemoryItem]:
        return self.retriever.retrieve_context(query, limit=limit)

    def forget_memory(self, query: str) -> int:
        matches = self.search_memory(query, limit=10)
        deleted_count = 0
        for item in matches:
            if self.store.delete(item.id):
                deleted_count += 1
        return deleted_count

    def clear_all_persistent(self) -> None:
        self.store.clear()

    def get_status(self) -> Dict[str, Any]:
        stats = self.store.get_stats()
        return {
            "status": "ONLINE",
            "persistent_db": stats["db_path"],
            "total_memories": stats["total_items"],
            "episodes_in_session": len(self.episodes)
        }
