from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel

class WebSearchTool(Tool):
    """
    Interface stub for local web search tools in Phase 4.
    """
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Interface stub for web search queries.",
            category="web",
            permission_level=PermissionLevel.USER_CONFIRMATION_REQUIRED,
            risk_description="Web network access"
        )

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            success=False,
            output=None,
            error="Web Search Interface Stub: Web network access is disabled in local-first Phase 4 mode."
        )
