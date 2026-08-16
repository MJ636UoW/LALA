import unittest
from lala.investigation.manager import InvestigationManager

class TestRAGInvestigation(unittest.TestCase):
    def test_investigation_manager_integration(self):
        mgr = InvestigationManager()
        self.assertIsNotNone(mgr)

if __name__ == "__main__":
    unittest.main()
