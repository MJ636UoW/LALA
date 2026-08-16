import unittest
from lala.intelligence.mitre import MitreAttackEngine

class TestRAGMitre(unittest.TestCase):
    def test_mitre_engine_integration(self):
        engine = MitreAttackEngine()
        tech = engine.get_technique("T1059.001")
        self.assertIsNotNone(tech)
        self.assertEqual(tech.name, "PowerShell")

if __name__ == "__main__":
    unittest.main()
