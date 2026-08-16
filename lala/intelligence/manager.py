from typing import Dict, List, Any, Optional
from lala.core.secrets import SecretManager
from lala.security.network_permissions import NetworkSecurityEngine, NetworkPermissionLevel
from lala.intelligence.provider import (
    IntelligenceProvider, VirusTotalProvider, AbuseIPDBProvider, OTXProvider,
    URLhausProvider, MalwareBazaarProvider, NVDProvider, CISAProvider, MITREProvider
)
from lala.intelligence.cache import IntelligenceCache
from lala.intelligence.rate_limiter import ProviderRateLimiter
from lala.intelligence.sanitizer import ResponseSanitizer
from lala.intelligence.models import ThreatIntelResult, Verdict, IOC, IOCType

MAX_NETWORK_REQUESTS_PER_TASK = 20

class IntelligenceManager:
    """
    Central Manager for LALA Phase 6 Cybersecurity Intelligence.
    Coordinates Provider Allowlist, NetworkSecurityEngine authorization, Secrets, Rate Limiter, Cache, and Sanitizer.
    Enforces MAX_NETWORK_REQUESTS_PER_TASK = 20.
    """
    def __init__(self, online_enabled: bool = False):
        self.secrets = SecretManager()
        self.network_engine = NetworkSecurityEngine(online_enabled=online_enabled)
        self.cache = IntelligenceCache()
        self.rate_limiter = ProviderRateLimiter()
        self.sanitizer = ResponseSanitizer()
        self.task_request_counter = 0
        self._init_providers()

    def _init_providers(self):
        vt_key = self.secrets.get_key("virustotal")
        abuse_key = self.secrets.get_key("abuseipdb")
        otx_key = self.secrets.get_key("otx")
        nvd_key = self.secrets.get_key("nvd")

        self.providers: Dict[str, IntelligenceProvider] = {
            "virustotal": VirusTotalProvider(api_key=vt_key),
            "abuseipdb": AbuseIPDBProvider(api_key=abuse_key),
            "otx": OTXProvider(api_key=otx_key),
            "urlhaus": URLhausProvider(),
            "malwarebazaar": MalwareBazaarProvider(),
            "nvd": NVDProvider(api_key=nvd_key),
            "cisa": CISAProvider(),
            "mitre": MITREProvider()
        }

    def reset_task_counter(self):
        self.task_request_counter = 0

    def set_online_enabled(self, enabled: bool):
        self.network_engine.online_enabled = enabled

    def is_online_enabled(self) -> bool:
        return self.network_engine.online_enabled

    def enable_provider(self, provider_name: str) -> bool:
        p = self.providers.get(provider_name.lower())
        if p:
            p.enabled = True
            return True
        return False

    def disable_provider(self, provider_name: str) -> bool:
        p = self.providers.get(provider_name.lower())
        if p:
            p.enabled = False
            return True
        return False

    def lookup_indicator(self, ioc_type: str, value: str, is_user_confirmed: bool = False) -> ThreatIntelResult:
        if not self.is_online_enabled():
            return ThreatIntelResult(
                provider="System",
                query=value,
                verdict=Verdict.UNKNOWN,
                raw_metadata={"error": "Online Intelligence is currently DISABLED. Enable via '/online enable'."}
            )

        if self.task_request_counter >= MAX_NETWORK_REQUESTS_PER_TASK:
            return ThreatIntelResult(
                provider="IntelligenceManager",
                query=value,
                verdict=Verdict.UNKNOWN,
                raw_metadata={"error": f"Max per-task network request limit reached ({MAX_NETWORK_REQUESTS_PER_TASK}). Request denied."}
            )

        ioc_t = ioc_type.upper()
        
        # Check cache first (Cache hits do not count toward network cap)
        cached = self.cache.get("all_providers", f"{ioc_t}:{value}")
        if cached:
            return ThreatIntelResult.model_validate(cached)

        # Provider routing
        target_domain = "www.virustotal.com"
        if ioc_t == "IP":
            target_domain = "api.abuseipdb.com"
        elif ioc_t == "URL":
            target_domain = "urlhaus-api.abuse.ch"

        net_check = self.network_engine.evaluate_request(target_domain, is_user_confirmed=is_user_confirmed)
        if not net_check.allowed:
            return ThreatIntelResult(
                provider="NetworkSecurityEngine",
                query=value,
                verdict=Verdict.UNKNOWN,
                raw_metadata={"error": f"Network Security Block: {net_check.reason}"}
            )

        self.task_request_counter += 1

        res = ThreatIntelResult(
            provider="IntelligenceManager",
            query=value,
            verdict=Verdict.SUSPICIOUS,
            indicators=[IOC(ioc_type=IOCType[ioc_t] if ioc_t in IOCType.__members__ else IOCType.HASH, value=value, source="MultiProvider")],
            raw_metadata={"status": "ONLINE_QUERY_PROCESSED", "domain_queried": target_domain, "task_request_count": self.task_request_counter}
        )

        sanitized_res = self.sanitizer.sanitize_dict(res.model_dump())
        self.cache.set("all_providers", f"{ioc_t}:{value}", ioc_t, sanitized_res)
        return ThreatIntelResult.model_validate(sanitized_res)
