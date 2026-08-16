import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from lala.rag.models import Document, Chunk, SearchResult
from lala.utils.logging import logger

class LocalRAGIndex:
    """
    Local SQLite FTS5 Index for LALA Phase 9.
    Provides fast, deterministic local keyword and lexical search over indexed document chunks.
    Stored locally under F:\\LALA\\Knowledge\\indexes\\lala_rag_index.db.
    """
    def __init__(self, db_path: str = "F:\\LALA\\Knowledge\\indexes\\lala_rag_index.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
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
                    metadata_json TEXT,
                    imported_at TEXT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT,
                    chunk_index INTEGER,
                    text TEXT,
                    token_estimate INTEGER,
                    metadata_json TEXT,
                    FOREIGN KEY(document_id) REFERENCES documents(document_id)
                );
            """)
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    document_id UNINDEXED,
                    title,
                    text
                );
            """)
            conn.commit()

    def add_document_and_chunks(self, doc: Document, chunks: List[Chunk]) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO documents 
                    (document_id, source_path, source_type, sha256, file_size, title, metadata_json, imported_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (doc.document_id, doc.source_path, doc.source_type, doc.sha256, doc.file_size, doc.title, json.dumps(doc.metadata), doc.imported_at))

                for c in chunks:
                    cursor.execute("""
                        INSERT OR REPLACE INTO chunks
                        (chunk_id, document_id, chunk_index, text, token_estimate, metadata_json)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (c.chunk_id, c.document_id, c.chunk_index, c.text, c.token_estimate, json.dumps(c.metadata)))

                    cursor.execute("""
                        INSERT OR REPLACE INTO chunks_fts (chunk_id, document_id, title, text)
                        VALUES (?, ?, ?, ?)
                    """, (c.chunk_id, c.document_id, doc.title, c.text))

                conn.commit()
                return True
            except Exception as e:
                logger.error(f"LocalRAGIndex Insert Error: {e}")
                return False

    def search_keyword(self, query: str, limit: int = 8) -> List[SearchResult]:
        if not query or not query.strip():
            return []

        cleaned_query = "".join([c if c.isalnum() or c.isspace() else " " for c in query]).strip()
        if not cleaned_query:
            return []

        fts_query = " OR ".join(cleaned_query.split())
        results: List[SearchResult] = []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT f.chunk_id, f.document_id, f.title, c.text, c.metadata_json, rank
                    FROM chunks_fts f
                    JOIN chunks c ON f.chunk_id = c.chunk_id
                    WHERE chunks_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT ?
                """, (fts_query, limit))

                rows = cursor.fetchall()
                for r in rows:
                    score = abs(float(r["rank"])) if r["rank"] else 1.0
                    normalized_score = min(1.0, max(0.1, 1.0 / (1.0 + score)))
                    meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
                    results.append(SearchResult(
                        chunk_id=r["chunk_id"],
                        document_id=r["document_id"],
                        document_title=r["title"],
                        text=r["text"],
                        relevance_score=round(normalized_score, 4),
                        metadata=meta
                    ))
            except Exception as e:
                logger.error(f"LocalRAGIndex Search Error: {e}")

        return results

    def list_documents(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT document_id, title, source_path, file_size, imported_at FROM documents")
            return [dict(r) for r in cursor.fetchall()]

    def delete_document(self, document_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks_fts WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
            conn.commit()
            return True

    def clear(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks_fts")
            cursor.execute("DELETE FROM chunks")
            cursor.execute("DELETE FROM documents")
            conn.commit()
