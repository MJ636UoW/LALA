import unittest
from lala.rag.models import Document, Chunk, QueryCategory

class TestRAGModels(unittest.TestCase):
    def test_document_and_chunk_initialization(self):
        doc = Document(
            document_id="doc1",
            source_path="D:\\test.txt",
            sha256="abc123hash",
            file_size=100,
            title="Test Doc",
            content="Hello world content"
        )
        self.assertEqual(doc.title, "Test Doc")

        chunk = Chunk(
            chunk_id="chunk1",
            document_id="doc1",
            chunk_index=0,
            text="Hello world",
            token_estimate=2
        )
        self.assertEqual(chunk.chunk_index, 0)
        self.assertEqual(QueryCategory.MITRE.value, "MITRE")

if __name__ == "__main__":
    unittest.main()
