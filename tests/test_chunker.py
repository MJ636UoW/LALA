import unittest
from lala.rag.models import Document
from lala.rag.chunker import DocumentChunker

class TestChunker(unittest.TestCase):
    def test_chunk_document_splitting(self):
        doc = Document(
            document_id="doc1",
            source_path="test.txt",
            sha256="hash1",
            file_size=2000,
            title="Title",
            content="A" * 1600
        )
        chunker = DocumentChunker(chunk_size=800, chunk_overlap=120)
        chunks = chunker.chunk_document(doc)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0].chunk_index, 0)

if __name__ == "__main__":
    unittest.main()
