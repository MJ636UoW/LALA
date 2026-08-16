import urllib.parse
import ipaddress
from lala.utils.logging import logger

ALLOWED_LOCAL_ENDPOINTS = [
    "http://127.0.0.1:11434",
    "http://localhost:11434",
    "http://127.0.0.1:8080",
    "http://localhost:8080"
]

FORBIDDEN_CLOUD_HOSTS = [
    "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com",
    "openai.azure.com", "api.cohere.ai", "api.mistral.ai", "api.replicate.com"
]

class LocalLLMPrivacyEngine:
    """
    Local LLM Privacy Engine for LALA Phase 8.
    Guarantees prompts, responses, and conversation context remain strictly local on the user's machine.
    Enforces rejection of remote/cloud LLM endpoints, public IPs, and cloud providers.
    """
    def is_local_endpoint(self, endpoint_url: str) -> bool:
        if not endpoint_url or not isinstance(endpoint_url, str):
            return False

        url_lower = endpoint_url.lower().strip()

        # Reject known cloud provider domain names
        for cloud_domain in FORBIDDEN_CLOUD_HOSTS:
            if cloud_domain in url_lower:
                logger.error(f"LocalLLMPrivacyEngine Rejection: Cloud provider endpoint detected '{endpoint_url}'")
                return False

        try:
            parsed = urllib.parse.urlparse(endpoint_url if "://" in endpoint_url else f"http://{endpoint_url}")
            host = (parsed.netloc or parsed.path).split(":")[0].lower()

            # Reject empty host or public domains
            if not host:
                return False

            if host in ["localhost", "127.0.0.1", "::1"]:
                return True

            # IP address check: Must be loopback (127.0.0.0/8 or ::1)
            try:
                ip_obj = ipaddress.ip_address(host)
                if ip_obj.is_loopback:
                    return True
                else:
                    logger.error(f"LocalLLMPrivacyEngine Rejection: Non-loopback IP endpoint '{host}'")
                    return False
            except ValueError:
                # Domain name supplied - only 'localhost' is acceptable for LLM_NETWORK
                logger.error(f"LocalLLMPrivacyEngine Rejection: Remote domain endpoint '{host}' for LLM inference")
                return False
        except Exception as e:
            logger.error(f"LocalLLMPrivacyEngine Validation Error: {e}")
            return False

    def assert_privacy_policy(self, endpoint_url: str):
        if not self.is_local_endpoint(endpoint_url):
            raise PermissionError(f"Privacy Policy Enforcement Denial: Endpoint '{endpoint_url}' is not a validated LOCAL loopback address.")
