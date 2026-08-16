import os
import tempfile
import unittest
from lala.tools.system_info import SystemInfoTool
from lala.tools.filesystem import FileListTool, FileReadTool, FileSearchTool, is_path_safe
from lala.tools.python_analysis import PythonAnalysisTool
from lala.tools.shell import SafeCommandTool
from lala.tools.git import GitTool
from lala.tools.file_edit import FileEditTool
from lala.tools.web import WebSearchTool

class TestLalaToolsSubsystem(unittest.TestCase):
    def test_path_sanitization(self):
        """Verify path traversal prevention."""
        self.assertTrue(is_path_safe("D:\\LALA\\README.md"))
        self.assertFalse(is_path_safe("D:\\LALA\\..\\..\\Windows\\System32"))
        self.assertFalse(is_path_safe("C:\\Windows\\System32\\cmd.exe"))

    def test_system_info_tool(self):
        """Verify SystemInfoTool execution."""
        tool = SystemInfoTool()
        res = tool.execute()
        self.assertTrue(res.success)
        self.assertIn("python_version", res.output)

    def test_filesystem_tools(self):
        """Verify file listing and reading within safe directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("LALA Phase 4 Test")

            read_tool = FileReadTool()
            res = read_tool.execute(path=file_path)
            self.assertTrue(res.success)
            self.assertEqual(res.output, "LALA Phase 4 Test")

    def test_python_analysis_tool(self):
        """Verify Python code AST analysis tool."""
        tool = PythonAnalysisTool()
        code = "def sample(): return 42"
        res = tool.execute(code=code)
        self.assertTrue(res.success)
        self.assertIn("sample", res.output["functions_found"])

    def test_safe_command_allowlist(self):
        """Verify SafeCommandTool enforces command allowlist."""
        tool = SafeCommandTool()
        res_safe = tool.execute(command="python --version")
        self.assertTrue(res_safe.success)

        res_unsafe = tool.execute(command="format C:")
        self.assertFalse(res_unsafe.success)
        self.assertIn("User Confirmation Required", res_unsafe.error)

    def test_file_edit_tool_diff(self):
        """Verify FileEditTool diff preview generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "edit_test.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Line 1\nLine 2\n")

            tool = FileEditTool()
            res_unconfirmed = tool.execute(path=file_path, new_content="Line 1\nLine 2 Modified\n", confirmed=False)
            self.assertFalse(res_unconfirmed.success)
            self.assertIn("diff_preview", res_unconfirmed.output)

            res_confirmed = tool.execute(path=file_path, new_content="Line 1\nLine 2 Modified\n", confirmed=True)
            self.assertTrue(res_confirmed.success)

if __name__ == "__main__":
    unittest.main()
