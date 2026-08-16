from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class CaseStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"

class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

class CorrelationConfidence(str, Enum):
    CONFIRMED = "CONFIRMED"
    PROBABLE = "PROBABLE"
    POSSIBLE = "POSSIBLE"
    UNKNOWN = "UNKNOWN"

class EvidenceItem(BaseModel):
    id: str
    ioc_value: str
    evidence_type: str
    source: str
    details: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TimelineEntry(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_description: str
    source: str = "LALA Investigation Engine"
    actor: str = "LALA Agent"
    evidence_ref: Optional[str] = None
    confidence: float = 1.0

class Correlation(BaseModel):
    source_ioc: str
    target_ioc: str
    relationship_type: str # e.g. "RESOLVES_TO", "HOSTED_ON", "USES_TECHNIQUE", "BELONGS_TO_FAMILY"
    confidence: CorrelationConfidence = CorrelationConfidence.POSSIBLE
    reason: str
    evidence_ref: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RiskScore(BaseModel):
    score: float # 0.0 to 100.0
    level: SeverityLevel = SeverityLevel.UNKNOWN
    factors: List[str] = Field(default_factory=list)

class InvestigationTarget(BaseModel):
    value: str
    target_type: str # IP, DOMAIN, URL, HASH, FILE

class InvestigationCase(BaseModel):
    case_id: str
    title: str
    status: CaseStatus = CaseStatus.OPEN
    target: Optional[InvestigationTarget] = None
    severity: SeverityLevel = SeverityLevel.UNKNOWN
    risk_score: Optional[RiskScore] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    correlations: List[Correlation] = Field(default_factory=list)
    timeline: List[TimelineEntry] = Field(default_factory=list)
    mitre_ids: List[str] = Field(default_factory=list)
    analyst_notes: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
