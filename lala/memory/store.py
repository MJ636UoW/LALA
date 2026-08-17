import sqlite3
import threading
from typing import List, Optional, Dict, Any
from pathlib import Path
from lala.memory.models import PersistentMemoryItem, MemoryCategory, MemoryType
from lala.core.config import sanitize_storage_path
from lala.utils.logging import logger

class SQLiteMemoryStore:
    """
    SQLite + FTS5 Full-Text Persistent Memory Store for LALA.
    Target Database Path: F:\\LALA\\Memory\\lala_memory.db.
    """
    def __init__(self, db_path: str = "F:\\LALA\\Memory\\lala_memory.db"):
        self.db_path = Path(sanitize_storage_path(db_path))
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Persistent memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persistent_memory (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # FTS5 full-text search table
            try:
                cursor.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                        id,
                        content,
                        content='persistent_memory',
                        content_rowid='rowid'
                    )
                """)
            except Exception as e:
                logger.warning(f"FTS5 creation fallback: {e}")

            conn.commit()
            conn.close()

    def store(self, item: PersistentMemoryItem) -> bool:
        if item.category == MemoryCategory.SENSITIVE or item.category == MemoryCategory.TEMPORARY:
            logger.info(f"Skipping persistence for {item.category.value} memory item.")
            return False

        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT OR REPLACE INTO persistent_memory (id, content, category, memory_type) VALUES (?, ?, ?, ?)",
                    (item.id, item.content, item.category.value, item.memory_type.value)
                )
                try:
                    cursor.execute("INSERT OR REPLACE INTO memory_fts (id, content) VALUES (?, ?)", (item.id, item.content))
                except Exception:
                    pass

                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error storing memory item: {e}")
                return False
            finally:
                conn.close()

    def search(self, query: str, limit: int = 5) -> List[PersistentMemoryItem]:
        results = []
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                # FTS search or LIKE search fallback
                clean_query = query.replace("'", "''")
                cursor.execute(
                    "SELECT id, content, category, memory_type FROM persistent_memory WHERE content LIKE ? ORDER BY rowid DESC LIMIT ?",
                    (f"%{clean_query}%", limit)
                )
                rows = cursor.fetchall()
                for r in rows:
                    results.append(PersistentMemoryItem(
                        id=r["id"],
                        content=r["content"],
                        category=MemoryCategory(r["category"]),
                        memory_type=MemoryType(r["memory_type"])
                    ))
            except Exception as e:
                logger.error(f"Error searching memory: {e}")
            finally:
                conn.close()
        return results

    def delete(self, item_id: str) -> bool:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM persistent_memory WHERE id = ?", (item_id,))
                try:
                    cursor.execute("DELETE FROM memory_fts WHERE id = ?", (item_id,))
                except Exception:
                    pass
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error deleting memory item {item_id}: {e}")
                return False
            finally:
                conn.close()

    def clear(self) -> None:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM persistent_memory")
            try:
                cursor.execute("DELETE FROM memory_fts")
            except Exception:
                pass
            conn.commit()
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM persistent_memory")
            count = cursor.fetchone()["cnt"]
            conn.close()
            return {"db_path": str(self.db_path), "total_items": count}
