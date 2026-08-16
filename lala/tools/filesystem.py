import os
import re
from pathlib import Path
from typing import List, Optional
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel

FORBIDDEN_PATTERNS = ["..", "\\\\", "//"]
RESTRICTED_DIRS = ["c:\\windows", "c:\\system32", "c:\\program files"]

def is_path_safe(target_path: str) -> bool:
    normalized = os.path.abspath(target_path).lower()
    
    # Path traversal check
    for pat in FORBIDDEN_PATTERNS:
        if pat in target_path:
            return False
            
    # Restricted system dir check
    for res_dir in RESTRICTED_DIRS:
        if normalized.startswith(res_dir):
            return False
            
    return True

class FileListTool(Tool):
    """List files in an allowed directory."""
    def __init__(self):
        super().__init__(
            name="file_list",
            description="List contents of a directory in allowed workspaces.",
            category="filesystem",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Directory listing read"
        )

    def validate(self, **kwargs) -> bool:
        path = kwargs.get("path", "")
        return is_path_safe(path)

    def execute(self, **kwargs) -> ToolResult:
        path_str = kwargs.get("path", ".")
        if not self.validate(path=path_str):
            return ToolResult(success=False, output=None, error=f"Access Denied: Unsafe path or path traversal detected: {path_str}")

        try:
            target = Path(path_str)
            if not target.exists() or not target.is_dir():
                return ToolResult(success=False, output=None, error=f"Directory does not exist: {path_str}")

            entries = []
            for item in target.iterdir():
                entries.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size_bytes": item.stat().st_size if item.is_file() else 0
                })
            return ToolResult(success=True, output=entries)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

class FileReadTool(Tool):
    """Read a text file in an allowed workspace."""
    def __init__(self):
        super().__init__(
            name="file_read",
            description="Read content of a text file.",
            category="filesystem",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="File content read"
        )

    def validate(self, **kwargs) -> bool:
        path = kwargs.get("path", "")
        return is_path_safe(path)

    def execute(self, **kwargs) -> ToolResult:
        path_str = kwargs.get("path", "")
        if not self.validate(path=path_str):
            return ToolResult(success=False, output=None, error=f"Access Denied: Unsafe path or path traversal detected: {path_str}")

        try:
            target = Path(path_str)
            if not target.exists() or not target.is_file():
                return ToolResult(success=False, output=None, error=f"File does not exist: {path_str}")

            with open(target, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(100000) # Max 100KB per read
            return ToolResult(success=True, output=content)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

class FileSearchTool(Tool):
    """Search for matching files or text within an allowed directory."""
    def __init__(self):
        super().__init__(
            name="file_search",
            description="Search files matching a name pattern or text query.",
            category="filesystem",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="File pattern search"
        )

    def validate(self, **kwargs) -> bool:
        path = kwargs.get("path", "")
        return is_path_safe(path)

    def execute(self, **kwargs) -> ToolResult:
        path_str = kwargs.get("path", ".")
        query = kwargs.get("query", "").lower()
        if not self.validate(path=path_str):
            return ToolResult(success=False, output=None, error=f"Access Denied: Unsafe path: {path_str}")

        try:
            target = Path(path_str)
            matches = []
            for root, dirs, files in os.walk(target):
                for f in files:
                    if query in f.lower():
                        matches.append(os.path.join(root, f))
                    if len(matches) >= 20:
                        break
                if len(matches) >= 20:
                    break
            return ToolResult(success=True, output=matches)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
