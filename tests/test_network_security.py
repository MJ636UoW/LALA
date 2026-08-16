import unittest
from lala.security.network_permissions import NetworkSecurityEngine, NetworkPermissionLevel

class TestNetworkSecurityEngine(unittest.TestCase):
    def test_online_disabled_by_default(self):
        """Verify network queries are strictly blocked when online intelligence is disabled."""
        net = NetworkSecurityEngine(online_enabled=False)
        res = net.evaluate_request("https://www.virustotal.com")
        self.assertFalse(res.allowed)
        self.assertEqual(res.permission_level, NetworkPermissionLevel.NETWORK_BLOCKED)

    def test_approved_domain_allowlisting(self):
        """Verify approved domains are authorized when online mode is enabled."""
        net = NetworkSecurityEngine(online_enabled=True)
        res = net.evaluate_request("https://api.abuseipdb.com")
        self.assertTrue(res.allowed)
        self.assertEqual(res.permission_level, NetworkPermissionLevel.NETWORK_READ_ONLY)

    def test_unknown_domain_requires_confirmation(self):
        """Verify unknown domains require user confirmation."""
        net = NetworkSecurityEngine(online_enabled=True)
        res_unconfirmed = net.evaluate_request("https://unknown-threat-site.com", is_user_confirmed=False)
        self.assertFalse(res_unconfirmed.allowed)
        self.assertEqual(res_unconfirmed.permission_level, NetworkPermissionLevel.NETWORK_CONFIRMATION_REQUIRED)

        res_confirmed = net.evaluate_request("https://unknown-threat-site.com", is_user_confirmed=True)
        self.assertTrue(res_confirmed.allowed)

if __name__ == "__main__":
    unittest.main()
