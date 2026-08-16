import os
import hashlib
import difflib
from pathlib import Path
from typing import Dict, Any, Optional
from lala.tools.base import Tool, ToolResult
from lala.security.permissions import PermissionLevel
from lala.tools.filesystem import is_path_safe

# Critical security system files protected from self-editing
PROTECTED_SECURITY_FILES = [
    "permissions.py",
    "security",
    "config.py",
    "default_config.yaml",
    "file_edit.py",
    "base.py",
    "registry.py"
]

class FileEditTool(Tool):
    """
    Hardened FileEditTool.
    Requires diff preview, SHA-256 confirmation hash token binding, and blocks self-editing of security policy files.
    """
    def __init__(self):
        super().__init__(
            name="file_edit",
            description="Propose and apply modifications to a text file with diff preview.",
            category="filesystem",
            permission_level=PermissionLevel.USER_CONFIRMATION_REQUIRED,
            risk_description="Modifying file contents on disk"
        )
        self._active_tokens: Dict[str, str] = {} # token -> canonical_path + content_hash

    def validate(self, **kwargs) -> bool:
        path = kwargs.get("path", "")
        if not is_path_safe(path):
            return False

        canonical = os.path.realpath(path).lower()
        # Protect security system files from modification
        for sec_file in PROTECTED_SECURITY_FILES:
            if sec_file in canonical:
                return False
        return True

    def compute_token(self, canonical_path: str, new_content: str) -> str:
        data = f"{canonical_path}:{new_content}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()[:16]

    def generate_diff(self, file_path: str, new_content: str) -> str:
        canonical = os.path.realpath(file_path)
        target = Path(canonical)
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
        provided_token = kwargs.get("token", "")

        if not self.validate(path=path_str):
            return ToolResult(success=False, output=None, error=f"Access Denied: Unsafe file edit path or protected security file: '{path_str}'")

        canonical = os.path.realpath(path_str)
        diff_text = self.generate_diff(canonical, new_content)
        expected_token = self.compute_token(canonical, new_content)

        if not confirmed or provided_token != expected_token:
            # Store active token for verification
            self._active_tokens[expected_token] = canonical
            return ToolResult(
                success=False,
                output={
                    "diff_preview": diff_text,
                    "path": canonical,
                    "confirmation_token": expected_token
                },
                error=f"User Confirmation Required: Review proposed diff preview for '{canonical}' and confirm with matching token '{expected_token}'."
            )

        # Verify token match
        if expected_token not in self._active_tokens:
            return ToolResult(success=False, output=None, error="Access Denied: Stale or invalid confirmation token. Please request a new diff preview.")

        try:
            target = Path(canonical)
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            # Consume single-use token
            del self._active_tokens[expected_token]
            return ToolResult(success=True, output=f"Successfully modified file: '{canonical}'")
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
