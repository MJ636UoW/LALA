import unittest
import tempfile
import os
from lala.rag.document_parser import DocumentParser

class TestDocumentParser(unittest.TestCase):
    def test_parse_text_file(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
            f.write("Sample cybersecurity incident response guide.")
            path = f.name
        try:
            parser = DocumentParser()
            doc = parser.parse_file(path)
            self.assertEqual(doc.source_type, "txt")
            self.assertIn("incident response", doc.content)
        finally:
            os.remove(path)

if __name__ == "__main__":
    unittest.main()
