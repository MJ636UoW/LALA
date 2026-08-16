from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class QueryCategory(str, Enum):
    IOC = "IOC"
    MALWARE = "MALWARE"
    YARA = "YARA"
    SIGMA = "SIGMA"
    MITRE = "MITRE"
    CVE = "CVE"
    NETWORK = "NETWORK"
    REVERSE_ENGINEERING = "REVERSE_ENGINEERING"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    THREAT_HUNTING = "THREAT_HUNTING"
    GENERAL = "GENERAL"

class Document(BaseModel):
    document_id: str
    source_path: str
    source_type: str = "txt"
    sha256: str
    file_size: int
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    imported_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    token_estimate: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    text: str
    relevance_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Citation(BaseModel):
    index: int
    document_title: str
    source_path: str
    chunk_id: str
    excerpt: str

class RAGConfig(BaseModel):
    knowledge_root: str = "F:\\LALA\\Knowledge"
    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 8
    max_top_k: int = 20
    max_doc_size_mb: int = 100
