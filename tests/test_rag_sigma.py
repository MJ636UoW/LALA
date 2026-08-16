import unittest
from lala.detection.sigma_engine import SigmaEngine

class TestRAGSigma(unittest.TestCase):
    def test_sigma_engine_integration(self):
        engine = SigmaEngine()
        self.assertIsNotNone(engine)

if __name__ == "__main__":
    unittest.main()
