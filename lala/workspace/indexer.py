import os
from typing import Dict, List
from lala.tools.filesystem import is_path_safe

class WorkspaceIndexer:
    """Workspace symbol and file path indexer for fast agent lookups."""
    def __init__(self, root_path: str = "D:\\LALA"):
        self.root_path = root_path
        self.index: Dict[str, str] = {}

    def build_index(self) -> int:
        if not is_path_safe(self.root_path):
            return 0
        canonical = os.path.realpath(self.root_path)
        self.index.clear()
        for root, dirs, files in os.walk(canonical):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules"]]
            for f in files:
                self.index[f.lower()] = os.path.join(root, f)
        return len(self.index)
