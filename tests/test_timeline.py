import unittest
from lala.investigation.timeline import TimelineGenerator

class TestTimeline(unittest.TestCase):
    def test_timeline_logging(self):
        gen = TimelineGenerator()
        entry = gen.log_event("IOC 1.1.1.1 queried")
        self.assertEqual(entry.event_description, "IOC 1.1.1.1 queried")
        self.assertIsNotNone(entry.timestamp)

if __name__ == "__main__":
    unittest.main()
