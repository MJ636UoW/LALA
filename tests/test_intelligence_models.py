import unittest
from lala.intelligence.models import IOC, IOCType, Verdict, ThreatIntelResult, HashReputation, Vulnerability

class TestIntelligenceModels(unittest.TestCase):
    def test_ioc_creation(self):
        ioc = IOC(ioc_type=IOCType.HASH, value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", source="VirusTotal")
        self.assertEqual(ioc.ioc_type, IOCType.HASH)
        self.assertEqual(ioc.source, "VirusTotal")

    def test_threat_intel_result_serialization(self):
        res = ThreatIntelResult(provider="AbuseIPDB", query="1.1.1.1", verdict=Verdict.CLEAN)
        data = res.model_dump(mode="json")
        self.assertEqual(data["provider"], "AbuseIPDB")
        self.assertEqual(data["verdict"], "CLEAN")

if __name__ == "__main__":
    unittest.main()
