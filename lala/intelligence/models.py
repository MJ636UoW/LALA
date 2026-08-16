from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class IOCType(str, Enum):
    IP = "IP"
    DOMAIN = "DOMAIN"
    URL = "URL"
    HASH = "HASH"
    CVE = "CVE"

class Verdict(str, Enum):
    MALICIOUS = "MALICIOUS"
    SUSPICIOUS = "SUSPICIOUS"
    CLEAN = "CLEAN"
    UNKNOWN = "UNKNOWN"

class IOC(BaseModel):
    ioc_type: IOCType
    value: str
    source: str = "local"
    confidence: float = 0.0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class ThreatIntelResult(BaseModel):
    provider: str
    query: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.0
    verdict: Verdict = Verdict.UNKNOWN
    indicators: List[IOC] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

class HashReputation(BaseModel):
    hash_value: str
    verdict: Verdict = Verdict.UNKNOWN
    malware_family: Optional[str] = None
    positives: int = 0
    total_scans: int = 0
    signatures: List[str] = Field(default_factory=list)

class IPReputation(BaseModel):
    ip_address: str
    verdict: Verdict = Verdict.UNKNOWN
    abuse_score: int = 0
    country: Optional[str] = None
    isp: Optional[str] = None
    total_reports: int = 0

class DomainReputation(BaseModel):
    domain: str
    verdict: Verdict = Verdict.UNKNOWN
    categories: List[str] = Field(default_factory=list)
    dns_records: List[str] = Field(default_factory=list)

class URLReputation(BaseModel):
    url: str
    verdict: Verdict = Verdict.UNKNOWN
    status: Optional[str] = None

class MalwareFamily(BaseModel):
    name: str
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    associated_iocs: List[str] = Field(default_factory=list)

class ThreatActor(BaseModel):
    name: str
    aliases: List[str] = Field(default_factory=list)
    target_sectors: List[str] = Field(default_factory=list)

class Vulnerability(BaseModel):
    cve_id: str
    cvss_score: float = 0.0
    severity: str = "UNKNOWN"
    description: str = ""
    affected_products: List[str] = Field(default_factory=list)
    is_cisa_kev: bool = False
    references: List[str] = Field(default_factory=list)

class AttackTechnique(BaseModel):
    technique_id: str
    name: str
    tactic: str
    description: str = ""
