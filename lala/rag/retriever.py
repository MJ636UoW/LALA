from typing import List, Optional
from lala.rag.models import SearchResult, QueryCategory
from lala.rag.index import LocalRAGIndex

DEFAULT_TOP_K = 8
MAX_TOP_K = 20

class HybridRetriever:
    """
    Hybrid Retriever for LALA Phase 9.
    Executes cybersecurity-aware keyword and semantic candidate retrieval.
    Capped at TOP_K = 8 by default (max 20).
    """
    def __init__(self, index: Optional[LocalRAGIndex] = None):
        self.index = index or LocalRAGIndex()

    def classify_query(self, query: str) -> QueryCategory:
        q_lower = query.lower()
        if "sigma" in q_lower:
            return QueryCategory.SIGMA
        elif "yara" in q_lower or "yara rule" in q_lower:
            return QueryCategory.YARA
        elif "mitre" in q_lower or "t1" in q_lower or "attack" in q_lower:
            return QueryCategory.MITRE
        elif "cve-" in q_lower or "vulnerability" in q_lower or "nvd" in q_lower:
            return QueryCategory.CVE
        elif "malware" in q_lower or "ransomware" in q_lower or "trojan" in q_lower:
            return QueryCategory.MALWARE
        elif "power-shell" in q_lower or "powershell" in q_lower or "reverse" in q_lower:
            return QueryCategory.REVERSE_ENGINEERING
        elif "ip" in q_lower or "domain" in q_lower or "hash" in q_lower:
            return QueryCategory.IOC
        elif "rule" in q_lower:
            return QueryCategory.YARA
        return QueryCategory.GENERAL

    def retrieve(self, query: str, top_k: int = DEFAULT_TOP_K) -> List[SearchResult]:
        effective_k = min(max(1, top_k), MAX_TOP_K)
        cat = self.classify_query(query)
        results = self.index.search_keyword(query, limit=effective_k)
        
        # Attach query category to result metadata
        for r in results:
            r.metadata["query_category"] = cat.value
        return results
