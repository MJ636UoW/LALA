import unittest
from lala.intelligence.mitre import MitreAttackEngine

class TestMitreIntegrationPhase7(unittest.TestCase):
    def test_mitre_technique_lookup(self):
        engine = MitreAttackEngine()
        tech = engine.get_technique("T1059")
        self.assertIsNotNone(tech)
        self.assertEqual(tech.name, "Command and Scripting Interpreter")

if __name__ == "__main__":
    unittest.main()
