from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class MemoryCategory(str, Enum):
    TEMPORARY = "TEMPORARY"   # Transient execution data, not persisted
    SESSION = "SESSION"       # Persisted during active session only
    PERSISTENT = "PERSISTENT" # Stored permanently in SQLite memory database
    SENSITIVE = "SENSITIVE"   # Never automatically persisted

class MemoryType(str, Enum):
    FACT = "FACT"
    PREFERENCE = "PREFERENCE"
    PROJECT = "PROJECT"
    EPISODIC = "EPISODIC"
    NOTE = "NOTE"

class PersistentMemoryItem(BaseModel):
    id: str
    content: str
    category: MemoryCategory = MemoryCategory.PERSISTENT
    memory_type: MemoryType = MemoryType.FACT
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationEpisode(BaseModel):
    episode_id: str
    user_query: str
    assistant_response: str
    tools_used: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
