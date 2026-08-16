from typing import Dict, Any
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.detection.yara_engine import YaraEngine

class YaraScanTool(Tool):
    """
    Phase 7 Safe Tool for scanning authorized workspace files with local YARA rules.
    """
    def __init__(self, engine: YaraEngine):
        super().__init__(
            name="yara_scan",
            description="Scans authorized workspace files/directories using validated local YARA rules.",
            category="cybersecurity",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Safe workspace YARA scanning."
        )
        self.engine = engine

    def execute(self, **kwargs) -> ToolResult:
        target_path = kwargs.get("path") or kwargs.get("target_path")
        if not target_path:
            return ToolResult(success=False, output=None, error="Missing required parameter 'path'.")

        try:
            matches = self.engine.scan_file(str(target_path))
            return ToolResult(
                success=True,
                output={
                    "target_path": str(target_path),
                    "total_matches": len(matches),
                    "matches": [m.model_dump(mode="json") for m in matches]
                }
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
