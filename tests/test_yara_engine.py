import os
import tempfile
import unittest
from lala.detection.yara_engine import YaraEngine

class TestYaraEngine(unittest.TestCase):
    def test_workspace_path_authorization(self):
        engine = YaraEngine()
        self.assertTrue(engine.is_path_authorized("D:\\LALA\\lala\\core\\config.py"))
        self.assertFalse(engine.is_path_authorized("C:\\Windows\\System32\\cmd.exe"))

    def test_scan_authorized_file(self):
        engine = YaraEngine()
        matches = engine.scan_file("D:\\LALA\\lala\\core\\config.py")
        self.assertIsInstance(matches, list)

if __name__ == "__main__":
    unittest.main()
