import os
import time
from typing import Dict, Any, List, Optional
from lala.utils.logging import logger

class MongoMemoryStore:
    """
    MongoDB Telemetry & Knowledge Persistence Adapter for LALA.
    Stores malware analysis reports, ProcMon process trees, Wireshark PCAPs, and session telemetry.
    Supports local MongoDB ('mongodb://localhost:27017') and remote MongoDB Atlas ('MONGO_URI').
    Fails safe if MongoDB server is offline.
    """
    def __init__(self, uri: Optional[str] = None, db_name: str = "lala_cybersecurity"):
        self.uri = uri or os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self.client = None
        self.db = None
        self.is_connected = False
        self._connect()

    def _connect(self):
        try:
            import pymongo
            self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            # Ping to verify connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.is_connected = True
            logger.info(f"MongoMemoryStore Connected to MongoDB at '{self.uri[:30]}...'")
        except Exception as e:
            self.is_connected = False
            logger.info(f"MongoMemoryStore: MongoDB offline or unconfigured ({e}). Falling back to local storage.")

    def save_malware_report(self, report_dict: Dict[str, Any]) -> bool:
        if not self.is_connected or self.db is None:
            return False
        try:
            self.db.malware_reports.insert_one(report_dict)
            return True
        except Exception as e:
            logger.error(f"MongoMemoryStore Save Report Error: {e}")
            return False

    def save_telemetry_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        if not self.is_connected or self.db is None:
            return False
        try:
            doc = {
                "event_type": event_type,
                "data": data,
                "timestamp": time.time()
            }
            self.db.telemetry_logs.insert_one(doc)
            return True
        except Exception as e:
            logger.error(f"MongoMemoryStore Save Telemetry Error: {e}")
            return False

    def get_recent_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.is_connected or self.db is None:
            return []
        try:
            cursor = self.db.malware_reports.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"MongoMemoryStore Get Reports Error: {e}")
            return []
