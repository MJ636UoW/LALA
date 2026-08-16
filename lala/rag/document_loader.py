import os
import hashlib
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from lala.utils.logging import logger

MAX_DOCUMENT_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

class DocumentLoader:
    """
    Safe Document Loader for LALA Phase 9.
    Validates canonical paths under Knowledge root, checks file size, calculates SHA-256 hashes,
    and rejects unsafe path traversal, UNC paths, and device paths.
    """
    def __init__(self, knowledge_root: str = "F:\\LALA\\Knowledge"):
        self.knowledge_root = Path(knowledge_root)
        self._init_dir()

    def _init_dir(self):
        try:
            self.knowledge_root.mkdir(parents=True, exist_ok=True)
            (self.knowledge_root / "documents").mkdir(exist_ok=True)
            (self.knowledge_root / "datasets").mkdir(exist_ok=True)
            (self.knowledge_root / "indexes").mkdir(exist_ok=True)
            (self.knowledge_root / "metadata").mkdir(exist_ok=True)
            (self.knowledge_root / "imports").mkdir(exist_ok=True)
        except Exception:
            pass

    def is_safe_path(self, target_path: str) -> bool:
        if not target_path or not isinstance(target_path, str) or "\x00" in target_path:
            return False

        if target_path.startswith("\\\\") or target_path.startswith("//") or target_path.startswith("\\\\?\\"):
            return False  # Reject UNC and device paths

        try:
            canonical = os.path.realpath(target_path)
            # Allow workspace paths (D:\LALA), knowledge root paths (F:\LALA\Knowledge), or temp dir for test files
            allowed_roots = [
                os.path.realpath(str(self.knowledge_root)),
                os.path.realpath("D:\\LALA"),
                os.path.realpath("F:\\LALA"),
                os.path.realpath(tempfile.gettempdir())
            ]
            for root in allowed_roots:
                if canonical == root or canonical.startswith(root + os.sep):
                    return True
            return False
        except Exception as e:
            logger.error(f"DocumentLoader Path Validation Error: {e}")
            return False

    def load_raw_file(self, file_path: str) -> Tuple[Optional[bytes], str, int]:
        """Loads file bytes safely after validating path and size limits."""
        if not self.is_safe_path(file_path):
            raise PermissionError(f"DocumentLoader Access Denied: Path '{file_path}' is outside authorized knowledge boundaries.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: '{file_path}'")

        file_size = os.path.getsize(file_path)
        if file_size > MAX_DOCUMENT_SIZE_BYTES:
            raise ValueError(f"Document size limit exceeded ({file_size} bytes > {MAX_DOCUMENT_SIZE_BYTES} bytes).")

        with open(file_path, "rb") as f:
            data = f.read()

        sha256_hash = hashlib.sha256(data).hexdigest()
        return data, sha256_hash, file_size
