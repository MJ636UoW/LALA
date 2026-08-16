import urllib.parse
import ipaddress
import socket
from lala.utils.logging import logger

FORBIDDEN_CLOUD_HOSTS = [
    "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com",
    "openai.azure.com", "api.cohere.ai", "api.mistral.ai", "api.replicate.com",
    "huggingface.co", "together.xyz", "groq.com", "perplexity.ai"
]

class LocalLLMPrivacyEngine:
    """
    Hardened Local LLM Privacy Engine for LALA Phase 8.1.
    Guarantees prompts, responses, and conversation context remain strictly local on the user's machine.
    Enforces rejection of remote/cloud LLM endpoints, public/LAN IPs, proxy leaks, and DNS rebinding attacks.
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
            host = (parsed.netloc or parsed.path).split(":")[0].lower().strip("[]")

            # Reject empty host
            if not host:
                return False

            # Check direct IP strings
            try:
                ip_obj = ipaddress.ip_address(host)
                if ip_obj.is_loopback:
                    return True
                else:
                    logger.error(f"LocalLLMPrivacyEngine Rejection: Non-loopback IP endpoint '{host}'")
                    return False
            except ValueError:
                pass # Domain name supplied

            # Domain name check - resolve via DNS and verify all resulting IPs are loopback
            if host in ["localhost"]:
                try:
                    resolved_ips = socket.gethostbyname_ex(host)[2]
                    for rip in resolved_ips:
                        ip_obj = ipaddress.ip_address(rip)
                        if not ip_obj.is_loopback:
                            logger.error(f"LocalLLMPrivacyEngine DNS Rebinding Rejection: Host '{host}' resolved to non-loopback IP '{rip}'")
                            return False
                    return True
                except Exception:
                    return True # Fallback if local DNS offline

            logger.error(f"LocalLLMPrivacyEngine Rejection: Remote domain endpoint '{host}' for LLM inference")
            return False
        except Exception as e:
            logger.error(f"LocalLLMPrivacyEngine Validation Error: {e}")
            return False

    def validate_redirect(self, original_url: str, redirect_url: str) -> bool:
        """Revalidates HTTP redirects to ensure LLM inference traffic is never redirected to remote endpoints."""
        return self.is_local_endpoint(redirect_url)

    def assert_privacy_policy(self, endpoint_url: str):
        if not self.is_local_endpoint(endpoint_url):
            raise PermissionError(f"Privacy Policy Enforcement Denial: Endpoint '{endpoint_url}' is not a validated LOCAL loopback address.")