from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.intelligence.manager import IntelligenceManager

class IntelLookupTool(Tool):
    """Tool for querying online threat intelligence sources (IP, Domain, URL, Hash)."""
    def __init__(self, intel_manager: IntelligenceManager):
        super().__init__(
            name="intel_lookup",
            description="Lookup cybersecurity intelligence for IP, Domain, URL, or Hash.",
            category="intelligence",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Online cybersecurity threat intelligence lookup"
        )
        self.intel_manager = intel_manager

    def execute(self, **kwargs) -> ToolResult:
        ioc_type = kwargs.get("ioc_type", "IP").upper()
        value = kwargs.get("value", "")
        confirmed = kwargs.get("confirmed", False)

        if not value:
            return ToolResult(success=False, output=None, error="No IOC value provided for lookup.")

        res = self.intel_manager.lookup_indicator(ioc_type=ioc_type, value=value, is_user_confirmed=confirmed)
        return ToolResult(success=True, output=res.model_dump(mode="json"))
