import os
import tempfile
import unittest
from lala.security.project_scanner import CybersecurityProjectScanner

class TestLalaSecurityScanner(unittest.TestCase):
    def test_dangerous_calls_detection(self):
        """Verify AST detector catches eval, exec, os.system."""
        scanner = CybersecurityProjectScanner(root_path="D:\\LALA")
        report = scanner.scan_project()
        self.assertIsNotNone(report)

    def test_secret_file_detection(self):
        """Verify secret files (.env, .pem, .key) are flagged in security scan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            secret_file = os.path.join(tmpdir, "id_rsa")
            with open(secret_file, "w") as f:
                f.write("PRIVATE KEY")

            scanner = CybersecurityProjectScanner(root_path=tmpdir)
            report = scanner.scan_project(tmpdir)
            self.assertGreater(report.total_findings, 0)
            self.assertEqual(report.findings[0].rule_id, "SEC-SECRET-FILE")

if __name__ == "__main__":
    unittest.main()
