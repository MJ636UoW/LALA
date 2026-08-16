from typing import List
from lala.investigation.models import SeverityLevel
from lala.remediation.policy import RemediationActionType

class RemediationRecommendationEngine:
    """
    Remediation Recommendation Generator for LALA Phase 7.
    Generates recommended defensive actions based on threat severity and evidence.
    Actions remain RECOMMENDATIONS ONLY and require user approval before execution.
    """
    def generate_recommendations(self, ioc_type: str, target: str, severity: SeverityLevel, yara_matched: bool = False) -> List[str]:
        recs = []
        ioc_t = ioc_type.upper()

        if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            if ioc_t == "IP":
                recs.append(f"[RECOMMENDATION] Block IP address '{target}' in perimeter firewall (Requires /confirm).")
                recs.append(f"[RECOMMENDATION] Review active network connections matching IP '{target}'.")
            elif ioc_t in ["DOMAIN", "URL"]:
                recs.append(f"[RECOMMENDATION] Block domain/URL '{target}' at DNS/Proxy level (Requires /confirm).")
            elif ioc_t == "HASH" or yara_matched:
                recs.append(f"[RECOMMENDATION] Quarantine file associated with hash '{target}' (Requires /confirm).")
                recs.append(f"[RECOMMENDATION] Scan all workspace hosts for hash '{target}'.")

            recs.append("[RECOMMENDATION] Audit user authentication logs for credential reuse.")
        else:
            recs.append(f"[RECOMMENDATION] Continue monitoring target '{target}' for suspicious activity.")
            recs.append("[RECOMMENDATION] Keep threat intelligence cache updated.")

        return recs
