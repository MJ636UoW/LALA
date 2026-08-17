import os
import re
import urllib.parse
from pathlib import Path
from typing import List, Optional
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel

# Allowed workspace roots for LALA operations
def get_allowed_workspace_roots() -> list[str]:
    roots = [
        os.path.realpath("D:\\LALA").lower(),
        os.path.realpath("D:\\Projects").lower() if os.path.exists("D:\\Projects") else "d:\\projects",
        os.path.realpath("F:\\LALA").lower(),
        os.path.realpath(os.getcwd()).lower(),
        os.path.realpath(os.environ.get("TEMP", "C:\\AppData\\Local\\Temp")).lower()
    ]
    return roots

ALLOWED_WORKSPACE_ROOTS = get_allowed_workspace_roots()

# Explicitly forbidden system directory prefixes (canonical lower-case)
FORBIDDEN_SYSTEM_DIRS = [
    "c:\\windows",
    "c:\\system32",
    "c:\\program files",
    "c:\\program files (x86)",
    "c:\\recovery",
    "c:\\system volume information"
]

FORBIDDEN_RAW_PATTERNS = ["..", "\\\\", "//", "file:", "%2e", "\x00", "\\\\?\\", "\\\\.\\"]

def is_path_safe(target_path: str, allow_test_tmp: bool = True) -> bool:
    if not target_path or not isinstance(target_path, str):
        return False

    # 1. Null-byte or URL-encoded traversal check
    if "\x00" in target_path:
        return False
        
    decoded_path = urllib.parse.unquote(target_path)
    if "\x00" in decoded_path:
        return False

    # 2. Raw string pattern checks
    raw_lower = target_path.lower()
    for pat in FORBIDDEN_RAW_PATTERNS:
        if pat in raw_lower:
            return False

    # 3. Canonical path resolution
    try:
        abs_path = os.path.abspath(decoded_path)
        canonical = os.path.realpath(abs_path).lower()
    except Exception:
        return False

    # 4. Check for forbidden system directories
    for sys_dir in FORBIDDEN_SYSTEM_DIRS:
        if canonical.startswith(sys_dir):
            return False

    # 5. Check symlink / junction reparse points
    try:
        if os.path.islink(abs_path) or os.path.islink(canonical):
            return False
    except Exception:
        pass

    # 6. Check workspace boundary containment
    is_in_workspace = False
    for root in get_allowed_workspace_roots():
        if canonical == root or canonical.startswith(root + os.sep):
            is_in_workspace = True
            break

    # Allow temp directory for automated test isolation if designated
    if not is_in_workspace and allow_test_tmp:
        tmp_dir = os.path.realpath(os.environ.get("TEMP", "C:\\AppData\\Local\\Temp")).lower()
        if canonical.startswith(tmp_dir + os.sep) or canonical == tmp_dir:
            is_in_workspace = True

    return is_in_workspace

class FileListTool(Tool):
    """List files in an allowed directory with canonical path sanitization."""
    def __init__(self):
        super().__init__(
            name="file_list",
            description="List contents of a directory in allowed workspaces.",
            category="filesystem",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Directory listing read"
        )

    def validate(self, **kwargs) -> bool:
        path = kwargs.get("path", "D:\\LALA")
        return is_path_safe(path)

    def execute(self, **kwargs) -> ToolResult:
        path_str = kwargs.get("path", "D:\\LALA")
        if not self.validate(path=path_str):
            return ToolResult(success=False, output=None, error=f"Access Denied: Path outside allowed workspace or invalid traversal: '{path_str}'")

        try:
            canonical = os.path.realpath(path_str)
            target = Path(canonical)
            if not target.exists() or not target.is_dir():
                return ToolResult(success=False, output=None, error=f"Directory does not exist: '{path_str}'")

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
    """Read a text file in an allowed workspace with canonical path sanitization."""
    def __init__(self):
        super().__init__(
            name="file_read",
            description="Read content of a text file in an allowed workspace.",
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
            return ToolResult(success=False, output=None, error=f"Access Denied: Path outside allowed workspace or invalid traversal: '{path_str}'")

        try:
            canonical = os.path.realpath(path_str)
            target = Path(canonical)
            if not target.exists() or not target.is_file():
                return ToolResult(success=False, output=None, error=f"File does not exist: '{path_str}'")

            with open(target, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(100000) # Max 100KB per read
            return ToolResult(success=True, output=content)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

class FileSearchTool(Tool):
    """Search for matching files or text within an allowed directory with canonical path sanitization."""
    def __init__(self):
        super().__init__(
            name="file_search",
            description="Search files matching a name pattern or text query.",
            category="filesystem",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="File pattern search"
        )

    def validate(self, **kwargs) -> bool:
        path = kwargs.get("path", "D:\\LALA")
        return is_path_safe(path)

    def execute(self, **kwargs) -> ToolResult:
        path_str = kwargs.get("path", "D:\\LALA")
        query = kwargs.get("query", "").lower()
        if not self.validate(path=path_str):
            return ToolResult(success=False, output=None, error=f"Access Denied: Path outside allowed workspace: '{path_str}'")

        try:
            canonical = os.path.realpath(path_str)
            target = Path(canonical)
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
