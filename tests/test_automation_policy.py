import unittest
from lala.automation.policy import AutomationPolicyEngine
from lala.automation.models import ActionClass, AutomationMode

class TestAutomationPolicy(unittest.TestCase):
    def test_action_classification(self):
        engine = AutomationPolicyEngine()
        self.assertEqual(engine.classify_action("read_file"), ActionClass.READ_ONLY)
        self.assertEqual(engine.classify_action("yara_scan"), ActionClass.ANALYSIS)
        self.assertEqual(engine.classify_action("intel_lookup"), ActionClass.NETWORK_LOOKUP)
        self.assertEqual(engine.classify_action("delete_file"), ActionClass.DESTRUCTIVE)

    def test_safe_mode_evaluation(self):
        engine = AutomationPolicyEngine(mode=AutomationMode.SAFE)
        allowed, msg, risk = engine.evaluate_action("read_file")
        self.assertTrue(allowed)

        allowed_dest, msg_dest, risk_dest = engine.evaluate_action("delete_file")
        self.assertFalse(allowed_dest)
        self.assertIn("USER_CONFIRMATION_REQUIRED", msg_dest)

if __name__ == "__main__":
    unittest.main()
