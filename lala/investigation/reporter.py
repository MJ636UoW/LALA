import os
import json
from pathlib import Path
from typing import Dict, Any
from lala.investigation.models import InvestigationCase

class InvestigationReporter:
    """
    Report Generator for LALA Phase 6.
    Generates professional reports in JSON, Markdown, and TXT format under F:\\LALA\\Investigations\\Reports\\.
    """
    def __init__(self, output_dir: str = "F:\\LALA\\Investigations\\Reports"):
        self.output_dir = Path(output_dir)
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def generate_markdown_report(self, case: InvestigationCase) -> str:
        report = (
            f"# LALA CYBERSECURITY INVESTIGATION REPORT: {case.title}\n"
            f"**Case ID**: {case.case_id}  \n"
            f"**Status**: {case.status.value}  \n"
            f"**Created At**: {case.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}  \n\n"
            f"## Executive Summary\n"
            f"Investigation case '{case.title}' contains {len(case.evidence_items)} evidence indicators.\n\n"
            f"## Evidence & Indicators\n"
        )
        for ev in case.evidence_items:
            report += f"- **{ev.ioc_value}** ({ev.evidence_type}) from `{ev.source}`\n"

        report += f"\n## Timeline of Events\n"
        for t in case.timeline:
            report += f"- `{t.timestamp.strftime('%H:%M:%S')}`: {t.event_description} (by {t.actor})\n"

        file_path = self.output_dir / f"case_{case.case_id}.md"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report)
        except Exception:
            pass
        return report

    def generate_json_report(self, case: InvestigationCase) -> str:
        data = case.model_dump(mode="json")
        file_path = self.output_dir / f"case_{case.case_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
        return json.dumps(data, indent=2)
