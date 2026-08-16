from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.workspace.scanner import WorkspaceScanner

class WorkspaceScanTool(Tool):
    """Registered tool for running safe workspace discovery."""
    def __init__(self):
        super().__init__(
            name="workspace_scan",
            description="Perform safe workspace discovery, project type detection, and file count analysis.",
            category="workspace",
            permission_level=PermissionLevel.SAFE_AUTOMATIC,
            risk_description="Safe workspace discovery scan"
        )
        self.scanner = WorkspaceScanner()

    def execute(self, **kwargs) -> ToolResult:
        path_str = kwargs.get("path", "D:\\LALA")
        context = self.scanner.scan(path_str)
        return ToolResult(
            success=True,
            output=context.model_dump()
        )
