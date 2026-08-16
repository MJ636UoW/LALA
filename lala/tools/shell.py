import subprocess
from typing import List
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel

SAFE_COMMAND_ALLOWLIST = [
    "python --version",
    "git --version",
    "git status",
    "git branch",
    "git log",
    "ollama list",
    "ollama --version",
    "where python",
    "where git"
]

RISKY_COMMAND_PATTERNS = [
    "pip install", "git push", "git reset", "git checkout",
    "remove-item", "del ", "format ", "shutdown", "taskkill", "netsh"
]

class SafeCommandTool(Tool):
    """
    Safe command execution tool protected by strict command allowlist.
    """
    def __init__(self):
        super().__init__(
            name="safe_command",
            description="Run whitelisted inspection commands (python --version, git status, ollama list, etc.).",
            category="system",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Allowlisted CLI command execution"
        )

    def validate(self, **kwargs) -> bool:
        command = kwargs.get("command", "").strip().lower()
        # Direct check against allowlist
        for safe in SAFE_COMMAND_ALLOWLIST:
            if command.startswith(safe):
                return True
        return False

    def execute(self, **kwargs) -> ToolResult:
        command = kwargs.get("command", "").strip()
        cmd_lower = command.lower()

        # Check if risky
        is_risky = any(pat in cmd_lower for pat in RISKY_COMMAND_PATTERNS)
        if is_risky:
            return ToolResult(
                success=False,
                output=None,
                error=f"User Confirmation Required: Command '{command}' is classified as risky and requires explicit user approval."
            )

        if not self.validate(command=command):
            return ToolResult(
                success=False,
                output=None,
                error=f"Access Denied: Command '{command}' is not in the safe allowlist. Safe commands: {SAFE_COMMAND_ALLOWLIST}"
            )

        try:
            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
            output = res.stdout if res.returncode == 0 else res.stderr
            return ToolResult(success=res.returncode == 0, output=output.strip(), error=None if res.returncode == 0 else res.stderr.strip())
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
