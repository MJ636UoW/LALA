from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.security.project_scanner import CybersecurityProjectScanner

class SecurityScanTool(Tool):
    """Registered tool for running safe static cybersecurity analysis."""
    def __init__(self):
        super().__init__(
            name="security_scan",
            description="Run defensive static cybersecurity scan on workspace.",
            category="security",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Static cybersecurity analysis read"
        )
        self.scanner = CybersecurityProjectScanner()

    def execute(self, **kwargs) -> ToolResult:
        path_str = kwargs.get("path", "D:\\LALA")
        report = self.scanner.scan_project(path_str)
        return ToolResult(
            success=True,
            output={
                "total_findings": report.total_findings,
                "high_count": report.high_count,
                "medium_count": report.medium_count,
                "findings": [f.model_dump() for f in report.findings[:10]]
            }
        )
