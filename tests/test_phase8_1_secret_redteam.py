import unittest
from lala.core.secrets import SecretManager

class TestPhase81SecretRedTeam(unittest.TestCase):
    """15. Secret Protection & Exposure Prevention Red-Team Tests."""

    def test_secrets_never_exposed_in_status_dictionary(self):
        mgr = SecretManager()
        status = mgr.get_status()
        for k, v in status.items():
            self.assertIsInstance(v, bool) # Only boolean indicators, never raw strings

if __name__ == "__main__":
    unittest.main()
