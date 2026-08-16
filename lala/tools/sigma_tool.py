from typing import Dict, Any
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.detection.sigma_engine import SigmaEngine

class SigmaTool(Tool):
    """
    Phase 7 Safe Tool for loading and inspecting defensive Sigma rules.
    """
    def __init__(self, engine: SigmaEngine):
        super().__init__(
            name="sigma_rules",
            description="Lists and validates local defensive Sigma detection rules.",
            category="cybersecurity",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Safe Sigma rule metadata inspection."
        )
        self.engine = engine

    def execute(self, **kwargs) -> ToolResult:
        try:
            rules = self.engine.list_rules()
            return ToolResult(
                success=True,
                output={
                    "total_rules": len(rules),
                    "rules": [r.model_dump(mode="json") for r in rules]
                }
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
