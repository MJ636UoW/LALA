from typing import Dict, Optional, List
from pydantic import BaseModel, Field

class APIServiceMetadata(BaseModel):
    """
    Schema for API provider capability registry.
    Phase 1 defines models without performing network scanning or storing API keys.
    """
    service_id: str
    name: str
    description: str
    requires_auth: bool = True
    is_discovered: bool = False
    supported_models: List[str] = Field(default_factory=list)

class APIRegistry:
    """
    In-memory catalog of available API endpoints and provider schemas.
    """
    def __init__(self):
        self._services: Dict[str, APIServiceMetadata] = {}

    def register_service(self, service: APIServiceMetadata):
        self._services[service.service_id] = service

    def get_service(self, service_id: str) -> Optional[APIServiceMetadata]:
        return self._services.get(service_id)

    def list_services(self) -> List[APIServiceMetadata]:
        return list(self._services.values())
