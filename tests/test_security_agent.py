import tempfile
import unittest
from lala.security.permissions import SecurityEngine, PermissionLevel

class TestLalaSecurityAgent(unittest.TestCase):
    def test_permission_authorization(self):
        """Verify permission authorization and check results."""
        engine = SecurityEngine(allow_privileged=False)
        
        check_safe = engine.authorize("system_info", PermissionLevel.SAFE_AUTOMATIC)
        self.assertTrue(check_safe.allowed)

        check_read = engine.authorize("file_read", PermissionLevel.READ_ONLY)
        self.assertTrue(check_read.allowed)

        check_priv = engine.authorize("system_shell", PermissionLevel.PRIVILEGED)
        self.assertFalse(check_priv.allowed)

    def test_audit_logging(self):
        """Verify audit trail logging to log file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            log_path = tmp.name

        engine = SecurityEngine(log_path=log_path)
        engine.audit("Mandar", "FileReadTool", "D:\\LALA\\README.md", "READ_ONLY", "SUCCESS")

        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("FileReadTool", content)
        self.assertIn("READ_ONLY", content)

if __name__ == "__main__":
    unittest.main()
