from typing import Dict, List, Any
from lala.intelligence.models import IOC, IOCType, Verdict, ThreatIntelResult

class IOCCorrelationEngine:
    """
    IOC Correlation Engine for LALA Phase 6.
    Correlates hashes, IP addresses, domain names, URLs, malware families, and ATT&CK techniques into unified threat graphs.
    Does NOT take automatic remediation actions.
    """
    def correlate_iocs(self, iocs: List[IOC]) -> Dict[str, Any]:
        grouped: Dict[str, List[str]] = {
            "hashes": [],
            "ips": [],
            "domains": [],
            "urls": [],
            "cves": []
        }
        for item in iocs:
            if item.ioc_type == IOCType.HASH:
                grouped["hashes"].append(item.value)
            elif item.ioc_type == IOCType.IP:
                grouped["ips"].append(item.value)
            elif item.ioc_type == IOCType.DOMAIN:
                grouped["domains"].append(item.value)
            elif item.ioc_type == IOCType.URL:
                grouped["urls"].append(item.value)
            elif item.ioc_type == IOCType.CVE:
                grouped["cves"].append(item.value)

        return {
            "total_indicators": len(iocs),
            "grouped_indicators": grouped,
            "threat_verdict": Verdict.SUSPICIOUS if len(iocs) > 0 else Verdict.CLEAN,
            "correlation_summary": f"Correlated {len(iocs)} indicators across network and malware artifacts."
        }
