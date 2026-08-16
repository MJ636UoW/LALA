import unittest
from lala.remediation.policy import RemediationPolicyEngine, RemediationActionType
from lala.remediation.recommendation import RemediationRecommendationEngine
from lala.investigation.models import SeverityLevel

class TestRemediationPolicy(unittest.TestCase):
    def test_remediation_requires_user_confirmation(self):
        engine = RemediationPolicyEngine()
        res_unconfirmed = engine.evaluate_remediation(RemediationActionType.BLOCK_IP, "1.1.1.1", is_user_confirmed=False)
        self.assertFalse(res_unconfirmed.allowed)
        self.assertTrue(res_unconfirmed.requires_user_confirmation)

        res_confirmed = engine.evaluate_remediation(RemediationActionType.BLOCK_IP, "1.1.1.1", is_user_confirmed=True)
        self.assertTrue(res_confirmed.allowed)

    def test_generate_defensive_recommendations(self):
        rec_gen = RemediationRecommendationEngine()
        recs = rec_gen.generate_recommendations("IP", "8.8.8.8", SeverityLevel.CRITICAL)
        self.assertGreater(len(recs), 0)
        self.assertIn("[RECOMMENDATION]", recs[0])

if __name__ == "__main__":
    unittest.main()
