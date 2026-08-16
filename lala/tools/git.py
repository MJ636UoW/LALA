import subprocess
import re
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel

FORBIDDEN_GIT_ARGS = ["--upload-pack", "--config", "-c", ";", "&", "|", "`", "$"]

class GitTool(Tool):
    """
    Hardened Git repository tool with permission tiering and option injection defense.
    Read operations (status, branch, log, diff) run automatically under READ_ONLY.
    Write operations (add, commit, push, checkout, reset) strictly require USER_CONFIRMATION_REQUIRED.
    """
    def __init__(self):
        super().__init__(
            name="git_tool",
            description="Perform Git status, log, diff, or commit operations.",
            category="vcs",
            permission_level=PermissionLevel.READ_ONLY,
            risk_description="Git repository inspection and management"
        )

    def validate(self, **kwargs) -> bool:
        subcommand = kwargs.get("subcommand", "status").strip().lower()
        args = kwargs.get("args", "").strip()

        for forbidden in FORBIDDEN_GIT_ARGS:
            if forbidden in args:
                return False
        return True

    def execute(self, **kwargs) -> ToolResult:
        subcommand = kwargs.get("subcommand", "status").strip().lower()
        args = kwargs.get("args", "").strip()
        confirmed = kwargs.get("confirmed", False)

        if not self.validate(subcommand=subcommand, args=args):
            return ToolResult(success=False, output=None, error=f"Access Denied: Unsafe Git subcommand or option injection detected: '{args}'")

        read_commands = ["status", "branch", "log", "diff"]
        write_commands = ["add", "commit", "push", "checkout", "reset", "rebase", "merge"]

        if subcommand in write_commands:
            if not confirmed:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"User Confirmation Required: Git '{subcommand}' modifies repository state. Please review and confirm with YES."
                )

        if subcommand not in read_commands and subcommand not in write_commands:
            return ToolResult(success=False, output=None, error=f"Invalid Git subcommand '{subcommand}'. Allowed: {read_commands + write_commands}")

        try:
            cmd_list = ["git", subcommand]
            if args:
                cmd_list.extend(args.split())

            res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=5, cwd="D:\\LALA")
            return ToolResult(success=res.returncode == 0, output=res.stdout.strip(), error=None if res.returncode == 0 else res.stderr.strip())
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
