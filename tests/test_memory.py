import os
import tempfile
import unittest
from lala.memory.manager import MemoryManager
from lala.memory.models import MemoryCategory, MemoryType

class TestLalaMemorySubsystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_memory.db")
        self.memory = MemoryManager(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_search_memory(self):
        """Verify saving facts and searching persistent memory."""
        saved = self.memory.save_memory("Source code is located at D:\\LALA", category=MemoryCategory.PERSISTENT)
        self.assertTrue(saved)

        results = self.memory.search_memory("Source code")
        self.assertGreater(len(results), 0)
        self.assertIn("D:\\LALA", results[0].content)

    def test_sensitive_memory_privacy(self):
        """Verify sensitive memories are not automatically persisted."""
        saved = self.memory.save_memory("Secret password123", category=MemoryCategory.SENSITIVE)
        self.assertFalse(saved)

        results = self.memory.search_memory("password123")
        self.assertEqual(len(results), 0)

    def test_forget_memory(self):
        """Verify memory deletion functionality."""
        self.memory.save_memory("Target project is LALA", category=MemoryCategory.PERSISTENT)
        count = self.memory.forget_memory("LALA")
        self.assertGreater(count, 0)
        
        results = self.memory.search_memory("LALA")
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()
