import sqlite3
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

SCHEMA_VERSION = "v1"

class IntelligenceCache:
    """
    SQLite TTL-based Cache for LALA Phase 6 Online Intelligence.
    Prevents unnecessary API requests by caching normalized intelligence data under F:\\LALA\\Memory\\lala_intel_cache.db.
    Cache keys include schema version, provider, and normalized query for cache poisoning protection.
    Never stores API keys or secrets.
    """
    def __init__(self, db_path: str = "F:\\LALA\\Memory\\lala_intel_cache.db", default_ttl_seconds: int = 86400):
        self.db_path = Path(db_path)
        self.default_ttl_seconds = default_ttl_seconds
        self._init_db()

    def _init_db(self):
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self.db_path))
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS intel_cache (
                        cache_key TEXT PRIMARY KEY,
                        provider TEXT,
                        query_type TEXT,
                        schema_version TEXT,
                        result_json TEXT,
                        created_at INTEGER,
                        expires_at INTEGER
                    )
                """)
            conn.close()
        except Exception:
            pass

    def get(self, provider: str, query: str) -> Optional[Dict[str, Any]]:
        cache_key = f"{SCHEMA_VERSION}:{provider.lower()}:{query.lower()}"
        now = int(time.time())
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT result_json FROM intel_cache WHERE cache_key = ? AND expires_at > ?",
                (cache_key, now)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row[0])
        except Exception:
            pass
        return None

    def set(self, provider: str, query: str, query_type: str, result_data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> bool:
        cache_key = f"{SCHEMA_VERSION}:{provider.lower()}:{query.lower()}"
        now = int(time.time())
        ttl = ttl_seconds or self.default_ttl_seconds
        expires_at = now + ttl
        try:
            conn = sqlite3.connect(str(self.db_path))
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO intel_cache (cache_key, provider, query_type, schema_version, result_json, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (cache_key, provider, query_type, SCHEMA_VERSION, json.dumps(result_data), now, expires_at))
            conn.close()
            return True
        except Exception:
            return False

    def clear(self) -> bool:
        try:
            conn = sqlite3.connect(str(self.db_path))
            with conn:
                conn.execute("DELETE FROM intel_cache")
            conn.close()
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        try:
            now = int(time.time())
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM intel_cache WHERE expires_at > ?", (now,))
            valid_count = cursor.fetchone()[0]
            conn.close()
            return {"db_path": str(self.db_path), "active_cache_entries": valid_count}
        except Exception:
            return {"db_path": str(self.db_path), "active_cache_entries": 0}
