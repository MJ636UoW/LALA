import unittest
from lala.rag.manager import LocalRAGManager

class TestAutomationRAG(unittest.TestCase):
    def test_automation_rag_integration(self):
        rag = LocalRAGManager()
        status = rag.get_status()
        self.assertTrue(status["offline_mode"])

if __name__ == "__main__":
    unittest.main()
