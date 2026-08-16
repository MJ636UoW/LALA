import unittest
from lala.rag.document_loader import DocumentLoader

class TestDocumentSecurity(unittest.TestCase):
    def test_unsafe_path_rejection(self):
        loader = DocumentLoader()
        self.assertFalse(loader.is_safe_path("..\\..\\Windows\\System32"))
        self.assertFalse(loader.is_safe_path("\\\\attacker-server\\share\\doc.txt"))
        self.assertFalse(loader.is_safe_path("C:\\Windows\\System32\\cmd.exe"))

if __name__ == "__main__":
    unittest.main()
