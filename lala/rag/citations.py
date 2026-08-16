from typing import List
from lala.rag.models import SearchResult, Citation

class CitationEngine:
    """
    Citation Engine for LALA Phase 9.
    Generates application-level, verifiable citations from retrieved search results.
    Prevents hallucinated or fabricated citations.
    """
    def generate_citations(self, results: List[SearchResult]) -> List[Citation]:
        citations = []
        for idx, res in enumerate(results, start=1):
            excerpt = res.text[:120].strip().replace("\n", " ") + "..." if len(res.text) > 120 else res.text.strip()
            source_path = res.metadata.get("source_path", res.document_title)
            citations.append(Citation(
                index=idx,
                document_title=res.document_title,
                source_path=source_path,
                chunk_id=res.chunk_id,
                excerpt=excerpt
            ))
        return citations

    def format_citation_block(self, citations: List[Citation]) -> str:
        if not citations:
            return ""

        lines = ["[RETRIEVED KNOWLEDGE SOURCES]"]
        for c in citations:
            lines.append(f"[{c.index}] Document: '{c.document_title}' | Chunk: {c.chunk_id}\n    Path: {c.source_path}\n    Excerpt: \"{c.excerpt}\"")

        return "\n".join(lines)
