import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SigmaRuleMetadata(BaseModel):
    title: str
    id: Optional[str] = None
    description: Optional[str] = None
    level: str = "medium"
    status: Optional[str] = "experimental"
    logsource: Dict[str, Any] = Field(default_factory=dict)
    detection: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class SigmaEngine:
    """
    Sigma Rule Parsing and Defensive Validation Engine for LALA Phase 7.
    Parses local Sigma YAML detection rules safely into structured metadata without executing arbitrary code.
    """
    def __init__(self, rules_dir: str = "F:\\LALA\\Rules\\Sigma"):
        self.rules_dir = Path(rules_dir)
        self._init_dir()

    def _init_dir(self):
        try:
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            sample_rule = self.rules_dir / "sample_process_creation.yml"
            if not sample_rule.exists():
                with open(sample_rule, "w", encoding="utf-8") as f:
                    f.write("""title: Suspicious PowerShell Encoded Command Execution
id: 5a8a1c90-9b34-460d-830a-9d93a6700010
status: experimental
description: Detects powershell execution with encoded command flags
level: high
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\powershell.exe'
        CommandLine|contains:
            - '-enc'
            - '-encodedcommand'
    condition: selection
tags:
    - attack.execution
    - attack.t1059.001
""")
        except Exception:
            pass

    def parse_rule_file(self, file_path: str) -> Optional[SigmaRuleMetadata]:
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return None

        try:
            with open(p, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict) or "title" not in data or "detection" not in data:
                return None

            return SigmaRuleMetadata(
                title=data.get("title", "Untitled Rule"),
                id=str(data.get("id", "")),
                description=data.get("description", ""),
                level=data.get("level", "medium"),
                status=data.get("status", "experimental"),
                logsource=data.get("logsource", {}),
                detection=data.get("detection", {}),
                tags=data.get("tags", [])
            )
        except Exception:
            return None

    def list_rules(self) -> List[SigmaRuleMetadata]:
        rules = []
        if not self.rules_dir.exists():
            return rules

        for yml_file in self.rules_dir.glob("*.yml*"):
            meta = self.parse_rule_file(str(yml_file))
            if meta:
                rules.append(meta)
        return rules
