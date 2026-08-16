from typing import Dict, Optional, List
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import SecurityEngine, PermissionLevel
from lala.utils.logging import logger

class ToolRegistry:
    """
    Registry for managing LALA tools.
    Enforces security authorization via SecurityEngine before executing any registered tool.
    """
    def __init__(self, security_engine: Optional[SecurityEngine] = None):
        self.tools: Dict[str, Tool] = {}
        self.security_engine = security_engine or SecurityEngine()

    def register_tool(self, tool: Tool) -> bool:
        if tool.name in self.tools:
            logger.warning(f"Tool '{tool.name}' is already registered. Overwriting registration.")
        self.tools[tool.name] = tool
        return True

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, output=None, error=f"Tool '{name}' not found in registry.")

        # Check permissions
        check = self.security_engine.evaluate(tool.name, tool.permission_level)
        if not check.allowed:
            return ToolResult(
                success=False,
                output=None,
                error=f"Security Policy Denied Execution: {check.reason}"
            )

        return tool.execute(**kwargs)
