import unittest
from lala.automation.recovery import SafeRecoveryEngine
from lala.automation.models import ActionClass

class TestAutomationRecovery(unittest.TestCase):
    def test_transient_error_retry(self):
        recovery = SafeRecoveryEngine()
        retry, msg = recovery.should_retry("Connection timeout", ActionClass.NETWORK_LOOKUP, 0)
        self.assertTrue(retry)

    def test_permission_denial_refuses_retry(self):
        recovery = SafeRecoveryEngine()
        retry, msg = recovery.should_retry("Permission denied by SecurityEngine", ActionClass.DESTRUCTIVE, 0)
        self.assertFalse(retry)

if __name__ == "__main__":
    unittest.main()
