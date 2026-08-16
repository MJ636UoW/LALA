from typing import List
from lala.rag.models import SearchResult

class LocalReranker:
    """
    Local Candidate Reranker for LALA Phase 9.
    Reranks candidate search results locally based on term frequency and document title relevance.
    """
    def rerank(self, query: str, candidates: List[SearchResult]) -> List[SearchResult]:
        if not candidates:
            return []

        query_terms = set(query.lower().split())

        def score_candidate(res: SearchResult) -> float:
            text_lower = res.text.lower()
            title_lower = res.document_title.lower()
            term_matches = sum(1 for t in query_terms if t in text_lower or t in title_lower)
            boost = 0.2 if any(t in title_lower for t in query_terms) else 0.0
            return res.relevance_score + (term_matches * 0.1) + boost

        sorted_candidates = sorted(candidates, key=score_candidate, reverse=True)
        return sorted_candidates
