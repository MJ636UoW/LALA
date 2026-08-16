import json
import os
from typing import Dict, Any, List, Optional
from lala.utils.logging import logger

class MetadataStore:
    """
    Metadata Store for LALA Phase 9 Knowledge Base & Datasets.
    Manages metadata records stored in F:\\LALA\\Knowledge\\metadata\\metadata_store.json.
    """
    def __init__(self, meta_path: str = "F:\\LALA\\Knowledge\\metadata\\metadata_store.json"):
        self.meta_path = meta_path
        self._records: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self._records = json.load(f)
            except Exception as e:
                logger.error(f"MetadataStore Load Error: {e}")
                self._records = {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.meta_path), exist_ok=True)
            with open(self.meta_path, "w", encoding="utf-8") as f:
                json.dump(self._records, f, indent=2)
        except Exception as e:
            logger.error(f"MetadataStore Save Error: {e}")

    def add_document_metadata(self, doc_id: str, metadata: Dict[str, Any]):
        self._records[doc_id] = metadata
        self._save()

    def get_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self._records.get(doc_id)

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._records.values())

    def remove_metadata(self, doc_id: str) -> bool:
        if doc_id in self._records:
            del self._records[doc_id]
            self._save()
            return True
        return False
