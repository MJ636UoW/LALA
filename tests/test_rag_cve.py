import unittest
from lala.intelligence.cve import CveVulnerabilityEngine

class TestRAGCve(unittest.TestCase):
    def test_cve_engine_integration(self):
        engine = CveVulnerabilityEngine()
        vuln = engine.get_cve("CVE-2021-44228")
        self.assertIsNotNone(vuln)
        self.assertEqual(vuln.severity, "CRITICAL")

if __name__ == "__main__":
    unittest.main()
