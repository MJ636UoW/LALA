from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class YaraRuleMeta(BaseModel):
    rule_name: str
    description: Optional[str] = None
    author: Optional[str] = None
    severity: Optional[str] = "MEDIUM"
    tags: List[str] = Field(default_factory=list)

class YaraMatch(BaseModel):
    rule_name: str
    target_path: str
    sha256: str
    tags: List[str] = Field(default_factory=list)
    matched_strings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
