import unittest
from lala.intelligence.mitre import MitreAttackEngine

class TestMitreAttack(unittest.TestCase):
    def test_mitre_technique_lookup(self):
        engine = MitreAttackEngine()
        tech = engine.get_technique("T1059.001")
        self.assertIsNotNone(tech)
        self.assertEqual(tech.name, "PowerShell")
        self.assertEqual(tech.tactic, "Execution")

if __name__ == "__main__":
    unittest.main()
