import uuid
from typing import Dict, Any
from lala.investigation.models import EvidenceItem

class EvidenceRecorder:
    """Helper for formatting and creating evidence items for cases."""
    def create_evidence(self, ioc_value: str, evidence_type: str, source: str, details: Dict[str, Any]) -> EvidenceItem:
        # Ensure API keys or credentials are stripped
        sanitized_details = {k: v for k, v in details.items() if "key" not in k.lower() and "token" not in k.lower()}
        return EvidenceItem(
            id=str(uuid.uuid4())[:8],
            ioc_value=ioc_value,
            evidence_type=evidence_type,
            source=source,
            details=sanitized_details
        )
