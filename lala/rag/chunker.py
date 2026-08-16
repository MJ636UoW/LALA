import uuid
from typing import List
from lala.rag.models import Document, Chunk

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

class DocumentChunker:
    """
    Deterministic Document Chunker for LALA Phase 9.
    Splits text into overlapping chunks (CHUNK_SIZE=800, CHUNK_OVERLAP=120).
    """
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: Document) -> List[Chunk]:
        text = doc.content or ""
        if not text.strip():
            return []

        chunks: List[Chunk] = []
        step = max(1, self.chunk_size - self.chunk_overlap)
        
        start = 0
        chunk_idx = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_text = text[start:end]
            
            chunk_id = f"{doc.document_id}_c{chunk_idx}"
            token_estimate = max(1, len(chunk_text) // 4)

            chunks.append(Chunk(
                chunk_id=chunk_id,
                document_id=doc.document_id,
                chunk_index=chunk_idx,
                text=chunk_text,
                token_estimate=token_estimate,
                metadata={"document_title": doc.title, "source_path": doc.source_path}
            ))

            chunk_idx += 1
            start += step
            if end >= text_len:
                break

        return chunks
