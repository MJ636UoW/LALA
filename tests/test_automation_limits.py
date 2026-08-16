import unittest
from lala.automation.workflow import MAX_ACTIONS, MAX_RUNTIME_SEC

class TestAutomationLimits(unittest.TestCase):
    def test_automation_hard_limits(self):
        self.assertEqual(MAX_ACTIONS, 25)
        self.assertEqual(MAX_RUNTIME_SEC, 300)

if __name__ == "__main__":
    unittest.main()
