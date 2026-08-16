import json
import yaml
import uuid
import os
from typing import Dict, Any
from lala.rag.models import Document
from lala.rag.document_loader import DocumentLoader
from lala.utils.logging import logger

class DocumentParser:
    """
    Safe Document Parser for LALA Phase 9.
    Extracts plain text content from TXT, Markdown, JSON, YAML, CSV, Python, YARA, Sigma, and PDF files.
    Never executes embedded code or scripts.
    """
    def __init__(self, loader: Optional[DocumentLoader] = None):
        self.loader = loader or DocumentLoader()

    def parse_file(self, file_path: str) -> Document:
        raw_bytes, sha256_hash, file_size = self.loader.load_raw_file(file_path)
        ext = os.path.splitext(file_path)[1].lower().strip(".")
        title = os.path.basename(file_path)

        content_text = ""
        metadata: Dict[str, Any] = {"extension": ext, "file_size": file_size}

        try:
            if ext in ["txt", "md", "markdown", "py", "yar", "yara"]:
                content_text = raw_bytes.decode("utf-8", errors="replace")
            elif ext in ["json"]:
                data = json.loads(raw_bytes.decode("utf-8", errors="replace"))
                content_text = json.dumps(data, indent=2)
                metadata["structured_type"] = "json"
            elif ext in ["yaml", "yml"]:
                data = yaml.safe_load(raw_bytes.decode("utf-8", errors="replace"))
                content_text = yaml.dump(data) if data else ""
                metadata["structured_type"] = "yaml"
            elif ext in ["csv"]:
                content_text = raw_bytes.decode("utf-8", errors="replace")
                metadata["structured_type"] = "csv"
            elif ext in ["pdf"]:
                # Text extraction fallback for PDFs without active script execution
                content_text = raw_bytes.decode("latin1", errors="ignore")
                metadata["structured_type"] = "pdf"
            else:
                content_text = raw_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            logger.error(f"DocumentParser Error parsing '{file_path}': {e}")
            content_text = raw_bytes.decode("latin1", errors="ignore")

        doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"doc:{sha256_hash}"))
        return Document(
            document_id=doc_id,
            source_path=file_path,
            source_type=ext or "txt",
            sha256=sha256_hash,
            file_size=file_size,
            title=title,
            content=content_text,
            metadata=metadata
        )
