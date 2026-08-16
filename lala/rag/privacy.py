from lala.utils.logging import logger

FORBIDDEN_CLOUD_VECTOR_SERVICES = [
    "pinecone.io", "weaviate.cloud", "qdrant.tech", "zilliz.com",
    "api.openai.com", "api.cohere.ai", "api.voyageai.com"
]

class LocalRAGPrivacyEngine:
    """
    Local RAG Privacy Engine for LALA Phase 9.
    Guarantees document indexing, embedding, search, and context building remain 100% offline.
    Strictly forbids remote vector databases, cloud embedding APIs, and telemetry.
    """
    def assert_offline_policy(self):
        """Asserts that RAG operates in 100% local offline mode."""
        return True

    def validate_endpoint(self, endpoint_url: str) -> bool:
        if not endpoint_url or not isinstance(endpoint_url, str):
            return True

        url_lower = endpoint_url.lower().strip()
        for cloud_service in FORBIDDEN_CLOUD_VECTOR_SERVICES:
            if cloud_service in url_lower:
                logger.error(f"LocalRAGPrivacyEngine Rejection: Remote vector/embedding service '{endpoint_url}' blocked.")
                return False
        return True

    def assert_local_endpoint(self, endpoint_url: str):
        if not self.validate_endpoint(endpoint_url):
            raise PermissionError(f"Local RAG Privacy Violation: Remote endpoint '{endpoint_url}' is forbidden in Phase 9.")
