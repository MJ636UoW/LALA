import unittest
from lala.rag.citations import CitationEngine
from lala.rag.models import SearchResult

class TestRAGCitations(unittest.TestCase):
    def test_citation_generation(self):
        engine = CitationEngine()
        results = [SearchResult(chunk_id="c1", document_id="d1", document_title="ATT&CK Guide", text="PowerShell execution technique.", relevance_score=0.95)]
        citations = engine.generate_citations(results)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0].document_title, "ATT&CK Guide")
        self.assertEqual(citations[0].index, 1)

if __name__ == "__main__":
    unittest.main()
