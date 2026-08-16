from typing import List, Dict, Any
from lala.investigation.models import RiskScore, SeverityLevel

class ThreatScoringEngine:
    """
    Deterministic Threat Risk Scoring Engine for LALA Phase 7.
    Calculates threat risk scores programmatically based on empirical evidence factors.
    Prevents LLM hallucination of risk scores.
    """
    def calculate_score(
        self,
        verdict: str = "UNKNOWN",
        provider_count: int = 0,
        is_cisa_kev: bool = False,
        has_malware_family: bool = False,
        has_mitre_attack: bool = False,
        yara_matches_count: int = 0,
        cvss_score: float = 0.0
    ) -> RiskScore:
        score = 0.0
        factors: List[str] = []

        # 1. Base Verdict
        v_upper = verdict.upper()
        if v_upper == "MALICIOUS":
            score += 40.0
            factors.append("Provider reputation verdict: MALICIOUS (+40)")
        elif v_upper == "SUSPICIOUS":
            score += 25.0
            factors.append("Provider reputation verdict: SUSPICIOUS (+25)")

        # 2. Multi-provider confirmation
        if provider_count > 1:
            prov_bonus = min(provider_count * 10.0, 30.0)
            score += prov_bonus
            factors.append(f"Confirmed by {provider_count} independent sources (+{prov_bonus})")

        # 3. CISA KEV Status
        if is_cisa_kev:
            score += 30.0
            factors.append("Listed in CISA Known Exploited Vulnerabilities (+30)")

        # 4. Malware Family association
        if has_malware_family:
            score += 20.0
            factors.append("Associated with known malware family (+20)")

        # 5. ATT&CK Technique association
        if has_mitre_attack:
            score += 15.0
            factors.append("Mapped to MITRE ATT&CK technique (+15)")

        # 6. YARA Rule Matches
        if yara_matches_count > 0:
            yara_bonus = min(yara_matches_count * 20.0, 40.0)
            score += yara_bonus
            factors.append(f"Matched {yara_matches_count} local YARA detection rules (+{yara_bonus})")

        # 7. CVSS Vulnerability Score
        if cvss_score > 0.0:
            cvss_bonus = cvss_score * 3.0 # e.g. CVSS 10.0 -> +30
            score += cvss_bonus
            factors.append(f"CVSS Score {cvss_score} (+{cvss_bonus})")

        # Cap score between 0 and 100
        final_score = min(max(score, 0.0), 100.0)

        # Determine Severity Level
        if final_score >= 75.0:
            level = SeverityLevel.CRITICAL
        elif final_score >= 50.0:
            level = SeverityLevel.HIGH
        elif final_score >= 25.0:
            level = SeverityLevel.MEDIUM
        elif final_score > 0.0:
            level = SeverityLevel.LOW
        else:
            level = SeverityLevel.UNKNOWN

        return RiskScore(score=round(final_score, 1), level=level, factors=factors)
