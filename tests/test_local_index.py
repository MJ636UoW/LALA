import unittest
import tempfile
import os
import gc
from lala.rag.models import Document, Chunk
from lala.rag.index import LocalRAGIndex

class TestLocalIndex(unittest.TestCase):
    def test_fts_search(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            index = LocalRAGIndex(db_path=db_path)
            doc = Document(document_id="d1", source_path="test.txt", sha256="h1", file_size=10, title="Ransomware Analysis", content="LockBit ransomware behavior.")
            c1 = Chunk(chunk_id="c1", document_id="d1", chunk_index=0, text="LockBit ransomware encrypts files using AES.", token_estimate=10)
            index.add_document_and_chunks(doc, [c1])

            results = index.search_keyword("LockBit")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].document_title, "Ransomware Analysis")
        finally:
            gc.collect()
            try:
                os.remove(db_path)
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
