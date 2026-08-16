from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel
from lala.security.permissions import PermissionLevel

class ToolResult(BaseModel):
    success: bool
    output: Any
    error: str | None = None

class Tool(ABC):
    """
    Abstract Base Class for all LALA Tools.
    Every tool must explicitly declare its PermissionLevel.
    """
    def __init__(self, name: str, description: str, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        self.name = name
        self.description = description
        self.permission_level = permission_level

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
