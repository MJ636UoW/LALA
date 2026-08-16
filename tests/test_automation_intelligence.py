import unittest
from lala.intelligence.manager import IntelligenceManager

class TestAutomationIntelligence(unittest.TestCase):
    def test_online_intelligence_disabled_by_default(self):
        intel = IntelligenceManager()
        self.assertFalse(intel.is_online_enabled())

if __name__ == "__main__":
    unittest.main()
