import difflib
from pathlib import Path
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.tools.filesystem import is_path_safe

class FileEditTool(Tool):
    """
    Controlled file editing tool.
    Generates a unified diff preview and requires USER_CONFIRMATION_REQUIRED before modifying any file.
    """
    def __init__(self):
        super().__init__(
            name="file_edit",
            description="Propose and apply modifications to a text file with diff preview.",
            category="filesystem",
            permission_level=PermissionLevel.USER_CONFIRMATION_REQUIRED,
            risk_description="Modifying file contents on disk"
        )

    def validate(self, **kwargs) -> bool:
        path = kwargs.get("path", "")
        return is_path_safe(path)

    def generate_diff(self, file_path: str, new_content: str) -> str:
        target = Path(file_path)
        old_lines = []
        if target.exists() and target.is_file():
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                old_lines = f.readlines()
        
        new_lines = new_content.splitlines(keepends=True)
        diff = difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{target.name}", tofile=f"b/{target.name}")
        return "".join(diff)

    def execute(self, **kwargs) -> ToolResult:
        path_str = kwargs.get("path", "")
        new_content = kwargs.get("new_content", "")
        confirmed = kwargs.get("confirmed", False)

        if not self.validate(path=path_str):
            return ToolResult(success=False, output=None, error=f"Access Denied: Unsafe file edit path: {path_str}")

        diff_text = self.generate_diff(path_str, new_content)

        if not confirmed:
            return ToolResult(
                success=False,
                output={"diff_preview": diff_text, "path": path_str},
                error=f"User Confirmation Required: Review proposed diff preview for '{path_str}' and confirm with YES."
            )

        try:
            target = Path(path_str)
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(new_content)
            return ToolResult(success=True, output=f"Successfully modified file: {path_str}")
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
