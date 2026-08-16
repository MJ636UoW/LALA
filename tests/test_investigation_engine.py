import unittest
from lala.investigation.investigation_engine import InvestigationEngine

class TestInvestigationEngine(unittest.TestCase):
    def test_determine_target_type(self):
        engine = InvestigationEngine()
        self.assertEqual(engine.determine_target_type("1.1.1.1"), "IP")
        self.assertEqual(engine.determine_target_type("virustotal.com"), "DOMAIN")
        self.assertEqual(engine.determine_target_type("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"), "HASH")

    def test_investigate_ip_target(self):
        engine = InvestigationEngine()
        case = engine.investigate("1.1.1.1")
        self.assertIsNotNone(case.case_id)
        self.assertEqual(case.target.value, "1.1.1.1")
        self.assertEqual(case.target.target_type, "IP")
        self.assertGreater(len(case.evidence_items), 0)

if __name__ == "__main__":
    unittest.main()
