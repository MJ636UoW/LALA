import unittest
from lala.intelligence.cve import CveVulnerabilityEngine

class TestCveIntelligence(unittest.TestCase):
    def test_known_cve_lookup(self):
        engine = CveVulnerabilityEngine()
        vuln = engine.get_cve("CVE-2021-44228")
        self.assertIsNotNone(vuln)
        self.assertEqual(vuln.cvss_score, 10.0)
        self.assertTrue(vuln.is_cisa_kev)

if __name__ == "__main__":
    unittest.main()
