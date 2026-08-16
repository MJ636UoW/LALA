import os
import unittest
from lala.workspace.scanner import WorkspaceScanner
from lala.workspace.models import ProjectType

class TestLalaWorkspace(unittest.TestCase):
    def test_workspace_scanning(self):
        """Verify workspace scanning, project type detection, and Git detection."""
        scanner = WorkspaceScanner(root_path="D:\\LALA")
        ctx = scanner.scan()
        self.assertEqual(ctx.project_type, ProjectType.PYTHON)
        self.assertTrue(ctx.git_detected)
        self.assertGreater(ctx.total_files, 0)
        self.assertGreater(ctx.python_files_count, 0)

    def test_unauthorized_workspace_path(self):
        """Verify path traversal outside authorized workspaces is rejected."""
        scanner = WorkspaceScanner(root_path="C:\\Windows\\System32")
        ctx = scanner.scan()
        self.assertEqual(ctx.project_type, ProjectType.UNKNOWN)
        self.assertIn("error", ctx.statistics)

if __name__ == "__main__":
    unittest.main()
