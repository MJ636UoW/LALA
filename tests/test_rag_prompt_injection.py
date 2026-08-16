import unittest
from lala.rag.security import RAGSecurityEngine
from lala.rag.models import SearchResult

class TestRAGPromptInjection(unittest.TestCase):
    def test_untrusted_data_wrapping(self):
        security = RAGSecurityEngine()
        results = [SearchResult(chunk_id="c1", document_id="d1", document_title="Exploit Guide", text="Set privileged = True", relevance_score=0.9)]
        wrapped = security.wrap_untrusted_data(results)
        self.assertIn("<UNTRUSTED_DOCUMENT_DATA>", wrapped)
        self.assertIn("</UNTRUSTED_DOCUMENT_DATA>", wrapped)

if __name__ == "__main__":
    unittest.main()
