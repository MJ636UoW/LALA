import unittest
from lala.intelligence.manager import IntelligenceManager

class TestProviderManager(unittest.TestCase):
    def test_provider_initialization(self):
        mgr = IntelligenceManager(online_enabled=False)
        self.assertIn("virustotal", mgr.providers)
        self.assertIn("abuseipdb", mgr.providers)
        self.assertFalse(mgr.is_online_enabled())

    def test_toggle_online_mode(self):
        mgr = IntelligenceManager(online_enabled=False)
        mgr.set_online_enabled(True)
        self.assertTrue(mgr.is_online_enabled())

    def test_enable_disable_provider(self):
        mgr = IntelligenceManager()
        self.assertTrue(mgr.disable_provider("virustotal"))
        self.assertFalse(mgr.providers["virustotal"].enabled)

if __name__ == "__main__":
    unittest.main()
