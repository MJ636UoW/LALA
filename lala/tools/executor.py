from typing import Optional
from lala.tools.base import ToolResult
from lala.tools.registry import ToolRegistry
from lala.tools.planner import ToolCallRequest

class ToolExecutor:
    """
    Executes tool requests validated by ToolPlanner through ToolRegistry and SecurityEngine.
    """
    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or ToolRegistry()

    def execute_request(self, request: ToolCallRequest) -> ToolResult:
        return self.registry.execute_tool(request.tool, **request.arguments)
