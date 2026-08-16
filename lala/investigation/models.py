from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class CaseStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"

class EvidenceItem(BaseModel):
    id: str
    ioc_value: str
    evidence_type: str
    source: str
    details: Dict[str, Any] = Field(default_factory=dict)
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TimelineEntry(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_description: str
    actor: str = "LALA Agent"

class InvestigationCase(BaseModel):
    case_id: str
    title: str
    status: CaseStatus = CaseStatus.OPEN
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    timeline: List[TimelineEntry] = Field(default_factory=list)
