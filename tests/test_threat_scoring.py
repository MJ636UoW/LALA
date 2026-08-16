import unittest
from lala.investigation.scoring import ThreatScoringEngine
from lala.investigation.models import SeverityLevel

class TestThreatScoring(unittest.TestCase):
    def test_calculate_score_clean(self):
        engine = ThreatScoringEngine()
        risk = engine.calculate_score(verdict="CLEAN")
        self.assertEqual(risk.score, 0.0)
        self.assertEqual(risk.level, SeverityLevel.UNKNOWN)

    def test_calculate_score_critical(self):
        engine = ThreatScoringEngine()
        risk = engine.calculate_score(
            verdict="MALICIOUS",
            provider_count=3,
            is_cisa_kev=True,
            yara_matches_count=2
        )
        self.assertGreaterEqual(risk.score, 75.0)
        self.assertEqual(risk.level, SeverityLevel.CRITICAL)

if __name__ == "__main__":
    unittest.main()
