import unittest
from lala.remediation.policy import RemediationPolicyEngine, RemediationActionType

class TestAutomationRemediation(unittest.TestCase):
    def test_remediation_confirmation_required(self):
        engine = RemediationPolicyEngine()
        res = engine.evaluate_remediation(RemediationActionType.QUARANTINE_FILE, target="malware.exe", is_user_confirmed=False)
        self.assertFalse(res.allowed)
        self.assertTrue(res.requires_user_confirmation)

if __name__ == "__main__":
    unittest.main()
