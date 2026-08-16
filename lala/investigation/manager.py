import os
import uuid
import json
from pathlib import Path
from typing import Dict, List, Optional
from lala.investigation.models import InvestigationCase, CaseStatus, EvidenceItem
from lala.investigation.evidence import EvidenceRecorder
from lala.investigation.timeline import TimelineGenerator
from lala.investigation.reporter import InvestigationReporter

class InvestigationManager:
    """
    Manager for LALA Cybersecurity Investigation Cases.
    Manages local case storage under F:\\LALA\\Investigations\\.
    Never stores API credentials.
    """
    def __init__(self, cases_dir: str = "F:\\LALA\\Investigations"):
        self.cases_dir = Path(cases_dir)
        self.evidence_recorder = EvidenceRecorder()
        self.timeline_generator = TimelineGenerator()
        self.reporter = InvestigationReporter()
        self.active_case: Optional[InvestigationCase] = None
        self._init_dir()

    def _init_dir(self):
        try:
            self.cases_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def create_case(self, title: str) -> InvestigationCase:
        cid = str(uuid.uuid4())[:8]
        case = InvestigationCase(case_id=cid, title=title)
        case.timeline.append(self.timeline_generator.log_event(f"Case '{title}' created."))
        self.active_case = case
        self.save_case(case)
        return case

    def add_evidence(self, ioc_value: str, evidence_type: str, source: str, details: Dict[str, Any]) -> bool:
        if not self.active_case:
            return False
        ev = self.evidence_recorder.create_evidence(ioc_value, evidence_type, source, details)
        self.active_case.evidence_items.append(ev)
        self.active_case.timeline.append(self.timeline_generator.log_event(f"Added evidence '{ioc_value}'."))
        self.save_case(self.active_case)
        return True

    def save_case(self, case: InvestigationCase) -> bool:
        safe_cid = "".join(c for c in case.case_id if c.isalnum() or c in "-_")
        file_path = self.cases_dir / f"case_{safe_cid}.json"
        try:
            canonical = os.path.realpath(file_path)
            if not canonical.startswith(os.path.realpath(self.cases_dir)):
                return False
            with open(canonical, "w", encoding="utf-8") as f:
                json.dump(case.model_dump(mode="json"), f, indent=2)
            return True
        except Exception:
            return False

    def list_cases(self) -> List[str]:
        try:
            return [f.name for f in self.cases_dir.glob("case_*.json")]
        except Exception:
            return []
