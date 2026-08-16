import os
import tempfile
import unittest
from lala.intelligence.cache import IntelligenceCache

class TestIntelligenceCache(unittest.TestCase):
    def test_cache_set_and_get(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_p = os.path.join(tmpdir, "test_cache.db")
            cache = IntelligenceCache(db_path=db_p, default_ttl_seconds=3600)
            data = {"verdict": "MALICIOUS", "positives": 45}
            self.assertTrue(cache.set("virustotal", "1.1.1.1", "IP", data))
            
            res = cache.get("virustotal", "1.1.1.1")
            self.assertIsNotNone(res)
            self.assertEqual(res["verdict"], "MALICIOUS")

if __name__ == "__main__":
    unittest.main()
