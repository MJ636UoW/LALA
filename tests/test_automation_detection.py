import unittest
from lala.detection.static_analysis import LocalStaticAnalyzer

class TestAutomationDetection(unittest.TestCase):
    def test_static_analyzer(self):
        analyzer = LocalStaticAnalyzer()
        self.assertIsNotNone(analyzer)

if __name__ == "__main__":
    unittest.main()
