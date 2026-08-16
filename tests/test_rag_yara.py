import unittest
from lala.detection.yara_engine import YaraEngine

class TestRAGYara(unittest.TestCase):
    def test_yara_engine_integration(self):
        engine = YaraEngine()
        self.assertIsNotNone(engine)

if __name__ == "__main__":
    unittest.main()
