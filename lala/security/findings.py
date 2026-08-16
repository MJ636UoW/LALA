from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class SeverityLevel(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityFinding(BaseModel):
    file_path: str
    line_number: int = 0
    rule_id: str
    severity: SeverityLevel = SeverityLevel.MEDIUM
    description: str
    code_snippet: str = ""
    recommendation: str = ""

class SecurityReport(BaseModel):
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    findings: List[SecurityFinding] = Field(default_factory=list)
