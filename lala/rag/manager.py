import os
from typing import List, Dict, Any, Optional
from lala.rag.models import Document, SearchResult, RAGConfig
from lala.rag.document_loader import DocumentLoader
from lala.rag.document_parser import DocumentParser
from lala.rag.chunker import DocumentChunker
from lala.rag.index import LocalRAGIndex
from lala.rag.retriever import HybridRetriever
from lala.rag.reranker import LocalReranker
from lala.rag.context_builder import ContextBuilder
from lala.rag.privacy import LocalRAGPrivacyEngine
from lala.rag.metadata import MetadataStore
from lala.utils.logging import logger

class LocalRAGManager:
    """
    Central Manager for LALA Phase 9 Offline Cybersecurity Knowledge Base & RAG.
    Coordinates document ingestion, chunking, SQLite FTS5 indexing, hybrid retrieval, datasets, and context building.
    100% Offline, Zero Cloud Fallback, Prompt-Injection Hardened.
    """
    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        self.loader = DocumentLoader(knowledge_root=self.config.knowledge_root)
        self.parser = DocumentParser(loader=self.loader)
        self.chunker = DocumentChunker(chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap)
        self.index = LocalRAGIndex(db_path=os.path.join(self.config.knowledge_root, "indexes", "lala_rag_index.db"))
        self.retriever = HybridRetriever(index=self.index)
        self.reranker = LocalReranker()
        self.context_builder = ContextBuilder()
        self.privacy = LocalRAGPrivacyEngine()
        self.metadata = MetadataStore(meta_path=os.path.join(self.config.knowledge_root, "metadata", "metadata_store.json"))

    def add_document(self, file_path: str) -> Optional[Document]:
        self.privacy.assert_offline_policy()
        try:
            doc = self.parser.parse_file(file_path)
            chunks = self.chunker.chunk_document(doc)
            success = self.index.add_document_and_chunks(doc, chunks)
            if success:
                self.metadata.add_document_metadata(doc.document_id, {
                    "document_id": doc.document_id,
                    "title": doc.title,
                    "source_path": doc.source_path,
                    "sha256": doc.sha256,
                    "file_size": doc.file_size,
                    "chunk_count": len(chunks),
                    "imported_at": doc.imported_at
                })
                logger.info(f"LocalRAGManager: Ingested document '{doc.title}' ({len(chunks)} chunks).")
                return doc
        except Exception as e:
            logger.error(f"LocalRAGManager Add Document Error for '{file_path}': {e}")
        return None

    def search(self, query: str, top_k: int = 8) -> List[SearchResult]:
        self.privacy.assert_offline_policy()
        candidates = self.retriever.retrieve(query, top_k=top_k)
        reranked = self.reranker.rerank(query, candidates)
        return reranked[:top_k]

    def build_prompt_context(self, base_prompt: str, user_query: str, top_k: int = 8) -> str:
        results = self.search(user_query, top_k=top_k)
        return self.context_builder.build_rag_prompt(base_prompt, user_query, results)

    def list_knowledge_documents(self) -> List[Dict[str, Any]]:
        return self.index.list_documents()

    def remove_document(self, document_id: str) -> bool:
        self.metadata.remove_metadata(document_id)
        return self.index.delete_document(document_id)

    def rebuild_index(self):
        docs = self.list_knowledge_documents()
        self.index.clear()
        for d in docs:
            path = d.get("source_path")
            if path and os.path.exists(path):
                self.add_document(path)

    def clear_knowledge_base(self):
        self.index.clear()

    def get_status(self) -> Dict[str, Any]:
        docs = self.list_knowledge_documents()
        return {
            "status": "ONLINE (100% LOCAL OFFLINE)",
            "knowledge_root": self.config.knowledge_root,
            "cloud_rag": False,
            "offline_mode": True,
            "indexed_documents": len(docs),
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap,
            "default_top_k": self.config.top_k
        }
