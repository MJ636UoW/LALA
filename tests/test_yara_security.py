import unittest
from lala.detection.yara_validator import YaraValidator

class TestYaraSecurity(unittest.TestCase):
    def test_reject_executable_keyword_in_yara_rule(self):
        val = YaraValidator()
        rule_text = """rule Bad_Rule { meta: desc = "powershell format C:" condition: true }"""
        is_valid, msg = val.validate_rule_text(rule_text)
        self.assertFalse(is_valid)
        self.assertIn("forbidden executable keyword", msg)

    def test_validate_clean_yara_rule(self):
        val = YaraValidator()
        rule_text = """rule Good_Rule { strings: $s1 = "malicious" condition: $s1 }"""
        is_valid, msg = val.validate_rule_text(rule_text)
        self.assertTrue(is_valid)

if __name__ == "__main__":
    unittest.main()
