from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from lala.security.permissions import PermissionLevel

class ToolResult(BaseModel):
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0

class Tool(ABC):
    """
    Abstract Base Class for all LALA Tools.
    Every tool explicitly defines name, category, permission_level, input_schema, output_schema, validate(), and risk_description.
    """
    def __init__(
        self,
        name: str,
        description: str,
        category: str = "general",
        permission_level: PermissionLevel = PermissionLevel.READ_ONLY,
        risk_description: str = "Standard safe read-only operation"
    ):
        self.name = name
        self.description = description
        self.category = category
        self.permission_level = permission_level
        self.risk_description = risk_description

    def validate(self, **kwargs) -> bool:
        """Validate input arguments before execution."""
        return True

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
