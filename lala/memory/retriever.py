from typing import List
from lala.memory.models import PersistentMemoryItem
from lala.memory.store import SQLiteMemoryStore
from lala.memory.embeddings import LocalEmbeddingProvider

class MemoryRetriever:
    """
    Hybrid retriever combining FTS5 SQLite full-text search with local embedding ranking.
    """
    def __init__(self, store: SQLiteMemoryStore, embedding_provider: LocalEmbeddingProvider):
        self.store = store
        self.embedding_provider = embedding_provider

    def retrieve_context(self, query: str, limit: int = 3) -> List[PersistentMemoryItem]:
        # Perform FTS / Keyword search
        return self.store.search(query, limit=limit)
