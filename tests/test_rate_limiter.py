import unittest
from lala.intelligence.rate_limiter import ProviderRateLimiter

class TestRateLimiter(unittest.TestCase):
    def test_rate_limiting_throttle(self):
        limiter = ProviderRateLimiter(max_requests_per_minute=3)
        self.assertTrue(limiter.is_allowed("virustotal"))
        self.assertTrue(limiter.is_allowed("virustotal"))
        self.assertTrue(limiter.is_allowed("virustotal"))
        self.assertFalse(limiter.is_allowed("virustotal")) # 4th request throttled

if __name__ == "__main__":
    unittest.main()
