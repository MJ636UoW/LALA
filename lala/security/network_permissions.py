import urllib.parse
import ipaddress
import socket
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from lala.utils.logging import logger

class NetworkPermissionLevel(str, Enum):
    NETWORK_SAFE = "NETWORK_SAFE"
    NETWORK_READ_ONLY = "NETWORK_READ_ONLY"
    NETWORK_CONFIRMATION_REQUIRED = "NETWORK_CONFIRMATION_REQUIRED"
    NETWORK_BLOCKED = "NETWORK_BLOCKED"

class NetworkCheckResult(BaseModel):
    allowed: bool
    permission_level: NetworkPermissionLevel
    reason: str
    target_domain: str

# Allowed Cybersecurity Intelligence API domains
APPROVED_INTEL_DOMAINS = [
    "virustotal.com",
    "www.virustotal.com",
    "api.abuseipdb.com",
    "otx.alienvault.com",
    "urlhaus-api.abuse.ch",
    "mb-api.abuse.ch",
    "services.nvd.nist.gov",
    "www.cisa.gov",
    "cisa.gov",
    "raw.githubusercontent.com"
]

FORBIDDEN_SCHEMES = ["file:", "ftp:", "data:", "javascript:", "gopher:", "tftp:", "http:"]
FORBIDDEN_INTERNAL_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254", "0x7f000001", "2130706433", "0177.0.0.1"]

class NetworkSecurityEngine:
    """
    Hardened Network Security Engine for LALA Phase 6.1.
    Enforces domain allowlisting, SSRF prevention, IP validation, redirect revalidation, and network permissions.
    Preserves all Phase 4.5 & 5.1 SecurityEngine boundaries.
    """
    def __init__(self, online_enabled: bool = False):
        self.online_enabled = online_enabled

    def is_ssrf_target(self, target_url: str) -> bool:
        url_lower = target_url.lower().strip()

        # 1. Reject UNC, relative slashes, and non-HTTPS schemes
        if url_lower.startswith("\\\\") or url_lower.startswith("//"):
            return True
        for sch in FORBIDDEN_SCHEMES:
            if url_lower.startswith(sch):
                return True

        # 2. Hostname parsing & credential userinfo check
        try:
            parsed = urllib.parse.urlparse(target_url if "://" in target_url else f"https://{target_url}")
            if parsed.username or parsed.password:
                return True # Reject embedded userinfo (user:pass@host)
            
            host_port = parsed.netloc or parsed.path
            if host_port.startswith("["):
                host = host_port.split("]")[0].strip("[")
            else:
                host = host_port.split(":")[0].lower()
            port = parsed.port
            if port and port not in [80, 443]:
                return True # Reject non-standard ports
        except Exception:
            return True

        if not host or host in FORBIDDEN_INTERNAL_HOSTS or host.endswith(".local") or host.endswith(".internal"):
            return True

        # 3. IP address range validation (Private, Loopback, Link-Local, Metadata, Hex/Octal/Decimal)
        try:
            ip_str = host.strip("[]")
            # Handle int / hex / octal IP conversion
            if ip_str.isdigit():
                ip_str = str(ipaddress.IPv4Address(int(ip_str)))
            elif ip_str.startswith("0x"):
                ip_str = str(ipaddress.IPv4Address(int(ip_str, 16)))

            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
                return True
        except ValueError:
            pass # Host is a domain name

        return False

    def validate_redirect(self, original_url: str, redirect_url: str) -> bool:
        """Revalidates redirect destination independently against SSRF and allowlist."""
        res = self.evaluate_request(redirect_url)
        return res.allowed

    def extract_domain(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url if "://" in url else f"https://{url}")
            return (parsed.netloc or parsed.path).split(":")[0].lower()
        except Exception:
            return ""

    def evaluate_request(self, target_url: str, is_user_confirmed: bool = False) -> NetworkCheckResult:
        # Rule 16: If online_enabled == False, absolutely zero network requests are permitted
        if not self.online_enabled:
            return NetworkCheckResult(
                allowed=False,
                permission_level=NetworkPermissionLevel.NETWORK_BLOCKED,
                reason="Online Intelligence is currently DISABLED. Enable via '/online enable'.",
                target_domain=self.extract_domain(target_url)
            )

        # Rule 7: Prevent SSRF against localhost, private RFC1918, link-local, file://, UNC, hex/decimal IP, non-standard ports
        if self.is_ssrf_target(target_url):
            return NetworkCheckResult(
                allowed=False,
                permission_level=NetworkPermissionLevel.NETWORK_BLOCKED,
                reason=f"SSRF Protection: Outbound connection to internal host/IP, non-HTTPS scheme, or non-standard port blocked: '{target_url}'",
                target_domain=""
            )

        domain = self.extract_domain(target_url)
        if not domain:
            return NetworkCheckResult(
                allowed=False,
                permission_level=NetworkPermissionLevel.NETWORK_BLOCKED,
                reason="Invalid target URL or domain format.",
                target_domain=""
            )

        # Rule 5: Approved Cybersecurity API domain allowlist
        for approved in APPROVED_INTEL_DOMAINS:
            if domain == approved or domain.endswith("." + approved):
                return NetworkCheckResult(
                    allowed=True,
                    permission_level=NetworkPermissionLevel.NETWORK_READ_ONLY,
                    reason=f"Approved cybersecurity intelligence domain: '{domain}'.",
                    target_domain=domain
                )

        # Unknown destination requires user confirmation
        if is_user_confirmed:
            return NetworkCheckResult(
                allowed=True,
                permission_level=NetworkPermissionLevel.NETWORK_CONFIRMATION_REQUIRED,
                reason=f"User explicitly authorized query to domain: '{domain}'.",
                target_domain=domain
            )

        return NetworkCheckResult(
            allowed=False,
            permission_level=NetworkPermissionLevel.NETWORK_CONFIRMATION_REQUIRED,
            reason=f"Domain '{domain}' is not in approved provider allowlist. Requires explicit user confirmation.",
            target_domain=domain
        )
