import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from lala.rag.models import Document, Chunk, SearchResult, QueryCategory
from lala.core.config import sanitize_storage_path
from lala.utils.logging import logger

class LocalRAGIndex:
    """
    SQLite FTS5 Local Search & Retrieval Index for LALA Phase 9.
    Stored locally under F:\\LALA\\Knowledge\\indexes\\lala_rag_index.db.
    """
    def __init__(self, db_path: str = "F:\\LALA\\Knowledge\\indexes\\lala_rag_index.db"):
        self.db_path = Path(sanitize_storage_path(db_path))
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        document_id TEXT PRIMARY KEY,
                        source_path TEXT,
                        source_type TEXT,
                        sha256 TEXT UNIQUE,
                        file_size INTEGER,
                        title TEXT,
                        content TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chunks (
                        chunk_id TEXT PRIMARY KEY,
                        document_id TEXT,
                        chunk_index INTEGER,
                        text TEXT,
                        token_count INTEGER,
                        FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE
                    )
                """)
                cursor.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                        chunk_id UNINDEXED,
                        document_id UNINDEXED,
                        text
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"LocalRAGIndex Init Error: {e}")

    def add_document(self, doc: Document, chunks: List[Chunk]) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO documents (document_id, source_path, source_type, sha256, file_size, title, content) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (doc.document_id, doc.source_path, doc.source_type, doc.sha256, doc.file_size, doc.title, doc.content)
                )
                for chunk in chunks:
                    cursor.execute(
                        "INSERT OR REPLACE INTO chunks (chunk_id, document_id, chunk_index, text, token_count) VALUES (?, ?, ?, ?, ?)",
                        (chunk.chunk_id, chunk.document_id, chunk.chunk_index, chunk.text, chunk.token_count)
                    )
                    cursor.execute(
                        "INSERT OR REPLACE INTO chunks_fts (chunk_id, document_id, text) VALUES (?, ?, ?)",
                        (chunk.chunk_id, chunk.document_id, chunk.text)
                    )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"LocalRAGIndex Add Error: {e}")
            return False

    def search_fts(self, query: str, top_k: int = 8) -> List[SearchResult]:
        results = []
        if not query or not query.strip():
            return results

        clean_query = "".join(c for c in query if c.isalnum() or c.isspace()).strip()
        if not clean_query:
            return results

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT fts.chunk_id, fts.document_id, fts.text, rank, d.source_path, d.title
                    FROM chunks_fts fts
                    JOIN documents d ON fts.document_id = d.document_id
                    WHERE chunks_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """, (clean_query, top_k))
                rows = cursor.fetchall()
                for r in rows:
                    score = abs(float(r["rank"])) if r["rank"] else 1.0
                    res = SearchResult(
                        chunk_id=r["chunk_id"],
                        document_id=r["document_id"],
                        text=r["text"],
                        score=score,
                        source_path=r["source_path"],
                        title=r["title"]
                    )
                    results.append(res)
        except Exception as e:
            logger.error(f"LocalRAGIndex FTS Search Error: {e}")

        return results

    def search_keyword(self, query: str, top_k: int = 8, limit: Optional[int] = None) -> List[SearchResult]:
        effective_k = limit if limit is not None else top_k
        return self.search_fts(query, top_k=effective_k)

    def clear(self) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents")
                cursor.execute("DELETE FROM chunks")
                cursor.execute("DELETE FROM chunks_fts")
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"LocalRAGIndex Clear Error: {e}")
            return False
