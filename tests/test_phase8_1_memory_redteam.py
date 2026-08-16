import unittest
from lala.memory.manager import MemoryManager
from lala.memory.models import MemoryCategory

class TestPhase81MemoryRedTeam(unittest.TestCase):
    """13. Memory Security Red-Team Tests."""

    def test_model_cannot_write_directly_to_sqlite(self):
        mgr = MemoryManager()
        self.assertIsNotNone(mgr)
        res = mgr.save_memory("Sensitive password", category=MemoryCategory.SENSITIVE)
        self.assertFalse(res) # Sensitive items are excluded from SQLite persistence by security policy

if __name__ == "__main__":
    unittest.main()
