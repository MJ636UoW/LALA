from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.intelligence.cve import CveVulnerabilityEngine

class CveLookupTool(Tool):
    """Tool for looking up CVE vulnerability details and CISA KEV status."""
    def __init__(self):
        super().__init__(
            name="cve_lookup",
            description="Lookup CVE vulnerability details, CVSS scores, and CISA KEV status.",
            category="intelligence",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="CVE vulnerability intelligence lookup"
        )
        self.engine = CveVulnerabilityEngine()

    def execute(self, **kwargs) -> ToolResult:
        cve_id = kwargs.get("cve_id", "")
        vuln = self.engine.get_cve(cve_id)
        if vuln:
            return ToolResult(success=True, output=vuln.model_dump(mode="json"))
        return ToolResult(success=False, output=None, error=f"CVE record '{cve_id}' not found.")
