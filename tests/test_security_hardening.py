import os
import tempfile
import unittest
from lala.tools.filesystem import FileListTool, FileReadTool, FileSearchTool, is_path_safe
from lala.tools.shell import SafeCommandTool
from lala.tools.file_edit import FileEditTool
from lala.tools.git import GitTool
from lala.security.permissions import SecurityEngine, PermissionLevel
from lala.memory.manager import MemoryManager
from lala.memory.models import MemoryCategory
from lala.core.orchestrator import Orchestrator, MAX_TOOL_ITERATIONS

class TestLalaSecurityHardening(unittest.TestCase):
    """
    Comprehensive Red-Team Regression Test Suite for LALA Phase 4.5.
    Verifies that security boundaries cannot be bypassed via path traversal, shell injection, confirmation tampering, or privilege escalation.
    """

    # 1. WINDOWS PATH SECURITY
    def test_path_traversal_rejection(self):
        """Verify path traversal (.., ../.., ..\\..) is strictly blocked."""
        self.assertFalse(is_path_safe("D:\\LALA\\..\\..\\Windows\\System32"))
        self.assertFalse(is_path_safe("../../../etc/passwd"))
        self.assertFalse(is_path_safe("..\\..\\Windows\\System32\\cmd.exe"))

    def test_absolute_system_path_escape(self):
        """Verify absolute paths outside allowed workspaces are strictly blocked."""
        self.assertFalse(is_path_safe("C:\\Windows\\System32\\cmd.exe"))
        self.assertFalse(is_path_safe("C:\\Users\\manda\\Desktop\\secrets.txt"))

    def test_unc_and_device_paths(self):
        """Verify UNC paths (\\\\server\\share) and device paths (\\\\?\\) are blocked."""
        self.assertFalse(is_path_safe("\\\\server\\share\\data.txt"))
        self.assertFalse(is_path_safe("\\\\localhost\\c$\\Windows"))
        self.assertFalse(is_path_safe("\\\\?\\C:\\Windows\\System32"))
        self.assertFalse(is_path_safe("\\\\.\\PhysicalDrive0"))

    def test_url_and_encoded_traversal(self):
        """Verify URL schemes and %2e encoded traversal are blocked."""
        self.assertFalse(is_path_safe("file:///C:/Windows/System32"))
        self.assertFalse(is_path_safe("%2e%2e%2f%2e%2e%2fWindows"))

    def test_null_byte_injection(self):
        """Verify null-byte character path injection is blocked."""
        self.assertFalse(is_path_safe("D:\\LALA\\README.md\x00.png"))

    # 2. SHELL COMMAND SECURITY
    def test_shell_chaining_rejection(self):
        """Verify shell chaining operators (&, &&, |, ||, ;) are rejected."""
        tool = SafeCommandTool()
        self.assertFalse(tool.validate(command="python --version & calc.exe"))
        self.assertFalse(tool.validate(command="git status && whoami"))
        self.assertFalse(tool.validate(command="ollama list | clip"))
        self.assertFalse(tool.validate(command="where python ; calc.exe"))

    def test_subshell_and_process_wrappers(self):
        """Verify process wrappers and subshells are rejected."""
        tool = SafeCommandTool()
        self.assertFalse(tool.validate(command="cmd.exe /c calc.exe"))
        self.assertFalse(tool.validate(command="powershell -c Get-Process"))
        self.assertFalse(tool.validate(command="python -c \"import os; os.system('calc')\""))
        self.assertFalse(tool.validate(command="$(whoami)"))

    def test_unwhitelisted_commands(self):
        """Verify unwhitelisted CLI commands are denied execution."""
        tool = SafeCommandTool()
        self.assertFalse(tool.validate(command="taskkill /f /im explorer.exe"))
        self.assertFalse(tool.validate(command="netstat -an"))

    # 3. FILE EDIT SECURITY
    def test_file_edit_unconfirmed_rejection(self):
        """Verify FileEditTool rejects edits without confirmation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            f_path = os.path.join(tmpdir, "test.py")
            with open(f_path, "w") as f:
                f.write("x = 1")
            
            tool = FileEditTool()
            res = tool.execute(path=f_path, new_content="x = 2", confirmed=False)
            self.assertFalse(res.success)
            self.assertIn("confirmation_token", res.output)

    def test_file_edit_stale_or_invalid_token(self):
        """Verify FileEditTool rejects edits with stale or invalid token."""
        with tempfile.TemporaryDirectory() as tmpdir:
            f_path = os.path.join(tmpdir, "test.py")
            with open(f_path, "w") as f:
                f.write("x = 1")

            tool = FileEditTool()
            res = tool.execute(path=f_path, new_content="x = 2", confirmed=True, token="invalid_token_123")
            self.assertFalse(res.success)

    def test_protected_security_files(self):
        """Verify FileEditTool blocks self-editing of security policy files."""
        tool = FileEditTool()
        self.assertFalse(tool.validate(path="D:\\LALA\\lala\\security\\permissions.py"))
        self.assertFalse(tool.validate(path="D:\\LALA\\lala\\tools\\file_edit.py"))
        self.assertFalse(tool.validate(path="D:\\LALA\\config\\default_config.yaml"))

    # 4. GIT SECURITY
    def test_git_write_ops_require_confirmation(self):
        """Verify Git write operations (commit, push) require confirmation."""
        tool = GitTool()
        res_commit = tool.execute(subcommand="commit", args="-m 'test'", confirmed=False)
        self.assertFalse(res_commit.success)
        self.assertIn("User Confirmation Required", res_commit.error)

        res_push = tool.execute(subcommand="push", args="origin main", confirmed=False)
        self.assertFalse(res_push.success)

    def test_git_option_injection_defense(self):
        """Verify Git option injection (--upload-pack, -c) is blocked."""
        tool = GitTool()
        self.assertFalse(tool.validate(subcommand="status", args="--upload-pack=calc.exe"))
        self.assertFalse(tool.validate(subcommand="log", args="; calc.exe"))

    # 5. SECURITY ENGINE SELF-PROTECTION
    def test_privilege_escalation_denial(self):
        """Verify SecurityEngine denies PRIVILEGED execution requests."""
        engine = SecurityEngine(allow_privileged=False)
        res = engine.authorize("system_shell", PermissionLevel.PRIVILEGED)
        self.assertFalse(res.allowed)
        self.assertIn("strictly disabled", res.reason)

    # 6. MEMORY SECURITY
    def test_sensitive_memory_persistence_blocked(self):
        """Verify sensitive memory is never written to disk database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_sec.db")
            mem = MemoryManager(db_path=db_path)
            saved = mem.save_memory("Master Key ABC123", category=MemoryCategory.SENSITIVE)
            self.assertFalse(saved)

            found = mem.search_memory("ABC123")
            self.assertEqual(len(found), 0)

    # 7. AGENT LOOP ITERATION LIMIT
    def test_max_tool_iteration_cap(self):
        """Verify MAX_TOOL_ITERATIONS cap equals 5."""
        self.assertEqual(MAX_TOOL_ITERATIONS, 5)

    # 8. AUDIT LOGGING
    def test_audit_logging_generation(self):
        """Verify audit log records authorization events."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            log_path = tmp.name

        engine = SecurityEngine(log_path=log_path)
        engine.audit("Mandar", "file_read", "D:\\LALA\\README.md", "READ_ONLY", "SUCCESS")

        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("file_read", content)
        self.assertIn("SUCCESS", content)

if __name__ == "__main__":
    unittest.main()
