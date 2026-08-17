import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from lala.rag.models import Document, Chunk, SearchResult
from lala.core.config import sanitize_storage_path
from lala.utils.logging import logger

class LocalRAGIndex:
    """
    Local SQLite FTS5 Index for LALA Phase 9.
    Provides fast, deterministic local keyword and lexical search over indexed document chunks.
    Stored locally under F:\\LALA\\Knowledge\\indexes\\lala_rag_index.db.
    """
    def __init__(self, db_path: str = "F:\\LALA\\Knowledge\\indexes\\lala_rag_index.db"):
        self.db_path = sanitize_storage_path(db_path)
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
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    sha256 TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    token_count INTEGER NOT NULL,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents (document_id)
                )
            """)
            # Create FTS5 virtual table for keyword search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    document_id UNINDEXED,
                    text
                )
            """)
            conn.commit()

    def add_document(self, doc: Document, chunks: List[Chunk]) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO documents VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (doc.document_id, doc.title, doc.category.value, doc.filepath, doc.created_at, doc.chunk_count, doc.sha256)
                )
                for chunk in chunks:
                    cursor.execute(
                        "INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (chunk.chunk_id, chunk.document_id, chunk.chunk_index, chunk.text, chunk.token_count, chunk.start_char, chunk.end_char)
                    )
                    cursor.execute(
                        "INSERT OR REPLACE INTO chunks_fts (chunk_id, document_id, text) VALUES (?, ?, ?)",
                        (chunk.chunk_id, chunk.document_id, chunk.text)
                    )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"LocalRAGIndex Add Document Error: {e}")
            return False

    def search_fts(self, query: str, top_k: int = 8) -> List[SearchResult]:
        cleaned_query = "".join(c if c.isalnum() or c.isspace() else " " for c in query).strip()
        if not cleaned_query:
            return []

        results = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Query FTS5 matching chunks
                cursor.execute("""
                    SELECT f.chunk_id, f.document_id, f.text, d.title, d.category, d.filepath
                    FROM chunks_fts f
                    JOIN documents d ON f.document_id = d.document_id
                    WHERE chunks_fts MATCH ?
                    LIMIT ?
                """, (cleaned_query, top_k))
                rows = cursor.fetchall()
                for rank, row in enumerate(rows, start=1):
                    res = SearchResult(
                        chunk_id=row["chunk_id"],
                        document_id=row["document_id"],
                        document_title=row["title"],
                        category=row["category"],
                        filepath=row["filepath"],
                        text=row["text"],
                        relevance_score=round(1.0 - (rank * 0.05), 2)
                    )
                    results.append(res)
        except Exception as e:
            logger.error(f"LocalRAGIndex FTS Search Error: {e}")

        return results

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
