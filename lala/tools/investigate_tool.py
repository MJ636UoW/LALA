from typing import Dict, Any
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.investigation.investigation_engine import InvestigationEngine

class InvestigateTool(Tool):
    """
    Phase 7 Safe Tool for running cybersecurity threat investigations on IOCs.
    """
    def __init__(self, engine: InvestigationEngine):
        super().__init__(
            name="investigate_ioc",
            description="Investigates an IP, domain, URL, hash, or local file, calculating threat score, correlations, and evidence provenance.",
            category="cybersecurity",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Safe read-only threat investigation."
        )
        self.engine = engine

    def execute(self, **kwargs) -> ToolResult:
        target = kwargs.get("target") or kwargs.get("ioc")
        if not target:
            return ToolResult(success=False, output=None, error="Missing required parameter 'target'.")

        try:
            case = self.engine.investigate(str(target))
            return ToolResult(
                success=True,
                output={
                    "case_id": case.case_id,
                    "title": case.title,
                    "target": case.target.model_dump() if case.target else None,
                    "severity": case.severity.value,
                    "risk_score": case.risk_score.model_dump() if case.risk_score else None,
                    "evidence_count": len(case.evidence_items),
                    "recommendations": case.recommendations
                }
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
