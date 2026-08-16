from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.intelligence.mitre import MitreAttackEngine

class MitreLookupTool(Tool):
    """Tool for looking up MITRE ATT&CK techniques, tactics, and procedures."""
    def __init__(self):
        super().__init__(
            name="mitre_lookup",
            description="Lookup MITRE ATT&CK technique details, tactics, and descriptions.",
            category="intelligence",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="MITRE ATT&CK technique lookup"
        )
        self.engine = MitreAttackEngine()

    def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query", "")
        tech = self.engine.get_technique(query)
        if tech:
            return ToolResult(success=True, output=tech.model_dump(mode="json"))

        matches = self.engine.search_techniques(query)
        return ToolResult(success=True, output=[m.model_dump(mode="json") for m in matches])
