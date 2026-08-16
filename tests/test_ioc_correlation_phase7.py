import unittest
from lala.intelligence.models import IOC, IOCType
from lala.intelligence.correlation import IOCCorrelationEngine

class TestIOCCorrelationPhase7(unittest.TestCase):
    def test_correlation_grouping(self):
        engine = IOCCorrelationEngine()
        iocs = [
            IOC(ioc_type=IOCType.HASH, value="sha256hash"),
            IOC(ioc_type=IOCType.IP, value="8.8.8.8"),
            IOC(ioc_type=IOCType.DOMAIN, value="example.com")
        ]
        res = engine.correlate_iocs(iocs)
        self.assertEqual(res["total_indicators"], 3)
        self.assertIn("hashes", res["grouped_indicators"])

if __name__ == "__main__":
    unittest.main()
