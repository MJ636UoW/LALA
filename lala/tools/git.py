import subprocess
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel

class GitTool(Tool):
    """
    Controlled Git repository tool with permission tiering.
    Read operations (status, branch, log, diff) run automatically;
    Write operations (add, commit, push) require USER_CONFIRMATION_REQUIRED.
    """
    def __init__(self):
        super().__init__(
            name="git_tool",
            description="Perform Git status, log, diff, or commit operations.",
            category="vcs",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Git repository inspection and management"
        )

    def execute(self, **kwargs) -> ToolResult:
        subcommand = kwargs.get("subcommand", "status").strip().lower()
        args = kwargs.get("args", "")

        read_commands = ["status", "branch", "log", "diff"]
        write_commands = ["add", "commit", "push", "checkout", "reset"]

        if subcommand in write_commands:
            return ToolResult(
                success=False,
                output=None,
                error=f"User Confirmation Required: Git '{subcommand}' modifies repository state and requires explicit approval."
            )

        if subcommand not in read_commands:
            return ToolResult(success=False, output=None, error=f"Invalid Git subcommand '{subcommand}'. Allowed: {read_commands + write_commands}")

        try:
            full_cmd = f"git {subcommand} {args}".strip()
            res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=5, cwd="D:\\LALA")
            return ToolResult(success=res.returncode == 0, output=res.stdout.strip(), error=None if res.returncode == 0 else res.stderr.strip())
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
