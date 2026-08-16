import unittest
from lala.detection.sigma_engine import SigmaEngine

class TestSigmaEngine(unittest.TestCase):
    def test_list_and_parse_sigma_rules(self):
        engine = SigmaEngine()
        rules = engine.list_rules()
        self.assertIsInstance(rules, list)

if __name__ == "__main__":
    unittest.main()
