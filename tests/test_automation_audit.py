import unittest
from lala.automation.audit import AutomationAuditLogger

class TestAutomationAudit(unittest.TestCase):
    def test_sanitize_entry_redacts_secrets(self):
        logger = AutomationAuditLogger()
        entry = {"action": "intel_lookup", "api_key": "secret_key_12345", "target": "1.1.1.1"}
        sanitized = logger.sanitize_entry(entry)
        self.assertEqual(sanitized["api_key"], "[REDACTED_SECRET]")

if __name__ == "__main__":
    unittest.main()
