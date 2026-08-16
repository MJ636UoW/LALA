import subprocess
import re
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

FORBIDDEN_SHELL_OPERATORS = [
    "&", "&&", "|", "||", ";", ">", ">>", "<", "`", "$(", "$env:",
    "cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe",
    "python -c", "python -m", "eval", "exec"
]

class SafeCommandTool(Tool):
    """
    Hardened SafeCommandTool protected by strict lexer inspection and command allowlist.
    Prevents shell chaining, redirection, argument injection, and subshell invocation.
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
        command = kwargs.get("command", "").strip()
        if not command:
            return False

        cmd_lower = command.lower()

        # 1. Reject forbidden operators, redirection, or shell chainings
        for op in FORBIDDEN_SHELL_OPERATORS:
            if re.search(r'(?:\s|^)' + re.escape(op) + r'(?:\s|$|;|=|:)', cmd_lower) or op in cmd_lower:
                return False

        # 2. Strict exact match or prefix match against allowlist
        for safe in SAFE_COMMAND_ALLOWLIST:
            if cmd_lower == safe or cmd_lower.startswith(safe + " "):
                return True
        return False

    def execute(self, **kwargs) -> ToolResult:
        command = kwargs.get("command", "").strip()

        if not self.validate(command=command):
            return ToolResult(
                success=False,
                output=None,
                error=f"Access Denied: Command '{command}' is not in the safe allowlist or contains forbidden shell operators. Safe commands: {SAFE_COMMAND_ALLOWLIST}"
            )

        try:
            # Execute command directly without shell=True to eliminate shell injection vulnerabilities
            cmd_parts = command.split()
            res = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=5)
            output = res.stdout if res.returncode == 0 else res.stderr
            return ToolResult(success=res.returncode == 0, output=output.strip(), error=None if res.returncode == 0 else res.stderr.strip())
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
