import os
import tempfile
import unittest
from lala.investigation.manager import InvestigationManager

class TestInvestigationCases(unittest.TestCase):
    def test_create_case_and_add_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = InvestigationManager(cases_dir=tmpdir)
            case = mgr.create_case("Operation Triangulation")
            self.assertEqual(case.title, "Operation Triangulation")
            
            added = mgr.add_evidence("1.1.1.1", "IP", "AbuseIPDB", {"score": 99})
            self.assertTrue(added)
            self.assertEqual(len(case.evidence_items), 1)

if __name__ == "__main__":
    unittest.main()
