import uuid
from typing import Dict, List, Any, Optional
from lala.intelligence.manager import IntelligenceManager
from lala.intelligence.correlation import IOCCorrelationEngine
from lala.intelligence.models import IOC, IOCType
from lala.investigation.models import (
    InvestigationCase, InvestigationTarget, SeverityLevel, CaseStatus, RiskScore
)
from lala.investigation.manager import InvestigationManager
from lala.investigation.scoring import ThreatScoringEngine
from lala.detection.static_analysis import LocalStaticAnalyzer
from lala.detection.yara_engine import YaraEngine
from lala.remediation.recommendation import RemediationRecommendationEngine

class InvestigationEngine:
    """
    Central Cybersecurity Investigation, Detection & Threat Correlation Engine for LALA Phase 7.
    Orchestrates target analysis, intel enrichment, YARA scanning, static analysis, threat scoring, and report generation.
    """
    def __init__(self, intel_manager: Optional[IntelligenceManager] = None):
        self.intel_manager = intel_manager or IntelligenceManager()
        self.case_manager = InvestigationManager()
        self.correlation_engine = IOCCorrelationEngine()
        self.scoring_engine = ThreatScoringEngine()
        self.static_analyzer = LocalStaticAnalyzer()
        self.yara_engine = YaraEngine()
        self.recommendation_engine = RemediationRecommendationEngine()

    def determine_target_type(self, value: str) -> str:
        v = value.strip()
        if len(v) in [32, 40, 64] and all(c in "0123456789abcdefABCDEF" for c in v):
            return "HASH"
        elif v.replace(".", "").isdigit() and v.count(".") == 3:
            return "IP"
        elif "://" in v or v.startswith("www."):
            return "URL" if "://" in v or "/" in v else "DOMAIN"
        elif "." in v and not v.endswith(".py"):
            return "DOMAIN"
        else:
            return "FILE"

    def investigate(self, target_value: str, is_user_confirmed: bool = False) -> InvestigationCase:
        target_type = self.determine_target_type(target_value)
        case = self.case_manager.create_case(f"Investigation: {target_type} {target_value}")
        case.target = InvestigationTarget(value=target_value, target_type=target_type)

        # 1. Threat Intelligence Enrichment
        intel_res = self.intel_manager.lookup_indicator(target_type, target_value, is_user_confirmed=is_user_confirmed)
        self.case_manager.add_evidence(
            ioc_value=target_value,
            evidence_type=target_type,
            source=intel_res.provider,
            details=intel_res.raw_metadata
        )

        # 2. Local Static Analysis / YARA Scan if target is a file or local path
        yara_matches_count = 0
        if target_type == "FILE" and self.yara_engine.is_path_authorized(target_value):
            try:
                static_res = self.static_analyzer.analyze_file(target_value)
                yara_matches_count = len(static_res.yara_matches)
                self.case_manager.add_evidence(
                    ioc_value=target_value,
                    evidence_type="LOCAL_STATIC_ANALYSIS",
                    source="LocalStaticAnalyzer",
                    details=static_res.model_dump()
                )
            except Exception:
                pass

        # 3. Deterministic Threat Risk Scoring
        risk = self.scoring_engine.calculate_score(
            verdict=intel_res.verdict.value,
            provider_count=1 if intel_res.verdict.value != "UNKNOWN" else 0,
            yara_matches_count=yara_matches_count
        )
        case.risk_score = risk
        case.severity = risk.level

        # 4. Generate Recommendations
        recs = self.recommendation_engine.generate_recommendations(
            ioc_type=target_type,
            target=target_value,
            severity=risk.level,
            yara_matched=(yara_matches_count > 0)
        )
        case.recommendations = recs

        self.case_manager.save_case(case)
        return case
