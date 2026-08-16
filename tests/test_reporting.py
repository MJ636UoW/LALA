import unittest
from lala.investigation.models import InvestigationCase
from lala.investigation.reporter import InvestigationReporter

class TestReporting(unittest.TestCase):
    def test_markdown_report_generation(self):
        reporter = InvestigationReporter()
        case = InvestigationCase(case_id="c123", title="Test Reporting Case")
        rep = reporter.generate_markdown_report(case)
        self.assertIn("# LALA CYBERSECURITY INVESTIGATION REPORT", rep)
        self.assertIn("Test Reporting Case", rep)

if __name__ == "__main__":
    unittest.main()
