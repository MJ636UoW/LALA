import uuid
from typing import List, Dict, Any, Optional
from lala.memory.models import PersistentMemoryItem, MemoryCategory, MemoryType, ConversationEpisode
from lala.memory.store import SQLiteMemoryStore
from lala.memory.embeddings import LocalEmbeddingProvider
from lala.memory.retriever import MemoryRetriever

class MemoryManager:
    """
    Central Memory Subsystem Manager for LALA Phase 5.
    Coordinates Short-Term Session Context, Episodic Memory, Persistent Knowledge, Project Metadata, and Security Findings.
    """
    def __init__(self, db_path: str = "F:\\LALA\\Memory\\lala_memory.db"):
        self.store = SQLiteMemoryStore(db_path=db_path)
        self.embedding_provider = LocalEmbeddingProvider()
        self.retriever = MemoryRetriever(self.store, self.embedding_provider)
        self.episodes: List[ConversationEpisode] = []
        self.project_metadata: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []
        self.security_findings_history: List[Dict[str, Any]] = []

    def save_memory(self, content: str, category: MemoryCategory = MemoryCategory.PERSISTENT, memory_type: MemoryType = MemoryType.FACT) -> bool:
        item = PersistentMemoryItem(
            id=str(uuid.uuid4()),
            content=content,
            category=category,
            memory_type=memory_type
        )
        return self.store.store(item)

    def save_project_metadata(self, key: str, value: Any) -> bool:
        self.project_metadata[key] = value
        return self.save_memory(f"Project Metadata [{key}]: {value}", category=MemoryCategory.PERSISTENT, memory_type=MemoryType.PROJECT)

    def record_task_history(self, task_id: str, goal: str, status: str, output: str) -> None:
        entry = {"task_id": task_id, "goal": goal, "status": status, "output": output}
        self.task_history.append(entry)
        self.save_memory(f"Task Execution [{task_id}]: {goal} -> Status: {status}", category=MemoryCategory.PERSISTENT, memory_type=MemoryType.EPISODIC)

    def record_security_finding(self, rule_id: str, description: str, severity: str) -> None:
        entry = {"rule_id": rule_id, "description": description, "severity": severity}
        self.security_findings_history.append(entry)
        self.save_memory(f"Security Finding [{rule_id}]: {description} ({severity})", category=MemoryCategory.PERSISTENT, memory_type=MemoryType.FACT)

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
            "episodes_in_session": len(self.episodes),
            "tasks_recorded": len(self.task_history),
            "security_findings_recorded": len(self.security_findings_history)
        }
