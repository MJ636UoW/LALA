from typing import List, Dict, Any, Optional
from lala.automation.models import ProposedAction, ActionClass
from lala.automation.policy import AutomationPolicyEngine

class AutomationPlanner:
    """
    Structured Action Planner for LALA Phase 10.
    Proposes structured investigation and analysis steps using registered LALA tool names.
    All proposals pass through AutomationPolicyEngine and SecurityEngine before execution.
    """
    def __init__(self, policy: Optional[AutomationPolicyEngine] = None):
        self.policy = policy or AutomationPolicyEngine()

    def propose_investigation_steps(self, target: str) -> List[ProposedAction]:
        proposals = [
            ProposedAction(
                action="workspace_scan",
                target=target,
                risk_class=ActionClass.READ_ONLY,
                reason="Collect initial workspace metadata, hashes, and size."
            ),
            ProposedAction(
                action="search_rag",
                target=target,
                risk_class=ActionClass.READ_ONLY,
                reason="Search local offline cybersecurity RAG knowledge base."
            ),
            ProposedAction(
                action="yara_scan",
                target=target,
                risk_class=ActionClass.ANALYSIS,
                reason="Execute local YARA signature scan."
            ),
            ProposedAction(
                action="security_scan",
                target=target,
                risk_class=ActionClass.ANALYSIS,
                reason="Calculate Shannon entropy and inspect safe static AST."
            ),
            ProposedAction(
                action="threat_scoring",
                target=target,
                risk_class=ActionClass.ANALYSIS,
                reason="Calculate deterministic threat score."
            )
        ]
        return proposals
