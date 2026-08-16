import unittest
from lala.intelligence.models import IOC, IOCType
from lala.intelligence.correlation import IOCCorrelationEngine

class TestIOCCorrelation(unittest.TestCase):
    def test_ioc_grouping_and_correlation(self):
        engine = IOCCorrelationEngine()
        iocs = [
            IOC(ioc_type=IOCType.HASH, value="abc123hash"),
            IOC(ioc_type=IOCType.IP, value="1.1.1.1"),
            IOC(ioc_type=IOCType.DOMAIN, value="malicious-site.com")
        ]
        res = engine.correlate_iocs(iocs)
        self.assertEqual(res["total_indicators"], 3)
        self.assertEqual(len(res["grouped_indicators"]["hashes"]), 1)
        self.assertEqual(len(res["grouped_indicators"]["ips"]), 1)

if __name__ == "__main__":
    unittest.main()
