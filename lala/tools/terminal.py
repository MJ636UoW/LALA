import subprocess
import shutil
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.utils.logging import logger

ALLOWED_TERMINAL_COMMANDS = ["curl", "wget", "git", "python", "dir", "ls", "echo", "ping", "systeminfo", "whoami"]

class TerminalToolInput(BaseModel):
    command: str

class SandboxedTerminalTool(Tool):
    """
    Sandboxed Terminal Tool for LALA.
    Allows LALA to execute inspection commands, download files via curl/wget, and inspect processes in the sandbox environment.
    Enforces command safety validation and timeout boundaries.
    """
    def __init__(self):
        super().__init__(
            name="sandboxed_terminal",
            description="Execute safe diagnostic commands, download resources (curl/wget), or inspect processes in the sandbox environment.",
            permission_level=PermissionLevel.READ_ONLY
        )

    def execute(self, **kwargs) -> ToolResult:
        cmd_str = str(kwargs.get("command", "")).strip()
        if not cmd_str:
            return ToolResult(success=False, output="", error="No command provided.")

        base_cmd = cmd_str.split()[0].lower() if cmd_str.split() else ""
        if base_cmd not in ALLOWED_TERMINAL_COMMANDS:
            return ToolResult(
                success=False,
                output="",
                error=f"Command '{base_cmd}' is not permitted in sandboxed terminal. Allowed commands: {', '.join(ALLOWED_TERMINAL_COMMANDS)}"
            )

        try:
            logger.info(f"SandboxedTerminalTool: Executing command '{cmd_str}'...")
            res = subprocess.run(
                cmd_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                cwd="D:\\LALA" if os.path.exists("D:\\LALA") else os.getcwd()
            )
            output = res.stdout if res.returncode == 0 else (res.stdout + "\n" + res.stderr)
            return ToolResult(success=res.returncode == 0, output=output.strip() or "Command completed with no output.")
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, output="", error=f"Command '{cmd_str}' timed out after 10s.")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
