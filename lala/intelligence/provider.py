from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from lala.intelligence.models import ThreatIntelResult, Verdict, IOC, IOCType

class IntelligenceProvider(ABC):
    """Abstract Base Class for all LALA Cybersecurity Intelligence Providers."""
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.enabled = True

    @abstractmethod
    def authenticate(self) -> bool:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

    def lookup_ip(self, ip_address: str) -> ThreatIntelResult:
        return ThreatIntelResult(provider=self.name, query=ip_address, verdict=Verdict.UNKNOWN)

    def lookup_domain(self, domain: str) -> ThreatIntelResult:
        return ThreatIntelResult(provider=self.name, query=domain, verdict=Verdict.UNKNOWN)

    def lookup_url(self, url: str) -> ThreatIntelResult:
        return ThreatIntelResult(provider=self.name, query=url, verdict=Verdict.UNKNOWN)

    def lookup_hash(self, hash_value: str) -> ThreatIntelResult:
        return ThreatIntelResult(provider=self.name, query=hash_value, verdict=Verdict.UNKNOWN)

    def search(self, query: str) -> ThreatIntelResult:
        return ThreatIntelResult(provider=self.name, query=query, verdict=Verdict.UNKNOWN)

    def normalize_response(self, raw_data: Dict[str, Any]) -> ThreatIntelResult:
        return ThreatIntelResult(provider=self.name, query=str(raw_data.get("query", "")), raw_metadata=raw_data)

class VirusTotalProvider(IntelligenceProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="VirusTotal", api_key=api_key)

    def authenticate(self) -> bool:
        return bool(self.api_key)

    def health_check(self) -> bool:
        return bool(self.api_key)

    def lookup_hash(self, hash_value: str) -> ThreatIntelResult:
        return ThreatIntelResult(
            provider=self.name,
            query=hash_value,
            verdict=Verdict.SUSPICIOUS if self.api_key else Verdict.UNKNOWN,
            indicators=[IOC(ioc_type=IOCType.HASH, value=hash_value, source=self.name)],
            references=["https://www.virustotal.com"]
        )

class AbuseIPDBProvider(IntelligenceProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="AbuseIPDB", api_key=api_key)

    def authenticate(self) -> bool:
        return bool(self.api_key)

    def health_check(self) -> bool:
        return bool(self.api_key)

    def lookup_ip(self, ip_address: str) -> ThreatIntelResult:
        return ThreatIntelResult(
            provider=self.name,
            query=ip_address,
            verdict=Verdict.SUSPICIOUS if self.api_key else Verdict.UNKNOWN,
            indicators=[IOC(ioc_type=IOCType.IP, value=ip_address, source=self.name)],
            references=["https://www.abuseipdb.com"]
        )

class OTXProvider(IntelligenceProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="AlienVault OTX", api_key=api_key)

    def authenticate(self) -> bool:
        return True # OTX allows unauthenticated basic queries or key-based

    def health_check(self) -> bool:
        return True

class URLhausProvider(IntelligenceProvider):
    def __init__(self):
        super().__init__(name="URLhaus")

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def lookup_url(self, url: str) -> ThreatIntelResult:
        return ThreatIntelResult(
            provider=self.name,
            query=url,
            verdict=Verdict.UNKNOWN,
            indicators=[IOC(ioc_type=IOCType.URL, value=url, source=self.name)]
        )

class MalwareBazaarProvider(IntelligenceProvider):
    def __init__(self):
        super().__init__(name="MalwareBazaar")

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def lookup_hash(self, hash_value: str) -> ThreatIntelResult:
        return ThreatIntelResult(
            provider=self.name,
            query=hash_value,
            verdict=Verdict.UNKNOWN,
            indicators=[IOC(ioc_type=IOCType.HASH, value=hash_value, source=self.name)]
        )

class NVDProvider(IntelligenceProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="NVD", api_key=api_key)

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

class CISAProvider(IntelligenceProvider):
    def __init__(self):
        super().__init__(name="CISA KEV")

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

class MITREProvider(IntelligenceProvider):
    def __init__(self):
        super().__init__(name="MITRE ATT&CK")

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True
